#!/usr/bin/env python3.8

import requests
import re
import random
import threading
import time

def deobfuscate_ports_js(obfuscated_ports_list):

    init_obfuscation = {var.split("=")[0] : var.split("=")[1] for var in obfuscated_ports_list if var.split("=")[1].isnumeric()}
    obfuscation = {var.split("=")[0] : eval("".join([var.split("=")[1].replace(value, init_obfuscation[value]) for value in init_obfuscation if value in var.split("=")[1]])) for var in obfuscated_ports_list if not var.split("=")[1].isnumeric()}
    init_obfuscation.update(obfuscation)

    return init_obfuscation

def get_proxies_list_from_spys():

    url = "http://spys.one/en/socks-proxy-list/"
    cookies = {
        "_ga": "GA1.2.1794933202.1595109709",
        "_gid": "GA1.2.1544213663.1595109709"
        }
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "http://spys.one",
        "Connection": "close",
        "Referer": "http://spys.one/en/socks-proxy-list/",
        "Upgrade-Insecure-Requests": "1"
        }
    data = {
        "xx0": "afe94e9376ca7c2ee442ab0c9e1c787e",
        "xpp": "5",
        "xf1": "0",
        "xf2": "0",
        "xf4": "0",
        "xf5": "2"
        }


    init_response = requests.post(url, headers=headers, cookies=cookies, data=data).text
    xx0 = re.search("<input type='hidden' name='xx0' value='(.{1,40})'>", init_response).groups()[0]
    data['xx0'] = xx0
    response_text = requests.post(url, headers=headers, cookies=cookies, data=data).text    
    obfuscation = re.search('<script type="text/javascript">(.*)</script>', response_text).groups()[0].split(";")[:-1]
    deobfuscated_ports = deobfuscate_ports_js(obfuscation)
    pattern = re.compile(r'<font class=spy14>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})<script type="text/javascript">.{1,44}\+(.{1,20}\+.{1,20}\+.{1,20}\+.{1,20})</script>')
    proxies_tuple = re.findall(pattern, response_text)
    proxies_list = []

    for proxy in proxies_tuple:
        obfuscated_port = [v.split("^") for v in proxy[1].replace("(","").replace(")","").split("+")]

        for e in obfuscated_port:
            e[0] = deobfuscated_ports[e[0]]
            e[1] = deobfuscated_ports[e[1]]

        ip = proxy[0]
        port = "".join([str(int(v[0])^int(v[1])) for v in obfuscated_port])

        proxies_list.append((ip, port))
    
    return proxies_list



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
    proxies = get_proxies_list_from_spys()
    check_proxies(proxies)
    time.sleep(37)
    for proxy in proxies:
        print(f'{proxy[0]}:{proxy[1]}')
