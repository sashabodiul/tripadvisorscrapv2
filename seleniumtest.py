from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
import time
from bs4 import BeautifulSoup
import re

def get_result_data(content,url):
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

# Список прокси
proxies = [
    "http://instacombine06ZaJ:NpU7hKC8hj@91.124.71.230:50100",
    "http://instacombine06ZaJ:NpU7hKC8hj@91.124.78.27:50100",
    "http://instacombine06ZaJ:NpU7hKC8hj@91.124.76.167:50100",
    "http://instacombine06ZaJ:NpU7hKC8hj@91.124.69.204:50100",
    "http://instacombine06ZaJ:NpU7hKC8hj@91.124.79.234:50100",
    "http://instacombine06ZaJ:NpU7hKC8hj@91.124.72.43:50100",
    "http://sashabodiul07:7UMNo7iRr6@91.124.69.153:50100",
    "http://sashabodiul07:7UMNo7iRr6@91.124.73.67:50100",
    "http://sashabodiul07:7UMNo7iRr6@91.124.78.223:50100",
    "http://sashabodiul07:7UMNo7iRr6@91.124.70.151:50100",
    "http://sashabodiul07:7UMNo7iRr6@91.124.77.65:50100",
    "http://sashabodiul07:7UMNo7iRr6@91.124.68.11:50100",
    "http://sashabodiul07:7UMNo7iRr6@91.124.75.198:50100",
    "http://sashabodiul07:7UMNo7iRr6@91.124.79.88:50100",
    "http://sashabodiul07:7UMNo7iRr6@91.124.71.196:50100",
    "http://sashabodiul07:7UMNo7iRr6@91.124.76.174:50100"
]

# Выберите один из прокси из списка
proxy = proxies[-1]

# Создание объекта WebDriver с настройками прокси
proxy_server = Proxy({
    'proxyType': ProxyType.MANUAL,
    'httpProxy': proxy,
    'ftpProxy': proxy,
    'sslProxy': proxy,
    'noProxy': ''
})

options = webdriver.ChromeOptions()
options.add_argument('--proxy-server='+proxy)
driver = webdriver.Chrome(options=options)

# Загрузка страницы
url = "https://fr.tripadvisor.be/Restaurant_Review-g298124-d7409937-Reviews-Schumann-Shizuoka_Shizuoka_Prefecture_Tokai_Chubu.html"  # Замените на ваш URL
driver.get(url)
time.sleep(10)
# Теперь вы можете взаимодействовать с веб-страницей с помощью объекта driver


data = get_result_data(content=driver.page_source,url=url)
print(data)
# Не забудьте закрыть браузер после использования
driver.quit()
