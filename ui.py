import sys
from sql import *
from datetime import datetime
from errors import YearError, GenreError

class User:
    def __init__(self, db_object, mong_object):
        self.db = db_object
        self.mymongo = mong_object.my_queries_db

    def print_found_movies(self, movies_found, pagination=10):
        while movies_found:
            for movie in movies_found:
                print(f"{movie['num']}. {movie['title']}, release year: {movie['release_year']},"
                      f" language: {movie['lang_name']}, genre: {movie['genre_name']}, duration:"
                      f" {movie['length']}m, rating: {movie['rating']}")
            length = len(movies_found)
            if length < pagination:
                print(f"Last {length} movies have been shown" if length > 1 else "Last movie has been shown")
                break
            movies_found = self.db.cursor.fetchmany(pagination)
            if movies_found:
                input(f"Press ENTER to show next {pagination} movies...")
            else:
                print("No more movies found.")

    def find_movie_by_year_genre(self, pagination=10):
        self.db.cursor.execute(film_genres)
        all_genres = self.db.cursor.fetchall()
        check = {genre['name'] for genre in all_genres}
        print("Available genres: ")
        for i, genre in enumerate(all_genres, 1):
            if not i % 6:
                print(genre['name'], end=",\n")
            else:
                print(genre['name'], end=', ')
        self.db.cursor.execute(min_max_years)
        years = self.db.cursor.fetchone()
        print(f"Min year in db: {years['min_year']}, Max year in db: {years['max_year']}")
        while True:
            try:
                which_genre = input("Enter preferred genre: ").lower().title()
                if which_genre not in check:
                    raise GenreError('Please use indicated above genres only.')
                break
            except GenreError as e:
                print(e)
        print("Please enter release years below.")
        while True:
            try:
                year_from = int(input("Starting from year: "))
                if year_from < years['min_year']:
                    raise YearError(f"Minimal year in DB: {years['min_year']}. Please try again.")
                break
            except ValueError:
                print("Use integer numbers only!!")
            except YearError as e:
                print(e)
        while True:
            try:
                year_to = int(input("... to year (Inclusive): "))
                if year_to > years['max_year']:
                    raise YearError(f"Maximal year in DB: {years['max_year']}. Please try again.")
                break
            except ValueError:
                print("Use integer numbers only!!")
            except YearError as e:
                print(e)
        self.mymongo.insert_one({"timestamp": datetime.now(), "genre": which_genre, "popular years": f"{year_from}, {year_to}"})
        self.db.cursor.execute(movie_by_genre_and_year, (which_genre, year_from, year_to))
        movies_found = self.db.cursor.fetchmany(pagination)
        if movies_found:
            self.print_found_movies(movies_found, pagination)
        else:
            print("No movie was found, we're sorry.")

    def find_movie_like(self, pagination=10):
        which_movie = input("Please enter any movie's title: ").lower()
        self.mymongo.insert_one({"timestamp": datetime.now(), "title": which_movie})
        self.db.cursor.execute(movies_like, (f"%{which_movie}%", which_movie, f"{which_movie} %", f"% {which_movie}",
                                            f"% {which_movie} %"))
        movies_found = self.db.cursor.fetchmany(pagination)
        if movies_found:
            self.print_found_movies(movies_found, pagination)
        else:
            print("No movie was found, we're sorry.")

    def show_top5_queries(self, by_title=False, by_genre = False):
        choice = "title" if by_title else "genre" if by_genre else "popular years"
        top5 = self.mymongo.aggregate([{"$match": {choice: {"$ne": "", "$exists": True}}},
                                        {"$group": {"_id": f"${choice}", "count": {"$sum": 1}}},
                                        {"$project": {"_id": 0, choice: "$_id", "count": 1}},
                                        {"$sort": {"count": -1}}, {"$limit": 5}])
        print(f"Top {choice}s: " if by_title or by_genre else f"Top {choice}: ",
              *(f"{num}. {query[choice]} - {query['count']} times" for num, query in enumerate(top5, 1)), sep="\n")

    def last_unique_queries(self):
        top10_unique = self.mymongo.aggregate([{"$match": {"title": {"$ne": ""}, "genre": {"$ne": ""}}},
                                               {"$group": {"_id": {"title": "$title", "genre": "$genre"},
                                                "timestamp": {"$max": "$timestamp"}}}, {"$sort": {"timestamp": -1}},
                                               {"$project": {"_id": 0, "title": "$_id.title", "genre": "$_id.genre",
                                                "timestamp": 1}}, {"$limit": 10}])
        print("Last 10 unique queries: ")
        for query in top10_unique:
            print(f"Title: {query.get('title', "N/A")}, Genre: {query.get('genre', "N/A")}, Date: {query['timestamp']}")

    def how_many_movies_in_db(self):
        print("All available movies, divided by genre: ")
        self.db.cursor.execute(available_movies_per_genre)
        print(*(f"{movie['name']}: {movie['count']}" for movie in self.db.cursor), sep='\n')
        self.db.cursor.execute(total_movies)
        total = self.db.cursor.fetchone()
        print(f"Total: {total['total']}")

def get_menu(user):
    return {"title": "Main menu: ",
                  "items": {
                      "1": {"text": "Поиск фильма по жанру и диапазону годов выпуска",
                            "action": user.find_movie_by_year_genre},
                      "2": {"text": "Поиск фильма по названию",
                            "action": user.find_movie_like},
                      "3": {"text": "Most popular queries",
                          "submenu": {"title": "Submenu: ",
                                      "items": {
                                          "1": {"text": "TOP5 Most popular movies",
                                                "action": lambda: user.show_top5_queries(by_title=True)},
                                          "2": {"text": "TOP5 Most popular genres",
                                                "action": lambda: user.show_top5_queries(by_genre=True)},
                                          "3": {"text": "TOP5 Most popular years",
                                                "action": user.show_top5_queries},
                                          "4": {"text": "Last unique queries",
                                                "action": user.last_unique_queries},
                                          "5": {"text": "Back to Main menu",
                                                "action": 'back'}}
                      }},
                      "4": {"text": "Show me all available in DB movies",
                            "action": user.how_many_movies_in_db},
                      "5": {"text": "Exit",
                            "action": lambda: print("Bye Bye :)") or sys.exit(0)}
                  }}

def ui_config(db_object, mong_object):
    user = User(db_object, mong_object)
    return get_menu(user)

def show_menu(menu_config):
    stack = [menu_config]
    while stack:
        current_menu = stack[-1]
        print(current_menu["title"])
        print(*(f"{key}. {value['text']}" for key, value in current_menu["items"].items()), sep="\n")
        your_choice = input('Your choice: ')
        if your_choice in current_menu["items"]:
            current_item = current_menu["items"][your_choice]
            if current_item.get('action') == 'back':
                stack.pop()
            elif 'submenu' in current_item:
                stack.append(current_item['submenu'])
            elif "action" in current_item:
                current_item['action']()
                input("Press ENTER to continue...")
        else:
            print("Menu option not found.")
            input("Press ENTER to continue...")