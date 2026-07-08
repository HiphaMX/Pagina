import json
import os
import urllib.request
import urllib.error
import ssl

# 1. Read token from auth.json
config_path = os.path.expanduser("~/Library/Application Support/com.vercel.cli/auth.json")
try:
    with open(config_path, "r") as f:
        auth_data = json.load(f)
    token = auth_data.get("token")
except Exception as e:
    print(f"Error reading auth.json: {e}")
    token = None

if not token:
    print("Token not found in auth.json")
    exit(1)

# 2. Call Vercel API for deployment details
deployment_id = "dpl_9aQyvRs7Txtg9ZRhznrRwZhVfBEK"
url = f"https://api.vercel.com/v13/deployments/{deployment_id}"

req = urllib.request.Request(
    url,
    headers={
        "Authorization": f"Bearer {token}"
    }
)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

try:
    with urllib.request.urlopen(req, context=ctx) as response:
        details = json.loads(response.read().decode("utf-8"))
        
    with open("scratch/latest_details.json", "w") as out:
        json.dump(details, out, indent=2)
    print("Details successfully written to scratch/latest_details.json")
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} - {e.reason}")
    print(e.read().decode("utf-8"))
except Exception as e:
    print(f"Error calling Vercel API: {e}")
