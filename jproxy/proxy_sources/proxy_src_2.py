#!/usr/bin/env python3.8

import requests
import re
import random
import threading
import time

def get_proxies_list_from_proxyscrape():

    url = "https://api.proxyscrape.com/?request=getproxies&proxytype=socks5&timeout=10000&country=all"
    response = requests.get(url)

    return [tuple(v.split(':')) for v in response.text.split('\r\n')][:-1]

def check_proxy_thread(proxy):

    global global_proxy_list
    
    for i in range(2):
        try:
            proxy_uri = "socks5://%s:%s"%(proxy[0], proxy[1])
            request = requests.Session()
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0'} 
            response = request.get("http://ip.42.pl/bitch", proxies={'http': proxy_uri},headers=headers, verify=False, timeout=5)
            if not 7 < len(response.text) < 15:
                continue
            if i==1:
                global_proxy_list.append((proxy[0], proxy[1]))          
        except:
            continue

        


def check_proxies(proxies):
    for proxy in proxies:
        thread = threading.Thread(target=check_proxy_thread, args=(proxy,))
        thread.start()


if __name__=="__main__":

    global_proxy_list = []
    proxies = get_proxies_list_from_proxyscrape()
    check_proxies(proxies)
    time.sleep(37)
    for proxy in proxies:
        print(f'{proxy[0]}:{proxy[1]}')
