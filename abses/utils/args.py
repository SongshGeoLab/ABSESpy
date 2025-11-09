#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from typing import Any, Dict, cast

from omegaconf import DictConfig, OmegaConf


def merge_parameters(parameters: DictConfig, **kwargs: Dict[str, Any]) -> DictConfig:
    """Merge parameters with struct mode handling for backward compatibility.

    This function merges keyword arguments into the base parameters while
    temporarily disabling struct mode to allow adding new keys. This ensures
    backward compatibility with projects using older ABSESpy versions.

    Args:
        parameters: basic parameters (can be dict or DictConfig)
        kwargs: keyword arguments

    Returns:
        merged parameters as DictConfig

    Note:
        Struct mode is temporarily disabled during merge to allow dynamic
        key addition, which is required for backward compatibility with
        projects from ABSESpy < 0.8.x.
    """
    # Convert plain dict to DictConfig if needed
    if isinstance(parameters, dict) and not isinstance(parameters, DictConfig):
        parameters = OmegaConf.create(parameters)

    # Temporarily disable struct mode to allow adding new keys
    # This is essential for backward compatibility
    if isinstance(parameters, DictConfig):
        OmegaConf.set_struct(parameters, False)

    dot_list = [f"{k}={v}" for k, v in kwargs.items()]
    merged = OmegaConf.merge(parameters, OmegaConf.from_dotlist(dot_list))

    # Keep struct mode disabled in the merged config for flexibility
    if isinstance(merged, DictConfig):
        OmegaConf.set_struct(merged, False)

    return cast(DictConfig, merged)
