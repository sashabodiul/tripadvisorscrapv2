from dotenv import load_dotenv
import os

load_dotenv()
DB_HOST = os.environ.get('DB_HOST')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')
DB_NAME = os.environ.get('DB_NAME')
THREADS_COUNT = int(os.environ.get('THREADS_COUNT'))
BATCH_COUNT = int(os.environ.get('BATCH_COUNTER'))
MAIN_DOMAIN = os.environ.get('MAIN_DOMAIN')

with open('data/security/proxy.txt', 'r') as file:
    # Читаем строки из файла и удаляем лишние символы переноса строки
    PROXY_LIST = [line.strip() for line in file.readlines()]
    
with open('data/security/user_agents.txt', 'r') as file:
    # Читаем строки из файла и удаляем лишние символы переноса строки
    USER_AGENTS_LIST = [line.strip() for line in file.readlines()]
    
with open('data/security/domains.txt', 'r') as file:
    # Читаем строки из файла и удаляем лишние символы переноса строки
    DOMAINS_LIST = [line.strip() for line in file.readlines()]