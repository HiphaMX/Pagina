import re

with open('/Users/fanssimarketingdigital/Documents/Chizko/HiphaMX-fastapi/projects/WhiteClean/web/css/webflow.css', 'r') as f:
    content = f.read()

# find any rules with 'grid' or 'layout-grid' or 'grid-7'
rules = re.findall(r'([^{}]*\{[^{}]*grid[^{}]*\})', content)
for rule in rules[:10]:
    print(rule)
