#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""测试自然模块"""

import numpy as np
import pytest
import rioxarray as rxr
import xarray
from shapely.geometry import box

from abses.agents.actor import Actor
from abses.agents.sequences import ActorsList
from abses.core.model import MainModel
from abses.space.cells import PatchCell, raster_attribute
from abses.space.patch import PatchModule


class MockPatchCell(PatchCell):
    """测试斑块"""

    def __init__(self, *agrs, x=1, y=2, **kwargs):
        super().__init__(*agrs, **kwargs)
        self._x = x
        self._y = y

    @raster_attribute
    def x(self) -> int:
        """x"""
        return self._x

    @x.setter
    def x(self, value) -> None:
        self._x = value

    @raster_attribute
    def y(self) -> int:
        """y"""
        return self._y

    @y.setter
    def y(self, value) -> None:
        self._y = value


class TestPatchModulePositions:
    """测试斑块模型的位置选取"""

    @pytest.mark.parametrize(
        "row, col, pos, indices",
        [
            (0, 1, (1, 1), (0, 1)),
            (1, 1, (1, 0), (1, 1)),
            (1, 0, (0, 0), (1, 0)),
            (0, 0, (0, 1), (0, 0)),
        ],
    )
    def test_pos_and_indices(self, module: PatchModule, row, col, pos, indices):
        """测试位置和索引。
        pos 应该是和 cell 的位置一致
        indices 应该是和 cell 的索引一致。

        Pos [0, 0] -> idx[1, 0]: 0
        Pos [0, 1] -> idx[0, 0]: 1
        Pos [1, 0] -> idx[1, 1]: 2
        Pos [1, 1] -> idx[0, 1]: 3

        >>> module.array_cells
        [[1, 3],
        [0, 2]]
        """
        # arrange
        cell = module.array_cells[row, col]
        # act / assert
        assert cell.pos == pos
        assert cell.indices == indices

    @pytest.mark.parametrize(
        "index, expected_value",
        [
            ((1, 1), 3),
            ((0, 0), 0),
        ],
    )
    def test_array_cells(self, module: PatchModule, index, expected_value):
        """测试数组单元格"""
        # arrange
        module.apply_raster(np.arange(4).reshape(1, 2, 2), "test")
        # act / assert
        cell = module.array_cells[index[0], index[1]]
        assert cell.test == expected_value


class TestPatchModule:
    """测试斑块模型"""

    @pytest.mark.parametrize(
        "y_changed, expected",
        [
            (2, 8),
            # ('1', '1111'),
            (2.5, 10),
        ],
    )
    def test_setup_attributes(self, model: MainModel, y_changed, expected):
        """测试斑块提取属性"""
        # arrange / act
        module = model.nature.create_module(shape=(2, 2), cell_cls=MockPatchCell)
        for cell in module:
            cell.y = y_changed
        # assert
        assert "x" in module.cell_properties
        assert "y" in module.cell_properties
        assert "x" in module.attributes
        assert "y" in module.attributes
        assert len(module.attributes) == 2
        assert module.get_raster("x").sum() == 4
        assert module.get_raster("y").sum() == expected

    @pytest.mark.parametrize(
        "shape, num",
        [
            ((5, 6), 5),
            ((1, 1), 1),
        ],
    )
    def test_properties(self, model: MainModel, shape, num):
        """测试一个斑块模块"""
        # arrange / act
        module = model.nature.create_module(
            shape=shape,
            cell_cls=MockPatchCell,
        )
        coords = module.coords

        # assert
        assert module.shape2d == shape
        assert module.shape3d == (1, *shape)
        assert module.array_cells.shape == shape
        assert isinstance(module.random.choice(num), (ActorsList, PatchCell))
        assert "x" in coords and "y" in coords
        assert len(coords["x"]) == shape[1]
        assert len(coords["y"]) == shape[0]

    def test_selecting_by_value(self, model: MainModel, module: PatchModule):
        """测试选择斑块"""
        # arrange
        model.agents.new(Actor, singleton=True)
        # act
        cells = module.select("init_value")
        # assert
        assert len(cells) == 3  # init_value = [0, 1, 2, 3]

    @pytest.mark.parametrize(
        "shape, geometry, expected_len, expected_sum",
        [
            ((3, 3), (0.1, 0.1, 2.1, 2.1), 4, 12),
        ],  # 这里box是从左下角到右上角进行选择的
    )
    def test_selecting_by_geometry(
        self, model: MainModel, shape, geometry, expected_len, expected_sum
    ):
        """测试使用地理图形选择斑块"""
        # arrange
        module = model.nature.create_module(shape=shape, resolution=1)
        module.apply_raster(
            np.arange(shape[0] * shape[1]).reshape(module.shape3d),
            attr_name="test",
        )
        # act
        cells = module.select(where=box(*geometry))
        # assert
        assert len(cells) == expected_len
        assert isinstance(cells, ActorsList)
        assert cells.array("test").sum() == expected_sum

    @pytest.mark.parametrize(
        "func_name, attr, data_type, dims",
        [
            ("get_xarray", "test", xarray.DataArray, 2),
            ("get_xarray", None, xarray.DataArray, 3),
            ("get_raster", "test", np.ndarray, 3),
            ("get_raster", None, np.ndarray, 3),
        ],
    )
    def test_get_data(self, module: PatchModule, attr, data_type, func_name, dims):
        """测试获取数据数组"""
        # arrange
        data = np.random.random(module.shape3d)
        module.apply_raster(data, "test")
        # act
        got_data = getattr(module, func_name)(attr)
        # assert
        assert len(got_data.shape) == dims
        assert isinstance(got_data, data_type), f"{type(got_data)}"

    @pytest.mark.parametrize(
        "ufunc, expected",
        [
            (lambda c: c.init_value, np.arange(4)),
            (
                lambda c: c.agents.has(),
                np.array([1, 0, 0, 0]),
            ),
        ],
    )
    def test_apply(
        self,
        module: PatchModule,
        ufunc,
        expected,
        cell_0_0: PatchCell,
    ):
        """Testing"""
        # arrange
        cell_0_0.agents.new(Actor, singleton=True)
        # act
        result = module.apply(ufunc=ufunc)
        # assert
        assert result.shape == module.shape2d
        np.testing.assert_array_equal(result, expected.reshape(module.shape2d))

    def test_copy_layer(self, model, module: PatchModule):
        """测试复制图层"""
        layer2 = model.nature.create_module(source_layer=module, name="test2")
        assert module.shape2d == layer2.shape2d
        assert layer2.name == "test2"


