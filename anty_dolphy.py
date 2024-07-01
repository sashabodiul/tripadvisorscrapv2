import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# def get_browser_profiles():
#     # Пример реализации функции получения профилей
#     response = requests.get("http://localhost:3001/v1.0/browser_profiles")
#     return response.json().get('data', [])

def main():
    # profiles_id = get_browser_profiles()

    # if profiles_id:
    # req_url = f"http://localhost:3001/v1.0/browser_profiles/411763254/start?autonation-1"
    # response = requests.get(url=req_url)
    # response_json = response.json()
    # print(response_json)
    # time.sleep(4)  # Даем время на запуск профиля

    # Используем порт 64849
    listen_ip = "127.0.0.1:49964"
    print(f"Listen ip for Anty: {listen_ip.strip()}")
    port = listen_ip.split(':')[-1].strip()  # Извлекаем номер порта
    print(f"Port: {port}")

    chrome_driver_path = "chromedriver/chromedriver.exe"
    options = webdriver.ChromeOptions()
    options.debugger_address = listen_ip.strip()  # Устанавливаем адрес отладки

    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    
    driver.get("https://www.mcdonalds.com/ua/uk-ua/product/200390.html#accordion-29309a7a60-item-9ea8a10642")
    time.sleep(3)
    
    driver.get("https://whatismyipaddress.com/")
    time.sleep(2)
    


    if 'driver' in locals():
        driver.quit()

if __name__ == "__main__":
    main()