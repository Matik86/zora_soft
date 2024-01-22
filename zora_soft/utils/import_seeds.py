from web3 import Web3
from eth_account.signers.local import LocalAccount
from web3.middleware import geth_poa_middleware

def wallets_filework() -> list:  
    with open('./seeds.txt', 'r') as file:
        seed_lst = []
        for seed in file:
            seed_lst.append(seed.rstrip())
    return seed_lst

def get_private_from_seed(seed_lst) -> str:
    private_keys = []
    web3 = Web3(provider=Web3.HTTPProvider(endpoint_uri='https://rpc.ankr.com/eth'))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    web3.eth.account.enable_unaudited_hdwallet_features()
    
    with open ('./private_keys.txt', 'w') as f:
        for seed in seed_lst:
            web3_account: LocalAccount = web3.eth.account.from_mnemonic(seed)
            private_key = web3_account._private_key.hex()
            address = web3_account.address
            print(address)
            f.write(private_key + '\n')
        
    
get_private_from_seed(wallets_filework())
            
        
            
            
        

    
    
    