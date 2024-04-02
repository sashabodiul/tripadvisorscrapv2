async def insert_into_restaurants(connection, restaurants_data):
    try:
        async with connection.cursor() as cursor:
            unique_restaurants_data = []  # Список для уникальных записей
            for data in restaurants_data:
                link = data[-1]  # Предполагается, что последний элемент в кортеже является ссылкой
                select_sql = "SELECT link FROM restaraunts WHERE link = %s"
                await cursor.execute(select_sql, (link,))
                existing_link = await cursor.fetchone()
                if not existing_link:  # Если нет совпадений, добавляем запись в список для вставки
                    unique_restaurants_data.append(data)

            if unique_restaurants_data:  # Если есть уникальные записи для вставки
                insert_sql = """
                    INSERT INTO restaraunts (
                        breadcrumbs, rate, name_rest, reviews_count, prices, 
                        telephone, location, website_link, position_in_rating, 
                        email, food_rating, service_rating, value_rating, 
                        atmosphere_rating, g_code, link
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                await cursor.executemany(insert_sql, unique_restaurants_data)

            await connection.commit()
    except Exception as e:
        print(e)