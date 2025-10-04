"""
Database packet for Atlas. Importing functions for easier access
"""

from oatlas.tools.nettacker.core.database.models import (
    HostsLog,
    TempEvents,
)
from oatlas.tools.nettacker.core.database.mysql_setup import (
    mysql_create_database,
    mysql_create_tables,
)
from oatlas.tools.nettacker.core.database.postgres_setup import postgres_create_database
from oatlas.tools.nettacker.core.database.sqlite_setup import sqlite_create_tables
