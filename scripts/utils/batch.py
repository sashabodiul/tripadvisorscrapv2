import os
from datetime import datetime

async def save_batch_counter(batch_counter):

    try:
        with open(f'batch_counter.txt', 'w') as f:
            f.write(str(batch_counter))
    except Exception as e:
        print(datetime.now(),':[ERROR] in saving index: ',e)
        
        
async def load_batch_counter():
    try:
        if os.path.exists(f'batch_counter.txt'):
            with open(f'batch_counter.txt', 'r') as f:
                return int(f.read())
        return None
    except Exception as e:
        print(datetime.now(),':[ERROR] in load index: ',e)