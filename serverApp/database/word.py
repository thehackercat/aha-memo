#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'LexusLee'
from tornado import gen

import decimal
import psycopg2
import DatabaseError

from serverApp.common.connectionPool import dbpool
from  DBModel import *
from ORM import _db

class Word_DB(object):
    """
    单词书模块接口
    """
    @gen.coroutine
    def word_add(self, word_id, user_id, word_ori, word_explain, word_phonetic, word_us_phonetic, word_uk_phonetic,
                 speak_url, easy_forget, is_memoried, word_tip, word_weight):
        """
       添加单词基本信息
       :param word_id:               int 词条id
       :param user_id:               str 用户id
       :param word_ori:              str 单词原意
       :param word_explain:          str 单词译意
       :param word_phonetic:         str 单词全局音标
       :param word_us_phonetic:      str 单词美式音标
       :param word_uk_phonetic:      str 单词英式音标
       :param speak_url:             str 单词音频地址
       :param easy_forget:           bool 易忘单词
       :param is_memoried:           bool 是否记住
       :param memory_time:           str 记住时间
       :param word_tip               str 词条备注
       :param word_weight            int 单词权重
       """
        word = Word(
            word_id=word_id,
            user_id=user_id,
            word_ori=word_ori,
            word_explain=word_explain,
            word_phonetic=word_phonetic,
            word_us_phonetic=word_us_phonetic,
            word_uk_phonetic=word_uk_phonetic,
            speak_url=speak_url,
            easy_forget=easy_forget,
            is_memoried=is_memoried,
            memory_time='NOW()' if is_memoried is True else None,
            word_tip=word_tip,
            word_weight=word_weight,
            create_time='NOW()',
            last_modify='NOW()',
            is_deleted='False',
        )

        try:
            rc = yield word.insert()
            if not rc:
                raise gen.Return(False)
        except psycopg2.IntegrityError as e:
            if 'word_id' in e.message:  # 违反数据完整性
                raise DatabaseError.ExistError('word', '''word(id = '%s') exists''' % word_id)
            raise e
        raise gen.Return(True)

    @gen.coroutine
    def word_add_rollback(self, word_id):
        """
        回滚添加单词时出现错误的情况
        :param word_id:        int  单词编号
        :return:               bool 操作结果
        """
        r1 = yield Word.where(word_id=word_id).delete()
        if not r1:
            raise gen.Return(True)
        # r2 = yield Word.where(word_id=word_id).returnings('word_id').delete()
        # if not r2:
        #     raise gen.Return(True)
        raise gen.Return(True)

    @gen.coroutine
    def word_modify(self, word_id, user_id, attr_dict):
        """
        根据单词id修改单词词条基本属性
        :param word_id:         int 单词id
        :param user_id:         str  用户id
        :param attr_dict:       dict 属性字典
        :return:                bool 修改结果
        attr_dict:dict 属性字典{
            :param word_id:               int 词条id
            :param user_id:               str 用户id
            :param word_ori:              str 单词原意
            :param word_explain:          str 单词译意
            :param word_phonetic:         str 单词全局音标
            :param word_us_phonetic:      str 单词美式音标
            :param word_uk_phonetic:      str 单词英式音标
            :param speak_url:             str 单词音频地址
            :param easy_forget:           bool 易忘单词
            :param is_memoried:           bool 是否记住
            :param memory_time:           str 记住时间
            :param word_tip               str 词条备注
            :param word_weight            int 单词权重
        }
        """
        try:
            rc = yield Word.where(word_id=word_id, user_id=user_id, is_deleted=False).update(
                word_ori=attr_dict['word_ori'] if 'word_ori' in attr_dict else None,
                word_explain=attr_dict['word_explain'] if 'word_explain' in attr_dict else None,
                word_phonetic=attr_dict['word_phonetic'] if 'word_phonetic' in attr_dict else None,
                word_us_phonetic=attr_dict['word_us_phonetic'] if 'word_us_phonetic' in attr_dict else None,
                word_uk_phonetic=attr_dict['word_uk_phonetic'] if 'word_uk_phonetic' in attr_dict else None,
                spaek_url=attr_dict['speak_url'] if 'speak_url' in attr_dict else None,
                easy_forget=attr_dict['easy_forget'] if 'easy_forget' in attr_dict else None,
                is_memoried=attr_dict['is_memoried'] if 'is_memoried' in attr_dict else None,
                memory_time='NOW()' if 'is_memoried' in attr_dict and attr_dict['is_memoried'] is True else None,
                word_tip=attr_dict['word_tip'] if 'word_tip' in attr_dict else None,
                word_weight=attr_dict['word_weight'] if 'word_weight' in attr_dict else None,
                last_modify='NOW()',
            )
        except Exception as e:
            raise e
        if not rc:
            raise DatabaseError.NotExistError('word', '''word(id = '%s') not exists''' % word_id)
        raise gen.Return(True)

    @gen.coroutine
    def word_scan_batch(self, *id_list):
        """
        根据词条id列表批量查询瓷套信息
        :param id_list:         list 词条id列表
        :return:                dict 返回字典
        dict 返回字典{
            str 词条id : dict 词条信息
        }
        """
        db_param = {
            'word_id': 'word_id',
            'user_id': 'user_id',
            'word_ori': 'word_ori',
            'word_explain': 'word_explain',
            'word_phonetic': 'word_phonetic',
            'word_us_phonetic': 'word_us_phonetic',
            'word_uk_phonetic': 'word_uk_phonetic',
            'speak_url': 'speak_url',
            'easy_forget': 'easy_forget',
            'is_memoried': 'is_memoried',
            'memory_time': 'memory_time',
            'word_tip': 'word_tip',
            'word_weight': 'word_weight',
            'create_time': 'create_time'
        }
        return_dict = dict()
        if not id_list:
            raise gen.Return(None)
        for l in id_list:
            if not isinstance(l, str):
                raise TypeError('id must be str')
        words = yield Word.where(word_id=id_list, is_deleted=False).select(-1)

        # 检查数据库查询结果
        if not words:
            raise DatabaseError.NotExistError('word', '''word(id = '%s') not exists''' % id_list)

        for word in words:
            # 检查词条是否被删除
            if word is None or len(word) == 0 or word['is_deleted']:
                raise DatabaseError.CommonError('''word(id = '%s') is deleted''' % word['word_id'])
            # 时间处理
            if 'create_time' in word and word['create_time'] is not None:
                word['create_time'] = word['create_time'].strftime("%Y-%m-%d %H:%M:%S")
            return_dict[word['pdt_id']] = _db._param_db_mapping(db_param, word)
        raise gen.Return(return_dict)

    @gen.coroutine
    def word_del(self, word_id, user_id):
        """
        用户删除单词本中的单词
        :param word_id:         int 单词id
        :param user_id:         str 用户id
        :return:                bool 删除结果
        """
        word = yield Word.where(word_id=word_id).select(1, 'is_deleted')
        # 判断词条是否已删除
        if word['is_deleted']:
            raise DatabaseError.CommonError('''word(id = '%s') can not delete again''' % word_id)

        rc = yield Word.where(word_id=word_id, user_id=user_id).update(is_deleted=True,
                                                                       delete_time='NOW()',
                                                                       last_modified='NOW()')
        if not rc:
            raise DatabaseError.NotExistError('word', '''word(id = '%s') not exists''' % word_id)
        raise gen.Return(True)