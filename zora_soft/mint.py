from web3 import Web3
from loguru import logger
import random

from config.config import CONTRACTS_DATA
from utils.utils import read_json
from client import Client


class Mint:
    
    def __init__(self, 
                 client: Client,
                 ):
        self.client = client
        self.address = self.client.address
            
    async def mint_nft(self,
                       contract_name, 
                       contract_address, 
                       CONTRACT_ABI):
        
        contract = self.client.w3.eth.contract(contract_address, abi=CONTRACT_ABI)
        
        try:
            if contract_name == 'BLCK':
                return await self.client.send_tx(
                    contract_address=contract_address,
                    data=contract.encodeABI('mint')
                    )
                
            if contract_name =='Uni2':
                return await self.client.send_tx(
                    contract_address=contract_address,
                    data=contract.encodeABI('mint')
                    )
                                        
            return await self.client.send_tx(
                contract_address=contract_address,
                data=contract.encodeABI('mint',
                                        args=(
                                            CONTRACTS_DATA[contract_name]['quantity'],
                                            ))
                )
            
        except Exception as err:
            logger.error(f'{err}: {contract_name}')
          
    async def play(self, contract_address, CONTRACT_ABI):
        contract = self.client.w3.eth.contract(contract_address, abi=CONTRACT_ABI)
        num = random.randint(1, 3)
        amount = random.choice([0.00001, 0.00005])
        try:
            return await self.client.send_tx(
                contract_address=contract_address,
                data=contract.encodeABI('play',
                                        args=(
                                            num, 
                                            Web3.to_wei(amount, 'ether'),
                                            )),
                value=Web3.to_wei(amount, 'ether')
                )
        except Exception as err:
            logger.error(f'{err}: PSC')
    
    async def mint_omni(self, contract_address, CONTRACT_ABI):
        
        contract = self.client.w3.eth.contract(contract_address, abi=CONTRACT_ABI)
        amount = random.randint(1,40)
        
        try:
            return await self.client.send_tx(
                contract_address=contract_address,
                data=contract.encodeABI('mint',
                                        args=(
                                            self.address,
                                            amount,
                                            )),
                value=Web3.to_wei(0.00008, 'ether')
                )
        except Exception as err:
            logger.error(f'{err}: OMNI')
        
    async def transaction(self):
        contract_name = random.choice(list(CONTRACTS_DATA.keys()))
        contract_address = Web3.to_checksum_address(CONTRACTS_DATA[contract_name]['contract'])
        CONTRACT_ABI = read_json(CONTRACTS_DATA[contract_name]['ABI'])
        
        try:
            if contract_name == 'PSC':
                return await self.play(contract_address, CONTRACT_ABI)
                
            if contract_name == 'OMNI':
                return await self.mint_omni(contract_address, CONTRACT_ABI)
                
            else:
                return await self.mint_nft(contract_name, contract_address, CONTRACT_ABI)
            
        except Exception as err:
            logger.error(f'{err}')
