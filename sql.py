

movies_like = """SELECT row_number() over () as num, 
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

movie_by_genre_and_year = """SELECT row_number() over () as num, 
                     f.title, f.release_year, l.name as lang_name, c.name as genre_name, f.length, f.rating
                 FROM film f
                 JOIN film_category fc ON f.film_id = fc.film_id
                 JOIN category c ON fc.category_id = c.category_id
                 JOIN language l ON f.language_id = l.language_id
                 WHERE c.name = %s and f.release_year >= %s and f.release_year <= %s
                 ORDER BY f.title"""

movie_by_genre_and_rating = """SELECT row_number() over () as num,
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

movie_by_actor = """SELECT row_number() over () as num,
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

film_genres = """SELECT name FROM category"""

film_ratings = """SELECT DISTINCT rating FROM film"""

min_max_years = "SELECT min(release_year) as min_year, max(release_year) as max_year from film"

available_movies_per_genre = """SELECT c.name , count(c.name) as count FROM film f
                                JOIN film_category fc ON f.film_id = fc.film_id
                                JOIN category c ON fc.category_id = c.category_id
                                GROUP BY c.name
                                ORDER BY count(c.name) DESC"""

total_movies = """SELECT count(film_id) as total FROM film"""

film_actors = """SELECT DISTINCT a.first_name, a.last_name
                 FROM film f
                          JOIN film_actor fa ON f.film_id = fa.film_id
                          JOIN actor a ON fa.actor_id = a.actor_id"""
