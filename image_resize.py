import cv2
import numpy as np
from pathlib import Path
from os import listdir
from os.path import isfile, join





data_set_path = Path("dataset/")
data_set_file = [f for f in listdir(data_set_path) if isfile(join(data_set_path, f))]

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
    dim = (width, height)
    res = cv2.resize(img, dsize=(54, 140), interpolation=cv2.INTER_CUBIC)
