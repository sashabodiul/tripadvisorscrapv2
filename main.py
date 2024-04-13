from scripts.data import get_files, read_data_from_file
from scripts.utils import emulation_scrape, scrape_data,batch,get_result_from_page,check_real, generate_ssl
from scripts.database import insert_city,insert_rest
import random
from data.config import *
from datetime import datetime
import aiomysql
import asyncio
import aiofiles

async def write_log(log_message):
    log_filename = 'data/logs/logfile.log'
    async with asyncio.Lock():
        async with aiofiles.open(log_filename, mode='a') as logfile:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_entry = f"[{timestamp}] {log_message}\n"
            await logfile.write(log_entry)

results_data = {'restaraunts_data': [], 'city_data': []}
rand_number = 0

async def process_file(filename, semaphore, xml_index):
    async with semaphore:
        batch_counter = await batch.load_batch_counter()
        block_batch = batch_counter % 50000
        list_rest = await read_data_from_file.read_lines_from_file(filename=filename)
        for start_index in range(block_batch, len(list_rest), BATCH_COUNT):
            end_index = start_index + BATCH_COUNT

            for link_index in range(start_index, end_index):
                old_domain = MAIN_DOMAIN.strip()
                new_domain = random.choice(DOMAINS_LIST).strip()
                user_agent = random.choice(USER_AGENTS_LIST).strip()
                rest_url = list_rest[link_index].strip()
                try:
                    # Где-то в вашем коде генерируется ключ и сертификат
                    key_file_path, cert_file_path = await generate_ssl.generate_self_signed_certificate()
                    proxies = [
                    "http://sashabodiul07:7UMNo7iRr6@161.77.75.248:50100",
                    "http://sashabodiul07:7UMNo7iRr6@168.158.37.211:50100",
                    'http://instacombine06ZaJ:NpU7hKC8hj@91.124.71.230:50100'
                    ]
                    proxy = random.choice(proxies)
                    content = await scrape_data.scrape_data(proxy=proxy,
                                                            old_domain=str(old_domain),
                                                            new_domain=str(new_domain),
                                                            user_agent=str(user_agent),
                                                            url=str(rest_url),
                                                            key_file_path=key_file_path,
                                                            cert_file_path=cert_file_path,
                                                            interaction_count=link_index)
                except Exception as e:
                    await write_log(str(e))
                try:
                    result = await get_result_from_page.get_result_data(content, rest_url)
                    if 'restaraunts_data' not in results_data:
                        results_data['restaraunts_data'] = []
                    try:
                        results_data['restaraunts_data'].append((
                                                            result['location'],
                                                            result['reviews'],
                                                            result['rating'],
                                                            result['name'],
                                                            result['email'],
                                                            result['pos_in_rate'].replace('\xa0',''),
                                                            result['number'],
                                                            result['prices'],
                                                            result['food_rating'],
                                                            result['service_rating'],
                                                            result['value_rating'],
                                                            result['atmosphere_rating'],
                                                            result['g_code'],
                                                            result['city'],
                                                            result['link']))
                        substring_before_g_code = result['link'].split(result['g_code'])[0]

                        # Replace 'Restaurant_Review' with 'Tourism' in the extracted substring
                        city_link = substring_before_g_code.replace('Restaurant_Review', 'Tourism')
                        city_code = result['g_code']
                        results_data['city_data'].append((city_code,result['location'],city_link))
                        print(f"\r\033[K{datetime.now()} - i: {link_index+len(results_data['restaraunts_data'])}, xml: {xml_index+1} rest: {result['name']}", end="", flush=True)
                    except Exception as e:
                        await write_log(f'[ERROR] Cannot add data to list, try again {e} URL: {rest_url}')
                    
                except Exception as e:
                    await write_log(str(e))
                    if result['name'] is not None or result['location'] is not None:
                        real = await check_real.check_true_page(content, rest_url)
                        if real:
                            link_index-=1
                            continue
                        else:
                            link_index+=1
                            continue
                
                if len(results_data['restaraunts_data']) >= BATCH_COUNT:
                    batch_counter += BATCH_COUNT
                    link_index+=len(results_data['restaraunts_data'])
                    await batch.save_batch_counter(batch_counter)
                    async with aiomysql.create_pool(host=DB_HOST, user=DB_USER, password=DB_PASS, db=DB_NAME) as pool:
                        async with pool.acquire() as connection:
                            await write_log(f"[INFO] starting create pool and connecting to database")
                            await insert_rest.insert_into_restaurants(connection, results_data['restaraunts_data'])
                            await insert_city.insert_into_city(connection, results_data['city_data'])
                        await connection.commit()
                    results_data['restaraunts_data'].clear()
                    results_data['city_data'].clear()


async def main():
    semaphore = asyncio.Semaphore(THREADS_COUNT)
    files = await get_files.get_files()

    while True:
        batch_counter = await batch.load_batch_counter()
        start_index = batch_counter // 50000
        tasks = [process_file(filename, semaphore, start_index) for filename in files[start_index:]]
        done = await asyncio.gather(*tasks, return_exceptions=True)  # Ожидаем выполнение всех задач

        # Проверяем результаты выполнения задач
        for result in done:
            if isinstance(result, Exception):
                await write_log(f"Ошибка при выполнении задачи: {result}")

        if not tasks:  # Если список задач пуст, то выходим из цикла
            break
                
if __name__ == '__main__':
    asyncio.run(main())
