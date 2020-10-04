from flask_restful import Api, Resource, reqparse
from flask import Flask
from os import getenv
from random import choice
import sqlite3


class ProxyManager(Resource):
    
    DATABASE_URI = getenv('PROXY_DB_URI','../database/jproxy.db')
    TABLE_NAME = 'jproxy'

    def connect_db(self):
        conn = sqlite3.connect(self.DATABASE_URI, timeout=30.0)
        cursor = conn.cursor()
        return conn, cursor

    def get_random_proxy(self, region):
        conn, cursor = self.connect_db()
        query = f'SELECT * FROM {self.TABLE_NAME}'
        bind = []
        if region != None:
            query = f'SELECT * FROM {self.TABLE_NAME} WHERE region=?'
            bind.append(region)
            
        cursor.execute(query, tuple(bind))
        rows = cursor.fetchall()
        count_row = len(rows)
        if count_row < 1:
            return {'message': 'can\'t find a proxy on the DB'}
        description = cursor.description
        proxy_list = self.dict_result(description, rows)

        proxy = choice(proxy_list)

        proxy_id = proxy['id']
        ip = proxy['ip']
        port= proxy['port']
        region = proxy['region']

        self.update_proxy_state(conn, cursor, proxy_id)
        conn.close()
        return {'ip': ip, 'port': port, 'region': region}

    def dict_result(self, description, rows):
        # return a nice array of dict
        proxy_array = []
        keys = [key[0] for key in description]
        for row in rows:
            row_dict = dict([value for value in zip(keys, row)])
            proxy_array.append(row_dict)
        return proxy_array

    def update_proxy_state(self, conn, cursor, proxy_id):
        query = f'DELETE FROM {self.TABLE_NAME} WHERE id={proxy_id}'
        cursor.execute(query)
        conn.commit()

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('region')
        args = parser.parse_args()
        return self.get_random_proxy(args['region']), 200

if __name__ == '__main__':
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(ProxyManager, '/newProxy')
    app.run('0.0.0.0', port=60137, debug=True)