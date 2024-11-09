# image_moderation.py
import urllib.request
import json
import hashlib
import random
import string
import datetime
from datetime import datetime, timezone, timedelta
from urllib.parse import urlencode
import hmac
import base64

class ImageModeration(object):
    def __init__(self, app_id, api_key, api_secret):
        self.post_image_url = "https://audit.iflyaisol.com/audit/v2/image"
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret

    # 1、鉴权参数
    def sign_param(self):
        # 1、获取utc时间
        tz = timezone(timedelta())
        fmt = '%Y-%m-%dT%H:%M:%S%z'
        zoned_time = datetime.today().astimezone(tz)
        zoned_time = str(zoned_time.strftime(fmt))
        # 2、url参数
        data_dict = {
            "appId": self.app_id,
            "accessKeyId": self.api_key,
            "accessKeySecret": self.api_secret,
            "utc": zoned_time,
            "uuid": ''.join(random.sample(string.ascii_letters + string.digits, 32))  # 随机生成
        }
        # 参数字典倒排序为列表
        params_list = sorted(data_dict.items(), key=lambda e: e[0], reverse=False)
        # 还原字典
        params_str_dict = dict(params_list)
        # 然后urlencode
        params_str_urlencode = urlencode(params_str_dict)
        print("params_str_urlencode", params_str_urlencode)
        return params_str_dict, params_str_urlencode

    # 2、鉴权获取
    def get_sign(self, secret):
        # 1、生成baseString
        params_str_dict, params_str_urlencode = self.sign_param()
        baseString = hmac.new(secret.encode('utf-8'), params_str_urlencode.encode('utf-8'), digestmod=hashlib.sha1).digest()
        print("baseString", baseString)
        # 2、得到signature
        signature = base64.b64encode(baseString).decode(encoding='utf-8')
        # 3、url参数加上signature
        params_str_dict["signature"] = signature
        # 4、：换=，去”“
        params_str = str(params_str_dict).replace(':', '=').replace(' ', '').replace("'", '')
        return params_str, params_str_dict

    # 3、获得请求结果
    def get_resp(self, request_url, bussiness_param_json):
        # 0、获取鉴权参数字典、鉴权参数url
        param_str, params_str_dict = self.get_sign(self.api_secret)
        param_str_url = urlencode(params_str_dict)
        # 1、拼接url
        url = request_url + "?" + param_str_url
        headers = {'Content-Type': 'application/json;charset=UTF-8'}
        req = urllib.request.Request(url, bussiness_param_json, headers)
        urlResp = urllib.request.urlopen(req)
        resp = urlResp.read().decode("utf-8")
        return resp

    # 4、图片审核
    def image_moderate(self, image_url):
        # 图片审核业务参数
        moderate_param = {
            "content": image_url
        }
        moderate_json = bytes(json.dumps(moderate_param), encoding='utf8')
        # 获取结果
        resp = self.get_resp(self.post_image_url, moderate_json)
        return resp



# https://haowallpaper.com/link/common/file/getCroppingImg/15812065827459392