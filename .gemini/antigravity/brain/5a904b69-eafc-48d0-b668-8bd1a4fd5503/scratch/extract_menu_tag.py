with open("watchhouse_body.html", "r", encoding="utf-8") as f:
    html = f.read()

import re

# Look for <header-menu tag or element with class 'header-menu'
menu_match = re.search(r'<header-menu[^>]*>([\s\S]*?)</header-menu>', html)
if menu_match:
    print("--- HEADER-MENU FOUND ---")
    menu_html = menu_match.group(0)
    with open("watchhouse_menu.html", "w", encoding="utf-8") as f:
        f.write(menu_html)
    print("Saved to watchhouse_menu.html")
    print("Length:", len(menu_html))
    print("Preview of menu contents:")
    print(menu_html[:3000])
else:
    print("header-menu tag not found")
