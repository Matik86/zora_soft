from web3 import Web3, AsyncHTTPProvider
from web3.eth import AsyncEth
from loguru import logger

from datas.DATA import headers, proxies, rpc, proxy 
from utils.utils import short_address


class Client:
    
    def __init__(
        self,
        private_key: str
        ):
        self.private_key = private_key
        
        if proxies: 
           self.w3 = Web3(AsyncHTTPProvider(rpc, request_kwargs={'proxy': proxies[self.private_key], 'headers':headers}), modules={"eth": (AsyncEth)}, middlewares=[])
        else:
            self.w3 = Web3(AsyncHTTPProvider(rpc, request_kwargs={'proxy': proxy, 'headers':headers}), modules={"eth": (AsyncEth)}, middlewares=[])
            
        self.address = Web3.to_checksum_address(self.w3.eth.account.from_key(private_key=private_key).address)
        
    async def send_tx(
        self,
        contract_address: str,
        data=None,
        value=None,
        ):
        tx_data = []
        try:
            tx_params = {
                    'chainId': await self.w3.eth.chain_id,
                    'nonce': await self.w3.eth.get_transaction_count(Web3.to_checksum_address(self.address)),
                    'from': Web3.to_checksum_address(self.address),
                    'to': Web3.to_checksum_address(contract_address),
                    'gasPrice': await self.w3.eth.gas_price
                }
                
            if value: 
               tx_params['value'] = value
               tx_data.append(tx_params['value'])
            else:
                tx_data.append(0)
                
                    
            if data: 
               tx_params['data'] = data
            
            try: 
                tx_params['gas'] = int(await self.w3.eth.estimate_gas(tx_params))
                tx_data.append(tx_params['gas']) 
                
            except Exception as err:
                logger.error(f'\n{self.address} | транзакция не выполнена | {err}')
                return 

            sign = self.w3.eth.account.sign_transaction(tx_params, self.private_key)
            tx_hash = await self.w3.eth.send_raw_transaction(sign.rawTransaction)
            tx_data.append(tx_hash) 
            return tx_data
        
        except Exception as e:
            print(f'{e}')
    
    async def verif_tx(self, tx_data: list) -> bool:
        try:
            data = await self.w3.eth.wait_for_transaction_receipt(tx_data[2], timeout=200)
            result = {}
            
            if 'status' in data and data['status'] == 1:
                logger.success(f'\n{short_address(self.address)} | транзакция выполнена: {tx_data[2].hex()}')
                result['status'] = True
                result['value'] = tx_data[0]
                result['gas'] = tx_data[1]
                return result
            
            else:
                logger.error(f'\n{short_address(self.address)} | транзакция не выполнена {data["transactionHash"].hex()}')
                result['status'] = False
                result['value'] = tx_data[0]
                result['gas'] = tx_data[1]
                return result
            
        except Exception as err:
            logger.error(f'\n{self.address} | {err}')
            result['status'] = False
            return result
        
    