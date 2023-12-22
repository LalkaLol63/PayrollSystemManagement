import psycopg2
from psycopg2.extras import DictCursor


class DBManager:
    def __init__(self, db):
        self._db = db

    def execute_query(self, query, params=None):
        try:
            with self._db.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except psycopg2.Error as e:
            print("Error executing query: " + str(e))
            return []
