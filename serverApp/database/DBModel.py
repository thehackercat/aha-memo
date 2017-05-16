# -*- coding:utf-8 -*-
__author__ = 'LexusLee'
"""
该模块是数据库模型类
"""

from ORM import Model
from ORM import Field


class Word(Model):
    word_serial = Field(primary_key=True)
    word_id = Field()
    user_id = Field()
    word_ori = Field()
    word_explain = Field()
    word_phonetic = Field()
    word_us_phonetic = Field()
    word_uk_phonetic = Field()
    speak_url = Field()
    easy_forget = Field()
    is_memoried = Field()
    memory_time = Field()
    word_tip = Field()
    is_deleted = Field()
    delete_time = Field()
    create_time = Field()
    last_modify = Field()
    word_weight = Field()
