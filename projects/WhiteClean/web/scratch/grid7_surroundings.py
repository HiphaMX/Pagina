import re

with open('/Users/fanssimarketingdigital/Documents/Chizko/HiphaMX-fastapi/projects/WhiteClean/web/css/webflow.css', 'r') as f:
    content = f.read()

# search for any rule starting with .grid-
grid_rules = re.findall(r'(\.grid-[^{}]*\{[^{}]*\})', content)
for rule in grid_rules:
    print(rule)
