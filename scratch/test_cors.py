import requests
r = requests.options("https://www.hipha.mx/api/contact/chilechillon/quiniela/matches/update", headers={"Origin": "https://elchilechillon.mx", "Access-Control-Request-Method": "POST"})
print("OPTIONS status:", r.status_code)
for k, v in r.headers.items():
    print(f"{k}: {v}")
