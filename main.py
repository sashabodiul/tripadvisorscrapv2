from scripts.data import get_files, read_data_from_file
from scripts.utils import emulation_scrape, scrape_data,batch,get_result_from_page,check_real, generate_ssl
from scripts.database import insert_city,insert_rest
import random
from data.config import *
import aiomysql
import asyncio
from loguru import logger
from datetime import datetime

results_data = {'restaraunts_data': [], 'city_data': []}
rand_number = 0

async def process_file(filename, semaphore, xml_index):
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
                    "http://sashabodiul07:7UMNo7iRr6@91.124.76.174:50100",
                    "http://sashabodiul07:7UMNo7iRr6@91.124.70.77:50100",
                    ]
    async with semaphore:
        batch_counter = await batch.load_batch_counter()
        block_batch = batch_counter % 50000
        list_rest = await read_data_from_file.read_lines_from_file(filename=filename)
        for start_index in range(block_batch, len(list_rest), BATCH_COUNT):
            end_index = start_index + BATCH_COUNT
            previous_length = 0 
            for link_index in range(start_index, end_index):
                old_domain = MAIN_DOMAIN.strip()
                new_domain = random.choice(DOMAINS_LIST).strip()
                user_agent = random.choice(USER_AGENTS_LIST).strip()
                rest_url = list_rest[link_index].strip()
                try:
                    # Где-то в вашем коде генерируется ключ и сертификат
                    key_file_path, cert_file_path = await generate_ssl.generate_self_signed_certificate()
                    
                    if len(proxies) > 0:
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
                    logger.error(f"{rest_url} Connection refused {e}")
                try:
                    if "Please enable JS and disable any ad blocker" not in content and content:
                        result = await get_result_from_page.get_result_data(content, rest_url)
                        if result['name'] is None:
                            if link_index > start_index:
                                link_index -= 1
                        #     results_data['restaraunts_data'].append((
                        #                                         result['location'],
                        #                                         result['reviews'],
                        #                                         result['rating'],
                        #                                         result['name'],
                        #                                         result['email'],
                        #                                         result['pos_in_rate'].replace('\xa0','') if result['pos_in_rate'] and '\xa0' in result['pos_in_rate'] else result['pos_in_rate'],
                        #                                         result['number'],
                        #                                         result['prices'],
                        #                                         result['food_rating'],
                        #                                         result['service_rating'],
                        #                                         result['value_rating'],
                        #                                         result['atmosphere_rating'],
                        #                                         result['g_code'],
                        #                                         result['city'],
                        #                                         result['link'].replace(new_domain,old_domain) if result['link'] else None
                        #                                         ))
                        # #     another_result = await get_result_from_page.get_all_data_from_restaurants(content,rest_url)
                        # #     if another_result['rating'] is not None:
                        # #         result['location']=another_result['location']
                        # #         result['reviews']=another_result['reviews_count']
                        # #         result['rating']=another_result['rating']
                        # #         result['name']=another_result['location'].split(',')[0] if another_result['location'] else None
                        # #         result['email']=another_result['email']
                        # #         result['pos_in_rate']=list(another_result['position_in_rating'])[0].replace('\xa0','') if len(list(another_result['position_in_rating'])) > 0 else None
                        # #         result['number']=another_result['telephone']
                        # #         result['prices']=another_result['prices']
                        # #         result['food_rating']=another_result['food_rating']
                        # #         result['service_rating']=another_result['service_rating']
                        # #         result['value_rating']=another_result['value_rating']
                        # #         result['atmosphere_rating']=another_result['atmosphere_rating']
                        # #         result['g_code']=another_result['g_code']
                        # #         result['city']=" ".join(list(another_result['position_in_rating'])[0].split(' ')[-2:]) if len(list(another_result['position_in_rating'])) > 0 and another_result['position_in_rating'] != 'NULL' or None else None
                        # #         result['link']=another_result['website_link']
                        # # rest_url = rest_url.replace(old_domain,new_domain)
                        if 'restaraunts_data' not in results_data:
                            results_data['restaraunts_data'] = []
                        try:
                            if result['name'] is not None:
                                results_data['restaraunts_data'].append((
                                                                    result['location'],
                                                                    result['reviews'],
                                                                    result['rating'],
                                                                    result['name'],
                                                                    result['email'],
                                                                    result['pos_in_rate'].replace('\xa0','') if result['pos_in_rate'] and '\xa0' in result['pos_in_rate'] else result['pos_in_rate'],
                                                                    result['number'],
                                                                    result['prices'],
                                                                    result['food_rating'],
                                                                    result['service_rating'],
                                                                    result['value_rating'],
                                                                    result['atmosphere_rating'],
                                                                    result['g_code'],
                                                                    result['city'],
                                                                    result['link'].replace(new_domain,old_domain) if result['link'] else None
                                                                    ))
                                substring_before_g_code = result['link'].split(result['g_code'])[0]

                                # Replace 'Restaurant_Review' with 'Tourism' in the extracted substring
                                try:
                                    city_link = substring_before_g_code.replace('Restaurant_Review', 'Tourism')
                                except Exception as e:
                                    city_link = substring_before_g_code
                                city_code = result['g_code']
                                results_data['city_data'].append((city_code,result['location'],city_link))
                                # Использование logger с символом возврата каретки для перезаписи
                                print(f"\rSUCCESS {datetime.now()} i: {link_index+len(results_data['restaraunts_data'])} xml: {xml_index+1} rest: {result['name']}", end='', flush=True)
                            else:
                                logger.debug(f'[DEBUG] Cannot get info from: {rest_url}')
                                if link_index > start_index:
                                    link_index -=1
                                    continue
                        except Exception as e:
                            logger.error(f'[ERROR] Cannot add data to list, try again {e} URL: {rest_url}')
                
                except Exception as e:
                    # logger.error(f"Invalid data from rest: {rest_url} {e}")
                    if result['name'] is not None or result['location'] is not None:
                        real = await check_real.check_true_page(content, rest_url)
                        if real:
                            if link_index >= start_index:
                                link_index -=1
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
                            logger.info(f"starting create pool and connecting to database")
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
                logger.warning(f"Ошибка при выполнении задачи: {result}")

        if not tasks:  # Если список задач пуст, то выходим из цикла
            break
                
if __name__ == '__main__':
    asyncio.run(main())
