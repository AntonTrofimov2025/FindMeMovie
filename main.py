from ui import show_menu, ui_config
from movie_db import DB
from mongodb import MongoDB

def main():
    with DB() as conn, MongoDB() as mong:
        show_menu(ui_config(conn, mong))

if __name__ == "__main__":
    main()
