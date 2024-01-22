import fake_useragent


rpc = 'https://rpc.zora.energy'

# добавляем одно прокси если хотим работать с ним на все аккаунты
proxy = 'http://log:passwd@ip:port'

# к каждому приватнику добавляем свой прокси
proxies = {
    'private_key_1':'http://log:passwd@ip1:port',  
    'private_key_2':'http://log:passwd@ip2:port',
    'private_key_3':'http://log:passwd@ip3:port',
    }

headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'user-agent': fake_useragent.UserAgent().random
        }

    

        
