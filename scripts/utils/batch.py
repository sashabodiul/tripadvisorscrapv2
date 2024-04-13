import os
from datetime import datetime
import asyncio
import aiofiles

async def save_batch_counter(batch_counter):

    try:
        with open(f'batch_counter.txt', 'w') as f:
            f.write(str(batch_counter))
    except Exception as e:
        log_filename = 'data/logs/logfile.log'
        log_message = (f"[ERROR] in saving index: {e}")
        async with asyncio.Lock():
            async with aiofiles.open(log_filename, mode='a') as logfile:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                log_entry = f"[{timestamp}] {log_message}\n"
                await logfile.write(log_entry)
        
        
async def load_batch_counter():
    try:
        if os.path.exists(f'batch_counter.txt'):
            with open(f'batch_counter.txt', 'r') as f:
                return int(f.read())
        return None
    except Exception as e:
        log_filename = 'data/logs/logfile.log'
        log_message = (f"[ERROR] in loading index: {e}")
        async with asyncio.Lock():
            async with aiofiles.open(log_filename, mode='a') as logfile:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                log_entry = f"[{timestamp}] {log_message}\n"
                await logfile.write(log_entry)