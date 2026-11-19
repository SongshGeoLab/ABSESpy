#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""Example datasets shipped inside the `abses.data` package."""

from importlib import resources
from pathlib import Path
from typing import List, Literal, TypeAlias, get_args

DataChoices: TypeAlias = Literal[
    "farmland.tif",
    "precipitation.nc",
    "irr_lands.csv",
    "YR_cities.zip",
]
DATA_LIST: List[str] = list(get_args(DataChoices))


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
