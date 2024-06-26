import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests

# Прокси список
proxies = [
    "http://sashabodiul07:7UMNo7iRr6@91.124.86.145:50100",
    "http://sashabodiul07:7UMNo7iRr6@91.124.99.49:50100",
    "http://sashabodiul07:7UMNo7iRr6@91.124.87.70:50100",
    "http://sashabodiul07:7UMNo7iRr6@91.124.84.115:50100",
    "http://sashabodiul07:7UMNo7iRr6@91.124.95.74:50100",
    "http://sashabodiul07:7UMNo7iRr6@91.124.98.106:50100",
    "http://sashabodiul07:7UMNo7iRr6@91.124.97.133:50100",
    "http://sashabodiul07:7UMNo7iRr6@91.124.92.6:50100",
    "http://sashabodiul07:7UMNo7iRr6@91.124.96.5:50100",
    "http://sashabodiul07:7UMNo7iRr6@91.124.76.174:50100",
    "http://sashabodiul07:7UMNo7iRr6@91.124.93.253:50100",
]

# URL для посещения
url = 'https://www.tripadvisor.com/Restaurant_Review-g186334-d13941837-Reviews-Cafe_Delhi-Leicester_Leicestershire_England.html'

# Словарь для хранения заголовков
headers_dict = {}

# Обход всех прокси из списка
for proxy in proxies:
    try:
        # Настройки прокси для Selenium
        chrome_options = Options()
        chrome_options.add_argument(f'--proxy-server={proxy}')

        # Запуск браузера
        driver = webdriver.Chrome(options=chrome_options)

        # Посещение страницы
        driver.get(url)

        # Получение заголовков с использованием requests
        response = requests.get(url, proxies={"http": proxy, "https": proxy})
        headers = dict(response.headers)

        # Сохранение заголовков в словарь
        headers_dict[proxy] = headers

        # Закрытие браузера
        driver.quit()

    except Exception as e:
        print(f"Ошибка при работе с прокси {proxy}: {e}")

# Сохранение заголовков в JSON файл
with open('headers.json', 'w') as f:
    json.dump(headers_dict, f, indent=4)

print("Все заголовки успешно сохранены в headers.json")
