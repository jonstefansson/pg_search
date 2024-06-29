import logging
import psycopg
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

"""
Creating a singleton database connection in Python involves creating a class that ensures only a single instance
of the database connection is created. This can be achieved using the singleton design pattern. Here's a simple
example of how you can do this:

In this code, SingletonMeta is a metaclass that ensures only one instance of DatabaseConnection is created. The
DatabaseConnection class uses SingletonMeta as its metaclass and initializes a database connection if it hasn't
been initialized yet.

You can use the DatabaseConnection class like this:
db = DatabaseConnection('localhost', 'pgsearch', 'boston')
connection = db.get_connection()
"""


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class DatabaseConnection(metaclass=SingletonMeta):
    """
    You can use the DatabaseConnection class like this:

    db = DatabaseConnection('postgresql://boston@localhost/pgsearch')
    connection = db.get_connection()
    """
    _connection = None

    def __init__(self, db_url):
        if self._connection is None:
            self._connection = psycopg.connect(db_url)
            logging.getLogger('pg_search.database').debug('connected to %s', db_url)

    def get_connection(self):
        return self._connection


@dataclass
class Query:
    template_name: str
    template_params: Dict[str, Any]
    query_params: Optional[Dict[str, Any]]
    fetch_one: bool = field(init=True, default=False)

    def execute(self, conn):
        """
        param: conn: the database connection
        """
        from .support.template import get_template
        with conn.execute(
            get_template(self.template_name).render(self.template_params),
            self.query_params
        ) as cur:
            if self.fetch_one:
                return cur.fetchone()
            else:
                return cur.fetchall()
