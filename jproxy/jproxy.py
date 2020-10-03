import requests
import subprocess
import threading
import sqlite3
import os
from time import sleep
import yaml
import logging

class JProxy():

    def __init__(self):
        self.DB_PATH = os.getenv('PROXY_DB_URI', './jproxy.db')
        self.PROXY_CONFIG_FILE = os.getenv('PROXY_CONFIG_FILE', './config.yaml')
        self.PROXY_TABLE = 'jproxy'
        self.IPINFO_URL = 'https://ipinfo.io/{}/json'
        self.SRC_BASE = os.getenv('PROXY_SRC', './proxy_sources')

        self.conn = sqlite3.connect(self.DB_PATH, timeout=30)
        self.cursor = self.conn.cursor()
        self.cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {self.PROXY_TABLE}
        (
            id INTEGER PRIMARY KEY,
            region TEXT,
            ip TEXT,
            port TEXT,
            created_at DATE,
            last_used DATE,
            used BOOLEAN
        )
        """)
        self.conn.close()
        self.start()

    def connect_db(self):
        conn = sqlite3.connect(self.DB_PATH, timeout=30)
        cursor = conn.cursor()
        return conn, cursor
    def get_config(self):
        with open(self.PROXY_CONFIG_FILE, 'r') as proxy_config_file:
            proxies_src_list = yaml.full_load(proxy_config_file)
        return proxies_src_list

    def insert_proxy_row(self, region, ip, port, src_info):
        name = src_info[0]
        conn, cursor = self.connect_db()
        query = f'SELECT * FROM {self.PROXY_TABLE} WHERE ip=?'
        cursor.execute(query, (ip,))
        exist = True if len(cursor.fetchall()) > 0 else False
        if exist:
            print(f'[{name}]{ip} already in the DB')
            conn.close()
            exit()
        query = f'INSERT INTO {self.PROXY_TABLE}(region, ip, port, created_at) VALUES(?, ?, ?, datetime())'
        cursor.execute(query, (region, ip, port))
        conn.commit()
        print(f'[{name}] proxy inserted')
        conn.close()
        exit()

    def insert_proxies(self, proxies, src_info):
        thread_count = []
        for ip, port in proxies:
            thread = threading.Thread(target=self.insert_proxy_thread, args=(ip, port, src_info))
            thread_count.append(thread)
            thread.start()
        name = src_info[0]
        wait_delay = src_info[2]
        print(f'[{name}] thread is sleeping for {wait_delay} seconds')
    
    def insert_proxy_thread(self, ip, port, src_info):
        name = src_info[0]
        print(f'[{name}]fetching region for {ip}')
        region = self.get_ip_region(ip)
        print(f'[{name}]inserting {ip} in the DB')
        self.insert_proxy_row(region, ip, port, src_info)
        print(f'[{name}]proxy {ip}:{port} inserted successfuly')

    def get_ip_region(self, ip):
        try:
            info = requests.get(self.IPINFO_URL.format(ip), timeout=10).json()
            return info['country']
        except:
            return 'N/A'

    def launch_proxy(self, name, path, wait_delay):
        while True:
            proxy_src_path = f'{self.SRC_BASE}/{path}'
            proxy_src_info = (name, path, wait_delay)
            print(f'[{name}] starting thread')
            src_proc = subprocess.Popen([proxy_src_path], stdout=subprocess.PIPE)
            proxies = src_proc.stdout.read().decode().split('\n')[:-1]
            proxies_list = [(proxy.split(':')[0], proxy.split(':')[1]) for proxy in proxies]
            self.insert_proxies(proxies_list, proxy_src_info)
            sleep(wait_delay)
        

    def start(self):
        config = self.get_config()
        for src in config:
            proxy_proc = threading.Thread(target=self.launch_proxy, args=(src["name"], src['path'], src['check_delay']))
            proxy_proc.start()


if __name__ == "__main__":
    JProxy()
