import asyncio
import json
from pyppeteer import launch
import time

async def main():
    browser = await launch(headless=False)  # Запуск браузера
    page = await browser.newPage()  # Создание новой вкладки

    # Зайти на нужную страницу
    await page.goto('https://www.tripadvisor.com/Restaurant_Review-g54273-d497884-Reviews-Hudson_s_Seafood_House_on_the_Docks-Hilton_Head_South_Carolina.html')
    
    # Получить куки
    cookies = await page.cookies()
    print(cookies)
    
    await browser.close()  # Закрытие браузера

asyncio.get_event_loop().run_until_complete(main())
