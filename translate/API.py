# -*- coding: utf-8 -*-

import requests
from http.client import HTTPConnection
from hashlib import md5
from urllib import parse
from random import randint
import json
import re
import time
from traceback import print_exc

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tmt.v20180321 import tmt_client, models


# 翻译主函数
def translate(texts, appid, secretKey, logger):
    sentence = []
    for one_ann in texts:
        text = one_ann["text"]
        conf = one_ann["confidence"]
        points = one_ann["text_region"]
        sentence.append(text)

    sentence = " ".join(sentence)

    translate_result = baidu(sentence, appid, secretKey, logger)
    return translate_result


# 有道翻译
def youdao(sentence):
    url = 'http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'}
    data = {
        'i': sentence,
        'from': 'AUTO',
        'to': 'zh',
        'smartresult': 'dict',
        'client': 'fanyideskweb',
        'doctype': 'json',
        'version': '2.1',
        'keyfrom': 'fanyi.web',
        'action': 'FY_BY_REALTIME',
        'typoResult': 'false'
    }
    try:
        res = requests.get(url, params=data, headers=headers)
        html = json.loads(res.text)
        result = ''
        for tgt in html['translateResult'][0]:
            result += tgt['tgt']

    except Exception:
        print_exc()
        result = "有道：我抽风啦！"

    return result


# 公共彩云翻译
def caiyun(sentence):
    url = "http://api.interpreter.caiyunai.com/v1/translator"
    token = "3975l6lr5pcbvidl6jl2"

    payload = {
        "source": [sentence],
        "trans_type": "auto2zh",
        "request_id": "demo",
        "detect": True,
    }

    headers = {
        'content-type': "application/json",
        'x-authorization': "token " + token,
    }
    try:
        response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
        result = json.loads(response.text)['target'][0]

    except Exception:
        print_exc()
        result = "彩云翻译：我抽风啦！"

    return result


# 金山翻译
def jinshan(sentence):
    url = 'http://fy.iciba.com/ajax.php?a=fy'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'}
    data = {
        'f': 'auto',
        't': 'zh',
        'w': sentence
    }
    try:
        response = requests.post(url, data=data)
        info = response.text
        data_list = json.loads(info)
        result = data_list['content']['out']
        if not result:
            result = "金山：我抽风啦！"

    except Exception:
        print_exc()
        result = "金山：我抽风啦！"

    return result


# yeekit翻译
def yeekit(sentence, yeekitLanguage):
    url = 'https://www.yeekit.com/site/dotranslate'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'}
    data = {
        'content[]': sentence,
        'sourceLang': yeekitLanguage,
        'targetLang': "nzh"
    }
    try:
        res = requests.get(url, data=data, headers=headers)
        html = res.text.encode('utf-8').decode('unicode_escape')
        result = re.findall(r'"text": "(.+?)"translate time"', html, re.S)[0]
        result = result.replace('\\', '').replace('}', '').replace(']', '').replace('"', '').replace('\n', '').replace(
            ' ', '')
        result = result[:-1]

    except Exception:
        print_exc()
        print(res.text)
        result = "yeekit：我抽风啦！"

    return result


def ALAPI(sentence):
    url = 'https://v1.alapi.cn/api/fanyi?q=%s&from=auto&to=zh' % sentence

    try:
        res = requests.post(url)
        html = json.loads(res.text)
        result = html["data"]["trans_result"][0]["dst"]

    except Exception:
        print_exc()
        result = "ALAPI：我抽风啦！"

    return result