class TestBaseNature:
    """测试基本自然模块"""

    def test_attributes(self, model: MainModel):
        """测试选择主要图层"""
        # arrange
        assert model.nature.is_empty
        # act
        module = model.nature.create_module(shape=(3, 3))
        # assert
        assert model.nature.major_layer is module
        assert model.nature.total_bounds is module.total_bounds
        assert module.name in model.nature.modules
        with pytest.raises(ValueError):
            model.nature.major_layer = "Wrong type"

    def test_module_select(self, model: MainModel):
        """测试创建模块"""
        # arrange
        module2 = model.nature.create_module(
            shape=(10, 10), resolution=1, name="test", major_layer=True
        )
        # act & assert
        assert model.nature.major_layer is module2
        assert model.nature.shape2d == module2.shape2d
        assert model.nature.shape3d == module2.shape3d
        result = model.nature.indices_out_of_bounds((3, 3))
        result2 = module2.indices_out_of_bounds((3, 3))
        assert result == result2

    @pytest.mark.parametrize(
        "row, col",
        [
            (53, 156),
            (97, 56),
            (78, 115),
            (67, 87),
            (64, 73),
        ],
    )
    def test_transform(self, model: MainModel, farmland_data, row, col):
        """Test transform point coords."""
        # arrange
        module = model.nature.create_module(raster_file=farmland_data)
        xda = rxr.open_rasterio(farmland_data)
        # act
        x1, y1 = xda.rio.transform() * (col, row)
        x = module.coords["x"][col].item()
        y = module.coords["y"][row].item()
        # assert
        assert np.isclose(x, x1, rtol=1e-2), f"{x}: {x1}"
        assert np.isclose(y, y1, rtol=1e-2), f"{y}: {y1}"


class MockModule(PatchModule):
    """用于测试"""


class MockCell(PatchCell):
    """用于测试"""


class TestCreatingNewPatch:
    """测试创建新斑块"""

    @pytest.mark.parametrize(
        "module_cls, cell_cls",
        [
            (PatchModule, PatchCell),
            (MockModule, MockCell),
        ],
    )
    def test_setup_layer(
        self,
        model: MainModel,
        module_cls,
        cell_cls,
    ) -> PatchModule:
        """创建一个新的斑块"""
        # arrange / act
        layer = model.nature.create_module(
            shape=(10, 10),
            resolution=1,
            module_cls=module_cls,
            name="testing",
            cell_cls=cell_cls,
        )
        # assert
        assert layer.name == "testing"
        assert issubclass(module_cls, PatchModule)
        assert issubclass(layer.cell_cls, cell_cls)
        assert isinstance(layer.cells_lst.random.choice(), cell_cls)
        assert isinstance(layer, module_cls)


