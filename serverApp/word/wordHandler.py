#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'LexusLee'

import time
from random import Random
from tornado.gen import coroutine
from tornado.escape import json_decode
import tornado.gen
from foundation.log import logger
from serverApp.common.aha import RequestHandlerAha, ResponseJSON
from serverApp.database.word import Word_DB

word_db = Word_DB()

class WordHander(RequestHandlerAha):
    """
    词条模块
    """
    def get(self, user_id, word_id):
        """
        用户查看词条的详细信息
        :param user_id: 用户id
        :param word_id: 词条id
        :return:
        """
        try:
            # 验证提交数据的合法性
            if (word_id is None) or (not word_id) or (word_id == 'None'):
                resp = ResponseJSON(400, description="url有误", status=103)
                raise tornado.gen.Return(self.write(resp.resultStr()))

            # 获取商品数据
            word = yield word_db.word_scan_batch(word_id)
            if word is None:
                rsp = ResponseJSON(code=404, description="查询不到商品")
            elif word == 403:
                rsp = ResponseJSON(code=403, description="品牌商信息有误")
            else:
                rsp = ResponseJSON(code=200, data=word)
        except Exception as e:
            rsp = ResponseJSON(code=500, description="查询出错")
            logger.error('WordHandler catch an exception, word_id: '
                         + str(word_id) + '\n' + '\tException: ' + e.message)
        finally:
            raise tornado.gen.Return(self.write(rsp.resultStr()))

    def post(self, *args, **kwargs):
        # 获得post的数据
        origineStr = self.request.body

        # 解析Json数据格式
        wordObj = json_decode(origineStr)

        # 解析json中的用户id
        try:
            user_id = int(wordObj["brand_id"])
        except Exception as e:
            logger.warning(e.message)
            respJson = ResponseJSON(400, description="json数据格式有误,无效用户id")
            raise tornado.gen.Return(self.write(respJson.resultStr()))

        try:
            word_ori = wordObj['word_ori']
            word_explain = wordObj.get("word_explain", None)
            word_phonetic = wordObj.get("word_phonetic", None)
            word_us_phonetic = wordObj.get("word_us_phonetic", None)
            word_uk_phonetic = wordObj.get("word_uk_phonetic", None)
            speak_url = wordObj.get("speak_url", None)
            easy_forget = wordObj.get("easy_forget", False)
            is_memoried = wordObj.get("is_memoried", False)
            word_tip = wordObj.get("word_tip", None)
            word_weight = wordObj.get("word_weight", None)
        except Exception as e:
            logger.error(e.message)
            respJson = ResponseJSON(400, description="json数据格式有误,请检查数据格式")
            raise tornado.gen.Return(self.write(respJson.resultStr()))

        # 判断一下用到的关键字是否合法
        key_words_legal = self.__validate_key_words(word_ori=word_ori,
                                                    word_explain=word_explain,
                                                    word_phonetic=word_phonetic,
                                                    word_us_phonetic=word_us_phonetic,
                                                    word_uk_phonetic=word_uk_phonetic,
                                                    speak_url=speak_url,
                                                    word_tip=word_tip,
                                                    word_weight=word_weight
                                                    )

        if not key_words_legal:
            logger.warning("提交的json数据可能数据格式不正确")
            respJson = ResponseJSON(400, description="你提交的json数据可能数据格式不正确")
            raise tornado.gen.Return(self.write(respJson.resultStr()))

        # 根据以上信息获得词条的id
        word_id = self.__generate_word_id()
        try:
            # 将商品基本信息和详细信息图片的名字保存到数据库
            result = yield word_db.word_add(word_id=int(word_id),
                                        user_id=int(user_id),
                                        word_ori=str(word_ori),
                                        word_explain=str(word_explain),
                                        word_phonetic=str(word_phonetic),
                                        word_us_phonetic=str(word_us_phonetic),
                                        word_uk_phonetic=str(word_uk_phonetic),
                                        speak_url=str(speak_url),
                                        word_tip=str(word_tip),
                                        word_weight=int(word_weight),
                                        easy_forget=bool(easy_forget),
                                        is_memoried=bool(is_memoried))
        except ValueError as e:
            logger.warning(e.message)
            respJson = ResponseJSON(400, description="参数错误！！！")
            yield word_db.word_add_rollback(word_id=word_id)
            raise tornado.gen.Return(self.write(respJson.resultStr()))
        except Exception as e:
            logger.error(e.message)
            yield word_db.word_add_rollback(word_id=word_id)
            logger.warning(e.message)
            respJson = ResponseJSON(400, description="json数据格式有误,请核对D（将商品基本信息和详细信息图片的名字保存到数据库）")
            raise tornado.gen.Return(self.write(respJson.resultStr()))

        # 数据库添加结果，失败则回滚数据库
        if result:
            # 回滚数据库
            yield word_db.word_add_rollback(word_id=word_id)
            respJson = ResponseJSON(500, description="将商品基本信息和详细信息图片的名字保存到数据库失败")
            raise tornado.gen.Return(self.write(respJson.resultStr()))
        # 成功则将id加入result_list
        else:
            data = {"word_id": word_id,
                    "user_id": user_id}
            resp = ResponseJSON(201, data=data, description="词条上传成功")
            raise tornado.gen.Return(self.write(resp.resultStr()))

    def __validate_key_words(self, word_ori, word_explain, word_phonetic, word_us_phonetic, word_uk_phonetic,
                             speak_url, word_tip, word_weight):
        """
        验证用户输入的关键字是否都满足要求（有效）
        :return:若有一个不有效都返回False
        """
        if word_ori is None:
            return False
        try:
            str(word_ori) if word_ori is not None else None
            str(word_explain) if word_explain is not None else None
            str(word_phonetic) if word_phonetic is not None else None
            str(word_us_phonetic) if word_us_phonetic is not None else None
            str(word_uk_phonetic) if word_uk_phonetic is not None else None
            str(speak_url) if speak_url is not None else None
            str(word_tip) if word_tip is not None else None
            int(word_weight) if word_weight is not None else None
        except Exception as e:
            logger.error(e.message)
            return False

        return True

    def random_str(self, randomlength=8):
        """
        生成n位随机数,默认为8位
        :param randomlength:
        :return:
        """
        str1 = ''
        chars = '0123456789'
        length = len(chars) - 1
        random = Random()
        for i in range(randomlength):
            str1 += chars[random.randint(0, length)]
        return str1

    def __is_non_negative(*args):
        """
        判断是否为 “非负值”
        :param args:
        :return:True OR False
        """
        for arg in args:
            if arg is not None:
                if arg < 0:
                    return False
        return True

    def __generate_word_id(self):
        """
        生成商品的word_id
        :return:
        """
        word_id_suffix = self.random_str()
        word_id_prefix = int(time.time())
        word_id = word_id_suffix + str(word_id_prefix)
        return word_id