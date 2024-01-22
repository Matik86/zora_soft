import random 
import aiofiles
import json
import requests
from typing import Optional


def read_json(path: str, encoding: Optional[str] = None) -> list | dict:
    return json.load(open(path, encoding=encoding))

async def wallets_filework() -> list:  
    async with aiofiles.open('./datas./private_keys.txt', 'r') as file:
        privates_lst = []
        async for private_key in file:
            privates_lst.append(private_key.rstrip())
            
    return privates_lst

def get_eth_price():
        url = 'https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=USDT'
        response = requests.get(url)
        data = response.json()
        
        return data['USDT']
    
def short_address(address):
    return address[:6] + '...' + address[-3:]
    
def privates_set(privates_lst, nonce):
    privates_set = {}
    for private_key in privates_lst:
        privates_set[private_key] = random.randint(nonce-3, nonce+3)
    
    return privates_set

    