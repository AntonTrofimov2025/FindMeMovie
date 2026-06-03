# pylint: disable=line-too-long

"""
MongoDB Connection and Resource Management Module.

Handles active session instantiation, connection pooling, health checks,
and clean context closure for the NoSQL application database layer.
"""

import os

from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv(".env")

class MongoDB:
    """
    Context manager wrapper for safe MongoDB client connectivity operations.

    Ensures environment variables are fetched correctly, provisions internal
    collection handles, runs connection health pings, and guarantees resource cleanups.
    """
    def __init__(self):
        self.__client = MongoClient(os.getenv("MONGO_DB"))
        self.__db = self.__client[os.getenv("MONGO_DB_NAME", "default_db")]
        self.__my_queries_db = self.__db[os.getenv("MONGO_TABLE_NAME", "default_collection")]

    @property
    def my_queries_db(self):
        """
        Expose the active log collection instance as a clean public attribute.

        Returns:
            Collection: PyMongo collection engine pointer.
        """
        return self.__my_queries_db

    def __enter__(self):
        """
        Validate database connectivity and enter the context block.

        Returns:
            MongoDB: The active fully configured instance with verified sockets.
        """
        self.__client.admin.command("ping")
        print("Mongo Connection successful!")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Safely shut down socket pools when exiting the context block.

        Args:
            exc_type: Exception type if raised inside the block.
            exc_val: Exception value if raised inside the block.
            exc_tb: Traceback object if raised inside the block.
        """
        if self.__client:
            self.__client.close()
            print("Mongo Connection closed.")
