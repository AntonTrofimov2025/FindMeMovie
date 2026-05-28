import os

import pymysql
from dotenv import load_dotenv
from pymysql.cursors import DictCursor
from sql import *

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

    def action1(self):
        print("action 1 performed")

    def find_movie_like(self):
        which_movie = input("Please enter any movie's title: ").lower()
        self.__cursor.execute(movies_like, (f"%{which_movie}%", which_movie, f"{which_movie} %", f"% {which_movie}",
                                            f"% {which_movie} %"))
        movies_found = self.__cursor.fetchmany(10)
        if movies_found:
            while movies_found:
                for movies in movies_found:
                    print(f"{movies['num']}. {movies['title']}, release year: {movies['release_year']},"
                          f" language: {movies['lang_name']}, genre: {movies['genre_name']}, duration:"
                          f" {movies['length']}m, rating: {movies['rating']}")
                length = len(movies_found)
                if length < 10:
                    print(f"Last {length} movies have been shown" if length > 1 else "Last movie has been shown")
                    break
                movies_found = self.__cursor.fetchmany(10)
                if movies_found:
                    input("Press ENTER to show next 10 movies...")
                else:
                    print("No more movies found.")
        else:
            print("No movie was found, we're sorry.")
            return

    def action3(self):
        print("action 3 performed")

    def action4(self):
        print("action 4 from submenu performed")

    def action5(self):
        print("action 5 from submenu performed")