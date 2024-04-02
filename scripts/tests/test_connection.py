import mysql.connector

# Параметры подключения к вашей базе данных MySQL
host = 'a7makeup.mysql.tools'
user = 'a7makeup_parsing'
password = 'u)A+28Fe2p'
database = 'a7makeup_parsing'

try:
    # Подключение к базе данных
    connection = mysql.connector.connect(host=host, user=user, password=password, database=database)
    if connection.is_connected():
        print("Успешное подключение к базе данных MySQL")

        # Создание курсора
        cursor = connection.cursor()

        # Пример выполнения SQL-запроса
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("Версия сервера MySQL:", record)

except mysql.connector.Error as error:
    print("Ошибка при подключении к базе данных MySQL:", error)

finally:
    # Закрытие соединения с базой данных
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
        print("Соединение с базой данных MySQL закрыто")
