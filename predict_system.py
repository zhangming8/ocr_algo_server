import os
from PIL import Image
import cv2
import copy
import numpy as np
import time

import tools.infer.predict_det as predict_det
import tools.infer.predict_rec as predict_rec
import tools.infer.predict_cls as predict_cls
from tools.infer.utility import draw_ocr_box_txt
from ppocr.utils.utility import get_image_file_list, check_and_read_gif


class OCR(object):
    def __init__(self, cfg, logger, language_list):
        self.text_sys = TextSystem(cfg, language_list, logger)
        self.logger = logger

    def read_images(self, paths=[]):
        images = []
        for img_path in paths:
            assert os.path.isfile(img_path), "The {} isn't a valid file.".format(img_path)
            img = cv2.imread(img_path)
            if img is None:
                self.logger.info("error in loading image:{}".format(img_path))
                continue
            images.append(img)
        return images

    def predict(self, language, images=[], paths=[]):
        """
        Get the chinese texts in the predicted images.
        Args:
            images (list(numpy.ndarray)): images data, shape of each is [H, W, C]. If images not paths
            paths (list[str]): The paths of images. If paths not images
        Returns:
            res (list): The result of chinese texts and save path of images.
        """

        if images != [] and isinstance(images, list) and paths == []:
            predicted_data = images
        elif images == [] and isinstance(paths, list) and paths != []:
            predicted_data = self.read_images(paths)
        else:
            raise TypeError("The input data is inconsistent with expectations.")

        assert predicted_data != [], "There is not any image to be predicted. Please check the input data."

        all_results = []
        for img in predicted_data:
            if img is None:
                self.logger.info("error in loading image")
                all_results.append([])
                continue
            starttime = time.time()
            dt_boxes, rec_res = self.text_sys(img, language)
            elapse = time.time() - starttime
            self.logger.info("检测+识别流程结束,总耗时 time: {}".format(elapse))

            dt_num = len(dt_boxes)
            rec_res_final = []

            for dno in range(dt_num):
                text, score = rec_res[dno]
                rec_res_final.append({
                    'text': text,
                    'confidence': float(score),
                    'text_region': dt_boxes[dno].astype(np.int).tolist()
                })
            all_results.append(rec_res_final)
        return all_results


class TextSystem(object):
    def __init__(self, args, language_list, logger):
        self.logger = logger
        self.text_detector = predict_det.TextDetector(args)
        self.logger.info(
            "初始化检测模型:{} 最大边:{} 路径:{}".format(args.det_algorithm, args.det_max_side_len, args.det_model_dir))

        self.language_map = args.language_map
        self.text_recognizer_classifier = {}
        for idx, language_m in enumerate(language_list):
            self.logger.info("---------- {} -----------".format(language_m))
            args.update(language_m)
            self.logger.info("{} 更新识别语言{}的配置文件".format(idx, language_m))

            text_recognizer = predict_rec.TextRecognizer(args)
            self.logger.info(
                "{} 初始化识别模型:{} 语言:{} 词典:{} 模型路径:{} 输入大小:{}, rec_batch_num:{}, max_text_length:{}".format(idx,
                                                                                                         args.rec_algorithm,
                                                                                                         args.rec_char_type,
                                                                                                         args.rec_char_dict_path,
                                                                                                         args.rec_model_dir,
                                                                                                         args.rec_image_shape,
                                                                                                         args.rec_batch_num,
                                                                                                         args.max_text_length))
            if args.use_angle_cls:
                text_classifier = predict_cls.TextClassifier(args)
                self.logger.info(
                    "{} 初始化方向分类模型路径:{}, 输入大小:{} batch_num:{}, cls_thresh:{}".format(idx, args.cls_model_dir,
                                                                                    args.cls_image_shape,
                                                                                    args.cls_batch_num,
                                                                                    args.cls_thresh))
            else:
                text_classifier = None
                self.logger.info("{} 未设置方向分类模型 use_angle_cls={}".format(idx, args.use_angle_cls))

            self.text_recognizer_classifier[language_m] = [text_recognizer, text_classifier]

    def get_rotate_crop_image(self, img, points):
        '''
        img_height, img_width = img.shape[0:2]
        left = int(np.min(points[:, 0]))
        right = int(np.max(points[:, 0]))
        top = int(np.min(points[:, 1]))
        bottom = int(np.max(points[:, 1]))
        img_crop = img[top:bottom, left:right, :].copy()
        points[:, 0] = points[:, 0] - left
        points[:, 1] = points[:, 1] - top
        '''
        img_crop_width = int(max(np.linalg.norm(points[0] - points[1]), np.linalg.norm(points[2] - points[3])))
        img_crop_height = int(max(np.linalg.norm(points[0] - points[3]), np.linalg.norm(points[1] - points[2])))
        pts_std = np.float32([[0, 0], [img_crop_width, 0], [img_crop_width, img_crop_height], [0, img_crop_height]])
        M = cv2.getPerspectiveTransform(points, pts_std)
        dst_img = cv2.warpPerspective(img, M, (img_crop_width, img_crop_height), borderMode=cv2.BORDER_REPLICATE,
                                      flags=cv2.INTER_CUBIC)
        dst_img_height, dst_img_width = dst_img.shape[0:2]
        if dst_img_height * 1.0 / dst_img_width >= 1.5:
            dst_img = np.rot90(dst_img)
        return dst_img

    def print_draw_crop_rec_res(self, img_crop_list, rec_res):
        bbox_num = len(img_crop_list)
        for bno in range(bbox_num):
            cv2.imwrite("./output/img_crop_%d.jpg" % bno, img_crop_list[bno])
            print(bno, rec_res[bno])

    def __call__(self, img, language):
        self.logger.info("输入的 language: {}".format(language))
        language = self.language_map[language]
        self.logger.info("转换后的 language: {}".format(language))
        # detect
        ori_im = img.copy()
        self.logger.info("开始检测, 图片原尺寸: {}".format(img.shape))
        dt_boxes, elapse = self.text_detector(img)
        if dt_boxes is None:
            self.logger.info("{} 未检测到文字, 检测耗时: {}".format(language, elapse))
            return None, None
        self.logger.info("{} 检测boxes个数: {}, 检测耗时: {}".format(language, len(dt_boxes), elapse))

        img_crop_list = []
        dt_boxes = sorted_boxes(dt_boxes)
        for bno in range(len(dt_boxes)):
            self.logger.info("检测的第{}/{}多边形区域: {}".format(bno, len(dt_boxes), list(dt_boxes[bno])))
            tmp_box = copy.deepcopy(dt_boxes[bno])
            img_crop = self.get_rotate_crop_image(ori_im, tmp_box)
            img_crop_list.append(img_crop)
            self.logger.info("crop图片尺寸: {}".format(img_crop.shape))

        text_recognizer, text_classifier = self.text_recognizer_classifier[language]

        # classify
        if text_classifier is not None:
            img_crop_list, angle_list, elapse = text_classifier(img_crop_list)
            self.logger.info("进行方向分类, 分类方向结果: {} 分类耗时: {}".format(angle_list, elapse))

        # recognize
        rec_res, elapse = text_recognizer(img_crop_list)
        self.logger.info("进行识别, 识别个数: {}, 识别耗时: {}".format(len(rec_res), elapse))
        # self.print_draw_crop_rec_res(img_crop_list, rec_res)
        return dt_boxes, rec_res


