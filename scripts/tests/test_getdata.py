import aiohttp
import asyncio
from bs4 import BeautifulSoup
import base64
import re
from data.config import *
import random


async def get_all_data_from_restaurants(content,url,restaraunt_index_error):
    try:
        soup = BeautifulSoup(content, 'html.parser')
        # Извлечение информации о местоположении ресторана
        breadcrumbs = soup.find('ul', class_='breadcrumbs')
        menu_text = name = None
        if breadcrumbs:
            menu = breadcrumbs.find_all('li')
            menu_text = ';'.join([li.text for li in menu])
            if menu_text:  # Проверяем, что menu_text не пустой
                name = menu_text.split(';')[-1].strip()
        # Извлечение информации о рейтинге и количестве отзывов
        rating = reviews_count = None
        block_a = soup.find('a', href='#REVIEWS')
        if block_a:
            svg_tag = block_a.find('svg')
            if svg_tag:
                title_tag = svg_tag.find('title')
                if title_tag:
                    try:
                        rating = title_tag.text.split(" ")[0]
                    except IndexError:
                        pass
            span_tag = block_a.find('span')
            if span_tag:
                try:
                    reviews_count = span_tag.text.split(" ")[0]
                    if ',' in reviews_count:
                        reviews_count = ''.join(filter(str.isdigit, reviews_count))
                except IndexError:
                    pass
        all_rating = soup.find_all('span', class_='vzATR')
        if all_rating is not None:
            food_rating = float(all_rating[0].find('span').get('class')[1][-2:])/10 if len(all_rating) > 0 else "NULL"
            service_rating = float(all_rating[1].find('span').get('class')[1][-2:])/10 if len(all_rating) > 1 else "NULL"
            value_rating = float(all_rating[2].find('span').get('class')[1][-2:])/10 if len(all_rating) > 2 else "NULL"
            atmosphere_rating = float(all_rating[3].find('span').get('class')[1][-2:])/10 if len(all_rating) > 3 else "NULL"
        else:
            food_rating = service_rating = value_rating = atmosphere_rating = "NULL"
        # Извлечение информации о ценах, телефоне, местоположении и веб-ссылке
        email = prices = telephone = location = website_link = decoded_url = None
        mailto_link = soup.find('a', href=lambda href: href and href.startswith("mailto:"))
        if mailto_link:
            # Получаем значение атрибута href
            href = mailto_link.get('href')
            # Находим индекс символа "?subject="
            subject_index = href.find('?subject=')
            if subject_index != -1:
                # Обрезаем href, чтобы получить только email
                email = href[len("mailto:") : subject_index]
        location_tag = soup.find('a', href="#MAPVIEW")
        if location_tag:
            location = location_tag.text
        website_link_tag = soup.find('a', class_="YnKZo Ci Wc _S C AYHFM")
        if website_link_tag:
            href = website_link_tag.get('data-encoded-url')
            if href:
                decoded_url = base64.b64decode(href).decode('utf-8')
                # Удаление первых четырех символов
                decoded_url = decoded_url[4:]
                # Удаление последних четырех символов
                decoded_url = decoded_url[:-4]
        prices_tags = soup.find_all('a', class_='dlMOJ')
        if prices_tags:
            prices = prices_tags[0].text
        telephone_tag = soup.find('a', href=lambda href: href and href.startswith('tel:'))
        if telephone_tag:
            telephone = telephone_tag.text
        # Извлечение информации о позиции в рейтинге
        position_in_rating = []
        span_tags_with_b = soup.find_all(lambda tag: tag.name == 'span' and tag.find('b'))
        for span_tag in span_tags_with_b:
            span_text = ''.join(span_tag.stripped_strings).strip()
            if '#' in span_text:
                position_in_rating.append(span_text)
        pattern = r"g(\d+)-"
        # Поиск совпадений в строке
        matches = re.search(pattern, url)
        g_code = None
        if matches:
            # Извлечение найденной части
            g_code = matches.group(1)

        return {
            'breadcrumbs':menu_text,
            'name':name,
            'rating': rating,
            'reviews_count': reviews_count,
            'prices': prices,
            'telephone': telephone,
            'location': location,
            'website_link': decoded_url,
            'position_in_rating': set(position_in_rating),
            'email': email,
            'food_rating': food_rating,
            'service_rating': service_rating,
            'value_rating': value_rating,
            'atmosphere_rating': atmosphere_rating,
            'g_code': g_code,
            'link': url
        }
    except Exception as e:
        if restaraunt_index_error > 1:
            restaraunt_index_error-=1

async def fetch_html(url, headers):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            return await response.text()

async def test_getdata():
    url = "https://www.tripadvisor.com/Restaurant_Review-g1006488-d25237320-Reviews-Mantela_Restaurante-Zapopan_Guadalajara_Metropolitan_Area.html"
    user_agent = random.choice(USER_AGENTS_LIST)
    headers = {
        'accept': 'text/html',
        'accept-language': 'en-US,en;q=0.9,uk;q=0.8,ru;q=0.7,ru-RU;q=0.6',
        'cache-control': 'max-age=0',
        'referer': 'https://www.tripadvisor.com/Restaurants-g1006488-Zapopan_Guadalajara_Metropolitan_Area.html',
        'sec-ch-device-memory': '8',
        'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        'sec-ch-ua-arch': '""',
        'sec-ch-ua-full-version-list': '"Google Chrome";v="123.0.6312.86", "Not:A-Brand";v="8.0.0.0", "Chromium";v="123.0.6312.86"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-model': '"Nexus 5"',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': f"{user_agent}"
    }

    html = await fetch_html(url, headers)
    data = await get_all_data_from_restaurants(html,url,0)
    print(data)
