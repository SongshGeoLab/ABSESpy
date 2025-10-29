#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""
ABSESpy - Agent-based Social-ecological System framework in Python
Copyright (c) 2021-2023 Shuang Song

Documentation: https://absespy.github.io/ABSESpy
Examples: https://absespy.github.io/ABSESpy/tutorial/user_guide/
Source: https://github.com/SongshGeoLab/ABSESpy
"""

__all__ = [
    "__version__",
    "MainModel",
    "BaseHuman",
    "BaseNature",
    "PatchModule",
    "Actor",
    "ActorsList",
    "PatchCell",
    "perception",
    "alive_required",
    "time_condition",
    "Experiment",
    "load_data",
    "ABSESpyError",
    "raster_attribute",
]

import os

# Disable loguru default output by setting environment variable BEFORE any imports
# This prevents loguru from adding default handlers automatically
os.environ["LOGURU_AUTOINIT"] = "0"

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = f"v{version('abses')}"
except PackageNotFoundError:
    # Fallback for development mode when package metadata is not available
    __version__ = "v0.7.5-dev"

from .agents.actor import Actor, alive_required, perception
from .agents.sequences import ActorsList
from .core.experiment import Experiment
from .core.model import MainModel
from .core.time_driver import time_condition
from .human.human import BaseHuman
from .space.cells import PatchCell, raster_attribute
from .space.nature import BaseNature, PatchModule
from .utils.data import load_data
from .utils.errors import ABSESpyError

# Configure loguru to be silent by default
# The LOGURU_AUTOINIT environment variable set above prevents automatic handler creation
# Users can explicitly enable logging via model configuration (log.console: true)
