import os

import pymysql
from dotenv import load_dotenv
from pymysql.cursors import DictCursor

load_dotenv(".env")

class DB:
    def __init__(self):
        self.__config = {"host": os.environ.get("DB_HOST", "localhost"),
                         "user": os.environ.get("DB_USER", "username"),
                         "password": os.environ.get("DB_PASSWORD", "password"),
                         "database": os.environ.get("DB_DATABASE", "sakila"),
                         "cursorclass": DictCursor}

        # self.__conn = None
        # self.__cursor = None

    @property
    def cursor(self):
        return self.__cursor

    def __enter__(self):
        self.__conn = pymysql.connect(**self.__config)
        self.__cursor = self.__conn.cursor()
        print("MySQL Connection successful!")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.__cursor:
            self.__cursor.close()
        if self.__conn:
            if exc_type:
                self.__conn.rollback()
            else:
                self.__conn.commit()
            self.__conn.close()
            print("MySQL Connection closed.")
