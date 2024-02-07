# -*- coding: utf-8 -*-
"""
@ Author     : zhufeng
@ Time       : 2024年02月07日
@ File       : config_sign.py
@ Description: 自动签到使用的配置文件模块
"""
import configparser
from src.commons.log import logger


# 对配置文件的内容进行一些预处理，例如将键和节名称转换为小写。
# conf = configparser.ConfigParser()
# 保留了配置文件中的原始大小写和特殊字符，不进行任何预处理。
config = configparser.RawConfigParser()
# settings.ini 可以不存在此文件，意味着准备新建配置文件。
config.read("config/settings_sign.ini", encoding='UTF-8')


# 读 Section 下所有配置
def read_section(section):
    try:
        return config.items(section)
    except configparser.NoSectionError:
        logger.warning('No section: {}', section)
    return None


# 读配置文件
def read_config(section, key, fallback=None):
    try:
        if fallback is None:
            return config.get(section, key)
        else:
            return config.get(section, key, fallback=fallback)
    except configparser.NoSectionError:
        logger.debug('No section: {}', section)
    except configparser.NoOptionError:
        logger.debug('No option: {}', key)
    return None


# 新增配置节点
def write_config(section, key, value, auto_save=False):
    try:
        if not config.has_section(section):
            # 添加节点 school
            config.add_section(section)
        # 添加新的 IP 地址参数
        config.set(section, key, value)
        if auto_save:
            save_config()
    except configparser.DuplicateSectionError:
        logger.warning('Section {} already exists', section)


# 保存配置文件
def save_config():
    # 写入文件
    config.write(open("config/settings_sign.ini", "w", encoding='UTF-8'))
