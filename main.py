from ui import show_menu, ui_config
from movie_db import DB











def main():
    with DB() as conn:
        cursor = conn.cursor
        # print()
        # cursor.execute("SHOW TABLES")
        # for table in cursor:
        #     print(table['Tables_in_sakila'])
        # print()
        cursor.execute("""SELECT * FROM film LIMIT 10""")
        print(*(movie for movie in cursor), sep="\n")
        show_menu(ui_config(conn))

if __name__ == "__main__":
    main()