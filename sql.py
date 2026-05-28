

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
