import asyncio
import os

async def get_files() -> list:
    # Путь к папке "Downloads"
    folder_path = "Downloads"

    try:
        # Асинхронно получаем список файлов в папке
        files = await asyncio.to_thread(os.listdir, folder_path)

        # Фильтруем файлы, оставляем только те, которые начинаются с "sitemap"
        sitemap_files = [file for file in files if file.startswith("sitemap")]

        # Выводим список файлов
        print(f"[INFO] Список файлов в папке 'Downloads', начинающихся с 'sitemap': {len(sitemap_files)}")
        return sitemap_files
    except FileNotFoundError:
        print(f"Папка '{folder_path}' не найдена.")
    except PermissionError:
        print(f"Недостаточно прав для доступа к папке '{folder_path}'.")