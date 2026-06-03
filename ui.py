import sys
from datetime import datetime

from sql import (
    movies_like,
    movie_by_genre_and_year,
    movie_by_genre_and_rating,
    film_genres,
    film_ratings,
    min_max_years,
    available_movies_per_genre,
    total_movies,
    film_actors,
    movie_by_actor
)
from errors import YearError, GenreError, RatingError, ActorError, YearIndex
from movie_logging import logger_decorator

class User:
    def __init__(self, db_object, mong_object):
        self.db = db_object
        self.mymongo = mong_object.my_queries_db

    @logger_decorator
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

    @staticmethod
    @logger_decorator
    def print_names(all_names, key, key2="", line_length=6):
        for i, name in enumerate(all_names, 1):
            if not i % line_length:
                print(name[key] + " " + name.get(key2, "") if key2 else name[key], end=",\n")
            else:
                print(name[key] + " " + name.get(key2, "") if key2 else name[key], end=', ')
        print()

    @logger_decorator
    def find_movie_by_actor(self, pagination=10):
        self.db.cursor.execute(film_actors)
        all_actors = self.db.cursor.fetchall()
        check_actors = {actor['first_name'] + " " + actor['last_name'] for actor in all_actors}
        print("Please select below one of our famous, beloved actors :)")
        self.print_names(all_actors, 'first_name', 'last_name', 7)
        while True:
            try:
                first_name_actor = input("Enter actor's first name: ").strip().upper()
                last_name_actor = input("Enter actor's last name: ").strip().upper()
                if first_name_actor + " " + last_name_actor not in check_actors:
                    raise ActorError('Please select existing actors only!!')
                break
            except ActorError as e:
                print(e)
        self.mymongo.insert_one({"timestamp": datetime.now(), "actor": first_name_actor + " " + last_name_actor})
        self.db.cursor.execute(movie_by_actor, (first_name_actor, last_name_actor))
        movies_found = self.db.cursor.fetchmany(pagination)
        if movies_found:
            self.print_found_movies(movies_found, pagination)
        else:
            print("No movie was found, we're sorry.")

    @logger_decorator
    def find_movie_by_rating_genre(self, pagination=10):
        self.db.cursor.execute(film_genres)
        all_genres = self.db.cursor.fetchall()
        check_genres = {genre['name'] for genre in all_genres}
        print("Available genres: ")
        self.print_names(all_genres, 'name')
        while True:
            try:
                which_genre = input("Enter preferred genre: ").strip().lower().title()
                if which_genre not in check_genres:
                    raise GenreError('Please use indicated above genres only.')
                break
            except GenreError as e:
                print(e)
        self.db.cursor.execute(film_ratings)
        all_ratings = self.db.cursor.fetchall()
        check_rating = {rating['rating'] for rating in all_ratings}
        print("Ratings: ")
        self.print_names(all_ratings, 'rating')
        while True:
            try:
                which_rating = input("Enter desired movie rating: ").upper()
                if which_rating not in check_rating:
                    raise RatingError('Please use indicated above ratings only.')
                break
            except RatingError as e:
                print(e)
        self.mymongo.insert_one({"timestamp": datetime.now(), "genre": which_genre, "rating": which_rating})
        self.db.cursor.execute(movie_by_genre_and_rating, (which_genre, which_rating))
        movies_found = self.db.cursor.fetchmany(pagination)
        if movies_found:
            self.print_found_movies(movies_found, pagination)
        else:
            print("No movie was found, we're sorry.")

    @logger_decorator
    def find_movie_by_year_genre(self, pagination=10):
        self.db.cursor.execute(film_genres)
        all_genres = self.db.cursor.fetchall()
        check = {genre['name'] for genre in all_genres}
        print("Available genres: ")
        self.print_names(all_genres, 'name')
        self.db.cursor.execute(min_max_years)
        years = self.db.cursor.fetchone()
        print(f"Min year in db: {years['min_year']}, Max year in db: {years['max_year']}")
        while True:
            try:
                which_genre = input("Enter preferred genre: ").strip().lower().title()
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
                if year_from > years['max_year']:
                    raise YearError(f"Start year cannot be greater than max year ({years['max_year']})."
                                    f" Please try again.")
                break
            except ValueError:
                print("Use integer numbers only!!")
            except YearError as e:
                print(e)
        while True:
            try:
                year_to = int(input("... to year (Inclusive): "))
                if year_to > years['max_year']:
                    raise YearError(f"Maximal year in DB: {years['max_year']}."
                                    f" Please try again.")
                if year_to < year_from:
                    raise YearIndex(f"End year cannot be less than start year ({year_from}). Please try again.")
                break
            except ValueError:
                print("Use integer numbers only!!")
            except (YearError, YearIndex) as e:
                print(e)
        self.mymongo.insert_one({"timestamp": datetime.now(), "genre": which_genre, "popular years": f"{year_from}, {year_to}"})
        self.db.cursor.execute(movie_by_genre_and_year, (which_genre, year_from, year_to))
        movies_found = self.db.cursor.fetchmany(pagination)
        if movies_found:
            self.print_found_movies(movies_found, pagination)
        else:
            print("No movie was found, we're sorry.")

    @logger_decorator
    def find_movie_like(self, pagination=10):
        which_movie = input("Please enter any movie's title: ").strip().lower()
        self.mymongo.insert_one({"timestamp": datetime.now(), "title": which_movie})
        self.db.cursor.execute(movies_like, (f"%{which_movie}%", which_movie, f"{which_movie} %", f"% {which_movie}",
                                            f"% {which_movie} %"))
        movies_found = self.db.cursor.fetchmany(pagination)
        if movies_found:
            self.print_found_movies(movies_found, pagination)
        else:
            print("No movie was found, we're sorry.")

    @logger_decorator
    def show_top5_queries(self, by_title=False, by_genre = False, by_rating = False, by_actor = False):
        choice = "title" if by_title else "genre" if by_genre else "rating" if by_rating else "actor"\
            if by_actor else "popular years"
        by_choice = choice
        top5 = self.mymongo.aggregate([{"$match": {choice: {"$ne": "", "$exists": True}}},
                                        {"$group": {"_id": f"${choice}", "count": {"$sum": 1}}},
                                        {"$project": {"_id": 0, choice: "$_id", "count": 1}},
                                        {"$sort": {"count": -1}}, {"$limit": 5}])
        print(f"Top {choice}s: " if by_choice != "popular years" else f"Top {choice}: ",
              *(f"{num}. {query[choice]} - {query['count']} times" for num, query in enumerate(top5, 1)), sep="\n")

    @logger_decorator
    def last_unique_queries(self):
        top10_unique = self.mymongo.aggregate(
            [{"$match": {"title": {"$ne": ""}, "genre": {"$ne": ""}, "rating": {"$ne": ""}, "actor": {"$ne": ""}}},
             {"$group": {"_id": {"title": "$title", "genre": "$genre", "rating": "$rating", "actor": "$actor"},
                         "timestamp": {"$max": "$timestamp"}}}, {"$sort": {"timestamp": -1}},
             {"$project": {"_id": 0, "title": "$_id.title", "genre": "$_id.genre", "rating": "$_id.rating",
                           "actor": "$_id.actor", "timestamp": 1}}, {"$limit": 10}])
        print("Last 10 unique queries: ")
        for query in top10_unique:
            print(f"Title: {query.get('title', 'N/A')}, Genre: {query.get('genre', 'N/A')},"
                f" Main actor: {query.get('actor', 'N/A')}, Rating: {query.get('rating', 'N/A')},"
                  f" Date: {query['timestamp']}")

    @logger_decorator
    def how_many_movies_in_db(self):
        print("All available movies, divided by genre: ")
        self.db.cursor.execute(available_movies_per_genre)
        print(*(f"{movie['name']}: {movie['count']}" for movie in self.db.cursor), sep='\n')
        print("-" * 14)
        self.db.cursor.execute(total_movies)
        total = self.db.cursor.fetchone()
        print(f"Total: {total['total']}")

