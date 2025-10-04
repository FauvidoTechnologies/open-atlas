import json
import time

import apsw
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from oatlas.config import Database, Config
from oatlas.logger import get_logger
from oatlas.tools.nettacker.core.database import HostsLog, TempEvents
from oatlas.tools.nettacker.core.messages import messages

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


def create_connection():
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


# ----------------------------------------------------
#               Nettacker functions
# ----------------------------------------------------


# This is in the core architecture, will let it be for now
def remove_old_logs(options):
    """
    this function remove old events (and duplicated)
    from nettacker.database based on target, module, scan_id

    Args:
        options: identifiers

    Returns:
        True if success otherwise False
    """
    session = create_connection()
    if isinstance(session, tuple):
        connection, cursor = session

        try:
            cursor.execute("BEGIN")
            cursor.execute(
                """
                DELETE FROM scan_events
                    WHERE target = ?
                      AND module_name = ?
                      AND scan_unique_id != ?
                """,
                (
                    options["target"],
                    options["module_name"],
                    options["scan_id"],
                ),
            )
            return send_submit_query(session)
        except Exception:
            cursor.execute("ROLLBACK")
            logging.warn("Could not remove old logs...")
            return False
        finally:
            cursor.close()
            connection.close()
    else:
        session.query(HostsLog).filter(
            HostsLog.target == options["target"],
            HostsLog.module_name == options["module_name"],
            HostsLog.scan_unique_id != options["scan_id"],
            # Don't remove old logs if they are to be used for the scan reports
        ).delete(synchronize_session=False)
        return send_submit_query(session)


# All the below functions are important because they are part of the core architecture
def submit_logs_to_db(log):
    """
    this function created to submit new events into database.
    This requires a little more robust handling in case of
    APSW in order to avoid database lock issues.

    Args:
        log: log event in JSON type

    Returns:
        True if success otherwise False
    """

    if isinstance(log, dict):
        session = create_connection()
        if isinstance(session, tuple):
            connection, cursor = session
            try:
                for _ in range(Config.nettacker.max_retries):
                    try:
                        if not connection.in_transaction:
                            connection.execute("BEGIN")
                        cursor.execute(
                            """
                            INSERT INTO scan_events (target, date, module_name, scan_unique_id, port, event, json_event)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                log["target"],
                                str(log["date"]),
                                log["module_name"],
                                log["scan_id"],
                                json.dumps(log["port"]),
                                json.dumps(log["event"]),
                                json.dumps(log["json_event"]),
                            ),
                        )
                        return send_submit_query(session)

                    except apsw.BusyError as e:
                        if "database is locked" in str(e).lower():
                            logging.warn(
                                f"[Retry {_ + 1}/{Config.nettacker.max_retries}] Database is locked. Retrying..."
                            )
                            if connection.in_transaction:
                                connection.execute("ROLLBACK")
                            time.sleep(Config.nettacker.retry_delay)
                            continue
                        else:
                            if connection.in_transaction:
                                connection.execute("ROLLBACK")
                            return False
                    except Exception:
                        try:
                            if connection.in_transaction:
                                connection.execute("ROLLBACK")
                        except Exception:
                            pass
                        return False
                # All retires exhausted but we want to continue operation
                logging.warn("All retries exhausted. Skipping this log.")
                return True
            finally:
                cursor.close()
                connection.close()

        else:
            session.add(
                HostsLog(
                    target=log["target"],
                    date=log["date"],
                    module_name=log["module_name"],
                    scan_unique_id=log["scan_id"],
                    port=json.dumps(log["port"]),
                    event=json.dumps(log["event"]),
                    json_event=json.dumps(log["json_event"]),
                )
            )
            return send_submit_query(session)
    else:
        logging.warn(messages("invalid_json_type_to_db").format(log))
        return False


def submit_temp_logs_to_db(log):
    """
    this function created to submit new events into database.
    This requires a little more robust handling in case of
    APSW in order to avoid database lock issues.

    Args:
        log: log event in JSON type

    Returns:
        True if success otherwise False
    """
    if isinstance(log, dict):
        session = create_connection()
        if isinstance(session, tuple):
            connection, cursor = session

            try:
                for _ in range(Config.nettacker.max_retries):
                    try:
                        if not connection.in_transaction:
                            cursor.execute("BEGIN")
                        cursor.execute(
                            """
                            INSERT INTO temp_events (target, date, module_name, scan_unique_id, event_name, port, event, data)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                log["target"],
                                str(log["date"]),
                                log["module_name"],
                                log["scan_id"],
                                log["event_name"],
                                json.dumps(log["port"]),
                                json.dumps(log["event"]),
                                json.dumps(log["data"]),
                            ),
                        )
                        return send_submit_query(session)
                    except apsw.BusyError as e:
                        if "database is locked" in str(e).lower():
                            logging.warn(
                                f"[Retry {_ + 1}/{Config.nettacker.max_retries}] Database is locked. Retrying..."
                            )
                            try:
                                if connection.in_transaction:
                                    connection.execute("ROLLBACK")
                            except Exception:
                                pass
                            time.sleep(Config.nettacker.retry_delay)
                            continue
                        else:
                            try:
                                if connection.in_transaction:
                                    connection.execute("ROLLBACK")
                            except Exception:
                                pass
                            return False
                    except Exception:
                        try:
                            if connection.in_transaction:
                                connection.execute("ROLLBACK")
                        except Exception:
                            pass
                        return False
                # All retires exhausted but we want to continue operation
                logging.warn("All retries exhausted. Skipping this log.")
                return True
            finally:
                cursor.close()
                connection.close()
        else:
            session.add(
                TempEvents(
                    target=log["target"],
                    date=log["date"],
                    module_name=log["module_name"],
                    scan_unique_id=log["scan_id"],
                    event_name=log["event_name"],
                    port=json.dumps(log["port"]),
                    event=json.dumps(log["event"]),
                    data=json.dumps(log["data"]),
                )
            )
            return send_submit_query(session)
    else:
        logging.warn(messages("invalid_json_type_to_db").format(log))
        return False


