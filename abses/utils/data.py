#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""Handling some example datasets."""

from importlib import resources
from pathlib import Path
from typing import Literal, TypeAlias

DATA_LIST = [
    "farmland.tif",
    "precipitation.nc",
    "irr_lands.csv",
    "YR_cities.zip",
]
DataChoices: TypeAlias = Literal[
    "farmland.tif",
    "precipitation.nc",
    "irr_lands.csv",
    "YR_cities.zip",
]


def load_data(filename: DataChoices) -> Path:
    """Return the path of an example dataset shipped with ABSESpy.

    The files live in the `abses.data` package, so they are available from
    a regular `pip install` as well as from a source checkout.

    Args:
        filename: One of the example datasets listed in `DATA_LIST`.

    Returns:
        The path of the dataset file.

    Raises:
        FileNotFoundError: If `filename` is not an example dataset.
    """
    if filename not in DATA_LIST:
        raise FileNotFoundError(
            f"Cannot load data {filename}, example datasets include: {DATA_LIST}."
        )
    return Path(str(resources.files("abses.data") / filename))
