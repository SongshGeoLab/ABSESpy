#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from enum import IntEnum


class State(IntEnum):
    """状态枚举，使用整数值确保可以比较"""

    NEW = 0
    INIT = 1
    READY = 2
    COMPLETE = 3
