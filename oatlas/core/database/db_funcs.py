import json
import time
from typing import Union, List, Dict

import apsw
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from oatlas.config import Database, Config
from oatlas.core.database.models import DBLogs
from oatlas.logger import get_logger

logging = get_logger()


def db_inputs(connection_type) -> str:
    """
    a function to determine the type of database the user wants to work with and
    selects the corresponding connection to the db. We ignore SQLite here because
    that is handled by APSW

    Args:
        connection_type: type of db we are working with

    Returns:
        corresponding command to connect to the db
    """
    context = Database.as_dict()
    return {
        "postgres": "postgresql+psycopg2://{username}:{password}@{host}:{port}/{name}?sslmode={ssl_mode}".format(
            **context
        ),
        "mysql": "mysql+pymysql://{username}:{password}@{host}:{port}/{name}".format(**context),
    }[connection_type]


def create_connection(Database):
    """
    For creating the database connection. Use APSW for SQLite database and
    SQLAlchemy for others.

    Returns:
        APSW: A tuple (connection, cursor) -> Either of them can be used to make commits
        SQLAlchemy: A session object
    """
    if Database.engine.startswith("sqlite"):
        # In case of sqlite, the name parameter is the database path
        DB_PATH = Database.as_dict()["name"]
        connection = apsw.Connection(DB_PATH)
        connection.setbusytimeout(int(Config.settings.timeout) * 100)
        cursor = connection.cursor()

        # Performance enhancing configurations. Put WAL cause that helps with concurrency
        cursor.execute(f"PRAGMA journal_mode={Database.journal_mode}")
        cursor.execute(f"PRAGMA synchronous={Database.synchronous_mode}")

        return connection, cursor

    else:
        db_engine = create_engine(
            db_inputs(Database.engine),
            connect_args={},
            pool_size=50,
            pool_pre_ping=True,
        )
        Session = sessionmaker(bind=db_engine)

        return Session()


def send_submit_query(session) -> bool:
    """
    a function to send submit based queries to db
    (such as insert and update or delete), it retries 100 times if
    connection returned an error.

    Args:
        session: session to commit, varies for APSW and SQLAlchemy

    Returns:
        True if submitted success otherwise False
    """
    if isinstance(session, tuple):
        connection, cursor = session
        for _ in range(100):
            try:
                cursor.execute("COMMIT")
                return True
            except Exception:
                cursor.execute("ROLLBACK")
                time.sleep(0.1)
            finally:
                cursor.close()
        cursor.close()
        logging.warn("database connection failed")
        return False
    else:
        try:
            for _ in range(1, 100):
                try:
                    session.commit()
                    return True
                except Exception:
                    time.sleep(0.1)
            logging.warn("database connection failed")
            return False
        except Exception:
            logging.warn("database connection failed")
            return False
        return False


