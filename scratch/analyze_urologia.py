import urllib.request
import urllib.parse
from html.parser import HTMLParser
import sys

base_url = "https://www.urologia-avanzada.com.mx"

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = set()
        self.images = set()
        self.stylesheets = set()
        self.scripts = set()
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'a' and 'href' in attrs_dict:
            self.links.add(attrs_dict['href'])
        elif tag == 'img' and 'src' in attrs_dict:
            self.images.add(attrs_dict['src'])
        elif tag == 'link' and attrs_dict.get('rel') == 'stylesheet' and 'href' in attrs_dict:
            self.stylesheets.add(attrs_dict['href'])
        elif tag == 'script' and 'src' in attrs_dict:
            self.scripts.add(attrs_dict['src'])

def analyze():
    try:
        req = urllib.request.Request(
            base_url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            
        parser = LinkParser()
        parser.feed(html)
        
        print("INTERNAL LINKS FOUND:")
        internal_paths = set()
        for link in parser.links:
            full_url = urllib.parse.urljoin(base_url, link)
            if full_url.startswith(base_url):
                parsed = urllib.parse.urlparse(full_url)
                path = parsed.path
                if path == '':
                    path = '/'
                # clean up double slashes
                path = '/' + path.strip('/')
                internal_paths.add(path)
                
        for path in sorted(internal_paths):
            print(f"LINK: {path}")
            
        print("\nEXTERNAL LINKS FOUND:")
        for link in sorted(parser.links):
            full_url = urllib.parse.urljoin(base_url, link)
            if not full_url.startswith(base_url):
                print(f"EXT-LINK: {full_url}")
                
        print("\nIMAGES FOUND:")
        for img in sorted(parser.images):
            print(f"IMG: {img}")
            
        print("\nSTYLESHEETS FOUND:")
        for sheet in sorted(parser.stylesheets):
            print(f"CSS: {sheet}")
            
        print("\nSCRIPTS FOUND:")
        for scr in sorted(parser.scripts):
            print(f"JS: {scr}")
            
    except Exception as e:
        print(f"Error during analysis: {e}", file=sys.stderr)

if __name__ == "__main__":
    analyze()
