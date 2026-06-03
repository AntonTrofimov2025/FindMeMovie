# pylint: disable=line-too-long

"""
SQL Queries Catalog for the FindMeMovie Application.

Contains parameterized SQL query strings for the Sakila database schema,
including film filtering, full-text pattern matching, metrics aggregation,
and metadata fetching.
"""

MOVIES_LIKE = """SELECT row_number() over () as num,
                     f.title, f.release_year, l.name as lang_name, c.name as genre_name, f.length, f.rating
                 FROM film f
                 JOIN film_category fc ON f.film_id = fc.film_id
                 JOIN category c ON fc.category_id = c.category_id
                 JOIN language l ON f.language_id = l.language_id
                 WHERE f.title LIKE %s
                 ORDER BY CASE
                              WHEN f.title = %s THEN 1
                              WHEN f.title LIKE %s OR f.title LIKE %s THEN 2
                              WHEN f.title LIKE %s THEN 3
                              ELSE 4
                              END ASC,
                          f.title ASC;"""

MOVIE_BY_GENRE_AND_YEAR = """SELECT row_number() over () as num,
                     f.title, f.release_year, l.name as lang_name, c.name as genre_name, f.length, f.rating
                 FROM film f
                 JOIN film_category fc ON f.film_id = fc.film_id
                 JOIN category c ON fc.category_id = c.category_id
                 JOIN language l ON f.language_id = l.language_id
                 WHERE c.name = %s and f.release_year >= %s and f.release_year <= %s
                 ORDER BY f.title"""

MOVIE_BY_GENRE_AND_RATING = """SELECT row_number() over () as num,
                                      f.title,
                                      f.release_year,
                                      l.name               as lang_name,
                                      c.name               as genre_name,
                                      f.length,
                                      f.rating
                               FROM film f
                                        JOIN film_category fc ON f.film_id = fc.film_id
                                        JOIN category c ON fc.category_id = c.category_id
                                        JOIN language l ON f.language_id = l.language_id
                               WHERE c.name = %s
                                 AND f.rating = %s"""

MOVIE_BY_ACTOR = """SELECT row_number() over () as num,
                                      f.title,
                                      f.release_year,
                                      l.name               as lang_name,
                                      c.name               as genre_name,
                                      f.length,
                                      f.rating
                               FROM film f
                                        JOIN film_category fc ON f.film_id = fc.film_id
                                        JOIN category c ON fc.category_id = c.category_id
                                        JOIN language l ON f.language_id = l.language_id
                                        JOIN film_actor fa ON f.film_id = fa.film_id
                                        JOIN actor a ON fa.actor_id = a.actor_id
                               WHERE a.first_name = %s and a.last_name = %s"""

FILM_GENRES = """SELECT name FROM category"""

FILM_RATINGS = """SELECT DISTINCT rating FROM film"""

MIN_MAX_YEARS = "SELECT min(release_year) as min_year, max(release_year) as max_year from film"

AVAILABLE_MOVIES_PER_GENRE = """SELECT c.name , count(c.name) as count FROM film f
                                JOIN film_category fc ON f.film_id = fc.film_id
                                JOIN category c ON fc.category_id = c.category_id
                                GROUP BY c.name
                                ORDER BY count(c.name) DESC"""

TOTAL_MOVIES = """SELECT count(film_id) as total FROM film"""

FILM_ACTORS = """SELECT DISTINCT a.first_name, a.last_name
                 FROM film f
                          JOIN film_actor fa ON f.film_id = fa.film_id
                          JOIN actor a ON fa.actor_id = a.actor_id"""
