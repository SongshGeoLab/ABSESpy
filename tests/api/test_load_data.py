#!/usr/bin/env python3
# -*-coding:utf-8 -*-
"""`load_data` must resolve to files shipped inside the `abses` package (#154)."""

from pathlib import Path

import pytest

import abses
from abses.utils.data import DATA_LIST, load_data

PACKAGE_DIR = Path(abses.__file__).parent


class TestLoadData:
    """`load_data` resolves the example datasets shipped in the wheel."""

    @pytest.mark.parametrize("filename", DATA_LIST)
    def test_example_data_ships_inside_the_package(self, filename: str) -> None:
        """A repository-root `data/` directory is not part of the wheel."""
        path = load_data(filename)  # type: ignore[arg-type]

        assert path.is_file()
        assert path.resolve().is_relative_to(PACKAGE_DIR.resolve())

    def test_unknown_dataset_raises(self) -> None:
        """Asking for a dataset that does not exist names the available ones."""
        with pytest.raises(FileNotFoundError, match="farmland.tif"):
            load_data("missing.tif")  # type: ignore[arg-type]
