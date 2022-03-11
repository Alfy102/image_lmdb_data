import lmdb
import cv2
import numpy as np
from pathlib import Path
from os import listdir
from os.path import isfile, join

from pip import main


def image_resize(data_set_path,data_set_file):
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

def write_lmdb_jpg(filename, image_id, image_data):

    lmdb_env = lmdb.open(filename, map_size=int(1e9))

    with lmdb_env.begin(write=True) as txn:
        # All key-value pairs need to be strings
       
        key = f"{image_id:08}"
        txn.put(key.encode("ascii"), cv2.imencode('.jpg', image_data)[1])
    lmdb_env.close()

def read_lmdb_jpg(filename,key):
    lmdb_env = lmdb.open(filename)
    lmdb_txn = lmdb_env.begin()


    with lmdb_env.begin() as lmdb_txn:
       image_data = lmdb_txn.get(key.encode("ascii"))

    return image_data

   

def main():
  
    data_set_path = Path("dataset/")
    data_set_file = [f for f in listdir(data_set_path) if isfile(join(data_set_path, f))]
    list_of_image_data = image_resize(data_set_path, data_set_file)
    for i,image_data in enumerate(list_of_image_data):
        write_lmdb_jpg('test_5_jpg_lmdb', f'product_{i+1:04}',image_data)

    image_data = read_lmdb_jpg('test_5_jpg_lmdb','product_0061')
    decoded_image = cv2.imdecode(np.fromstring(image_data, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
    cv2.imwrite('image.jpg',decoded_image,[int(cv2.IMWRITE_PNG_COMPRESSION), 9])

if __name__ == "__main__":
    main()
