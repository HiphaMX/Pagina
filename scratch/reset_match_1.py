import requests

url = "https://www.hipha.mx/api/contact/chilechillon/quiniela/matches/update"
payload = {
    "email": "efe.creativo@gmail.com",
    "password": "SoyElWero",
    "id": 1,
    "phase": "grupo",
    "teamA": "arb",
    "teamB": "neg",
    "scoreA": None,
    "scoreB": None,
    "status": "active"
}

response = requests.post(url, json=payload)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")
