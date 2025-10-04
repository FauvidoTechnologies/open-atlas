from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

from oatlas.config import Database
from oatlas.tools.nettacker.core.database.models import Base


def postgres_create_database():
    """
    Database creation for a postgresql database
    """
    try:
        engine = create_engine(
            "postgresql+psycopg2://{username}:{password}@{host}:{port}/{name}".format(
                **Database.as_dict()
            )
        )
        Base.metadata.create_all(engine)
    except OperationalError:
        # if the database does not exist, revert to the default
        engine = create_engine(
            "postgresql+psycopg2://{username}:{password}@{host}:{port}/postgres".format(
                **Database.as_dict()
            )
        )
        conn = engine.connect()
        conn = conn.execution_options(isolation_level="AUTOCOMMIT")
        conn.execute(text(f"CREATE DATABASE {Database.name}"))
        conn.close()
        engine = create_engine(
            "postgresql+psycopg2://{username}:{password}@{host}:{port}/{name}".format(
                **Database.as_dict()
            )
        )
        Base.metadata.create_all(engine)
