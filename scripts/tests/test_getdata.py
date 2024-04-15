from datetime import datetime, timedelta
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.x509.oid import NameOID
import tempfile
import uuid
import asyncio
import string
from bs4 import BeautifulSoup
import ssl
from aiohttp import TCPConnector
import re
import base64
import aiohttp
import brotli
from data.config import *
import random

async def get_result_data(content,url):
    soup = BeautifulSoup(content, 'html.parser')
    result_data = {}
    div_rate = soup.find('div',class_='QSyom f e Q3 _Z')
    reviews = soup.find('span', class_='GPKsO')
    rating = soup.find('span', class_='biGQs _P fiohW uuBRH')
    name = soup.find('h1', class_='biGQs _P egaXP rRtyp')
    other_ratings = div_rate.find_all('svg', class_='UctUV d H0') if div_rate else None
    div_pos_rate = soup.find('div',class_='CsAqy u Ci Ph w')
    div_emails = soup.find_all('div',class_='hpxwy e j')
    email = None
    for div in div_emails:
        test_res = div.find('a')
        if test_res.get('aria-label') == 'Email':
            email = test_res.get('href').replace('mailto:','')
    main_div = soup.find('div',class_='lJSal _T')
    main_spans = main_div.find_all('span',class_='biGQs _P pZUbB hmDzD') if main_div else None
    prices = main_spans[1] if main_spans else None
    pattern = r"g(\d+)-"
        # Поиск совпадений в строке
    matches = re.search(pattern, url)
    g_code = None
    if matches:
        # Извлечение найденной части
        g_code = matches.group(1)
    
    location_elements = soup.find_all('span',class_='ExtaW f Wh')
    location_elements = [element.text for element in location_elements]
    location = ','.join(location_elements)
    number = soup.find_all('a', href=lambda href: href and 'tel' in href)
    food_rating = service_rating = value_rating = atmosphere_rating = None
    pos_in_rate = div_pos_rate.find('span', class_='biGQs _P pZUbB hmDzD') if div_pos_rate else None
    try:
        city = pos_in_rate.text.split(' ')[-1] if len(pos_in_rate.text.split(' ')) > 2 else ''
    except:
        city = None
    if other_ratings:
        if len(other_ratings[1:]) >= 1:
            food_rating = other_ratings[1].text.split(' ') if other_ratings[1] else None
        if len(other_ratings[1:]) >= 2:
            service_rating = other_ratings[2].text.split(' ') if other_ratings[2] else None
        if len(other_ratings[1:]) >= 3:
            value_rating = other_ratings[3].text.split(' ') if other_ratings[3] else None
        if len(other_ratings[1:]) >= 4:
            atmosphere_rating = other_ratings[4].text.split(' ') if other_ratings[4] else None
        
    result_data['location'] = location if location else None
    result_data['reviews'] = reviews.text.replace(' reviews','') if reviews else None
    result_data['rating'] = rating.text if rating else None
    result_data['name'] = name.text if name else None
    result_data['email'] = email if email else None
    result_data['pos_in_rate'] = pos_in_rate.text if pos_in_rate else None
    result_data['number'] = number[0].text if number else None
    result_data['prices'] = prices.text if prices else None
    result_data['food_rating'] = food_rating[0] if food_rating else None
    result_data['service_rating'] = service_rating[0] if service_rating else None
    result_data['value_rating'] = value_rating[0] if value_rating else None
    result_data['g_code'] = g_code if g_code else None
    result_data['atmosphere_rating'] = atmosphere_rating[0] if atmosphere_rating else None
    result_data['city'] = city
    result_data['link'] = url
    
    return result_data

async def get_all_data_from_restaurants(content,url):
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
        name = soup.find('h1', class_='biGQs _P egaXP rRtyp')
        print(name)
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
                    # Создаем таблицу перевода, которая удаляет все непечатаемые символы и пробелы
                    translation_table = str.maketrans('', '', '\u202f ')
                    # Применяем таблицу перевода к строке
                    reviews_count = reviews_count.translate(translation_table)
                    # Оставляем только цифры
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
        else:
            print(datetime.now(),":[ERROR] No match fount for g code")

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
        print(datetime.now(),':[ERROR] with BeautifulSoup get response: ',e)

