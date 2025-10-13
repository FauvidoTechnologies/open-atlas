import time

import apsw
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from oatlas.config import Database, Config
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
