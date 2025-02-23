#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

import pytest

from abses.utils.regex import is_camel_name, is_snake_name


@pytest.mark.parametrize(
    "name,expected",
    [
        # 有效的模块名
        ("module", True),
        ("module_name", True),
        ("module123", True),
        ("m", True),
        ("name_123_more", True),
        # 无效的模块名
        ("Module", False),
        ("MODULE", False),
        ("module-name", False),
        ("123module", False),
        ("_module", False),
        ("module_", False),
        ("", False),
        ("module.name", False),
        ("module name", False),
        ("模块名", False),
        ("module#name", False),
    ],
)
def test_module_name(name: str, expected: bool):
    """test the module name"""
    assert is_snake_name(name) == expected


@pytest.mark.parametrize(
    "name,expected",
    [
        # 有效的类名
        ("Class", True),
        ("ClassName", True),
        ("Class123", True),
        ("C", True),
        ("ClassNameLong", True),
        ("XML", True),
        ("ClassABCTest", True),
        # 无效的类名
        ("class", False),
        ("className", False),
        ("Class_Name", False),
        ("Class-Name", False),
        ("123Class", False),
        ("_Class", False),
        ("Class_", False),
        ("", False),
        ("Class.Name", False),
        ("Class Name", False),
        ("类名", False),
        ("Class#Name", False),
        ("cLASS", False),
    ],
)
def test_class_name(name: str, expected: bool):
    """test the class name"""
    assert is_camel_name(name) == expected
