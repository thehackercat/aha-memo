#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'LexusLee'

import os
import ConfigParser

from foundation import const

Loaded_Section_Or_File = []


class EnvironmentError(Exception):
    def __init__(self, conf_file, message):
        self.conf_file = conf_file
        self.message = message

    def __str__(self):
        return repr(self.message)


def load_config():
    load_authority_config()
    load_intlong_conf('all')


def load_authority_config():
    """
    解析authority.conf文件
    """
    BASE_DIR = os.path.dirname(__file__)
    # 解析authority.conf
    authorityConfig = _AuthorityConfig()
    config_path_authority = os.path.abspath(os.path.join(BASE_DIR, os.pardir, 'configureFiles/authority.conf'))
    cfauthority = ConfigParser.ConfigParser()
    cfauthority.read(config_path_authority)
    allsections_authority = cfauthority.sections()
    for section_authority in allsections_authority:
        roleStr = cfauthority.get(section_authority, "role")
        authorityConfig[section_authority] = tuple(roleStr.replace(' ', '').split(','))
    const.authority = authorityConfig

    Loaded_Section_Or_File.append('authority')


def load_intlong_conf(which_section):
    """
    根据which_section解析intlong.conf
    :param which_section: 需要解析的哪个section, 如果值是all，则解析所有的section
    :return 如果解析成功，返回True，否则返回False
    """
    if which_section in Loaded_Section_Or_File:
        return

    BASE_DIR = os.path.dirname(__file__)
    if const.env == "development":
        config_path_intlong = os.path.abspath(os.path.join(BASE_DIR, os.pardir, 'configureFiles/development/intlong.conf'))
    elif const.env == "production":
        config_path_intlong = os.path.abspath(os.path.join(BASE_DIR, os.pardir, 'configureFiles/production/intlong.conf'))
    elif const.env == "test":
        config_path_intlong = os.path.abspath(os.path.join(BASE_DIR, os.pardir, 'configureFiles/test/intlong.conf'))
    else:
        print "环境错误，既不是development，也不是production和test"
        raise EnvironmentError("环境错误，既不是development，也不是production和test")
    # 解析intlong.conf
    cfintlong = ConfigParser.ConfigParser()
    cfintlong.read(config_path_intlong)
    allsections_intlong = cfintlong.sections()
    print os.pardir
    for section_intlong in allsections_intlong:
        if which_section != 'all' and section_intlong != which_section:
            continue
        section_result_intlong = {}
        alloptions_intlong = cfintlong.options(section_intlong)
        for op_intlong in alloptions_intlong:
            section_result_intlong[op_intlong] = cfintlong.get(section_intlong, op_intlong)

        const.__dict__[section_intlong] = section_result_intlong
        Loaded_Section_Or_File.append(section_intlong)


class _AuthorityConfig:
    """
    该类用来存储权限配置
    """
    class ConstError(TypeError):
        pass

    def __setitem__(self, key, value):
        key = str(key)
        if key in self.__dict__.keys():
            raise self.ConstError, "Can't rebind const (%s)" % key
        self.__dict__[key] = value

    def __getitem__(self, item):
        return self.__dict__[str(item)]

    def get(self, key):
        try:
            return self.__dict__[str(key)]
        except:
            return []
