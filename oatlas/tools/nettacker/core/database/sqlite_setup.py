from sqlalchemy import create_engine

from oatlas.config import Database
from oatlas.tools.nettacker.core.database.models import Base


def sqlite_create_tables():
    """
    when using sqlite database, this is the function that is used to create
    the database schema for the first time when you run the nettacker module.

    """
    db_engine = create_engine(
        "sqlite:///{name}".format(**Database.as_dict()),
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(db_engine)
