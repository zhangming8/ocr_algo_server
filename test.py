from base64 import b64encode
import requests
import glob
import time
import cv2
import numpy as np
import shutil
import os
from PIL import Image, ImageDraw, ImageFont

label_color = [[31, 0, 255], [0, 159, 255], [255, 0, 0], [0, 255, 25], [255, 0, 133],
               [255, 172, 0], [108, 0, 255], [0, 82, 255], [255, 0, 152], [223, 0, 255], [12, 0, 255], [0, 255, 178],
               [108, 255, 0], [184, 0, 255], [255, 0, 76], [146, 255, 0], [51, 0, 255], [0, 197, 255], [255, 248, 0],
               [255, 0, 19], [255, 0, 38], [89, 255, 0], [127, 255, 0], [255, 153, 0], [0, 255, 255]]


def mkdir(path, rm=False):
    if os.path.exists(path):
        if rm:
            shutil.rmtree(path)
            os.makedirs(path)
    else:
        os.makedirs(path)


def add_chinese_text(img, text, left, top, color=(0, 255, 0)):
    if isinstance(img, np.ndarray):
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    draw.text((left, top), text, color, font=font_text)
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)


def draw_txt(img, ann, show=False):
    num = 0
    for one_ann in ann:
        text = one_ann["text"]
        conf = one_ann["confidence"]
        points = one_ann["text_region"]

        text = "{:.2f} {}".format(conf, text)
        # print("points num:", len(points))

        color = tuple(label_color[num % len(label_color)])
        points = (np.reshape(points, [-1, 2])).astype(np.int32)
        img = cv2.polylines(img, [points], True, color, 1)
        for idx, pt in enumerate(points):
            cv2.circle(img, (pt[0], pt[1]), 5, color, thickness=2)
            cv2.putText(img, str(idx), (pt[0], pt[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, color, thickness=1)
        img = add_chinese_text(img, text, points[0][0], points[0][1]-20, color=color[::-1])
        num += 1

    if show:
        cv2.namedWindow("result", 0)
        cv2.imshow("result", img)
        key = cv2.waitKey(0)
        if key == 27:
            exit()

    return img


if __name__ == "__main__":
    port = '8812'
    # language = ['ENG', 'JAP', 'KOR', 'CH']
    language = ['JAP']
    request_url = "http://180.76.228.199:{}/dango/algo/ocr/server".format(port)
    # request_url = "http://0.0.0.0:{}/dango/algo/ocr/server".format(port)
    img_path = "/media/ming/DATA3/Dango/received_imgs/8801/detect/test/2020-10-30_test"
    font_path = "/media/ming/DATA2/PaddleOCR/doc/japan.ttc"
    test_num = 10

    font_text = ImageFont.truetype(font_path, 20, encoding="utf-8")
    img_list = glob.glob(img_path + "/*.jpg")
    for lang in language:
        num = 0
        for i, img_p in enumerate(img_list):
            if lang not in img_p:
                continue

            num += 1
            print("{}/{} {} {}".format(i, len(img_list), lang, img_p))
            f = open(img_p, 'rb')
            img = b64encode(f.read())  # .decode()
            # print(img)
            s1 = time.time()
            data = {"image": img, "language_type": lang, "user_id": "234232", "platform": "win32"}
            # print(img)
            response = requests.post(request_url, data=data).json()
            print(response)
            s2 = time.time()
            print("time cost:", s2 - s1)

            result = response['data']['result'][0]  # batch result, now we only use first one
            img_cv = cv2.imread(img_p)
            draw_txt(img_cv, result, True)

            if num > test_num:
                break