async def scrape_data(proxy, old_domain, new_domain, user_agent, url):
    other_chunk_url = url.split('/')[-1]
    random_three_number = random.randint(100, 999)
    # Определяем символы, которые могут быть использованы для генерации строки
    characters = string.ascii_letters + string.digits
    # Генерируем случайную строку из 10 символов
    interaction_count = 666
    random_string = ''.join(random.choices(characters, k=10))
    current_date = datetime.now()

    # Форматирование даты в виде "ДД.ММ.ГГГГ"
    formatted_date = current_date.strftime("%Y%m%d")
    formatted_data_snake = current_date.strftime("%Y_%m_%d")
    headers = [{
    'User-Agent': f'{user_agent}',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Cookie': 'TADCID=GekU0dISJ60ZiZXtABQCmq6heh9ZSU2yA8SXn9Wv5HzmP6z_PWn1sDuaXQtMb__9WpOcD1Lqs-c5QYl4fEJublgaweQkLsLi1uI; TASameSite=1; TAUnique=%1%enc%3ADn1nlaYvNYDkt1wYQe8H4JoopTqTGq60AzoJvlyN6oOMrrjHe5x7ovfyyxaUPHueNox8JbUSTxk%3D; __vt=qSlC0IaeEeQd12iAABQCwRB1grfcRZKTnW7buAoPsSzEP0jz6SfAKr6j5_jVTdQN0_gwGpbMf6Tbc9PYrhYDMGkWoJlfUCoG63frLCxTWJmfyfWsylx4V0KKZMhc5yTTOZUE1XO2kRKi3QKlORoU7CqNdB8; TASSK=enc%3AAM%2B06nxPNkTnDUuubW%2BsKmLmKamM2NJvRtJqAS9XdWem3v3HEnxN92SBvPtKEyK5aNtmXYuM4JrGfTnO8haiBP9yyxzjZZZT3oRw56xrS1Ju92TZ%2B%2F7uFzC69a%2BRi3MDJw%3D%3D; TASession=V2ID.68FA693727FB404F8882782600D69733*SQ.8*LS.Restaurant_Review*HS.recommended*ES.popularity*DS.5*SAS.popularity*FPS.oldFirst*FA.1*DF.0*TRA.true*LD.5912517*EAU._; PAC=AC25VJLP31ebhFh6qplcY4Y3StxwO8ek8dZJoksZrqmvoQXCLaXE5Y8K75gGdYtD7QdUYdI1gkuLeJM239-NWwgVApIwnGPZF9qbE7AUKC_hce-rM8DWDjeS5a4v9m0uAz0_yuat4OcF-o9ruk-yLydZhfTXODa-hOxgA-US9wd7_rSIHJ3IR_xXyNXBjES0UySLIvYx-m6Kh1pX6QUVq--B8uO_DnRMRM99TvJNvBIM; ServerPool=B; PMC=V2*MS.60*MD.20240414*LD.20240414; TART=%1%enc%3AtYcH6QSNFOXhdyshaNzTc6NbAuGJccl2JRllnhF8t0vrWi0gE5s7AcLUnIFPb4np4ieoPdYMDDY%3D; TATravelInfo=V2*A.2*MG.-1*HP.2*FL.3*RS.1; TAUD=LA-1713138613973-1*RDD-1-2024_04_15*LG-5519938-2.1.F.*LD-5519939-.....; datadome=bgtPtFcIPtRT254_btvMnNdky~KGgRnOoOdtRXLAYP5QJJMNd5POPNjT9v1whLXjXpRb9vSO5oDCmx5uAHOJC3Su8O22I4yiI9Ns5dmaZlrQ1C1mnwZWujGPOyPLyy5p; OptanonConsent=isGpcEnabled=0&datestamp=Mon+Apr+15+2024+04%3A22%3A14+GMT%2B0300+(%D0%92%D0%BE%D1%81%D1%82%D0%BE%D1%87%D0%BD%D0%B0%D1%8F+%D0%95%D0%B2%D1%80%D0%BE%D0%BF%D0%B0%2C+%D0%BB%D0%B5%D1%82%D0%BD%D0%B5%D0%B5+%D0%B2%D1%80%D0%B5%D0%BC%D1%8F)&version=202310.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=e2541746-8327-45a9-b6c1-74fe00fe12d9&interactionCount=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&AwaitingReconsent=false; TATrkConsent=eyJvdXQiOiJTT0NJQUxfTUVESUEiLCJpbiI6IkFEVixBTkEsRlVOQ1RJT05BTCJ9; ab.storage.sessionId.6e55efa5-e689-47c3-a55b-e6d7515a6c5d=%7B%22g%22%3A%22a2e1b441-949c-3e42-0eb2-bada9abc362e%22%2C%22e%22%3A1713144157747%2C%22c%22%3A1713144135137%2C%22l%22%3A1713144142747%7D; ab.storage.deviceId.6e55efa5-e689-47c3-a55b-e6d7515a6c5d=%7B%22g%22%3A%22f4dd5fe3-cbf6-44bb-c97e-135d4dbad0e8%22%2C%22c%22%3A1713138412922%2C%22l%22%3A1713144135137%7D; _ga_QX0Q50ZC9P=GS1.1.1713144135.2.0.1713144145.50.0.0; _ga=GA1.1.507837918.1713138413; pbjs_sharedId=23652d01-b1c0-4c27-b157-0e8bb944a841; pbjs_sharedId_cst=zix7LPQsHA%3D%3D; _li_dcdm_c=.tripadvisor.com.hk; _lc2_fpi=53d526bd5ca2--01hvfg3bzbp4yxeahfqg1tv76c; _lc2_fpi_meta=%7B%22w%22%3A1713138413547%7D; __gads=ID=267f24a9295c9246:T=1713138414:RT=1713144137:S=ALNI_MYWGDMWptKQg28RXtakxs511dZZXw; __gpi=UID=00000deffc09e05d:T=1713138414:RT=1713144137:S=ALNI_Mbtn44sx5d7stpp6rjHVLqFN54l4Q; __eoi=ID=216bf2a94f22f5d2:T=1713138414:RT=1713144137:S=AA-AfjYPrto5dCOZFPMQdKLTTtUa; _lr_sampling_rate=100; _lr_env_src_ats=false; pbjs_unifiedID=%7B%22TDID_LOOKUP%22%3A%22FALSE%22%2C%22TDID_CREATED_AT%22%3A%222024-04-14T23%3A47%3A01%22%7D; pbjs_unifiedID_cst=zix7LPQsHA%3D%3D; pbjs_li_nonid=%7B%7D; pbjs_li_nonid_cst=zix7LPQsHA%3D%3D; TASID=68FA693727FB404F8882782600D69733; _lr_retry_request=true',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'TE': 'trailers'
    },
    {
    'accept': 'text/html',
    'accept-language': 'en-US,en;q=0.7',
    'cache-control': 'max-age=0',
    'cookie': f'TADCID=GekU0dISJ60ZiZXtABQCm{random_string}yA8SXn9Wv5HzmP6z_PWn1sDuaXQtMb__9WpOcD1Lqs-c5QYl4fEJublgaweQkLsLi1uI; TAUnique=%1%enc%3Ax5Hs5PvM{random_string}yXl357SiNWHlWuy7vIs7U%2FmOnJPHzeE5N7iNHfN3xBEeTENox8JbUSTxk%3D; TASameSite=1; TASSK=enc%3AANuwdJ4qdJhe%2FVtBDH5D{random_string}sl1JBFiUn1Ebh9zhNJgPgwsWotJamCFavcq%2BUgVKbXJMzmz6d4Amkca{random_string}hLmzqBIJfSqMGcKiKbKnDjJJDicFsWgVDVA%3D%3D; ServerPool=C; TAReturnTo=%1%%2F{other_chunk_url}; TATravelInfo=V2*A.2*MG.-1*HP.2*FL.3*RS.1*RY.2024*RM.4*RD.2*RH.20*RG.2; TADCID=zOkVKt_KmuLOXpLTABQCmq6h{random_string}SXn9Wv5Hzb-kQyKzVcuh854KuPxW-tVcS-y7OnPUOOGHH-6V3benJfY2r_d6Fng0M; TART=%1%enc%3AaLTtdWnIauQyh23O{random_string}7h2ynMKJgQlWWLiJSdIos%2FrsIORXckiGPcmx%2FHDNqVqMpuLEk%3D; PMC=V2*MS.86*MD.{formatted_date}*LD.{formatted_date}; TATrkConsent=eyJvdXQiOiJBRFYsQU5BLEZVTkNUSU9OQUwsU09DSUFMX01FRElBIiwiaW4iOiIifQ==; PAC=AKrriyTQYrXRHGaZHgcS3ZQryjaDxRTLtK7IFbli1eIE-crHXD5gMNeL7GQEC1LRX3Ln60cUzoZVmxbqVft8dQxakN2NUbTEeJ6QBUAbRfpISLDsaB-EQf5oSbc5if4iraXappRlFf6KSk3aE5asx1-axnesj4F2J5WFbNXnM5Fa6oshImADlGv4PxeQtVV6VdxbgfsqI9MOZ7eOdXxwMkVBd2qoFnSVKQBCVEA8qWXybe6ugmIewyvNFMnpQIRRVRosaTBtI9VBAZVuxYcbzx4%3D; TAUD=LA-1712011712305-1*RDD-1-{formatted_data_snake}*RD-8779815-{formatted_data_snake}.919129*LG-1051019018-2.1.F.*LD-1051019019-.....; datadome=dok5w8TF5Kq8e0FclNKD0cDRNp~XjYx5Uux7e08PZZSiKw97W9HeRerqqmudr0DA6dqJOcP3~Vi4JAyKvOMUUNHAauPx1xmVS814_aBtGx_SULJifciiJwtCuV7gaE3O; OptanonConsent=isGpcEnabled=1&datestamp=Sun+Apr+14+2024+05%3A45%3A32+GMT%2B0300+(Eastern+European+Summer+Time)&version=202310.2.0&browserGpcFlag=1&isIABGlobal=false&hosts=&consentId=a96c8819-14bd-4454-8857-1bcdeece929b&interactionCount=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0004%3A0%2CC0002%3A0%2CC0003%3A0&AwaitingReconsent=false; TASession=V2ID.472230AB5B3443C0940DE6A4F55B5689*SQ.23*LS.Restaurant_Review*HS.recommended*ES.popularity*DS.5*SAS.popularity*FPS.oldFirst*LF.en*FA.1*DF.0*TRA.false*LD.1701933*EAU._',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'sec-gpc': '1',
    'upgrade-insecure-requests': '1',
    'user-agent': f'{user_agent}'
    },
    {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'accept-language': 'en-US,en;q=0.5',
    'cache-control': 'max-age=0',
    'cookie': f'TASameSite=1; TAUnique=%1%enc%3ArDJ0EzlkZHMkXVDUjo{random_string}nYC6Xy%2BlDBh8F8yg9MzvqlfcNH9qyL%2Bh7uVpNox8JbUSTxk%3D; TASSK=enc%3AAJSwtYFawrNeoFfTFnWfg2SIai{random_string}Pwi%2F%2F8R2AYDybzS4D1SboD4%2FOeFbU8sV8tAgivPVMYpd0a55jXtnwOXRH%2FZHq%2FTqxKdLUkZK3mKx3OqtNYaK9%2FV98QAo4w%3D%3D; ServerPool=C; TATravelInfo=V2*A.2*MG.-1*HP.2*FL.3*RS.1; TADCID=PdbuL2dZ47IRHg2-ABQCmq6heh9ZSU2yA8SXn9Wv5HzmohXMEnbShqwd1bvkBZR8UHZSfTyzcBIrb2Kawjs90bJIRHXLFf302Bo; __vt=68XtpmMiXBhAuR8MABQCwRB1grfcRZKTnW7buAoPsSzEQhGh1Wa_x70jEg9rLhVU8Cnk_eu-dem29vOx0I2SMImptmQizsh4idtN1E4RywLJ-KQGBlxTkwMGEvapd8tMR6C0PuVEZiG9bBO4uiHIz37S; PAC=ABP9T7_Fu7qvYht3aUTtklwHhyOTbo41t-2LynHuYGAQ5n_2njW_qZ1q3Rojo6GhbzE8uisyOSkvZ6jOZp-iSD4pTGY-HzVDAUEJLpkWBcZ8IwHcLY8B_FsAX-vT-xiCCHkRqODp1t-Mx_73clFVEs3dii_M1FwAE5BeAxIW37kyIzRIFjnW8lqCuhBqmEkCFYvSnXY0ZS7FdXb881z0gILLQZALUl5MsN5mI6beNZUuINFcV1GhukGWL2BrhHDOWw%3D%3D; SRT=TART_SYNC; PMC=V2*MS.59*MD.20240401*LD.20240414; TART=%1%enc%3AtYcH6QSNFOWM7D3Bkf9g4CT7ExDzMLzJmYHi7g%2BYzo7QnHNf5%2F4AW%2BR2NuvKwonWJ7r1iEgl44g%3D; TASID=851851282B8D4F899CD2B6412666D5DA; TAReturnTo=%1%%2F{other_chunk_url}; roybatty=TNI1625!AEABitUXBw0AF1TVuIthdjEtdGh4gAcKe0jsLnwLDFfZmOBElMmCQrWj1Rh6gAuBa1KWwlIs5ly3Qnp%2FohpgvaM%2FNrzADqOG5BqloPSeZ8%2BY1eaAAhHNz3UDrNkzObADGHNXG4xhadBhayO2BAeDOjkctyJZZGndqcK1UtQvtp4ry0204Mv8CqYEcCvP19b2qg%3D%3D%2C1; TATrkConsent=eyJvdXQiOiJBRFYsU09DSUFMX01FRElBIiwiaW4iOiJBTkEsRlVOQ1RJT05BTCJ9; datadome=3yrO2lOEcO2H_2KHvix22MHhmf1amdo3gcyW3MjqpeKz_s0cw9Ew6HB3OA2HZB~KRE_pbp2peBMbwD8TZExDiQR2qRtmMoR~GB~fk0dREd2~coGwXIsdm8BHmIJLmX7C; TASession=V2ID.851851282B8D4F899CD2B6412666D5DA*SQ.22*LS.DemandLoadAjax*HS.recommended*ES.popularity*DS.5*SAS.popularity*FPS.oldFirst*LF.fr*FA.1*DF.0*TRA.true*LD.14029549*EAU._; TAUD=LA-1712013140063-1*RDD-1-2024_04_02*LG-1131222230-2.1.F.*LD-1131222231-.....; OptanonConsent=isGpcEnabled=1&datestamp=Mon+Apr+15+2024+04%3A26%3A08+GMT%2B0300+(Eastern+European+Summer+Time)&version=202310.2.0&browserGpcFlag=1&isIABGlobal=false&hosts=&consentId=9c41e751-7e44-444a-96ee-b6e2c5784206&interactionCount=1&landingPath=https%3A%2F%2Ffr.tripadvisor.be%2F{other_chunk_url}.html&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A0',
    'referer': f'{url}',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'sec-gpc': '1',
    'upgrade-insecure-requests': '1',
    'user-agent': f'{user_agent}'
    },
    {
    'User-Agent': f'{user_agent}',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Cookie': f'_ga_QX0Q50ZC9P=GS1.1.171{random_three_number}4696.11.0.171{random_three_number}4702.54.0.0; TAUnique=%1%enc%3Ae6Cz0r{random_string}5v8u%2FFtiYE3%2FyiW0EDOi7KVvePPj8LiWKc8Y4XNH0tB%2BAHD7Nox8JbUSTxk%3D; TATravelInfo=V2*AY.2024*AM.4*AD.28*DY.2024*DM.4*DD.29*A.2*MG.-1*HP.2*FL.3*DSM.1713144695913*RS.1*RY.2024*RM.4*RD.1*RH.20*RG.2; TAUD=LA-1711838732794-1*RDD-1-2024_03_30*RD-176991627-2024_04_01.919129*ARC-416825301*HDD-1177790422-2024_04_21.2024_04_22*LD-1305968774-2024.4.28.2024.4.29*LG-1305968776-2.1.F.*ARDD-1305968777-2024_04_28.2024_04_29; _abck=E423D2A3711F6B3092A32DF16AEAB4F2~-1~YAAQdawQAk2/ScmOAQAAz3Nh3wt9jCvOtXhJ+SFwucp36VXLPMAQiwaVSTdTCwMB1qSuDMloXKnYe2GZKnu4k76uY0vA7BO05HAUXtyBzlKKLFiee23rkvTTtv73r7bTeMEb92BdDGOEJI6Qfiu/za72JCVT56g/NKZTSATwY8DqWrLl1AvqVGMqaAPagNhqDUg4vpGpoh/F/hGksdJJe1cOejveBnZMefZN3hIL0QCeZPMcJg1FBcEXeTqYyKK0G6lL29C7wGpYhqd8JZecgUnVWtNI+Uc1a2vLDKdHo27giZ3m+1zawNEBGtWgOWfIWI2Ev0B/8LASlGYEV2NgBDGF2mqravP3ZdR3ZRI50v6E5buqP+MQQjKa3tR+QwHsPMCcBZT4bOuIoqqrFqJqbtxwkTn7+8CPzg3T7Q==~-1~-1~-1; datadome=gY9_uAFXo3or_pu1l6MUBuInFp6nq8HbQa1ZjtU8QJejx13Q0BqFltobI2KD1Kw4pc3WPWrhA7kAudaifcOkn0_i0P7EAn3_b_WqfNUtSBfFl4~pu~oGgjyWeuy54IgG; OptanonConsent=isGpcEnabled=0&datestamp=Mon+Apr+15+2024+04%3A31%3A36+GMT%2B0300+(%D0%92%D0%BE%D1%81%D1%82%D0%BE%D1%87%D0%BD%D0%B0%D1%8F+%D0%95%D0%B2%D1%80%D0%BE%D0%BF%D0%B0%2C+%D0%BB%D0%B5%D1%82%D0%BD%D0%B5%D0%B5+%D0%B2%D1%80%D0%B5%D0%BC%D1%8F)&version=202310.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=0d1b6f8b-25fb-4129-8570-f901a1d419c8&interactionCount=2&landingPath=NotLandingPage&groups=C0001%3A1%2CC0004%3A1%2CC0002%3A1%2CC0003%3A1%2CV2STACK42%3A1&AwaitingReconsent=false&geolocation=NL%3BNH; ab.storage.sessionId.6e55efa5-e689-47c3-a55b-e6d7515a6c5d=%7B%22g%22%3A%22e6e51c6b-b7eb-de37-0d11-2f17ff06c4a8%22%2C%22e%22%3A1713144715928%2C%22c%22%3A1713144696699%2C%22l%22%3A1713144700928%7D; ab.storage.deviceId.6e55efa5-e689-47c3-a55b-e6d7515a6c5d=%7B%22g%22%3A%224475cc90-d597-3b2b-3c8d-2727d0ac0e76%22%2C%22c%22%3A1712009725648%2C%22l%22%3A1713144696700%7D; _ga=GA1.1.1933623039.1712009726; pbjs_sharedId=d3af9fd2-43e6-4c4f-9f4c-59bc5cff40b0; pbjs_sharedId_cst=CSzfLKsskA%3D%3D; _lc2_fpi=b140173de591--01htdvpjcs55ta01ngct9rpqt1; _lc2_fpi_meta=%7B%22w%22%3A1712009726361%7D; __gads=ID=c3612db02b09ea57:T=1712009727:RT=1713144698:S=ALNI_MZ2vYyYwxsbRZpkVeGKTfakttGpcQ; __gpi=UID=00000d8767181424:T=1712009727:RT=1713144698:S=ALNI_MYdsnII3IZuqwvvhJE8ReYpzn6SCA; __eoi=ID=959e08674f2f0073:T=1712009727:RT=1713144698:S=AA-AfjaD3N0V71grRuZguVsGgqs5; OptanonAlertBoxClosed=2024-04-04T21:42:29.460Z; eupubconsent-v2=CP8iaEgP8iaEgAcABBENAuEsAP_gAEPgACiQg1NX_D5ebWti8XZUIbtkaYwP55izokQhBhaIEewFwAOG7BgCB2EwNAV4JiACGBAEkiLBAQNlHABUCQAAAIgRiSCMYkWMgTNKJKBAiFMRO0NYCBxmmgFDWQCY5kosszdxmDeAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAA_cff79LgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEQaoMoACIAFAAXAA4ADwAKgAXAA4AB4AEAAJAAXwAxADKAGgAagA8AB-AEQAJgAUwAqwBcAF0AMQAaAA3gB-AEJAIgAiQBHACWAE0AMAAYYAywBmgDZAHIAPiAfYB-wD_AQAAg4BEYCLAIwARqAjgCOgEiAJKAT8AqABcwC8gF9AMUAZ8A0QBrwDaAG4AOkAdsA-wB_wEIAImAReAj0BIgCVgExQJkAmUBOwCh4FIAUiApMBUgCrAFZAK7gWIBYoC0YFsAWyAt0BcgC6AF2gLvgXkBeYC-gGCANsgm2CbkE3gTfAnDBOUE5gJ0gTrgnaCdwE8AJ5gT7gn6CfwFAAKCBBqAKBACQAdABcAGyARAAwgCdAFyANsAgcEADAA6AFcARAAwgCdAIHBgA4AOgAuADZAIgAYQBcgEDhAAcAHQA2QCIAGEAToAuQCBwoAGAFwAwgEDhgAIAwgEDhwAYAHQBEADCAJ0AgcBFcgACAMIBA4kADAIgAYQCBxQAKADoAiABhAE6AQO.f_wACHwAAAAA; OTAdditionalConsentString=1~43.46.55.61.70.83.89.93.108.117.122.124.135.136.143.144.147.149.159.192.196.202.211.228.230.239.259.266.286.291.311.320.322.323.327.338.367.371.385.394.397.407.413.415.424.430.436.445.453.486.491.494.495.522.523.540.550.559.560.568.574.576.584.587.591.737.802.803.820.821.839.864.899.904.922.931.938.979.981.985.1003.1027.1031.1040.1046.1051.1053.1067.1085.1092.1095.1097.1099.1107.1135.1143.1149.1152.1162.1166.1186.1188.1205.1215.1226.1227.1230.1252.1268.1270.1276.1284.1290.1301.1307.1312.1345.1356.1364.1365.1375.1403.1415.1416.1421.1423.1440.1449.1455.1495.1512.1516.1525.1540.1548.1555.1558.1570.1577.1579.1583.1584.1591.1603.1616.1638.1651.1653.1659.1667.1677.1678.1682.1697.1699.1703.1712.1716.1721.1725.1732.1745.1750.1765.1782.1786.1800.1810.1825.1827.1832.1838.1840.1842.1843.1845.1859.1866.1870.1878.1880.1889.1899.1917.1929.1942.1944.1962.1963.1964.1967.1968.1969.1978.1985.1987.2003.2008.2027.2035.2039.2047.2052.2056.2064.2068.2072.2074.2088.2090.2103.2107.2109.2115.2124.2130.2133.2135.2137.2140.2145.2147.2150.2156.2166.2177.2183.2186.2205.2213.2216.2219.2220.2222.2225.2234.2253.2279.2282.2292.2299.2305.2309.2312.2316.2322.2325.2328.2331.2334.2335.2336.2337.2343.2354.2357.2358.2359.2370.2376.2377.2387.2392.2400.2403.2405.2407.2411.2414.2416.2418.2425.2440.2447.2461.2462.2465.2468.2472.2477.2481.2484.2486.2488.2493.2498.2499.2501.2510.2517.2526.2527.2532.2535.2542.2552.2563.2564.2567.2568.2569.2571.2572.2575.2577.2583.2584.2596.2604.2605.2608.2609.2610.2612.2614.2621.2628.2629.2633.2636.2642.2643.2645.2646.2650.2651.2652.2656.2657.2658.2660.2661.2669.2670.2677.2681.2684.2687.2690.2695.2698.2713.2714.2729.2739.2767.2768.2770.2772.2784.2787.2791.2792.2798.2801.2805.2812.2813.2816.2817.2821.2822.2827.2830.2831.2834.2838.2839.2844.2846.2849.2850.2852.2854.2860.2862.2863.2865.2867.2869.2873.2874.2875.2876.2878.2880.2881.2882.2883.2884.2886.2887.2888.2889.2891.2893.2894.2895.2897.2898.2900.2901.2908.2909.2916.2917.2918.2919.2920.2922.2923.2927.2929.2930.2931.2940.2941.2947.2949.2950.2956.2958.2961.2963.2964.2965.2966.2968.2973.2975.2979.2980.2981.2983.2985.2986.2987.2994.2995.2997.2999.3000.3002.3003.3005.3008.3009.3010.3012.3016.3017.3018.3019.3024.3025.3028.3034.3038.3043.3048.3052.3053.3055.3058.3059.3063.3066.3068.3070.3073.3074.3075.3076.3077.3078.3089.3090.3093.3094.3095.3097.3099.3100.3106.3109.3112.3117.3119.3126.3127.3128.3130.3135.3136.3145.3150.3151.3154.3155.3163.3167.3172.3173.3182.3183.3184.3185.3187.3188.3189.3190.3194.3196.3209.3210.3211.3214.3215.3217.3219.3222.3223.3225.3226.3227.3228.3230.3231.3234.3235.3236.3237.3238.3240.3244.3245.3250.3251.3253.3257.3260.3270.3272.3281.3288.3290.3292.3293.3296.3299.3300.3306.3307.3309.3314.3315.3316.3318.3324.3328.3330.3331.3531.3731.3831.3931.4131.4531.4631.4731.4831.5231.6931.7031.7235.7831.7931.8931.9731.10231.10631.10831.11031.11531.12831.13632.13731.14237.15731.16831.21233.23031.24431.24533.25731.25931.26031.26831; TASession=V2ID.B51D8692E8DF49DCBF79D6F8E4AEC2E7*SQ.19*LS.DemandLoadAjax*HS.recommended*ES.popularity*DS.5*SAS.popularity*FPS.oldFirst*LF.en*FA.1*DF.0*TRA.false*LD.8354459*EAU._; ServerPool=X; TAReturnTo=%1%%2F{other_chunk_url}; bm_sz=DF67DDFFF5931553C23D4C4DA2440A69~YAAQdawQAnW/ScmOAQAA4Ilh3xe2nI7GcwljccQsafjyitn0b3RxmFJ+wLtV2tNFjBSvARayfAVrgQBmX3giIFIWPE77WEpLpbGgLQM/IXmwFxUdOeJeyOoA/rjO2ey6AnSMHyMtDZnDjeFz+d1R7V2qu1fXhKr6FHEc+og2YqVIvOkXBhBA7Wk3F5IWEdN4pb0ev3laNJOsLhtODYh94MS176Nfpg3Z3N/3EYQdCCvg91sjDj4B/euRO5GqV84txmgn+3YEuepWNjwimWCHCWaCGtEG5XaqhBpNdRmWZJmmhBeEcAcocTMbVLxygbSJF2HnphYuoqnXevnU+9SP0WNJtwbLZOsKaKK/88+gj2M2tyylbBHljEYYhBgSRrZjNnGcC6TvH700vVtzXGFttloYuuWLs8Q=~3225136~4343110; TADCID=4MoKuq2TSbucQmsgABQCmq6heh9ZSU2yA8SXn9Wv5HzmqIUdjNpGvz5qegW4KTeFMdCyEe4RFcQoYHTTDNeo0Lzfhtx0cqSC0Hg; TASameSite=1; __vt=RdO4RmfaSg5f-BrVABQCwRB1grfcRZKTnW7buAoPsSzESAgwfIEDShMpkhiLonaHIuhMcTdm2tOqxbsokim8dwybof6sLaa_aiVgG9UQJNv9CLSQ2nJTCJ6cpmeMbUyReTqb5jVAC0A4YFCHIQsnwCPeug; TASSK=enc%3AAPVC0R%2BxaKgz2olEwO5IzMjxYdrqNE367nxgVuOnBEtwGHLOoH%2BY0FSAGqNIYJSIHFiLBuaWzuemQl63iib6W9%2BapIboUKxvFAIoq0S%2Fgnd5XV6X4NHZa5c%2BGmJRR7u5wg%3D%3D; PAC=AFESH1_UYvOvMQO0dCrXj9-j-xhM97u4YaO5LCNwFgTj-ekWXQjSMu5bpHTZDI90ObUhnkPzn968H5p9X4_IIjpOQXo-JjcF3YkJ74mZ5DSWX1r5NDTlU1Iv5mi0Mf6QiYvuL4L0omozmaB1pMD0Jz69qVMVg_GCDnNXCb-2UQbd2-Zhq3bDuPJ15rIlsk-yOlZWnbu8Hs3Z7zSD9pKgXxeMTrwUWy9ohieJVBpZLEkamnVwPXC_1Huz_ahRqVqYvg%3D%3D; SRT=TART_SYNC; PMC=V2*MS.72*MD.20240414*LD.20240414; TART=%1%enc%3AtYcH6QSNFOVAY45YC%2FX3%2FA1KaaCn7tT6ha4SjYT217fEYItjIFrFi65H%2FrSFOqrVkagyFvowwb0%3D; TASID=B51D8692E8DF49DCBF79D6F8E4AEC2E7; roybatty=TNI1625!AI18bSMJEgZ5o7t9JR550iMoOtvtlMFiWNvCmay%2Fsa9GPrioX3UOi%2FQjZPMdff1XyUGp22WyZju%2BzE7mbJ1PjJcMK76n6RZ2FY0Yb1lVDIP0z1%2BBk7ZauZQSVunGdoAgtau2nmrkT1yvsQWv0js7%2FsihJX7caLXTVqv4hZ95%2Fq6ybhhIA3v25gf065hqE9QPJA%3D%3D%2C1; TATrkConsent=eyJvdXQiOiJTT0NJQUxfTUVESUEiLCJpbiI6IkFEVixBTkEsRlVOQ1RJT05BTCJ9; _lr_sampling_rate=100; CM=%1%sesswifi%2C%2C-1%7CPremiumMobSess%2C%2C-1%7Ct4b-pc%2C%2C-1%7CRCPers%2C%2C-1%7Csesstch15%2C%2C-1%7CRestAds%2FRPers%2C%2C-1%7CCYLPUSess%2C%2C-1%7CTheForkMCCPers%2C%2C-1%7Ctvsess%2C%2C-1%7CTBPers%2C%2C-1%7Cperstch15%2C%2C-1%7CRestPremRSess%2C%2C-1%7CCCSess%2C%2C-1%7CCYLSess%2C%2C-1%7CPremRetPers%2C%2C-1%7Cpershours%2C%2C-1%7C%24%2C%2C-1%7Csesssticker%2C%2C-1%7CPremiumORSess%2C%2C-1%7Ct4b-sc%2C%2C-1%7CMC_IB_UPSELL_IB_LOGOS2%2C%2C-1%7CTrayspers%2C%2C-1%7Cb2bmcpers%2C%2C-1%7CPremMCBtmSess%2C%2C-1%7CMC_IB_UPSELL_IB_LOGOS%2C%2C-1%7Csess_rev%2C%2C-1%7Csessamex%2C%2C-1%7CPremiumRRSess%2C%2C-1%7CTADORSess%2C%2C-1%7CMCPPers%2C%2C-1%7Csesshours%2C%2C-1%7CSPMCSess%2C%2C-1%7CTheForkORSess%2C%2C-1%7Cpers_rev%2C%2C-1%7Cmdpers%2C%2C-1%7CTheForkRRSess%2C%2C-1%7CRestAds%2FRSess%2C%2C-1%7CPremiumMobPers%2C%2C-1%7CRCSess%2C%2C-1%7CRestAdsCCSess%2C%2C-1%7Csesslaf%2C%2C-1%7CRestPremRPers%2C%2C-1%7CCYLPUPers%2C%2C-1%7Cperslaf%2C%2C-1%7CRevHubRMPers%2C%2C-1%7Cpssamex%2C%2C-1%7CTheForkMCCSess%2C%2C-1%7CCYLPers%2C%2C-1%7CCCPers%2C%2C-1%7Ctvpers%2C%2C-1%7CTBSess%2C%2C-1%7Cb2bmcsess%2C%2C-1%7Cperswifi%2C%2C-1%7CPremRetSess%2C%2C-1%7CRevHubRMSess%2C%2C-1%7CPremiumRRPers%2C%2C-1%7CRestAdsCCPers%2C%2C-1%7CMCPSess%2C%2C-1%7CTADORPers%2C%2C-1%7CTheForkORPers%2C%2C-1%7CTrayssess%2C%2C-1%7CPremMCBtmPers%2C%2C-1%7CTheForkRRPers%2C%2C-1%7CPremiumORPers%2C%2C-1%7Cperssticker%2C%2C-1%7CSPORPers%2C%2C-1%7Cbooksticks%2C%2C-1%7Cbookstickp%2C%2C-1%7Cmdsess%2C%2C-1%7C; TASession=V2ID.1BD355853A2E4C75B7E8A4D071B1E2CE*SQ.30*LS.DemandLoadAjax*HS.recommended*ES.popularity*DS.5*SAS.dateRecent*FPS.oldFirst*LF.en*FA.1*DF.0*TRA.false*LD.497884*EAU._; TAUD=LA-1713059605396-1*RDD-1-2024_04_14*RD-45249-2024_04_14.1164633*LG-2067809-2.1.F.*LD-2067810-.....; datadome=GltthGER4N0CMKStnmCsaK8NiC9~D09rAu8E{random_string}KkjNyOvf8_7zs4Me1s5P0yGMRtevZfzer2_FiKDBhgqjZr66sJGrNbb2f_xb2An_la9_EFYM7wOYRG2_Ff',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'TE': 'trailers'
    }
    ]

    proxies = [
    "http://sashabodiul07:7UMNo7iRr6@161.77.75.248:50100",
    "http://sashabodiul07:7UMNo7iRr6@168.158.37.211:50100",
    'http://instacombine06ZaJ:NpU7hKC8hj@91.124.71.230:50100'
    ]
    proxy = random.choice(proxies)

    async with aiohttp.ClientSession() as session:
        # HTTP
        async with session.get(url=url, headers=random.choice(headers), proxy=proxy) as response:
            content = await response.text()
            if len(content)>5000:
                return content
            else:
                # HTTPS
                async with session.get(url=url, headers=random.choice(headers), proxy=proxy) as response:
                    content = await response.text()
                    
                    return content


