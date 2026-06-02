import os

from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv(".env")

class MongoDB:
    def __init__(self):
        self.__client = MongoClient(os.getenv("MONGO_DB"))
        self.__db = self.__client['ich_edit']
        self.__my_queries_db = self.__db['final_project_121225ptm_anton_t']

    @property
    def my_queries_db(self):
        return self.__my_queries_db

    def __enter__(self):
        self.__client.admit.command("ping")
        print("Mongo Connection successful!")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.__client:
            self.__client.close()
            print("Mongo Connection closed.")