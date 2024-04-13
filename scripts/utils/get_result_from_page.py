from datetime import datetime
from bs4 import BeautifulSoup
import re
import base64
import asyncio
import aiofiles


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
            log_filename = 'data/logs/logfile.log'
            log_message = ':[ERROR] No match fount for g code'
            async with asyncio.Lock():
                async with aiofiles.open(log_filename, mode='a') as logfile:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    log_entry = f"[{timestamp}] {log_message}\n"
                    await logfile.write(log_entry)

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
        log_filename = 'data/logs/logfile.log'
        log_message = (f"[ERROR] with BeautifulSoup get response: ,{e}")
        async with asyncio.Lock():
            async with aiofiles.open(log_filename, mode='a') as logfile:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                log_entry = f"[{timestamp}] {log_message}\n"
                await logfile.write(log_entry)
        
        
async def get_result_data(content,url):
    try:
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
        result_data['city'] = city if city else None
        result_data['link'] = url if url else None
        
        return result_data
    except Exception as e:
        log_filename = 'data/logs/logfile.log'
        log_message = f'[ERROR] Cannot get data with BS4 {e}'
        async with asyncio.Lock():
            async with aiofiles.open(log_filename, mode='a') as logfile:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                log_entry = f"[{timestamp}] {log_message}\n"
                await logfile.write(log_entry)