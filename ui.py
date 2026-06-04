# pylint: disable=line-too-long

"""
User Interface (UI) Module for the Movie Search Application.

This module acts as the Presentation and Routing layer (View/Controller).
It manages terminal-based menus, interactive user inputs, operational
validation flows, and links terminal triggers to relational and non-relational
database systems.
"""

import sys
from datetime import datetime

from sql import (
    MOVIES_LIKE,
    MOVIE_BY_GENRE_AND_YEAR,
    MOVIE_BY_GENRE_AND_RATING,
    FILM_GENRES,
    FILM_RATINGS,
    MIN_MAX_YEARS,
    AVAILABLE_MOVIES_PER_GENRE,
    TOTAL_MOVIES,
    FILM_ACTORS,
    MOVIE_BY_ACTOR
)
from errors import YearError, GenreError, RatingError, ActorError, YearIndex
from movie_logging import logger_decorator

class User:
    """
    Controller engine handling core movie database query workflows.

    Coordinates search workflows (by genre, timeline, partial titles, or actors),
    manages interactive terminal parameter validation routines, structures grid outputs,
    and concurrently logs interaction historical telemetry into MongoDB.
    """
    def __init__(self, db_object, mong_object):
        self.db = db_object
        self.mymongo = mong_object.my_queries_db

    @logger_decorator
    def print_found_movies(self, movies_found: list[dict], pagination: int=10) -> None:
        """
        Display found movies and handle interactive pagination for the result set.

        Prints the technical specifications of each movie in the current batch
        and checks if further records are available. Prompts the user to continue
        fetching until the database cursor is exhausted.

        Args:
            movies_found (list[dict]): Initial batch of movie records from the database.
            pagination (int, optional): The chunk size limit for the query output.
                Defaults to 10.
        """
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
    def print_names(all_names: list[dict], key: str, key2: str="", line_length: int=6) -> None:
        """
        Pretty-print a list of names or entity fields in a structured grid layout.

        Iterates through the provided sequence and outputs specific dictionary keys
        side-by-side, adding automated line breaks based on the line length constraint.

        Args:
            all_names (list[dict]): Collection of dictionaries containing the target data.
            key (str): Primary dictionary key to extract and display.
            key2 (str, optional): Secondary dictionary key for concatenation (e.g., surname).
                Defaults to "".
            line_length (int, optional): Number of items allowed per printed terminal row.
                Defaults to 6.
        """
        for i, name in enumerate(all_names, 1):
            if not i % line_length:
                print(name[key] + " " + name.get(key2, "") if key2 else name[key], end=",\n")
            else:
                print(name[key] + " " + name.get(key2, "") if key2 else name[key], end=', ')
        print()

    @logger_decorator
    def find_movie_by_actor(self, pagination: int=10) -> None:
        """
        Execute an interactive movie search filtering by actor names.

        Fetches available talent records from the database, guides the user through
        validated first and last name lookups, tracks queries via MongoDB logs,
        and triggers paginated output for matching films.

        Args:
            pagination (int, optional): The chunk size limit for the query output.
                Defaults to 10.
        """
        self.db.cursor.execute(FILM_ACTORS)
        all_actors = self.db.cursor.fetchall()
        check_actors = {actor['first_name'] + " " + actor['last_name'] for actor in all_actors}
        print("Please select below one of our famous, beloved actors :)")
        User.print_names(all_actors, 'first_name', 'last_name', 7)
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
        self.db.cursor.execute(MOVIE_BY_ACTOR, (first_name_actor, last_name_actor))
        movies_found = self.db.cursor.fetchmany(pagination)
        if movies_found:
            self.print_found_movies(movies_found, pagination)
        else:
            print("No movie was found, we're sorry.")

    @logger_decorator
    def find_movie_by_rating_genre(self, pagination: int=10) -> None:
        """
        Search and display movies matching specific rating and genre boundaries.

        Leverages shared validators to fetch a targeted genre choice, prompts
        and verifies the film rating classification against known DB records, logs
        the selection pattern to MongoDB, and fetches filtered film records.

        Args:
            pagination (int, optional): The chunk size limit for the query output.
                Defaults to 10.
        """
        self.db.cursor.execute(FILM_GENRES)
        all_genres = self.db.cursor.fetchall()
        check_genres = {genre['name'] for genre in all_genres}
        print("Available genres: ")
        User.print_names(all_genres, 'name')
        which_genre = User.genre_checker(check_genres)
        self.db.cursor.execute(FILM_RATINGS)
        all_ratings = self.db.cursor.fetchall()
        check_rating = {rating['rating'] for rating in all_ratings}
        print("Ratings: ")
        User.print_names(all_ratings, 'rating')
        while True:
            try:
                which_rating = input("Enter desired movie rating: ").strip().upper()
                if which_rating not in check_rating:
                    raise RatingError('Please use indicated above ratings only.')
                break
            except RatingError as e:
                print(e)
        self.mymongo.insert_one({"timestamp": datetime.now(), "genre": which_genre, "rating": which_rating})
        self.db.cursor.execute(MOVIE_BY_GENRE_AND_RATING, (which_genre, which_rating))
        movies_found = self.db.cursor.fetchmany(pagination)
        if movies_found:
            self.print_found_movies(movies_found, pagination)
        else:
            print("No movie was found, we're sorry.")

    @staticmethod
    @logger_decorator
    def year_from_checker(years_buf: dict) -> int:
        """
        Prompt the user for a valid start year and cross-check against database limits.

        Maintains an active loop until an integer matching chronologically within
        the minimum and maximum database year markers is entered.

        Args:
            years_buf (dict): Context schema holding verified 'min_year' and 'max_year'.

        Returns:
            int: A verified starting release year.
        """
        while True:
            try:
                year_from = int(input("Starting from year: "))
                if year_from < years_buf['min_year']:
                    raise YearError(f"Minimal year in DB: {years_buf['min_year']}. Please try again.")
                if year_from > years_buf['max_year']:
                    raise YearError(f"Start year cannot be greater than max year ({years_buf['max_year']})."
                                    f" Please try again.")
                return year_from
            except ValueError:
                print("Use integer numbers only!!")
            except YearError as e:
                print(e)

    @staticmethod
    @logger_decorator
    def year_to_checker(years_buf: dict, your_year_from: int) -> int:
        """
        Prompt the user for an end year and cross-check against DB and start year limits.

        Ensures the final year range parameter is an integer, does not exceed historical
        database maxima, and structurally follows the user's previously picked start point.

        Args:
            years_buf (dict): Context schema holding verified 'min_year' and 'max_year'.
            your_year_from (int): The verified lower-bound year to cross-reference.

        Returns:
            int: A verified ending release year.
        """
        while True:
            try:
                year_to = int(input("... to year (Inclusive): "))
                if year_to > years_buf['max_year']:
                    raise YearError(f"Maximal year in DB: {years_buf['max_year']}."
                                    f" Please try again.")
                if year_to < your_year_from:
                    raise YearIndex(f"End year cannot be less than start year ({your_year_from})."
                                    f" Please try again.")
                return year_to
            except ValueError:
                print("Use integer numbers only!!")
            except (YearError, YearIndex) as e:
                print(e)

    @staticmethod
    @logger_decorator
    def genre_checker(genres_list: set) -> str:
        """
        Validate user-entered film genre inputs against active database records.

        Standardizes text casing patterns from incoming terminal entries and checks
        existence thresholds against known valid types before passing control back.

        Args:
            genres_list (set): Pre-aggregated set containing active legal genre titles.

        Returns:
            str: Title-cased validated movie genre value.
        """
        while True:
            try:
                which_genre = input("Enter preferred genre: ").strip().lower().title()
                if which_genre not in genres_list:
                    raise GenreError('Please use indicated above genres only.')
                return which_genre
            except GenreError as e:
                print(e)

    @logger_decorator
    def find_movie_by_year_genre(self, pagination: int=10) -> None:
        """
        Search for movies based on user-selected genre and release year range.

        Fetches available genres and year boundaries from the SQL database,
        delegates validation to class-level checkers, logs the history token
        into MongoDB, and displays the paginated movie records.

        Args:
            pagination (int, optional): The chunk size limit for the query output.
                Defaults to 10.
        """
        self.db.cursor.execute(FILM_GENRES)
        all_genres = self.db.cursor.fetchall()
        check_genres = {genre['name'] for genre in all_genres}
        print("Available genres: ")
        User.print_names(all_genres, 'name')
        self.db.cursor.execute(MIN_MAX_YEARS)
        years = self.db.cursor.fetchone()
        print(f"Min year in db: {years['min_year']}, Max year in db: {years['max_year']}")
        which_genre = User.genre_checker(check_genres)
        print("Please enter release years below.")
        year_from = User.year_from_checker(years)
        year_to = User.year_to_checker(years, year_from)
        self.mymongo.insert_one({"timestamp": datetime.now(), "genre": which_genre, "popular years": f"{year_from}, {year_to}"})
        self.db.cursor.execute(MOVIE_BY_GENRE_AND_YEAR, (which_genre, year_from, year_to))
        movies_found = self.db.cursor.fetchmany(pagination)
        if movies_found:
            self.print_found_movies(movies_found, pagination)
        else:
            print("No movie was found, we're sorry.")

    @logger_decorator
    def find_movie_like(self, pagination: int=10) -> None:
        """
        Search for movies using a fuzzy title match via SQL LIKE operator.

        Prompts the user for a partial string, indexes the query payload
        into MongoDB logs, and runs a pattern match against film titles.

        Args:
            pagination (int, optional): Maximum number of movies to display per page.
                Defaults to 10.
        """
        which_movie = input("Please enter any movie's title: ").strip().lower()
        self.mymongo.insert_one({"timestamp": datetime.now(), "title": which_movie})
        self.db.cursor.execute(MOVIES_LIKE, (f"%{which_movie}%", which_movie, f"{which_movie} %", f"% {which_movie}",
                                            f"% {which_movie} %"))
        movies_found = self.db.cursor.fetchmany(pagination)
        if movies_found:
            self.print_found_movies(movies_found, pagination)
        else:
            print("No movie was found, we're sorry.")

    @logger_decorator
    def show_top5_queries(self, by_title: bool=False,
                          by_genre: bool = False, by_rating: bool = False, by_actor: bool = False) -> None:
        """
        Aggregate and display the top 5 most frequent search queries by metric.

        Dynamically evaluates search criteria flags, executes a MongoDB aggregation
        pipeline with grouping and sorting operations, and displays the top counters.

        Args:
            by_title (bool, optional): Filter top queries by movie title. Defaults to False.
            by_genre (bool, optional): Filter top queries by movie genre. Defaults to False.
            by_rating (bool, optional): Filter top queries by movie rating. Defaults to False.
            by_actor (bool, optional): Filter top queries by actor name. Defaults to False.
        """
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
    def last_unique_queries(self) -> None:
        """
        Fetch and display the last 10 unique searches made by users.

        Executes a MongoDB aggregation pipeline using fields configuration to eliminate
        duplicated query histories based on historical timestamps.
        """
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
    def how_many_movies_in_db(self) -> None:
        """
        Calculate and output comprehensive storage metrics for movies inside the DB.

        Prints analytical rows reflecting general film distributions categorized by genre
        branches alongside global dataset sum values.
        """
        print("All available movies, divided by genre: ")
        self.db.cursor.execute(AVAILABLE_MOVIES_PER_GENRE)
        print(*(f"{movie['name']}: {movie['count']}" for movie in self.db.cursor), sep='\n')
        print("-" * 14)
        self.db.cursor.execute(TOTAL_MOVIES)
        total = self.db.cursor.fetchone()
        print(f"Total: {total['total']}")

@logger_decorator
def get_menu(user: User) -> dict:
    """
    Generate the hierarchical application menu dictionary tree.

    Maps console hotkeys to specific runtime submenus or directly registers
    executable class methods bound to the passed User session instance.

    Args:
        user (User): The active operational class instance handling queries.

    Returns:
        dict: A nested structural directory representing system routes.
    """
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
def ui_config(db_object, mong_object) -> dict:
    """
    Bootstrap the User session driver and bundle it with the core menu tree.

    Acts as the main operational orchestrator that initializes the backend
    User controller instance and instantly feeds it into the navigation tree.

    Args:
        db_object: Database pool cursor provider (MySQL connection).
        mong_object: Active MongoDB logs collection connection reference.

    Returns:
        dict: A fully route-configured operational application root menu.
    """
    user = User(db_object, mong_object)
    return get_menu(user)

@logger_decorator
def show_menu(menu_config: dict):
    """
    Execute the core terminal UI infinite runtime navigation stack engine.

    Pushes and pops menu branches from a standard tracking history array to allow
    infinite deep nesting lookups and instant backtracking using 'back' states.

    Args:
        menu_config (dict): Initial fully generated configuration menu structure.
    """
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
