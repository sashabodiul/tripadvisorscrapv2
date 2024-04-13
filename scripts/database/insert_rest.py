from datetime import datetime
import asyncio
import aiofiles

async def write_log(log_message):
    log_filename = 'data/logs/logfile.log'
    async with asyncio.Lock():
        async with aiofiles.open(log_filename, mode='a') as logfile:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_entry = f"[{timestamp}] {log_message}\n"
            await logfile.write(log_entry)

async def insert_into_restaurants(connection, restaurants_data):
    try:
        async with connection.cursor() as cursor:
            unique_restaurants_data = []  # List for unique records
            for data in restaurants_data:
                link = data[-1]  # Assuming the last element in the tuple is the link
                select_sql = "SELECT link FROM restaraunts WHERE link = %s"
                await cursor.execute(select_sql, (link,))
                existing_link = await cursor.fetchone()
                if not existing_link:  # If no matches, add the record to the list for insertion
                    unique_restaurants_data.append(data)

            # Check for uniqueness of links in unique_restaurants_data
            unique_links = set()
            unique_restaurants_data_no_duplicates = []
            for data in unique_restaurants_data:
                link = data[-1]
                if link not in unique_links:
                    unique_links.add(link)
                    unique_restaurants_data_no_duplicates.append(data)

            if unique_restaurants_data_no_duplicates:  # If there are unique records to insert
                insert_sql = """
                    INSERT INTO restaraunts (
                        `location`, reviews, rating, `name`, email, 
                        pos_in_rate, `number`, prices, food_rating, 
                        service_rating, value_rating, atmosphere_rating, 
                        g_code, city, link
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                await cursor.executemany(insert_sql, unique_restaurants_data_no_duplicates)
                
            await write_log(f"[INFO DB] Restaurants unique pool: {len(unique_restaurants_data_no_duplicates)} update pool: {len(restaurants_data)-len(unique_restaurants_data_no_duplicates)}")

            await connection.commit()  # Commit only after all data has been added
    except Exception as e:
        await write_log(f":[ERROR] inserting/restaurants: {e}")