class TestPatchModuleIndexing:
    """Test the __getitem__ method of PatchModule.

    This test class covers various indexing patterns:
    - Single cell indexing
    - Column/row selection
    - Subregion selection
    - Full array selection
    - Edge cases and error handling
    """

    @pytest.fixture(name="large_module")
    def create_large_module(self, model: MainModel) -> PatchModule:
        """Create a larger module (5x5) for testing various indexing patterns."""
        return model.nature.create_module(shape=(5, 5), resolution=1, name="large_test")

    @pytest.mark.parametrize(
        "key, expected_length",
        [
            # Single cell
            ((0, 0), 1),
            ((2, 3), 1),
            ((4, 4), 1),
            # First column (all rows, column 0)
            ((slice(None), 0), 5),
            # Last column (all rows, column 4)
            ((slice(None), 4), 5),
            # First row (row 0, all columns)
            ((0, slice(None)), 5),
            # Last row (row 4, all columns)
            ((4, slice(None)), 5),
            # Subregion (rows 1-3, columns 2-4)
            ((slice(1, 4), slice(2, 5)), 9),
            # All cells
            ((slice(None), slice(None)), 25),
        ],
    )
    def test_getitem_returns_actorslist(
        self, large_module: PatchModule, key: tuple, expected_length: int
    ) -> None:
        """Test that __getitem__ returns ActorsList with correct length.

        Scenarios tested:
            - Single cell returns ActorsList with 1 element
            - Column/row selection returns appropriate number of cells
            - Subregion selection returns correct subset
            - Full array returns all cells

        Args:
            large_module: A 5x5 grid module for testing
            key: Index or slice tuple to test
            expected_length: Expected number of cells in the result
        """
        # act
        result = large_module[key]

        # assert
        assert isinstance(result, ActorsList)
        assert len(result) == expected_length
        for cell in result:
            assert isinstance(cell, PatchCell)

    @pytest.mark.parametrize(
        "key",
        [
            (0, 0),
            (2, 2),
            (4, 4),
        ],
    )
    def test_single_cell_indexing(self, large_module: PatchModule, key: tuple) -> None:
        """Test indexing a single cell returns ActorsList with one element.

        Scenarios:
            - Accessing cells at different positions
            - Verifying the single cell is the correct one

        Args:
            large_module: A 5x5 grid module for testing
            key: Tuple of (row, col) to index
        """
        # act
        result = large_module[key]

        # assert
        assert len(result) == 1
        cell = result[0]
        assert cell.indices == key

    def test_single_cell_access_and_operations(self, large_module: PatchModule) -> None:
        """Test that single cell access supports batch operations.

        Scenario:
            Access a single cell and verify it can be used in batch operations
            like shuffle_do or trigger.

        Args:
            large_module: A 5x5 grid module for testing
        """
        # Setup: Add a custom method to PatchCell for testing
        original_step = PatchCell.step if hasattr(PatchCell, "step") else None

        def mock_step(self):
            self._test_called = True

        PatchCell.step = mock_step

        try:
            # act
            cell_list = large_module[0, 0]

            # Assert: Can call shuffle_do on single cell
            cell_list.shuffle_do("step")
            assert cell_list[0]._test_called

        finally:
            # Cleanup
            if original_step:
                PatchCell.step = original_step

    @pytest.mark.parametrize(
        "col_index",
        [0, 1, 2, 3, 4],
    )
    def test_column_selection(self, large_module: PatchModule, col_index: int) -> None:
        """Test selecting entire column returns all cells in that column.

        Scenarios:
            - Select first column (index 0)
            - Select middle column (index 2)
            - Select last column (index 4)

        Args:
            large_module: A 5x5 grid module for testing
            col_index: Column index to select
        """
        # act
        column = large_module[:, col_index]

        # assert
        assert len(column) == 5
        for i, cell in enumerate(column):
            # Check that cells are in the same column
            assert cell.indices[1] == col_index

    @pytest.mark.parametrize(
        "row_start, row_end, col_start, col_end, expected_count",
        [
            (1, 3, 1, 3, 4),  # 2x2 subregion
            (0, 2, 0, 2, 4),  # 2x2 starting at origin
            (1, 4, 1, 4, 9),  # 3x3 subregion
        ],
    )
    def test_subregion_selection(
        self,
        large_module: PatchModule,
        row_start: int,
        row_end: int,
        col_start: int,
        col_end: int,
        expected_count: int,
    ) -> None:
        """Test selecting a subregion returns correct subset of cells.

        Scenarios:
            - Select 2x2 region in middle of grid
            - Select 2x2 region at origin
            - Select 3x3 region

        Args:
            large_module: A 5x5 grid module for testing
            row_start: Starting row index (inclusive)
            row_end: Ending row index (exclusive)
            col_start: Starting column index (inclusive)
            col_end: Ending column index (exclusive)
            expected_count: Expected number of cells in result
        """
        # act
        subregion = large_module[row_start:row_end, col_start:col_end]

        # assert
        assert len(subregion) == expected_count
        for cell in subregion:
            # Check all cells are within the subregion bounds
            row, col = cell.indices
            assert row_start <= row < row_end
            assert col_start <= col < col_end

    def test_full_array_selection(self, large_module: PatchModule) -> None:
        """Test selecting all cells returns complete ActorsList.

        Scenario:
            Access all cells using [:,:] returns all 25 cells.

        Args:
            large_module: A 5x5 grid module for testing
        """
        # act
        all_cells = large_module[:, :]

        # assert
        assert len(all_cells) == 25
        assert len(all_cells) == large_module.width * large_module.height

    def test_indexing_supports_batch_operations(
        self, large_module: PatchModule
    ) -> None:
        """Test that indexed selection can be used with batch operations.

        Scenarios:
            - Select first column and call shuffle_do
            - Verify all cells in column are processed

        Args:
            large_module: A 5x5 grid module for testing
        """
        # Setup: Add test attribute to track calls
        for cell in large_module.cells_lst:
            cell._test_called = False

        # act
        first_column = large_module[:, 0]
        first_column.trigger(lambda c: setattr(c, "_test_called", True))

        # assert
        for cell in first_column:
            assert cell._test_called

    @pytest.mark.parametrize(
        "key, operation",
        [
            (slice(None, None), "shuffle_do"),
            (slice(None, None), "trigger"),
        ],
    )
    def test_indexing_chainable_operations(
        self, large_module: PatchModule, key: slice, operation: str
    ) -> None:
        """Test that indexed selection can be chained with operations.

        Scenarios:
            - Select cells and call shuffle_do
            - Select cells and call trigger

        Args:
            large_module: A 5x5 grid module for testing
            key: Slice to select cells
            operation: Operation to test ('shuffle_do' or 'trigger')
        """
        # Setup
        for cell in large_module.cells_lst:
            cell._test_attr = 0

        # act
        selected = large_module[key]
        getattr(selected, operation)(lambda c: setattr(c, "_test_attr", 1))

        # assert
        for cell in selected:
            assert cell._test_attr == 1

    def test_indexing_with_real_world_example(self, model: MainModel) -> None:
        """Test __getitem__ with a real-world fire spread example.

        Scenario:
            Simulate the fire spread model's usage:
            1. Select leftmost column
            2. Call batch operation on selected cells
            3. Verify operation succeeds

        Args:
            model: A MainModel instance for testing
        """
        # arrange: Create a grid like in fire_spread model
        grid = model.nature.create_module(shape=(5, 5), cell_cls=PatchCell)

        # act: Use __getitem__ to select leftmost column
        leftmost_column = grid[:, 0]

        # assert
        assert isinstance(leftmost_column, ActorsList)
        assert len(leftmost_column) == 5

        # Verify can perform batch operations
        leftmost_column.shuffle_do(lambda c: c)

    @pytest.mark.parametrize(
        "shape",
        [
            (1, 1),  # Minimum size
            (3, 3),  # Small grid
            (10, 10),  # Medium grid
        ],
    )
    def test_indexing_on_various_grid_sizes(
        self, model: MainModel, shape: tuple[int, int]
    ) -> None:
        """Test __getitem__ works on grids of various sizes.

        Scenarios:
            - Works on 1x1 grid
            - Works on 3x3 grid
            - Works on 10x10 grid

        Args:
            model: A MainModel instance for testing
            shape: Grid shape to test (height, width)
        """
        # arrange
        grid = model.nature.create_module(shape=shape, cell_cls=PatchCell)

        # act: Test full selection
        all_cells = grid[:, :]

        # assert
        assert isinstance(all_cells, ActorsList)
        assert len(all_cells) == shape[0] * shape[1]
