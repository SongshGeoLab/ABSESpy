#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from typing import Any, Dict

from omegaconf import DictConfig, OmegaConf


def merge_parameters(parameters: DictConfig, **kwargs: Dict[str, Any]) -> DictConfig:
    """Merge parameters.

    Args:
        parameters: basic parameters
        kwargs: keyword arguments

    Returns:
        merged parameters
    """
    dot_list = [f"{k}={v}" for k, v in kwargs.items()]
    return OmegaConf.merge(parameters, OmegaConf.from_dotlist(dot_list))
