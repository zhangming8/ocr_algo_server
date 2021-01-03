# -*-coding:utf-8-*-
import os
import json
import cv2
import sys
import traceback
import argparse
from flask import Flask, Response, request
import datetime
from queue import Queue
import threading
import multiprocessing
import random
from setproctitle import setproctitle

from config import Config
import tools.logger as logger_
from tools.infer.utility import base64_to_cv2, mkdir
from predict_system import OCR
from translate.API import translate

app = Flask("server", static_url_path='')
app.config['PROPAGATE_EXCEPTIONS'] = True
_save_image_q = Queue(1000)

config = Config()


@app.route("/dango/algo/ocr/server", methods=['POST', 'GET'])
def ocr_server():
    try:
        logger.info("-" * 50)
        logger.info("端口 {} /dango/algo/ocr/server 收到请求".format(g_port))

        now_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f')
        day = "-".join(now_time.split("-")[:3])
        # params = request.get_json()
        content = request.form

        images = content['image']
        language_type = content['language_type']
        user_id = content["user_id"]
        platform = content.get('platform', None)
        need_translate = content.get("translate", 'no')

        images_decode = [base64_to_cv2(images)]
        logger.info("收到: {}, {}, {}".format(user_id, platform, language_type))

        result = ocr.predict(language_type, images=images_decode)
        logger.info("识别结果为: {}, 是否需要翻译: {}".format(result, need_translate))
        save_basename = "{}/{}/{}_{}_{}_{}_{}".format(config.save_dir + "/" + g_port, day, g_port, platform, user_id,
                                                      language_type, now_time)
        _save_image_q.put([save_basename, images_decode, result])

        translated = False
        response_data = {'result': result, 'translated': translated}
        if need_translate == 'yes':
            logger.info("开始进行翻译...")
            rand_idx = random.randint(0, len(config.baidu_translate_secret_key)-1)
            fanyi_app_id, fanyi_secret_key = config.baidu_translate_app_id[rand_idx], config.baidu_translate_secret_key
            translate_result, translated = translate(result[0], fanyi_app_id, fanyi_secret_key)
            if translated:
                logger.info("翻译成功: {}, 结果为: {}".format(translated, translate_result))
                response_data = {'result': translate_result, 'translated': translated, 'org': result}
            else:
                logger.info("翻译失败: {}, 错误码: {}".format(translated, translate_result))

        return Response(json.dumps({'status': 0, 'data': response_data}),
                        mimetype='application/json')

    except:
        e = traceback.format_exc()
        logger.info("错误")
        logger.error(e)
        return Response(json.dumps({'status': -1, 'data': 'None'}), mimetype='application/json')


def save_img():
    while True:
        try:
            save_basename, image_cv2, words_result = _save_image_q.get(block=True)
            assert len(image_cv2) == len(words_result)
            for idx, img in enumerate(image_cv2):
                save_name = save_basename + "_" + str(idx) + ".jpg"
                mkdir(os.path.dirname(save_name))
                cv2.imwrite(save_name, img)
                with open(save_name.replace(".jpg", ".txt"), "w") as f:
                    f.write(str(words_result[idx]))
                logger.info('保存图片 {}及txt'.format(save_name))
        except:
            e = traceback.format_exc()
            logger.info(e)


def do_work(gpu, port):
    global logger, g_port, ocr
    try:
        os.environ["CUDA_VISIBLE_DEVICES"] = "{}".format(gpu)
        logger = logger_.get_logger("./log/ocr_{}.log".format(port))
        g_port = port
        logger.info("===>>> 初始化模型到gpu:{}, port: {}".format(gpu, port))
        ocr = OCR(config, logger, language_list)
        logger.info("==>> 启动成功")
        app.run(host=config.host, port=port, threaded=True)

    except BaseException as e:
        logger.error('错误,启动flask异常{}'.format(e))
        logger.info(traceback.format_exc())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--gpu', type=str, help='gpu index: 0_1_2_3', default="0")
    parser.add_argument('--port', type=str, help='server port: 8811_8812_8813', default="8811")
    parser.add_argument('--det', type=str, help='detection model', default="DB")
    parser.add_argument('--rec', type=str, help='recognize language model', default="ch,japan,en,korean")
    args = parser.parse_args()

    setproctitle('ocr_server_{}_{}'.format(args.port, args.rec))

    ports = args.port.split("_")  # [args.port]
    gpus = args.gpu.split("_")  # [args.gpu]
    language_list = args.rec.replace(" ", "").split(",")
    if len(gpus) == 1:
        gpus = gpus * len(ports)

    gpu_num = len(gpus)
    port_num = len(ports)

    if gpu_num != port_num:
        print('启动失败:GPU数量 != 端口数量！')
        sys.exit(1)

    threading.Thread(target=save_img, name="save img").start()
    do_work(gpu=gpus[0], port=ports[0])

    # pool = multiprocessing.Pool(processes=port_num)
    # for index in range(port_num):
    #     pool.apply_async(do_work, (gpus[index], ports[index]))
    # pool.close()
    # pool.join()
    # save_img()
