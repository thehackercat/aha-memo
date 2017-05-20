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
    @coroutine
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

    @coroutine
    def post(self, *args, **kwargs):
        # 获得post的数据
        origineStr = self.request.body

        # 解析Json数据格式
        wordObj = json_decode(origineStr)

        # 解析json中的用户id
        try:
            user_id = int(wordObj["user_id"])
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
            result = yield word_db.word_add(word_id=str(word_id),
                                        user_id=str(user_id),
                                        word_ori=word_ori,
                                        word_explain=word_explain,
                                        word_phonetic=word_phonetic,
                                        word_us_phonetic=word_us_phonetic,
                                        word_uk_phonetic=word_uk_phonetic,
                                        speak_url=speak_url,
                                        word_tip=word_tip,
                                        word_weight=word_weight,
                                        easy_forget=easy_forget,
                                        is_memoried=is_memoried)
        except ValueError as e:
            logger.warning(e.message)
            respJson = ResponseJSON(400, description="参数错误！！！")
            yield word_db.word_add_rollback(word_id=word_id)
            raise tornado.gen.Return(self.write(respJson.resultStr()))
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.error(e.message)
            yield word_db.word_add_rollback(word_id=word_id)
            logger.warning(e.message)
            respJson = ResponseJSON(400, description="json数据格式有误")
            raise tornado.gen.Return(self.write(respJson.resultStr()))

        # 数据库添加结果，失败则回滚数据库
        if not result:
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

    @coroutine
    def patch(self, user_id, word_id, **kwargs):
        """
        该方法用于处理用户修改词条信息
        :param args:
        :param kwargs:
        :return:
        """
        origineStr = self.request.body

        # 验证提交数据的合法性
        if (word_id is None) or (not word_id) or (word_id == 'None'):
            resp = ResponseJSON(400, description="url有误", status=103)
            raise tornado.gen.Return(self.write(resp.resultStr()))

        wordObj = json_decode(origineStr)

        # 获取基本信息
        attr_dict = dict()
        attr_dict["word_ori"] = wordObj.get("word_ori", None)
        attr_dict["word_explain"] = wordObj.get("word_explain", None)
        attr_dict["word_phonetic"] = wordObj.get("word_phonetic", None)
        attr_dict["word_us_phonetic"] = wordObj.get("word_us_phonetic", None)
        attr_dict["word_uk_phonetic"] = wordObj.get("word_uk_phonetic", None)
        attr_dict["speak_url"] = wordObj.get("speak_url", None)
        attr_dict["word_tip"] = wordObj.get("word_tip", None)
        attr_dict["word_weight"] = wordObj.get("word_weight", None)
        attr_dict["easy_forget"] = wordObj.get("easy_forget", None)
        attr_dict["is_memoried"] = wordObj.get("is_memoried", None)

        # 判断是否需要修改
        if all(attr_dict[idx] is None for idx in attr_dict):
            respJson = ResponseJSON(500, description="没有要更新的条目")
            raise tornado.gen.Return(self.write(respJson.resultStr()))

        # 判断一下用到的关键字是否合法
        key_words_legal = self.__validate_key_words(word_ori=attr_dict['word_ori'],
                                                    word_explain=attr_dict['word_explain'],
                                                    word_phonetic=attr_dict['word_phonetic'],
                                                    word_us_phonetic=attr_dict['word_us_phonetic'],
                                                    word_uk_phonetic=attr_dict['word_uk_phonetic'],
                                                    speak_url=attr_dict['speak_url'],
                                                    word_tip=attr_dict['word_tip'],
                                                    word_weight=attr_dict['word_weight'])
        if not key_words_legal:
            logger.warning("提交的json数据可能数据格式不正确")
            respJson = ResponseJSON(400, description="你提交的json数据可能数据格式不正确,请核对")
            raise tornado.gen.Return(self.write(respJson.resultStr()))

        # 调用数据库存储词条基本信息的接口
        try:
            result = yield word_db.word_modify(str(word_id), str(user_id), attr_dict)
            logger.debug("调用数据库修改词条基本信息的接口")
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.error(e.message)
            respJson = ResponseJSON(500, description="更新词条基本信息时数据库报错")
            raise tornado.gen.Return(self.write(respJson.resultStr()))

        if result:
            respJson = ResponseJSON(200, description="词条修改成功")
            raise tornado.gen.Return(self.write(respJson.resultStr()))
        else:
            respJson = ResponseJSON(500, description="词条修改失败")
            raise tornado.gen.Return(self.write(respJson.resultStr()))

    @coroutine
    def delete(self, user_id, word_id):
        """
        该方法用于用户在删除词条
        :param args:
        :param kwargs:
        :return:
        """
        # 验证提交数据的合法性
        if (word_id is None) or (not word_id) or (word_id == 'None'):
            resp = ResponseJSON(400, description="url有误", status=103)
            raise tornado.gen.Return(self.write(resp.resultStr()))

        try:
            result = yield word_db.word_del(str(word_id), str(user_id))
        except Exception as e:
            logger.error(e.message)
            resp = ResponseJSON(500, description="删除词条失败,检查词条是否已删除", status=105)
            raise tornado.gen.Return(self.write(resp.resultStr()))

        if result:
            resp = ResponseJSON(201, description="删除词条成功")
            raise tornado.gen.Return(self.write(resp.resultStr()))
        else:
            resp = ResponseJSON(400, description="删除词条失败", status=106)
            raise tornado.gen.Return(self.write(resp.resultStr()))

    def __validate_key_words(self, word_ori, word_explain, word_phonetic, word_us_phonetic, word_uk_phonetic,
                             speak_url, word_tip, word_weight):
        """
        验证用户输入的关键字是否都满足要求（有效）
        :return:若有一个不有效都返回False
        """
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