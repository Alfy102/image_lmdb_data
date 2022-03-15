from tabnanny import check
import lmdb
import cv2
import numpy as np
from pathlib import Path
from os import listdir
from os.path import isfile, join
import random
import string
from pip import main
import requests
import json
import re
import urllib.request
import sqlite3

url_list = [
    'https://www.aliexpress.com/item/1005003955339121.html',
    'https://www.aliexpress.com/item/1005003137851432.html',
    'https://www.aliexpress.com/item/1005003298868131.html',
    'https://www.aliexpress.com/item/4001275226820.html',
    'https://www.aliexpress.com/item/1005003238495616.html',
    'https://www.aliexpress.com/item/1005003884713089.html',
    'https://www.aliexpress.com/item/1005003914571286.html',
    'https://www.aliexpress.com/item/1005003972241655.html',
    'https://www.aliexpress.com/item/1005002687633672.html',
    'https://www.aliexpress.com/item/1005002991447277.html',
    'https://www.aliexpress.com/item/1005002991024823.html',
    'https://www.aliexpress.com/item/1005002944982447.html'
]
class ImageLmdb(object):
    def __init__(self,product_db_file, image_db_file):
        self.conn = sqlite3.connect(product_db_file)
        self.image_lmdb = image_db_file


    def image_resize(self,data_set_path,data_set_file):
        new_list = []
        for image_file in data_set_file:
            img = cv2.imread(f'{data_set_path}/{image_file}')
            image_height, image_width, image_depth = img.shape
            scale_factor = 1
            if image_height > 800:
                scale_factor = (800/image_height)
            elif image_width > 800:
                scale_factor = (800/image_width)
            width = int(image_width * scale_factor)
            height = int(image_height * scale_factor)
            
            res = cv2.resize(img, dsize=(width, height), interpolation=cv2.INTER_CUBIC)
            new_list.append(res)
        return new_list

    def write_lmdb_jpg(self,filename, product_image_id, image_data):
        lmdb_env = lmdb.open(filename, map_size=int(1e9))
        with lmdb_env.begin(write=True) as lmdb_txn:
            # All key-value pairs need to be strings
            key = f"{product_image_id}"
            lmdb_txn.put(key.encode("ascii"), cv2.imencode('.jpg', image_data)[1])
        lmdb_env.close()


    def check_key_in_lmdb(self,filename, key):
        lmdb_env = lmdb.open(filename, map_size=int(1e9))
        with lmdb_env.begin(write=True) as lmdb_txn:
            result = lmdb_txn.get(key.encode("ascii"))
        return bool(result)


    def read_lmdb_jpg(self,filename,key):
        lmdb_env = lmdb.open(filename)
        #lmdb_txn = lmdb_env.begin()

        with lmdb_env.begin() as lmdb_txn:
            image_data = lmdb_txn.get(key.encode("ascii"))

        return image_data


    def get_image(self,product_url):        
        r = requests.get(product_url)
        match = re.search(r'data: ({.+})', r.text).group(1)
        data = json.loads(match)
        image_list = data['imageModule']['imagePathList']#.keys())#['pageModule'].keys())#['imageModule'])
        product_id = product_url.split('/')[-1]
        product_id = product_id.replace('.html','')
        image_key_list =[]
        image_data_list = {}
        
        for image_url in image_list:
            resp = urllib.request.urlopen(image_url)
            image_data = np.asarray(bytearray(resp.read()), dtype="uint8")
            image_data_decode = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
            image_id = image_url.split('/')[-2]
            image_key_list.append(image_id)
            image_data_list.update({image_id:image_data_decode})
        return product_id, image_key_list, image_data_list

    def conn_commit(self, sql_instruction):
        cur = self.conn.cursor()
        cur.execute(sql_instruction)
        self.conn.commit()

    def random_name_generator(self,length):
        all = string.ascii_uppercase + string.digits
        temp = random.sample(all,length)
        random_name = "".join(temp)
        return random_name

    def insert_product_in_db(self, product_id, image_list):
        insert_data = f"""
            INSERT INTO product_image_keys (product_id, image_list)
            VALUES ('{product_id}', '{json.dumps(image_list)}');
            """
        self.conn_commit(insert_data)

    def check_product_in_db(self, product_id):
        check_query = f"""SELECT product_id 
                    FROM product_image_keys
                    WHERE product_id={product_id}"""
        cur = self.conn.cursor()
        cur.execute(check_query)
        result = cur.fetchone()
        return bool(result)
    
    def update_product_in_db(self, product_id, data_category, updated_data):
        sql_update_query = f"""Update product_image_keys set {data_category} = '{json.dumps(updated_data)}' where product_id = {product_id}"""
        self.conn_commit(sql_update_query)

    def create_table_if_not_exist(self):
        sql_create_table = """CREATE TABLE IF NOT EXISTS product_image_keys (
                    id integer PRIMARY KEY,
                    product_id string NOT NULL,
                    image_list string NOT NULL
                );"""

        self.conn_commit(sql_create_table)

    def main(self):
        self.create_table_if_not_exist() 
        #self.check_key_in_lmdb(self.image_lmdb,'9S4718f9f560ca4312abef2119d55bfc01h')
        for url in url_list:
            product_id, image_key_list, image_data_list = self.get_image(url)
            if not self.check_product_in_db(product_id):
                self.insert_product_in_db(product_id, image_key_list)
            else: 
                self.update_product_in_db(product_id,'image_list', image_key_list)
            for image_id,image_data in image_data_list.items():
                self.write_lmdb_jpg(self.image_lmdb,f"{image_id}", image_data)



        #image_data = read_lmdb_jpg('database/test_jpg_lmdb','F5HBL9TEP62S_NVM5TZQ96HAG')
        #decoded_image = cv2.imdecode(np.fromstring(image_data, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
        #cv2.imwrite('image.jpg',decoded_image,[int(cv2.IMWRITE_PNG_COMPRESSION), 9])

if __name__ == "__main__":
    lmdb_class = ImageLmdb('product_image_db.sqlite3','database/image_db')
    lmdb_class.main()
    
    #print(random_name_generator(12))