def sorted_boxes(dt_boxes):
    """
    Sort text boxes in order from top to bottom, left to right
    args:
        dt_boxes(array):detected text boxes with shape [4, 2]
    return:
        sorted boxes(array) with shape [4, 2]
    """
    num_boxes = dt_boxes.shape[0]
    sorted_boxes = sorted(dt_boxes, key=lambda x: (x[0][1], x[0][0]))
    _boxes = list(sorted_boxes)

    for i in range(num_boxes - 1):
        if abs(_boxes[i + 1][0][1] - _boxes[i][0][1]) < 10 and (_boxes[i + 1][0][0] < _boxes[i][0][0]):
            tmp = _boxes[i]
            _boxes[i] = _boxes[i + 1]
            _boxes[i + 1] = tmp
    return _boxes


def main(args):
    image_file_list = get_image_file_list(args.image_dir)
    text_sys = TextSystem(args)

    is_visualize = True
    font_path = args.vis_font_path
    for image_file in image_file_list:
        img, flag = check_and_read_gif(image_file)
        if not flag:
            img = cv2.imread(image_file)
        if img is None:
            print("error in loading image:{}".format(image_file))
            continue
        starttime = time.time()
        dt_boxes, rec_res = text_sys(img)
        elapse = time.time() - starttime
        print("Predict time of %s: %.3fs" % (image_file, elapse))

        drop_score = 0.5
        dt_num = len(dt_boxes)
        for dno in range(dt_num):
            text, score = rec_res[dno]
            if score >= drop_score:
                text_str = "%s, %.3f" % (text, score)
                print(text_str)

        if is_visualize:
            image = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            boxes = dt_boxes
            txts = [rec_res[i][0] for i in range(len(rec_res))]
            scores = [rec_res[i][1] for i in range(len(rec_res))]

            draw_img = draw_ocr_box_txt(
                image,
                boxes,
                txts,
                scores,
                drop_score=drop_score,
                font_path=font_path)
            draw_img_save = "./inference_results/"
            if not os.path.exists(draw_img_save):
                os.makedirs(draw_img_save)
            cv2.imwrite(
                os.path.join(draw_img_save, os.path.basename(image_file)),
                draw_img[:, :, ::-1])
            print("The visualized image saved in {}".format(
                os.path.join(draw_img_save, os.path.basename(image_file))))


if __name__ == "__main__":
    from config import Config

    config = Config()
    config.vis_font_path = "/media/ming/DATA2/PaddleOCR/doc/japan.ttc"
    config.image_dir = "/media/ming/DATA3/Dango/received_imgs/8801/detect/test/2020-10-30_test"
    main(config)
