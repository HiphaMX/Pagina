import re

with open("watchhouse_menu.html", "r", encoding="utf-8") as f:
    menu = f.read()

# Let's find all li items that have data-ref="header-menu.item" and print their text and href
items = re.findall(r'<li[^>]*?class="header-menu__item"[\s\S]*?<a[^>]*?href="([^"]*)"[^>]*>([\s\S]*?)</a>', menu)
print("Menu items:")
for href, text in items:
    # strip HTML and whitespace
    text_clean = re.sub('<[^<]+?>', '', text).strip()
    print(f"- {text_clean} -> {href}")
