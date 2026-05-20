import re

with open('/Users/fanssimarketingdigital/Documents/Chizko/HiphaMX-fastapi/projects/WhiteClean/web/css/style.css', 'r') as f:
    content = f.read()

# search for logotipos or grid-7 rules
logotipo_rules = re.findall(r'(\.[^{}]*logotipos[^{}]*\{[^{}]*\})', content)
for rule in logotipo_rules:
    print(rule)