@logger_decorator
def get_menu(user):
    return {"title": "Main menu: ",
            "items": {
                "1": {"text": "Find me movie",
                      "submenu": {"title": "Find me movie:",
                                  "items": {"1": {"text": "Find movie by genre and release year range",
                                                  "action": user.find_movie_by_year_genre},
                                            "2": {"text": "Find movie by genre and rating",
                                                  "action": user.find_movie_by_rating_genre},
                                            "3": {"text": "Find movie by title",
                                                  "action": user.find_movie_like},
                                            "4": {"text": "Find movie by actor",
                                                  "action": user.find_movie_by_actor},
                                            "5": {"text": "Back to Main menu",
                                                  "action": 'back'}
                                            }
                                  }
                      },
                "2": {"text": "Most popular queries",
                      "submenu": {"title": "Most popular queries: ",
                                  "items": {
                                      "1": {"text": "TOP5 Most popular movies",
                                            "action": lambda: user.show_top5_queries(by_title=True)},
                                      "2": {"text": "TOP5 Most popular genres",
                                            "action": lambda: user.show_top5_queries(by_genre=True)},
                                      "3": {"text": "TOP5 Most popular years",
                                            "action": user.show_top5_queries},
                                      "4": {"text": "TOP5 Rating",
                                            "action": lambda: user.show_top5_queries(by_rating=True)},
                                      "5": {"text": "TOP5 Actors",
                                            "action": lambda: user.show_top5_queries(by_actor=True)},
                                      "6": {"text": "Last unique queries",
                                            "action": user.last_unique_queries},
                                      "7": {"text": "Back to Main menu",
                                            "action": 'back'}}
                                  }
                      },
                "3": {"text": "Show me all available in DB movies",
                      "action": user.how_many_movies_in_db},
                "4": {"text": "Exit",
                      "action": lambda: print("Bye Bye :)") or sys.exit(0)}
                    }
            }

@logger_decorator
def ui_config(db_object, mong_object):
    user = User(db_object, mong_object)
    return get_menu(user)

@logger_decorator
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
