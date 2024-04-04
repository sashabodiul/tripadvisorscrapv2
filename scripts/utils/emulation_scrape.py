from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
import time
import random

def get_html_with_delay(url, old_domain,new_domain,delay=3):
    # Генерация случайного юзер-агента
    user_agent = UserAgent().random
    url = url.replace(old_domain,new_domain)
    # Установка опций браузера для Firefox
    options = Options()
    options.headless = True  # Установка headless режима
    options.set_preference("general.useragent.override", user_agent)
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference("intl.accept_languages", "en-US,en;q=0.9")  # Установка предпочтительных языков
    options.set_preference("webdriver.firefox.profile", "default")  # Использование профиля по умолчанию
    options.set_preference("network.http.referer.XOriginPolicy", 1)  # Отправка HTTP-заголовка Referer на другой источник
    options.set_preference("browser.startup.homepage_override.mstone", "ignore")  # Игнорирование проверки версии браузера

    # Инициализация сервиса GeckoDriver
    service = Service(GeckoDriverManager().install())

    # Инициализация драйвера браузера (Firefox)
    driver = webdriver.Firefox(service=service, options=options)

    try:
        # Загрузка страницы
        driver.get(url)

        # Задержка перед получением HTML-кода (в секундах)
        time.sleep(delay)

        # Получение HTML-кода страницы
        html_code = driver.page_source

        return html_code

    finally:
        # Закрытие браузера
        driver.quit()
