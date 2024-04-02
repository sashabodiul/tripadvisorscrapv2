import xml.etree.ElementTree as ET
import aiohttp
import aiofiles
import gzip
import asyncio
from lxml import etree
from datetime import datetime
from data.config import *
import os
import random


async def check_completed():
    # Путь к папке "Downloads"
    folder_path = "Downloads"

    try:
        # Асинхронно получаем список файлов в папке
        files = await asyncio.to_thread(os.listdir, folder_path)

        # Выводим список файлов
        print("Список файлов в папке 'Downloads':")
        return files
    except FileNotFoundError:
        print(f"Папка '{folder_path}' не найдена.")
    except PermissionError:
        print(f"Недостаточно прав для доступа к папке '{folder_path}'.")


async def get_all_xml_links(url,session) -> list:
    print(f"{datetime.now()} :[INFO] Starting get all xml links")
    try:
        async with session.get(url) as response:
            if response.status == 200:
                print(f"{datetime.now()} :[INFO] GET all XML: status response: {response.status} from {url}")
                xml_content = await response.text()
                tree = etree.fromstring(xml_content.encode('utf-8'))
                # Используем пространство имен для элементов XML
                ns = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
                list_link = []
                # Ищем все теги <loc> и выводим их содержимое
                for loc in tree.findall(".//ns:loc", ns):
                    if 'restaurant_review' in loc.text:
                        list_link.append(loc.text)
                print(f"{datetime.now()} :[INFO] Successfully donwload XML")
                return list_link
            else:
                print(datetime.now(),":[ERROR] failed to retrieve XML data. Status code:", response.status)
                await write_links_to_file("failed to retrieve XML data. Status code:"+response.status,"logfile.log")
                return None
    except Exception as e:
        print(datetime.now(),":[ERROR] download XML:", e)
        await write_links_to_file(f"{datetime.now()} - [ERROR] download XML from url: {url}",'errorlog.log')
        return None

async def write_links_to_file(links, filename):
    # Путь к папке "Downloads"
    downloads_folder = "Downloads"
    # Полный путь к файлу
    filepath = os.path.join(downloads_folder, filename)
    if isinstance(links, list):
        async with aiofiles.open(filepath, mode='w') as f:
            await f.write('\n'.join(links))
    else:
        async with aiofiles.open(filename, mode='a') as f:
            await f.write(links + '\n')

async def process_xml_from_url(user_agent, url):
    try:
        print(f"{datetime.now()} :[INFO] try get gzip {url}")
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'TE': 'trailers'
        }
        
        async with aiohttp.ClientSession(headers=headers) as session:
            print(f"{datetime.now()} :[INFO] starting download gzip files from {url} with USER_AGENT={user_agent}")
            async with session.get(url) as response:
                print(f"{datetime.now()} :[INFO] Try connecting to download gzip {url}")
                if response.status:
                    print(f"{datetime.now()} :[INFO] XML download: status response: {response.status} from {url}")
                    await write_links_to_file(f"{datetime.now()} - [INFO] XML download: status response: {response.status} from {url}", "logfile.log")
                response.raise_for_status()
                content = await response.read()
                
        # Декомпрессия данных gzip
        decompressed_data = gzip.decompress(content)
        
        # Разбор XML
        root = ET.fromstring(decompressed_data)
        loc_elements = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
        links = [element.text for element in loc_elements]
        
        name_file = url.split('/')
        name_file = name_file[-1]
        name_file = name_file[:-7]
        # Сохранение ссылок в файл
        await write_links_to_file(links, f"{name_file}.txt")
        
        print(f"{datetime.now()} :[INFO] len response {len(links)} from {url}")

        return True
    except Exception as e:
        print(datetime.now(),':[ERROR] while downloading xml file: ', e)
        await write_links_to_file(f"{datetime.now()} - [ERROR] while downloading xml file: {e}", "errorlog.log")
        return False


async def main():
    url = 'http://tripadvisor-sitemaps.s3-website-us-east-1.amazonaws.com/2/en_US/sitemap_en_US_index.xml'
    async with aiohttp.ClientSession() as session:
        # Получение списка XML ссылок
        print(datetime.now(),":[INFO] starting get all xml links gzip files...")
        user_agent = random.choice(USER_AGENTS_LIST)
        list_xml = await get_all_xml_links(url, session)
        check_list = await check_completed()
        print(check_list)
        for i, xml_url in enumerate(list_xml):
            name_file = xml_url.split('/')[-1][:-7]
            if name_file in check_list:
                print(f"{datetime.now()} :[INFO] File '{name_file}' already exists. Skipping...")
                i+=1
                continue
            
            print(f"{datetime.now()} :[INFO] downloading xml file {i+1}")
            print(f"{datetime.now()} :[USER_AGENT] - {user_agent}")
            result = await process_xml_from_url(user_agent, xml_url)
            if not result:
                user_agent = random.choice(USER_AGENTS_LIST)
                i-=1
                continue
                

asyncio.run(main())