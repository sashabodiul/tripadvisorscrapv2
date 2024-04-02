from datetime import datetime

async def insert_into_city(connection, city_data):
    try:
        async with connection.cursor() as cursor:
            insert_values = []  # Создаем список для значений, которые нужно вставить
            for data in city_data:
                G_id, location, link = data
                select_sql = "SELECT link FROM city WHERE link = %s"
                await cursor.execute(select_sql, (link,))
                existing_link = await cursor.fetchone()
                if not existing_link:  # Если нет совпадений, то добавляем данные в список для вставки
                    insert_values.append((G_id, location, link))
            print(f"\r\033[K{datetime.now()} :[INFO DB] City Unique pool {len(insert_values)}", end="", flush=True)
            if insert_values:  # Проверяем, есть ли данные для вставки
                insert_sql = """
                    INSERT INTO city (G_id, location, link) 
                    VALUES (%s, %s, %s)
                """
                await cursor.executemany(insert_sql, insert_values)  # Выполняем вставку данных с помощью executemany
            await connection.commit()
    except Exception as e:
        print(datetime.now(),':[ERROR] inserting/city: ', e)