# 私人百度翻译
def baidu(sentence, appid, secretKey, logger, fromLang='auto', toLang='zh'):
    httpClient = None
    myurl = '/api/trans/vip/translate'

    salt = randint(32768, 65536)
    q = sentence
    sign = appid + q + str(salt) + secretKey
    sign = md5(sign.encode()).hexdigest()
    myurl = myurl + '?appid=' + appid + '&q=' + parse.quote(q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(
        salt) + '&sign=' + sign
    logger.info("生成请求url: {}".format(myurl))

    success = True
    try:
        httpClient = HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', myurl)

        response = httpClient.getresponse()
        result_all = response.read().decode("utf-8")
        result = json.loads(result_all)

        string = ''
        for word in result['trans_result']:
            if word == result['trans_result'][-1]:
                string += word['dst']
            else:
                string += word['dst'] + '\n'

    except Exception:
        success = False
        if result['error_code'] == '54003':
            string = "翻译：我抽风啦！"
        elif result['error_code'] == '52001':
            string = '翻译：请求超时，请重试'
        elif result['error_code'] == '52002':
            string = '翻译：系统错误，请重试'
        elif result['error_code'] == '52003':
            string = '翻译：APPID 或 密钥 不正确'
        elif result['error_code'] == '54001':
            string = '翻译：APPID 或 密钥 不正确'
        elif result['error_code'] == '54004':
            string = '翻译：账户余额不足'
        elif result['error_code'] == '54005':
            string = '翻译：请降低长query的发送频率，3s后再试'
        elif result['error_code'] == '58000':
            string = '翻译：客户端IP非法，注册时错误填入服务器地址，请前往开发者信息-基本信息修改，服务器地址必须为空'
        elif result['error_code'] == '90107':
            string = '翻译：认证未通过或未生效'
        else:
            string = '翻译：%s，%s' % (result['error_code'], result['error_msg'])

    finally:
        if httpClient:
            httpClient.close()

    return string, success


# 私人腾讯翻译
def tencent(sentence, data):
    secretId = data['tencentAPI']['Key']
    secretKey = data['tencentAPI']['Secret']

    if (not secretId) or (not secretKey):
        string = '私人腾讯：还未注册私人腾讯API，不可使用'
    else:
        try:
            cred = credential.Credential(secretId, secretKey)
            httpProfile = HttpProfile()
            httpProfile.endpoint = "tmt.tencentcloudapi.com"

            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            client = tmt_client.TmtClient(cred, "ap-guangzhou", clientProfile)

            req = models.TextTranslateRequest()
            sentence = sentence.replace('"', "'")
            params = '''{"SourceText":"%s","Source":"auto","Target":"zh","ProjectId":0}''' % (sentence)
            req.from_json_string(params)

            resp = client.TextTranslate(req)
            result = re.findall(r'"TargetText": "(.+?)"', resp.to_json_string())[0]

        except TencentCloudSDKException as err:

            err = str(err)
            code = re.findall(r'code:(.*?) message', err)[0]
            error = re.findall(r'message:(.+?) requestId', err)[0]

            if code == 'MissingParameter':
                pass

            elif code == 'FailedOperation.NoFreeAmount':
                result = "私人腾讯：本月免费额度已经用完"

            elif code == 'FailedOperation.ServiceIsolate':
                result = "私人腾讯：账号欠费停止服务"

            elif code == 'FailedOperation.UserNotRegistered':
                result = "私人腾讯：还没有开通机器翻译服务"

            elif code == 'InternalError':
                result = "私人腾讯：内部错误"

            elif code == 'InternalError.BackendTimeout':
                result = "私人腾讯：后台服务超时，请稍后重试"

            elif code == 'InternalError.ErrorUnknown':
                result = "私人腾讯：未知错误"

            elif code == 'LimitExceeded':
                result = "私人腾讯：超过配额限制"

            elif code == 'UnsupportedOperation':
                result = "私人腾讯：操作不支持"

            elif code == 'InvalidCredential':
                result = "私人腾讯：secretId或secretKey错误"

            elif code == 'AuthFailure.SignatureFailure':
                result = "私人腾讯：secretKey错误"

            elif code == 'AuthFailure.SecretIdNotFound':
                result = "私人腾讯：secretId错误"

            elif code == 'AuthFailure.SignatureExpire':
                result = "私人腾讯：签名过期，请将电脑系统时间调整至准确的时间后重试"

            else:
                result = "私人腾讯：%s，%s" % (code, error)

        except Exception:
            print_exc()
            result = '私人腾讯：我抽风啦！'

    return result


def caiyunAPI(sentence, data):
    token = data["caiyunAPI"]
    if not token:
        result = '私人彩云：还未注册私人彩云API，不可使用'
    else:
        url = "http://api.interpreter.caiyunai.com/v1/translator"
        payload = {
            "source": [sentence],
            "trans_type": "auto2zh",
            "request_id": "demo",
            "detect": True,
        }

        headers = {
            'content-type': "application/json",
            'x-authorization': "token " + token,
        }
        try:
            response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
            result = json.loads(response.text)['target'][0]

        except Exception:
            print_exc()
            result = "私人彩云：我抽风啦！"

    return result
