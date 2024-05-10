import psycopg

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

    def get_connection(self):
        return self._connection
