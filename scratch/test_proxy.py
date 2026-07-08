import requests

url = "https://elchilechillon.mx/api/contact/chilechillon/quiniela/matches/update"
payload = {
    "email": "efe.creativo@gmail.com",
    "password": "SoyElWero",
    "id": 1,
    "phase": "grupo",
    "teamA": "arb",
    "teamB": "neg",
    "scoreA": 2,
    "scoreB": 1,
    "status": "finished"
}

# Disable redirect handling to inspect the raw response first
print("--- Raw request without following redirects ---")
r_no_redir = requests.post(url, json=payload, allow_redirects=False)
print("Status:", r_no_redir.status_code)
print("Headers:")
for k, v in r_no_redir.headers.items():
    print(f"  {k}: {v}")

print("\n--- Request following redirects ---")
r_with_redir = requests.post(url, json=payload, allow_redirects=True)
print("Status:", r_with_redir.status_code)
print("Final URL:", r_with_redir.url)
print("Response:", r_with_redir.text)