async def generate_self_signed_certificate():
    # Генерация закрытого ключа RSA
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    # Генерация случайного серийного номера для сертификата
    serial_number = int(uuid.uuid4())

    # Генерация случайных атрибутов для имени сертификата
    common_name = str(uuid.uuid4())

    # Генерация самоподписанного сертификата
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"California"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Mountain View"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"OpenAI"),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])

    certificate = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        serial_number
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName(common_name),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256())

    # Создание уникальных имен для временных файлов ключа и сертификата
    with tempfile.NamedTemporaryFile(delete=False) as key_file:
        key_filename = key_file.name
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
        key_file.write(private_key_pem)

    with tempfile.NamedTemporaryFile(delete=False) as cert_file:
        cert_filename = cert_file.name
        cert_pem = certificate.public_bytes(serialization.Encoding.PEM)
        cert_file.write(cert_pem)

    return key_filename, cert_filename


# Пример использования:
async def main():
    old_domain = MAIN_DOMAIN.strip()
    new_domain = random.choice(DOMAINS_LIST).strip()
    user_agent = random.choice(USER_AGENTS_LIST).strip()
    rest_url = "https://en.tripadvisor.com.hk/Restaurant_Review-g54273-d497884-Reviews-Hudson_s_Seafood_House_on_the_Docks-Hilton_Head_South_Carolina.html"
    proxies = [
    "http://sashabodiul07:7UMNo7iRr6@161.77.75.248:50100",
    "http://sashabodiul07:7UMNo7iRr6@168.158.37.211:50100",
    'http://instacombine06ZaJ:NpU7hKC8hj@91.124.71.230:50100'
    ]
    proxy = random.choice(proxies)
    content = await scrape_data(proxy=proxy,
                                            old_domain=str(old_domain),
                                            new_domain=str(new_domain),
                                            user_agent=str(user_agent),
                                            url=str(rest_url))
    
    with open('test.html','w') as f:
        f.write(content)
    res = await get_result_data(content,rest_url)
    print(res)
    result = await get_all_data_from_restaurants(content,rest_url)
    print(result)

