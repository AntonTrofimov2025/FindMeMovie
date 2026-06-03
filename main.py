# pylint: disable=line-too-long

"""
Main Entry Point for the FindMeMovie Console Application.

This module bootstraps the system by initializing secure context managers
for relational and MongoDB database gateways, compiles the configuration maps,
and triggers the infinite terminal UI loop runtime.
"""

from ui import show_menu, ui_config
from movie_db import DB
from mongodb import MongoDB

def main() -> None:
    """
    Initialize resources and launch the core application runtime environment.

    Safely opens database connection sockets inside resource manager blocks
    and handles global orchestration by passing initial handles to UI managers.
    """
    with DB() as conn, MongoDB() as mong:
        show_menu(ui_config(conn, mong))

if __name__ == "__main__":
    main()
