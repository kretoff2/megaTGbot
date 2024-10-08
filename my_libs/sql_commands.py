import sqlite3 as sql

def sql_conn():
    conn = sql.connect("db.sql")
    return conn

class SQL_connection():
    def __init__(self):
        self.conn = sql_conn()
        self.cur = self.conn.cursor()
    def sql_command(self, SQL:str, args:tuple):
        self.cur.execute(SQL, args)
    def SQL_fetchone(self, SQL:str, args:tuple) -> tuple:
        self.sql_command(SQL, args)
        data = self.cur.fetchone()
        return data
    def SQL_fetchall(self, SQL:str, args:tuple) -> list:
        self.sql_command(SQL, args)
        data = self.cur.fetchall()
        return data
    def sql_save(self):
        self.conn.commit()
    def sql_close(self):
        self.cur.close()
        self.conn.close()
class SQL_one_command():
    def __init__(self, SQL:str, args:tuple, commit = False, fetchMode: None | str = None):
        self.conn = sql_conn()
        self.cur = self.conn.cursor()
        self.cur.execute(SQL, args)
        if commit:
            self.conn.commit()
        self.data = None
        match fetchMode:
            case "all":
                self.data = self.cur.fetchall()
            case "one":
                self.data = self.cur.fetchone()
        self.cur.close()
        self.conn.close()