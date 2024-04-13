from datetime import datetime, timedelta
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.x509.oid import NameOID
import tempfile
import uuid
import asyncio
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
    rating = soup.find('span', class_='biGQs _P fiohW uuBRH').text
    name = soup.find('h1', class_='biGQs _P egaXP rRtyp').text
    other_ratings = div_rate.find_all('svg', class_='UctUV d H0')
    div_pos_rate = soup.find('div',class_='CsAqy u Ci Ph w')
    div_emails = soup.find_all('div',class_='hpxwy e j')
    email = None
    for div in div_emails:
        test_res = div.find('a')
        if test_res.get('aria-label') == 'Email':
            email = test_res.get('href').replace('mailto:','')
    main_div = soup.find('div',class_='lJSal _T')
    main_spans = main_div.find_all('span',class_='biGQs _P pZUbB hmDzD')
    prices = main_spans[1]
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
    pos_in_rate = div_pos_rate.find('span', class_='biGQs _P pZUbB hmDzD')
    city = pos_in_rate.text.split(' ')[-1] if len(pos_in_rate.text.split(' ')) > 2 else ''
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
    result_data['rating'] = rating if rating else None
    result_data['name'] = name if name else None
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
    try:
        other_chunk_url = url.split('/')[-1]
        # url = url.replace(old_domain,new_domain)
        domain = new_domain.split('/')[-2]
        dom2 = domain.split('.')[1:]
        domain2 = '.'.join(dom2)
        
        payload = {}
        headers = {
                'accept': 'text/html',
                'accept-language': 'en-US,en;q=0.6',
                'cache-control': 'max-age=0',
                'cookie': f'TASameSite=1; TAUnique=%1%enc%3AR0ej7L4E8DnRN9qtQ92%2FkeHOgMiyBexu9boTKBqB8E3smifpu%2BS23UpCaVh1IJQVNox8JbUSTxk%3D; TASSK=enc%3AAIYXoM0CO0t4IyvUWtEtCsw22QXCOKdVDo8YeSUyprlazNIK3PW7swWvCko9KkWnyHnzmAXzHNiqjZdsUAiS6IJnTz%2F%2BXna6xRjReTfc5Hgunr1WMu3rX7BSoNyxRVLtlQ%3D%3D; ServerPool=X; G_AUTH2_MIGRATION=informational; TATrkConsent=eyJvdXQiOiJBRFYsU09DSUFMX01FRElBIiwiaW4iOiJBTkEsRlVOQ1RJT05BTCJ9; VRMCID=%1%V1*id.13091*llp.%2FRestaurants-g187275-Germany%5C.html*e.1712444845523; TATravelInfo=V2*AY.2024*AM.4*AD.14*DY.2024*DM.4*DD.15*A.2*MG.-1*HP.2*FL.3*DSM.1712018799988*AZ.1*RS.1*RY.2024*RM.3*RD.30*RH.20*RG.2; TAReturnTo=%1%%2F{other_chunk_url}; TART=%1%enc%3AtYcH6QSNFOVvXZbzIvGyUBW4fWd3qtDpTrNYG7p0UMrm7XED%2B%2FPsIRtj8WFAaXbqZQnMIP2Q3mY%3D; TADCID=IJR3ePM9teLUJgN3ABQCmq6heh9ZSU2yA8SXn9Wv5HzaqZbXSk8mtnqY3JMuC21PBGuJXPtGuoslRSaWuZVTcxttgO57AGtw_8M; TAAUTHEAT=GewofqlUVI25xqtTABQCNrrFLZA9QSOijcELs1dvVzyxqYgCZWN43F5JmMkaFo8P12z50lneHPYjXbKT5THPkp0JLU9bVj0egkt0Mpx0AcLbZeD3mx_rAvxsBjU9dT3HJLRH7qyZMSH84JY_4N76wHBWBr2n_NlEMtAK00eBUegQZFmaE8jqS0DET1Eczkz1Kr2ToQs01dWwEV3ntEZurK-OhoTF-0gpSft6; __vt=yk0hqNbuTRW8rXjLABQCwRB1grfcRZKTnW7buAoPsSy4SSbsvcBOfCDu8FswCj3H9riqch50ZDDOvIHkOfe4wr_PCyHYwfA2ufUddMP_rUGAU9EodLJxxI7gVgbxjEOktbV1LpZXYKT-6csCAbjUcA-kBYk; TASID=1DDC4ACE2BDEB6BDC17D13EE23F1DF92; _abck=B5E8EB88F4793A85F7D0DB43DEDB5DBA~-1~YAAQXjYQYL+spNGOAQAAietl1AthB70pB/ZdGLUouI9SmfZZO4tlgtvNgOdCqGqU8ct71CGTZ7zdH9i86GUc/7ZzSAle2o1ohjpm8W5DmThLSxWORSVaSpBwb4pGcKAG/MvO2FuC+373GT2I9a9J3NqG5BoTInEiBSNTRXEDUpznT+4IUija1y4M7nAuDaQDkgiOefKD5E0uTUmmTTZeoIZzNLLg4m+E0GfJKldyJ8zsnz6cD4duPPs3rUiXU7opD1uOYHx4BjDofuRbukAnPgUQPyr9db/x/dS3ox0R+Gmb23uSyn6e3oF5JxRRe7OevpaFBa7PTOtCZeRfddClQj9jFP+k3MMNJ83YXHvOyaRDeArTg8cNwUQ2dr0RNHeXEzRCGFFQGsQZgowvH4zy~-1~-1~-1; PAC=AJ-AkRhwk6dYwk9A2tJzzIEKjPuC3TvGeqlOBINGaAwWmiQi9mhKydtSpPaN2AEaVjXTA9VRROSrrtPypL5tNICGffessQ-vhmJUsNXrkdo1XYO80Lgb1EQ-VrU5jBT7HA%3D%3D; SRT=TART_SYNC; roybatty=TNI1625!AMj9YlElfJN7pKy%2BC98LfaEePPd5NjvPAgk6%2BGwaUFIz87ObOW2dT9%2BD0XMKHG4dWCZvMWwalS8M4PBdlp0u%2FUvPoeNrL6nCduhw8bnMeyixrIKgkFSorfaVOrN3H5DNc769JCOX3lMEAUHs9jcmDEcWf8zLk%2B1e6hkHxH9F90DlC8mVH2609qZTcFArsnJCNA%3D%3D%2C1; datadome=KzGPkNK_C05CimTIULGK8n9RQqWxosRwueZad5t93nWLbsS1hchxKsnuJIV04bqspV06OE6yIZmvl_M9gv21qmgqvVek~QwwJtFaQmkxo9qc0ujvy0iXub6Kq5AL2UR9; bm_sz=B2FEEA5DC4D2933AE0B640A862622924~YAAQXjYQYM6vpNGOAQAAwF1m1BcLa+cbP9IKIavjnhnKtIB1sMxRVOYPmms2v2K6E9dwEjaVjPtmYRx1j+oOGRUA2barxL78Xat0bOjnIdl0+L9ztzSVzQdJifNxi05FFqiIq1nEO48u9OSGYBlijlzvy1XP/64S5vE7s0mSWQETERAjIMmjBCrt7sdXXcRDw0IiGFh3Y0RbwatFs4+3oxwoxPGDjpmzGqmL8qIyv/ELt/pggcph87fpw+6jOcOqTuPTHsQ4Y/jM+hgb3RtnchHDNhH1j1Qvpv7acfMHakVFo6IIEvSFGxNSYera+kAfAzliDzPd2spWke+6KoZGlngonqeAOKwrC9bomarBRJpfM5+yWc8q9XFTtfJ/xjS92c+FXpDRGRxcGt07Dxv7+f/P2jAWOcPNUcd35nXJ~3553094~4604471; TASession=V2ID.1DDC4ACE2BDEB6BDC17D13EE23F1DF92*SQ.1364*LS.Restaurant_Review*HS.recommended*ES.popularity*DS.5*SAS.popularity*FPS.oldFirst*TS.1B32A4EB67F120996C79F7754BEA64F2*FV.T*LF.en*FA.1*DF.0*TRA.false*LD.1079658*EAU.o',
                'referer': 'https://www.tripadvisor.com/Search?searchSessionId=000a310fbff7fb9f.ssid&searchNearby=false&ssrc=e&q=fdd&sid=1DDC4ACE2BDEB6BDC17D13EE23F1DF921712960458460&blockRedirect=true&geo=1',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'sec-gpc': '1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'
                }

        # Где-то в вашем коде генерируется ключ и сертификат
        key_file_path, cert_file_path = await generate_self_signed_certificate()

        # Создание SSL контекста с использованием сгенерированного ключа и сертификата
        ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ssl_context.load_cert_chain(certfile=cert_file_path, keyfile=key_file_path)

        # Использование SSL контекста при создании TCPConnector
        connector = TCPConnector(ssl=ssl_context)

        async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
            async with session.get(url) as response:
                if response.content_type == 'application/octet-stream' and response.headers.get('content-encoding') == 'br':
                    # Decode Brotli content
                    content = await response.read()
                    decoded_content = brotli.decompress(content)
                    return decoded_content.decode('utf-8')
                else:
                    return await response.text()
    except Exception as e:
        print(datetime.now(),':[ERROR] scrap page: ', e, 'with url: ', url)


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
    rest_url = "https://www.tripadvisor.com/Restaurant_Review-g39604-d7803737-Reviews-Yummy_Pollo-Louisville_Kentucky.html"
    content = await scrape_data(proxy=random.choice(PROXY_LIST),
                                            old_domain=str(old_domain),
                                            new_domain=str(new_domain),
                                            user_agent=str(user_agent),
                                            url=str(rest_url))
    # with open('test.html','w') as f:
    #     f.write(content)
    res = await get_result_data(content,rest_url)
    print(res)
    # result = await get_all_data_from_restaurants(content,rest_url)
    # print(content)

