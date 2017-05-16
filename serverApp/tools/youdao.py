#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'LexusLee'
import random
import hashlib
import requests
from tornado import gen
from foundation.log import logger
from serverApp.common.serverAppConfig import YOUDAO_APP_KEY, YOUDAO_APP_SECRET

youdao_url = 'https://openapi.youdao.com/api'

class YoudaoSpider(object):
    """
    该模块用于调用有道智云api
    """
    def __init__(self):
        self.youdao_key = YOUDAO_APP_KEY
        self.youdao_secret = YOUDAO_APP_SECRET
        self.salt = random.randint(1, 10)  # 生成(1,10)随机salt值

    def build_signature(self, q, salt, app_key, app_secret):
        if isinstance(q, unicode):
            q = str(q)
        md5 = hashlib.md5()
        md5.update(str(app_key)+q+str(salt)+str(app_secret))
        sign = md5.hexdigest()
        return sign

    def build_get_url(self, q, src_lang, dst_lang):
        get_url = youdao_url + '?q={q}&from={src_lang}&to={dst_lang}&appKey={appkey}&salt={salt}&sign={sign}'.format(
            q=q,
            src_lang=src_lang,
            dst_lang=dst_lang,
            appkey=self.youdao_key,
            salt=self.salt,
            sign=self.build_signature(q, self.salt, self.youdao_key, self.youdao_secret)
        )
        return get_url

    @gen.coroutine
    def get_result(self, q, src_lang, dst_lang):
        url = self.build_get_url(q, src_lang, dst_lang)
        r = requests.get(url)
        raise gen.Return(r.content)