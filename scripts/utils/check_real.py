from datetime import datetime
from urllib.parse import urlparse, urlunparse
from bs4 import BeautifulSoup

async def check_true_page(content, url):
    try:
        soup = BeautifulSoup(content, 'html.parser')
        meta_tags = soup.find("meta", {"content": lambda x: x.startswith('tripadvisor://')})
        meta = meta_tags['content']
        parsed_url = urlparse(meta)
        clean_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
        clean_url = clean_url.replace('tripadvisor://','https://')
        if clean_url == url:
            return True
        return False
    except Exception as e:
        print(f"{datetime.now()} :[ERROR] Cannot check real restaraunt",url,e)