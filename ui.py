import sys

def ui_config(db_object):
    return {"title": "Main menu: ",
              "items": {
                  "1": {"text": "Поиск фильма по жанру и диапазону годов выпуска",
                        "action": db_object.action1},
                  "2": {"text": "Поиск фильма по названию",
                        "action": db_object.find_movie_like},
                  "3": {"text": "Most popular movie queries",
                        "action": db_object.action3},
                  "4": {"text": "sss",
                      "submenu": {"title": "Submenu: ",
                                  "items": {
                                      "1": {"text": "submenu1",
                                            "action": db_object.action4},
                                      "2": {"text": "submenu2",
                                            "action": db_object.action5},
                                      "3": {"text": "Back to Main menu",
                                            "action": 'back'}}
                  }},
                  "5": {"text": "Exit",
                        "action": lambda: print("Bye Bye :)") or sys.exit(0)}
              }}

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


