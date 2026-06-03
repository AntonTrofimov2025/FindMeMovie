# pylint: disable=line-too-long

"""
MySQL Database Connection and Transaction Management Module.

Handles configuration bootstrapping, stateful cursor provisioning, and clean
session commit/rollback workflows for the relational data storage layer.
"""

import os

import pymysql
from dotenv import load_dotenv
from pymysql.cursors import DictCursor

load_dotenv(".env")

class DB:
    """
    Context manager wrapper for ACID-compliant MySQL database operations.

    Ingests environment parameters, instantiates active connection pools,
    manages transactional commit/rollback cycles, and guarantees resource closure.
    """
    def __init__(self):
        self.__config = {"host": os.environ.get("DB_HOST", "localhost"),
                         "user": os.environ.get("DB_USER", "username"),
                         "password": os.environ.get("DB_PASSWORD", "password"),
                         "database": os.environ.get("DB_DATABASE", "sakila"),
                         "cursorclass": DictCursor}

        self.__conn = None
        self.__cursor = None

    @property
    def cursor(self):
        """
        Expose the active relational database cursor engine.

        Returns:
            DictCursor: Active PyMySQL dict-based query execution cursor.
        """
        return self.__cursor

    def __enter__(self):
        """
        Establish connection pipelines and return the operational instance.

        Returns:
            DB: Fully aggregated self instance with ready cursor states.
        """
        self.__conn = pymysql.connect(**self.__config)
        self.__cursor = self.__conn.cursor()
        print("MySQL Connection successful!")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Safely manage transaction completions and close connection pipelines.

        Triggers a state rollback if exceptions block execution, otherwise
        saves modifications via commits before disposing handles.

        Args:
            exc_type: Exception type if raised inside the block.
            exc_val: Exception value if raised inside the block.
            exc_tb: Traceback object if raised inside the block.
        """
        if self.__cursor:
            self.__cursor.close()
        if self.__conn:
            if exc_type:
                self.__conn.rollback()
            else:
                self.__conn.commit()
            self.__conn.close()
            print("MySQL Connection closed.")
