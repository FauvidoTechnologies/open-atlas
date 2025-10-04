# Database files

This directory holds the files for database configs

- [ ] models.py -> Database schemas for all the databases (under progress)
- [x] sqlite_setup.py -> Database creation functions for SQLiteDB
- [x] postgres_setup.py -> Database creation functions for PostgreSQL
- [x] mysql_setup.py -> Database creation functions for MySQL
- [x] database.py -> Functions to query the database


Querying the database is done seperately for SQLAlchemy (the ORM used for MySQL and PostgreSQL) and APSW (lower-level wrapper for SQLite3). The default database is SQLite since it doesn't require a lot of configurations from the user's end.

For switching databases, please refer to the configuration file.