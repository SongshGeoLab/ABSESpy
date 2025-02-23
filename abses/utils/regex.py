#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""
This module contains some commonly used regular expressions for checking names.
这个模块里存储一些检查名称常用的正则表达式。
"""

import re

# 模块名称应该符合蛇形命名法，且不能以下划线开头或结尾
MODULE_NAME = re.compile(r"^[a-z][a-z0-9_]*[a-z0-9]$|^[a-z]$")

# 类名应该符合驼峰命名法
# Class name should be in camel case
CAMEL_NAME = re.compile(r"^[A-Z][a-zA-Z0-9]*$")


def is_snake_name(name: str) -> bool:
    """Check if the name is a valid module name.

    Args:
        name (str): The name to check

    Returns:
        bool: If the name is a valid module name, return True, otherwise return False

    Examples:
        >>> is_snake_name("module_name")
        True
        >>> is_snake_name("module-name")
        False
        >>> is_snake_name("ModuleName")
        False
    """
    return bool(MODULE_NAME.match(name))


def is_camel_name(name: str) -> bool:
    """Check if the name is a valid class name.

    Args:
        name (str): The name to check

    Returns:
        bool: If the name is a valid class name, return True, otherwise return False

    Examples:
        >>> is_camel_name("ClassName")
        True
        >>> is_camel_name("class-name")
        False
    """
    return bool(CAMEL_NAME.match(name))
