from datetime import datetime
from urllib.parse import urlparse, urlunparse
from bs4 import BeautifulSoup
import asyncio
import aiofiles

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
        log_filename = 'data/logs/logfile.log'
        log_message = (f"[ERROR] Cannot check real restaraunt{url} with {e}")
        async with asyncio.Lock():
            async with aiofiles.open(log_filename, mode='a') as logfile:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                log_entry = f"[{timestamp}] {log_message}\n"
                await logfile.write(log_entry)