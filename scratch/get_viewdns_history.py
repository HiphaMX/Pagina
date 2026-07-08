import urllib.request
import re

url = "https://viewdns.info/iphistory/?domain=amdi.mx"
req = urllib.request.Request(
    url, 
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
)

print(f"Descargando historial de IPs desde: {url}...")
try:
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
    
    # Let's find the IP history table. 
    # The table usually contains headers: IP Address, Location, Owner, Last Seen
    # We can search for pattern matching the table or rows.
    # Regular expression to extract rows:
    # <tr><td>IP Address</td><td>Location</td><td>Owner</td><td>Last Seen</td></tr>
    # Find all table rows with 4 cells
    rows = re.findall(r'<tr>\s*<td[^>]*>\s*([\d\.]+)\s*</td>\s*<td[^>]*>\s*([^<]*)\s*</td>\s*<td[^>]*>\s*([^<]*)\s*</td>\s*<td[^>]*>\s*([^<]*)\s*</td>\s*</tr>', html, re.IGNORECASE)
    
    if rows:
        print(f"\nSe encontraron {len(rows)} registros de IP históricos:")
        print(f"{'IP Address':<16} | {'Location':<15} | {'Owner':<35} | {'Last Seen':<12}")
        print("-" * 88)
        for row in rows:
            ip, loc, owner, last_seen = row
            print(f"{ip:<16} | {loc.strip():<15} | {owner.strip():<35} | {last_seen.strip():<12}")
    else:
        print("No se pudieron parsear las filas de la tabla con regex simple.")
        # Print a snippet of the HTML containing table tags to inspect
        print("\nSnippet HTML:")
        tables = re.findall(r'<table[^>]*>.*?</table>', html, re.DOTALL)
        for i, table in enumerate(tables):
            if "IP Address" in table:
                print(f"Mesa {i}: {table[:1000]}...")
                
except Exception as e:
    print(f"Error al descargar o procesar la página: {e}")
