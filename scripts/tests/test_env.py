from dotenv import load_dotenv
import os

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение значений переменных окружения
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
THREADS_COUNT = os.getenv("THREADS_COUNT")

# Вывод значений для проверки
print(DB_PASS, type(DB_PASS))
print(DB_HOST)
print(DB_USER)
print(DB_PASS)
print(DB_NAME)
print(THREADS_COUNT)

