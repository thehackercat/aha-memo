#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'LexusLee'

from tornado.gen import coroutine
from tornado import gen
from foundation.log import logger
from serverApp.common.serverAppConfig import YOUDAO_LANG_TYPE
from serverApp.common.aha import RequestHandlerAha, ResponseJSON
from serverApp.tools.youdao import YoudaoSpider

youdao = YoudaoSpider()

class TranslateHandler(RequestHandlerAha):
    """
    aha取词翻译模块
    """
    @coroutine
    def get(self):
        q = self.get_query_argument("q", None, strip=True)
        src_lang = self.get_query_argument("from", None)
        dst_lang = self.get_query_argument("to", None)

        if not q:
            resp_json = ResponseJSON(400, description="无效搜索关键字")
            raise gen.Return(self.write(resp_json.resultStr()))

        if not src_lang or src_lang in YOUDAO_LANG_TYPE:
            resp_json = ResponseJSON(400, description="无效源语言类型")
            raise gen.Return(self.write(resp_json.resultStr()))

        if not dst_lang or dst_lang in YOUDAO_LANG_TYPE:
            resp_json = ResponseJSON(400, description="无效源语言类型")
            raise gen.Return(self.write(resp_json.resultStr()))

        try:
            result = yield youdao.get_result(q=str(q), src_lang=str(src_lang), dst_lang=str(dst_lang))
        except Exception, e:
            # import traceback
            # traceback.print_exc()
            logger.error('调用翻译接口出错：' + str(e))
            resp_json = ResponseJSON(500, description="调用翻译接口出错", status=108)
            raise gen.Return(self.write(resp_json.resultStr()))

        if result is None:
            logger.error('未查到关于' + str(q) + '的翻译内容')
            resp_json = ResponseJSON(500, description="未查到内容", status=110)
            raise gen.Return(self.write(resp_json.resultStr()))
        else:
            resp_json = ResponseJSON(200, data=result)
            raise gen.Return(self.write(resp_json.resultStr()))
