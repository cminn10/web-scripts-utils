import sqlite3
from config import DB_PATH


class Blog_db_utils:
    def __init__(self):
        self.db = DB_PATH
        self.conn = None

    def connect(self):
        self.conn = sqlite3.connect(self.db)
        self.conn.row_factory = sqlite3.Row

    def execute_query(self, query, params=None):
        cursor = self.conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        dict_result = [dict(row) for row in result]
        cursor.close()
        return dict_result

    def execute_update(self, query, params=None):
        cursor = self.conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        self.conn.commit()
        cursor.close()

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
