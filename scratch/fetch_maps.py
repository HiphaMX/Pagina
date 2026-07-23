import urllib.request
import re

urls = {
    "Isla ancla restaurante": "https://maps.app.goo.gl/Dm3sy83mrzyUDuqV8",
    "La sirenita restaurante": "https://maps.app.goo.gl/tk2EByNFNX62bZTt7",
    "Botanas balbuena": "https://maps.app.goo.gl/5FxhzjTCDbr2cUwS7",
    "Slovensko Delicatessen": "https://maps.app.goo.gl/M2JSWsQczox7QSYH6",
    "La Gretta Supercito y Carnicería": "https://maps.app.goo.gl/KQMz5dk4MmdRMH9w6",
    "El senador": "https://maps.app.goo.gl/KEzBeNK9XWCbZYUf6",
    "Jalsin pescaderka": "https://maps.app.goo.gl/dorkBvB87updTySQA",
    "Los equipales express": "https://maps.app.goo.gl/EdGCNBeGTj3xGUQ48",
    "Cucara macara": "https://maps.app.goo.gl/RAjE7nH9eddGmXW16"
}

class RedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        print(f"Redirecting to: {newurl}")
        return super().redirect_request(req, fp, code, msg, headers, newurl)

opener = urllib.request.build_opener(RedirectHandler)
opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')]

for name, url in urls.items():
    print(f"\nResolving: {name} ({url})")
    try:
        req = urllib.request.Request(url)
        with opener.open(req, timeout=10) as response:
            final_url = response.geturl()
            print(f"Final URL: {final_url}")
            
            # Try to extract coordinates from URL using regex
            # format: @20.578647,-102.775836,17z
            coords_match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', final_url)
            if coords_match:
                lat, lng = coords_match.groups()
                print(f"Coordinates found: {lat}, {lng}")
            else:
                # Also try format search query: /place/Name/@20.578647,-102.775836
                # or query params like q=20.578647,-102.775836
                q_match = re.search(r'q=(-?\d+\.\d+),(-?\d+\.\d+)', final_url)
                if q_match:
                    lat, lng = q_match.groups()
                    print(f"Coordinates (q) found: {lat}, {lng}")
                else:
                    print("Coordinates not found in URL")
    except Exception as e:
        print(f"Error resolving: {e}")
