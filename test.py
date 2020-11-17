from base64 import b64encode
import requests
import glob
import time
import numpy as np


port = '8811'
# request_url = "http://180.76.228.199:{}/dango/algo/ocr/server".format(port)
request_url = "http://0.0.0.0:{}/dango/algo/ocr/server".format(port)
img_path = "/media/lishundong/DATA2/docker/data/ocr/Dango/received_imgs/8801/2020-11-01"

img_list = glob.glob(img_path + "/*.jpg")
for i, img_p in enumerate(img_list):
    print("{}/{} {}".format(i, len(img_list), img_p))
    f = open(img_p, 'rb')
    img = b64encode(f.read())  # .decode()
    # print(img)
    s1 = time.time()
    language = ['ENG', 'JAP', 'KOR', 'CH']
    rand_idx = np.random.randint(0, len(language))
    data = {"image": img, "language_type": "JAP", "user_id": "234232", "platform": "win32"}
    # print(img)
    response = requests.post(request_url, data=data).json()
    print(response)
    s2 = time.time()
    print("time cost:", s2 - s1)
