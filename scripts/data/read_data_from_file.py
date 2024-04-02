import os
import aiofiles

async def read_lines_from_file(filename:str) -> list:
    try:
        # Путь к папке "Downloads"
        folder_path = "Downloads"
        # Формируем полный путь к файлу
        filepath = os.path.join(folder_path, filename)
        
        async with aiofiles.open(filepath, mode='r') as f:
            lines = await f.readlines()
            return lines
    except FileNotFoundError:
        print(f"Файл '{filename}' не найден.")
        return []
    except Exception as e:
        print(f"Ошибка при чтении файла '{filename}': {e}")
        return []