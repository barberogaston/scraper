from dataclasses import dataclass

import pymysql
import pymysql.cursors

from scraper.infrastructure.db.client import DatabaseClient


@dataclass
class MySQLConnectionData:
    user: str
    password: str
    host: str
    port: int
    database: str


class MySQLClient(DatabaseClient):
    def __init__(self, connection_data: MySQLConnectionData) -> None:
        self._connection = pymysql.connect(
            **connection_data.__dict__,
            cursorclass=pymysql.cursors.DictCursor
        )

    def execute(self, query: str) -> None:
        """Executes a query with no result."""
        with self._connection.cursor() as cursor:
            cursor.execute(query)
        self._connection.commit()
