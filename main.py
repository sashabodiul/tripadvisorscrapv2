from scripts.data import get_files, read_data_from_file
from scripts.utils import emulation_scrape, scrape_data,batch,get_result_from_page,check_real, generate_ssl
from scripts.database import insert_city,insert_rest
import random
from data.config import *
from datetime import datetime
import aiomysql
import asyncio
import json
import aiofiles

async def write_log(log_message):
    log_filename = 'data/logs/logfile.log'
    async with asyncio.Lock():
        async with aiofiles.open(log_filename, mode='a') as logfile:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_entry = f"[{timestamp}] {log_message}\n"
            await logfile.write(log_entry)

results_data = {'restaraunts_data': [], 'city_data': []}

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
                    content = await scrape_data.scrape_data(proxy=random.choice(PROXY_LIST),
                                                            old_domain=str(old_domain),
                                                            new_domain=str(new_domain),
                                                            user_agent=str(user_agent),
                                                            url=str(rest_url),
                                                            key_file_path=key_file_path,
                                                            cert_file_path=cert_file_path)
                    if "Please enable JS and disable any ad blocker" in content:
                        content = emulation_scrape.get_html_with_delay(url=str(rest_url),
                                                            old_domain=str(old_domain),
                                                            new_domain=str(new_domain))
                except Exception as e:
                    try:
                        content = emulation_scrape.get_html_with_delay(url=str(rest_url),
                                                            old_domain=str(old_domain),
                                                            new_domain=str(new_domain))
                    except Exception as e:
                        link_index-=1
                        await write_log(str(e))
                try:
                    result = await get_result_from_page.get_all_data_from_restaurants(content, rest_url)
                except Exception as e:
                    link_index-=1
                    await write_log(str(e))
                    if result is not None and not result.get('breadcrumbs', []):
                        real = await check_real.check_true_page(content, rest_url)
                        if real:
                            link_index -= 1
                            continue
                        else:
                            continue
                if 'restaraunts_data' not in results_data:
                    results_data['restaraunts_data'] = []
                is_insert_needed = False

                if len(results_data['restaraunts_data']) >= BATCH_COUNT and not is_insert_needed:
                    is_insert_needed = True
                    batch_counter += BATCH_COUNT
                    await batch.save_batch_counter(batch_counter)
                    async with aiomysql.create_pool(host=DB_HOST, user=DB_USER, password=DB_PASS, db=DB_NAME) as pool:
                        async with pool.acquire() as connection:
                            print(f"\r\033[K{datetime.now()} :[INFO] starting create pool and connecting to database", end="", flush=True)
                            await write_log("[INFO] starting create pool and connecting to database")
                            await insert_rest.insert_into_restaurants(connection, results_data['restaraunts_data'])
                            await insert_city.insert_into_city(connection, results_data['city_data'])
                        await connection.commit()
                    results_data['restaraunts_data'].clear()
                    results_data['city_data'].clear()
                if isinstance(result['breadcrumbs'], str):
                    position_in_rating = str(next(iter(result['position_in_rating']))) if result['position_in_rating'] else None
                    if position_in_rating:
                        city = position_in_rating.split(' ')[-1] if len(position_in_rating.split(' ')) > 2 else ''
                    else:
                        city = ''
                    if result['breadcrumbs']:
                        city = result['breadcrumbs'].split(';')[-3].replace(' ', '') if len(result['breadcrumbs'].split(';')) > 5 else result['breadcrumbs'].split(';')[2].replace(' ', '')
                    reviews_count = float(result['reviews_count']) if result['reviews_count'] is not None and result['reviews_count'].isdigit() else 0
                    results_data['city_data'].append((result['g_code'], city if city else 'NULL', 'https://www.tripadvisor.com/Tourism-g' + result['g_code']))
                    breadcrumbs = result['breadcrumbs'].replace('\xa0', ' ')
                    breadcrumbs = breadcrumbs.replace(' ', '')
                    results_data['restaraunts_data'].append((json.dumps(breadcrumbs),
                                                                result['rating'] if result['rating'] is not None else "NULL",
                                                                result['name'] if result['name'] is not None else "NULL",
                                                                reviews_count if reviews_count is not None else 0,
                                                                result['prices'] if result['prices'] is not None else "NULL",
                                                                result['telephone'] if result['telephone'] is not None else 'NULL',
                                                                result['location'] if result['location'] is not None else 'NULL',
                                                                result['website_link'] if result['website_link'] is not None else 'NULL',
                                                                position_in_rating if position_in_rating is not None else 'NULL',
                                                                result['email'] if result['email'] is not None else 'NULL',
                                                                result['food_rating'] if result['food_rating'] is not None else 'NULL',
                                                                result['service_rating'] if result['service_rating'] is not None else 'NULL',
                                                                result['value_rating'] if result['value_rating'] is not None else 'NULL',
                                                                result['atmosphere_rating'] if result['atmosphere_rating'] is not None else 'NULL',
                                                                result['g_code'] if result['g_code'] is not None else 'NULL',
                                                                result['link'] if result['link'] is not None else 'NULL'))
                    print(f"\r\033[K{datetime.now()} - i: {link_index}, xml: {xml_index+1} rest: {result['name']}", end="", flush=True)


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
                print(f"Ошибка при выполнении задачи: {result}")

        if not tasks:  # Если список задач пуст, то выходим из цикла
            break
                
if __name__ == '__main__':
    asyncio.run(main())