def add_logs_to_database(
    session_id: str,
    function_name: str,
    function_output: str,
) -> bool:
    """
    Function to add logs to the DBLogs table. For each session_id, the function_called and
    function_output are maintained as stacks. If a record already exists, new logs are appended
    to the existing stack; otherwise, a new record is created.

    Args:
        session_id: Unique identifier for this run
        function_name: Name of the function being logged
        function_output: Output of the function being logged

    Returns:
        boolean indicating success or failure
    """
    session = create_connection(Database)
    if isinstance(session, tuple):
        connection, cursor = session
        try:
            cursor.execute("BEGIN")
            cursor.execute(
                "SELECT function_called, function_output FROM DBLogs WHERE session_id = ?",
                (session_id,),
            )
            record = cursor.fetchone()

            if record:
                current_functions, current_outputs = record
                try:
                    function_stack = json.loads(current_functions)
                    output_stack = json.loads(current_outputs)
                except json.JSONDecodeError:
                    function_stack = [current_functions] if current_functions else []
                    output_stack = [current_outputs] if current_outputs else []

                function_stack.append(function_name)
                output_stack.append(function_output)

                cursor.execute(
                    """
                    UPDATE DBLogs
                    SET function_called = ?, function_output = ?
                    WHERE session_id = ?
                    """,
                    (json.dumps(function_stack), json.dumps(output_stack), session_id),
                )

            else:
                cursor.execute(
                    """
                    INSERT INTO DBLogs (session_id, function_called, function_output)
                    VALUES (?, ?, ?)
                    """,
                    (session_id, json.dumps([function_name]), json.dumps([function_output])),
                )

            return send_submit_query(session)

        except Exception as e:
            cursor.execute("ROLLBACK")
            logging.warn(f"Could not add logs to DBLogs (SQLite): {e}")
            return False
        finally:
            cursor.close()

    else:
        try:
            record = session.query(DBLogs).filter_by(session_id=session_id).first()

            if record:
                try:
                    function_stack = json.loads(record.function_called)
                    output_stack = json.loads(record.function_output)
                except json.JSONDecodeError:
                    function_stack = [record.function_called] if record.function_called else []
                    output_stack = [record.function_output] if record.function_output else []

                function_stack.append(function_name)
                output_stack.append(function_output)

                record.function_called = json.dumps(function_stack)
                record.function_output = json.dumps(output_stack)

            else:
                new_entry = DBLogs(
                    session_id=session_id,
                    function_called=json.dumps([function_name]),
                    function_output=json.dumps([function_output]),
                )
                session.add(new_entry)

            return send_submit_query(session)

        except Exception as e:
            logging.warn(f"Could not add logs to DBLogs (SQLAlchemy): {e}")
            return False


def get_logs_from_database(
    session_id: str,
    k: int = -1,
) -> Union[List[Dict[str, str]], None]:
    """
    Function to retrieve the last `k` logs from the DBLogs table for a given session_id.
    The logs are maintained as stacks (function_called, function_output). This function
    returns the most recent `k` function-output pairs.

    Args:
        session_id: Unique identifier for this run
        k: Number of recent entries to fetch (-1 returns the entire stack)

    Returns:
        A list of dictionaries in the format:
            [
                {"function_called": "func1", "function_output": "output1"},
                {"function_called": "func2", "function_output": "output2"},
                ...
            ]
        or None if no logs are found or an error occurs.
    """
    session = create_connection(Database)
    if isinstance(session, tuple):
        connection, cursor = session
        try:
            cursor.execute(
                "SELECT function_called, function_output FROM DBLogs WHERE session_id = ?",
                (session_id,),
            )
            record = cursor.fetchone()

            if not record:
                logging.warn(f"No logs found for session_id: {session_id}")
                return None

            functions_raw, outputs_raw = record
            try:
                function_stack = json.loads(functions_raw)
                output_stack = json.loads(outputs_raw)
            except json.JSONDecodeError:
                function_stack = [functions_raw] if functions_raw else []
                output_stack = [outputs_raw] if outputs_raw else []

            if k != -1:
                function_stack = function_stack[-k:]
                output_stack = output_stack[-k:]

            return [
                {"function_called": f, "function_output": o}
                for f, o in zip(function_stack, output_stack)
            ]

        except Exception as e:
            logging.warn(f"Could not fetch logs from DBLogs (SQLite): {e}")
            return None
        finally:
            cursor.close()

    else:
        try:
            record = session.query(DBLogs).filter_by(session_id=session_id).first()

            if not record:
                logging.warn(f"No logs found for session_id: {session_id}")
                return None

            try:
                function_stack = json.loads(record.function_called)
                output_stack = json.loads(record.function_output)
            except json.JSONDecodeError:
                function_stack = [record.function_called] if record.function_called else []
                output_stack = [record.function_output] if record.function_output else []

            if k != -1:
                function_stack = function_stack[-k:]
                output_stack = output_stack[-k:]

            return [
                {"function_called": f, "function_output": o}
                for f, o in zip(function_stack, output_stack)
            ]

        except Exception as e:
            logging.warn(f"Could not fetch logs from DBLogs (SQLAlchemy): {e}")
            return None
