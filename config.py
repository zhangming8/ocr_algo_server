# -*- coding:utf-8 -*-


class Config(object):
    # server parmas
    host = '0.0.0.0'
    use_gpu = True
    ir_optim = True
    enable_mkldnn = False
    gpu_mem = 8000
    save_dir = "./received_imgs"
    language_map = {"ENG": "en", "JAP": "japan", "KOR": "korean", "CH": "ch", "CH_h": "ch_h", "French": 'french',
                    "German": 'german'}
    baidu_translate_app_id = ["20201017000591885"]
    baidu_translate_secret_key = ["CK6fgXm9h3heLd4HWoqD"]
    language_map_reverse = {v: k for k, v in language_map.items()}

    # params for text detector
    det_algorithm = "DB"
    det_model_dir = "./inference/det_db/ch_ppocr_server_v1.1_det_infer/"
    # det_model_dir = "./output/det_r18_vd_db/best_accuracy_infer/"
    det_max_side_len = 960

    # DB parmas
    det_db_thresh = 0.3
    det_db_box_thresh = 0.5
    det_db_unclip_ratio = 1.8  # 2.0

    # EAST parmas
    det_east_score_thresh = 0.8
    det_east_cover_thresh = 0.1
    det_east_nms_thresh = 0.2

    use_zero_copy_run = False
    use_pdserving = False
    assert len(baidu_translate_app_id) == len(baidu_translate_secret_key)

    def update(self, language):
        if language == "japan" or language == self.language_map_reverse["japan"]:
            self.update_jap()
        elif language == "en" or language == self.language_map_reverse["en"]:
            self.update_eng()
        elif language == "korean" or language == self.language_map_reverse["korean"]:
            self.update_korean()
        elif language == "ch" or language == self.language_map_reverse["ch"]:
            self.update_chinese()
        elif language == "ch_h" or language == self.language_map_reverse["ch_h"]:
            self.update_chinese_high()
        elif language == "french" or language == self.language_map_reverse["french"]:
            self.update_french()
        elif language == "german" or language == self.language_map_reverse["german"]:
            self.update_german()
        else:
            print("language not right: {}".format(language))
            raise NotImplementedError

    def update_jap(self):
        # params for text recognizer
        self.rec_algorithm = "CRNN"
        # self.rec_model_dir = "./inference/rec_crnn/japan_ppocr_mobile_v1.1_rec_infer/"
        self.rec_model_dir = "./output/rec_japan/best_accuracy_infer/"

        self.rec_image_shape = "3, 32, 800"  # "3, 32, 320"
        self.rec_char_type = 'japan'  # "en", "ch", 'japan', 'korean', 'french', 'german'
        self.rec_batch_num = 4
        self.max_text_length = 50  # 25

        self.rec_char_dict_path = "ppocr/utils/dict/japan_dict.txt"
        self.use_space_char = False

        self.use_angle_cls = False
        self.cls_model_dir = "./inference/cls/ch_ppocr_mobile_v1.1_cls_infer/"
        self.cls_image_shape = "3, 48, 192"
        self.label_list = ['0', '180']
        self.cls_batch_num = 30
        self.cls_thresh = 0.9

    def update_eng(self):
        # params for text recognizer
        self.rec_algorithm = "CRNN"
        self.rec_model_dir = "./inference/rec_crnn/en_ppocr_mobile_v1.1_rec_infer/"

        self.rec_image_shape = "3, 32, 320"
        self.rec_char_type = 'ch'  # "en", "ch", 'japan', 'korean', 'french', 'german'
        self.rec_batch_num = 4
        self.max_text_length = 30

        self.rec_char_dict_path = "./ppocr/utils/ic15_dict.txt"
        self.use_space_char = True

        self.use_angle_cls = False
        self.cls_model_dir = "./inference/cls/ch_ppocr_mobile_v1.1_cls_infer/"
        self.cls_image_shape = "3, 48, 192"
        self.label_list = ['0', '180']
        self.cls_batch_num = 30
        self.cls_thresh = 0.9

    def update_korean(self):
        # params for text recognizer
        self.rec_algorithm = "CRNN"
        self.rec_model_dir = "./inference/rec_crnn/korean_ppocr_mobile_v1.1_rec_infer/"

        self.rec_image_shape = "3, 32, 320"
        self.rec_char_type = 'korean'  # "en", "ch", 'japan', 'korean', 'french', 'german'
        self.rec_batch_num = 4
        self.max_text_length = 25

        self.rec_char_dict_path = "./ppocr/utils/dict/korean_dict.txt"
        self.use_space_char = False

        self.use_angle_cls = False
        self.cls_model_dir = "./inference/cls/ch_ppocr_mobile_v1.1_cls_infer/"
        self.cls_image_shape = "3, 48, 192"
        self.label_list = ['0', '180']
        self.cls_batch_num = 30
        self.cls_thresh = 0.9

    def update_chinese(self):
        # params for text recognizer
        self.rec_algorithm = "CRNN"
        self.rec_model_dir = "./inference/rec_crnn/ch_ppocr_mobile_v1.1_rec_infer/"

        self.rec_image_shape = "3, 32, 320"
        self.rec_char_type = 'ch'  # "en", "ch", 'japan', 'korean', 'french', 'german'
        self.rec_batch_num = 4
        self.max_text_length = 25

        self.rec_char_dict_path = "./ppocr/utils/ppocr_keys_v1.txt"
        self.use_space_char = True

        self.use_angle_cls = False  # True
        self.cls_model_dir = "./inference/cls/ch_ppocr_mobile_v1.1_cls_infer/"
        self.cls_image_shape = "3, 48, 192"
        self.label_list = ['0', '180']
        self.cls_batch_num = 30
        self.cls_thresh = 0.9

    def update_chinese_high(self):
        # params for text recognizer
        self.rec_algorithm = "CRNN"
        self.rec_model_dir = "./inference/rec_crnn/ch_ppocr_server_v1.1_rec_infer/"

        self.rec_image_shape = "3, 32, 320"
        self.rec_char_type = 'ch'  # "en", "ch", 'japan', 'korean', 'french', 'german'
        self.rec_batch_num = 4
        self.max_text_length = 25

        self.rec_char_dict_path = "./ppocr/utils/ppocr_keys_v1.txt"
        self.use_space_char = True

        self.use_angle_cls = False  # True
        self.cls_model_dir = "./inference/cls/ch_ppocr_mobile_v1.1_cls_infer/"
        self.cls_image_shape = "3, 48, 192"
        self.label_list = ['0', '180']
        self.cls_batch_num = 30
        self.cls_thresh = 0.9

    def update_french(self):
        # params for text recognizer
        self.rec_algorithm = "CRNN"
        self.rec_model_dir = "./inference/rec_crnn/french_ppocr_mobile_v1.1_rec_infer/"

        self.rec_image_shape = "3, 32, 320"
        self.rec_char_type = 'french'  # "en", "ch", 'japan', 'korean', 'french', 'german'
        self.rec_batch_num = 4
        self.max_text_length = 25

        self.rec_char_dict_path = "./ppocr/utils/dict/french_dict.txt"
        self.use_space_char = False

        self.use_angle_cls = False
        self.cls_model_dir = "./inference/cls/ch_ppocr_mobile_v1.1_cls_infer/"
        self.cls_image_shape = "3, 48, 192"
        self.label_list = ['0', '180']
        self.cls_batch_num = 30
        self.cls_thresh = 0.9

    def update_german(self):
        # params for text recognizer
        self.rec_algorithm = "CRNN"
        self.rec_model_dir = "./inference/rec_crnn/german_ppocr_mobile_v1.1_rec_infer/"

        self.rec_image_shape = "3, 32, 320"
        self.rec_char_type = 'german'  # "en", "ch", 'japan', 'korean', 'french', 'german'
        self.rec_batch_num = 4
        self.max_text_length = 25

        self.rec_char_dict_path = "./ppocr/utils/dict/german_dict.txt"
        self.use_space_char = False

        self.use_angle_cls = False
        self.cls_model_dir = "./inference/cls/ch_ppocr_mobile_v1.1_cls_infer/"
        self.cls_image_shape = "3, 48, 192"
        self.label_list = ['0', '180']
        self.cls_batch_num = 30
        self.cls_thresh = 0.9