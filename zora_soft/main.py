from web3 import Web3, AsyncHTTPProvider
from web3.eth import AsyncEth
from termcolor import cprint
from decimal import Decimal
from loguru import logger
import random
import asyncio
import aiofiles
import csv

from utils.utils import wallets_filework, privates_set, get_eth_price
from datas.DATA import headers, proxy, rpc
from client import Client
from mint import Mint


class RandomActivity:
    
    num_of_done = 0
    accounts_results = {}
    
    def __init__(self, privates_dict):
        self.w3 = Web3(AsyncHTTPProvider(rpc, request_kwargs={'proxy': proxy, 'headers':headers}), modules={"eth": (AsyncEth)}, middlewares=[])
        self.wallets_num = len(list(privates_dict.keys()))
        
    async def random_tx(self, privates_dict):
        try:            
            if privates_dict:
                wallets_num = len(list(privates_dict.keys()))
                private_keys = list(privates_dict.keys())
                logger.info('начинаем выполнение транзакций')
                await asyncio.gather(*[self.process_account(private_key, wallets_num, privates_dict) for private_key in private_keys])
                 
        except Exception as err:
            logger.info(f'{err}')
            
        finally:
            if self.accounts_results:
                    logger.success(f'Все {self.num_of_done} аккаунтов выполнено')
                    await self.generate_csv()
            else:
                if self.num_of_done == 0:    
                   logger.warning('Программа не успела выполнить ни один из аккаунтов')
                else:
                   logger.success(f'{self.num_of_done} аккаунтов выполнено')
                 
    async def process_account(self, private_key,wallets_num, privates_dict):
        try:            
            address = Web3.to_checksum_address(self.w3.eth.account.from_key(private_key).address)
            nonce = await self.w3.eth.get_transaction_count(address)
                        
            if nonce < privates_dict[private_key]:
                logger.info(f'{address} осталось выполнить {privates_dict[private_key] - nonce} транзакций')
                await self.init_transaction(private_key)
                return await self.process_account(private_key, wallets_num, privates_dict)
            
            else:
                self.num_of_done += 1
                privates_dict.pop(private_key)
                logger.success(f'{self.num_of_done}/{wallets_num} аккаунтов выполнено')
                return 
                
        except Exception as err:
            logger.error(f'{err}')
    
    async def init_transaction(self, private_key):
        address = Web3.to_checksum_address(self.w3.eth.account.from_key(private_key).address)
        delay = random.randint(30, 600) # Генерируем случайный промежуток ожидания (в секундах)
        logger.info(f'{address} | ожидает выполнение транзакции...({delay//60} мин {delay%60} сек)') 
        await asyncio.sleep(delay)
        
        if private_key not in self.accounts_results:
           self.accounts_results[private_key] = {}
           self.accounts_results[private_key]['count'] = 0
           self.accounts_results[private_key]['gas'] = 0
           self.accounts_results[private_key]['value'] = 0
        try:
            client = Client(private_key)
            mint = Mint(client)
            result = await client.verif_tx(await mint.transaction())
            if result['status']:
                self.accounts_results[private_key]['count'] += 1
                self.accounts_results[private_key]['gas'] += result['gas']
                self.accounts_results[private_key]['value'] += result['value']
                return
            
            else:
                await self.init_transaction(private_key)
            
        except Exception as err:
            logger.error(f'{err}')
            await self.init_transaction(private_key)
              
    async def generate_csv(self):
        async with aiofiles.open(f'./results./results.csv', 'w', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            headers = ['num', 'address', 'tx total count', 'tx count', 'eth value', 'usd value', 'average gas']
            await writer.writerow(headers)
            
            for i, private_key in enumerate(list(self.accounts_results.keys())):
                address = Web3.to_checksum_address(self.w3.eth.account.from_key(private_key).address)
                nonce = await self.w3.eth.get_transaction_count(address)
                row = [i + 1, address]
                row.append(nonce)
                row.append(self.accounts_results[private_key]['count'])
                value = self.w3.from_wei(self.accounts_results[private_key]['value'], 'ether')
                eth = self.w3.from_wei(self.accounts_results[private_key]['gas']*10**9 / 1.4, 'ether') + value
                row.append(f'{round(eth, 5)} ETH')
                row.append(f'${(eth * Decimal(get_eth_price())):,.2f}')
                row.append(self.accounts_results[private_key]['gas'] / self.accounts_results[private_key]['count'])
                
                await writer.writerow(row)
                
        return cprint('\nВсе результаты записаны в файл: results.csv\n', 'blue')
                             
async def run():
    try:
        privates_lst = await wallets_filework()
        privates_dict = privates_set(privates_lst, nonce=int(input('\nВведите нужное кол-во транзакций: ')))
        action = RandomActivity(privates_dict)
        return await action.random_tx(privates_dict)
        
    except Exception as err:
        logger.error(f'{err}')
        
    
asyncio.run(run())