def find_temp_events(target, module_name, scan_id, event_name):
    """
    select all events by scan_unique id, target, module_name

    Args:
        target: target
        module_name: module name
        scan_id: unique scan identifier
        event_name: event_name

    Returns:
        an array with JSON events or an empty array
    """
    session = create_connection()
    if isinstance(session, tuple):
        connection, cursor = session
        try:
            cursor.execute(
                """
                SELECT event
                FROM temp_events
                WHERE target = ? AND module_name = ? AND scan_unique_id = ? AND event_name = ?
                LIMIT 1
            """,
                (target, module_name, scan_id, event_name),
            )

            row = cursor.fetchone()
            cursor.close()
            connection.close()
            if row:
                return row[0]
            return []
        except Exception:
            logging.warn(messages("database_connect_fail"))
            return []
        return []
    else:
        result = (
            session.query(TempEvents)
            .filter(
                TempEvents.target == target,
                TempEvents.module_name == module_name,
                TempEvents.scan_unique_id == scan_id,
                TempEvents.event_name == event_name,
            )
            .first()
        )

        return result.event if result else []


def find_events(target, module_name, scan_id):
    """
    select all events by scan_unique id, target, module_name

    Args:
        target: target
        module_name: module name
        scan_id: unique scan identifier

    Returns:
        an array with JSON events or an empty array
    """
    session = create_connection()
    if isinstance(session, tuple):
        connection, cursor = session

        try:
            cursor.execute(
                """
                SELECT json_event FROM scan_events
                WHERE target = ? AND module_name = ? and scan_unique_id = ?
                """,
                (target, module_name, scan_id),
            )

            rows = cursor.fetchall()
            cursor.close()
            connection.close()
            if rows:
                return [json.dumps((json.loads(row[0]))) for row in rows]
            return []
        except Exception:
            logging.warn("Database query failed...")
            return []
    else:
        return [
            row.json_event
            for row in session.query(HostsLog)
            .filter(
                HostsLog.target == target,
                HostsLog.module_name == module_name,
                HostsLog.scan_unique_id == scan_id,
            )
            .all()
        ]


# This funciton MIGHT be useful but I am not 100% sure if I will need to. So keeping this here for now
def logs_to_report_json(target):
    """
    select all reports of a host

    Args:
        host: the host to search

    Returns:
        an array with JSON events or an empty array
    """
    try:
        session = create_connection()
        if isinstance(session, tuple):
            connection, cursor = session
            return_logs = []

            cursor.execute(
                """
                SELECT scan_unique_id, target, port, event, json_event
                FROM scan_events WHERE target = ?
                """,
                (target,),
            )
            rows = cursor.fetchall()
            cursor.close()
            connection.close()
            if rows:
                for log in rows:
                    data = {
                        "scan_id": log[0],
                        "target": log[1],
                        "port": json.loads(log[2]),
                        "event": json.loads(log[3]),
                        "json_event": json.loads(log[4]),
                    }
                    return_logs.append(data)
                return return_logs

        else:
            return_logs = []
            logs = session.query(HostsLog).filter(HostsLog.target == target)
            for log in logs:
                data = {
                    "scan_id": log.scan_unique_id,
                    "target": log.target,
                    "port": json.loads(log.port),
                    "event": json.loads(log.event),
                    "json_event": json.loads(log.json_event),
                }
                return_logs.append(data)
            return return_logs

    except Exception:
        return []
