import re

with open("scratch/maps_page.html", "r", encoding="utf-8") as f:
    html = f.read()

# Let's find all quoted string fragments of size 20-250 characters that might contain reviews
# Usually, they are inside double quotes: "..."
strings = re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"', html)

print(f"Total quoted strings found: {len(strings)}")

# Let's filter for strings that look like Spanish sentences (e.g. have spaces and common spanish words or reviews keywords)
keywords = ["excelente", "buen", "servicio", "recomiendo", "gracias", "atención", "producto", "calidad", "maravilla", "experiencia", "mejor", "adaptógenos", "hongos", "herbolaria"]
potential_reviews = []

for s in strings:
    s_clean = s.replace('\\n', ' ').replace('\\"', '"').strip()
    if len(s_clean) > 25 and len(s_clean) < 300:
        # Check if it has spaces and some keyword
        if ' ' in s_clean:
            matches_keyword = any(kw in s_clean.lower() for kw in keywords)
            if matches_keyword:
                potential_reviews.append(s_clean)

# Print unique potential reviews
unique_reviews = list(set(potential_reviews))
print(f"Potential reviews found: {len(unique_reviews)}")
for i, r in enumerate(unique_reviews[:20]):
    print(f"{i+1}: {r}\n")
