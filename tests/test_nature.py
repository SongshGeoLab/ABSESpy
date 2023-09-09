#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

import geopandas as gpd
import numpy as np
import pytest
from shapely.geometry import Point, box

from abses.actor import Actor
from abses.main import MainModel
from abses.nature import PatchCell, PatchModule


class MockActor:
    def __init__(self, geometry=None):
        self.geometry = geometry
        self.test = 1


def test_patch_cell_attachment():
    """测试斑块可以连接到一个主体"""
    cell = PatchCell()
    actor = MockActor()
    cell.link_to(actor, "actor_1")

    assert "actor_1" in cell.links
    assert len(cell.links) == 1
    assert cell.linked("actor_1") == actor

    with pytest.raises(KeyError):
        cell.link_to(actor, "actor_1")

    cell.detach("actor_1")
    assert "actor_1" not in cell.links

    with pytest.raises(KeyError):
        cell.detach("actor_1")


def test_patch_module_properties():
    """测试一个斑块模块"""
    model = MainModel()
    shape = (6, 5)
    patch_module = PatchModule.from_resolution(model, shape=shape)

    assert patch_module.shape2d == shape
    assert patch_module.shape3d == (1, *shape)
    assert patch_module.array_cells.shape == shape
    assert isinstance(patch_module.random_positions(5), np.ndarray)
    coords = patch_module.coords
    assert "x" in coords and "y" in coords
    assert len(coords["x"]) == 5 and len(coords["y"]) == 6

    actor = MockActor()
    patch_module.land_allotment(
        agent=actor, link="land", where=np.ones(shape, dtype=bool)
    )
    assert np.all(patch_module.has_agent() == 1)


@pytest.fixture(name="raster_layer")
def simple_raster_layer() -> PatchModule:
    """测试一个斑块模块"""
    # Sample setup for RasterLayer (you may need to adjust based on your setup)
    model = MainModel()
    width, height = 10, 10
    layer = PatchModule.from_resolution(model=model, shape=(width, height))
    data = np.random.rand(1, height, width)
    layer.apply_raster(data, "test_1")
    return layer


def test_get_dataarray(raster_layer: PatchModule):
    """测试获取数据数组"""
    data = np.random.random(raster_layer.shape3d)
    raster_layer.apply_raster(data, "test_2")
    data = np.random.random(raster_layer.shape3d)
    raster_layer.apply_raster(data, "test_3")
    dataarray_2d = raster_layer.get_xarray("test_2")
    assert dataarray_2d.shape == raster_layer.shape2d
    dataarray_3d = raster_layer.get_xarray()
    assert dataarray_3d.shape == (3, *raster_layer.shape2d)


def test_geometric_cells(raster_layer):
    """测试几何搜索"""
    # Define a geometry (for this example, a box)
    geom = box(2, 2, 8, 8)

    # Get cells intersecting with the geometry
    cells = raster_layer.geometric_cells(geom)

    # Check if each cell's position is within the geometry
    for cell in cells:
        x, y = cell.pos
        assert geom.contains(
            box(x, y, x + 1, y + 1)
        ), f"Cell at {x}, {y} is not within the geometry!"


@pytest.fixture(name="linked_raster_layer")
def simple_linked_raster_layer(raster_layer):
    """测试每一个斑块可以连接到一个主体"""
    # Define a polygon (for this example, a box)
    geom = box(2, 2, 8, 8)
    agent = MockActor(geom)
    raster_layer.link_by_geometry(agent, "link")
    return agent, raster_layer


def test_link_by_geometry(linked_raster_layer):
    """测试每一个斑块可以连接到一个主体"""
    agent, raster_layer = linked_raster_layer
    linked_cells = sum(
        agent is cell.linked("link")
        for cell in raster_layer.array_cells.flatten()
    )
    assert linked_cells > 0, "No cells were linked to the agent!"


def test_batch_link_by_geometry(raster_layer):
    """测试批量将一些斑块连接到某个主体"""
    agents = [MockActor(box(2, 2, 4, 4)), MockActor(box(6, 6, 8, 8))]

    raster_layer.batch_link_by_geometry(agents, "link")

    agents_wrong = [MockActor(box(2, 2, 7, 7)), MockActor(box(6, 6, 8, 8))]
    with pytest.raises(KeyError):
        # 斑块6～7之间将被重复链接，这是不允许的
        raster_layer.batch_link_by_geometry(agents_wrong, "link")


def test_read_attrs_from_linked_agent(linked_raster_layer):
    """测试从相连接的主体中读取属性"""
    _, raster_layer = linked_raster_layer
    array = raster_layer.linked_attr("test", link="link")
    assert isinstance(array, np.ndarray)
    assert array.shape == raster_layer.shape2d
    assert np.nansum(array) == 36

    # 测试某个主体是否被正确链接并读取
    linked_cell = raster_layer.array_cells[4][4]
    not_linked_cell = raster_layer.array_cells[1][1]

    assert linked_cell.linked_attr("test") == 1
    with pytest.raises(KeyError):
        not_linked_cell.linked_attr("test")

    with pytest.raises(AttributeError):
        linked_cell.linked_attr("not_a_attr")


def test_major_layer(raster_layer):
    """测试选择主要图层"""
    layer = raster_layer
    model = layer.model
    assert model.nature.total_bounds is None
    model.nature.major_layer = layer
    assert model.nature.total_bounds is layer.total_bounds


def test_create_agents_from_gdf():
    """测试从GeoDataFrame创建主体"""
    # Step 1: Create a sample geopandas.GeoDataFrame with some dummy data
    data = {
        "name": ["agent_1", "agent_2", "agent_3"],
        "age": [25, 30, 35],
        "geometry": [Point(0, 0), Point(1, 1), Point(2, 2)],
    }
    gdf = gpd.GeoDataFrame(data, crs="epsg:4326")

    # Initialize BaseNature instance
    model = MainModel()
    nature = model.nature

    # Step 2: Use the create_agents_from_gdf method
    agents = nature.create_agents_from_gdf(
        gdf, unique_id="name", agent_cls=Actor
    )

    # Step 3: Assert number of created agents
    assert len(agents) == len(gdf)

    # Step 4: Check each agent's attributes and geometry
    for idx, agent in enumerate(agents):
        assert agent.unique_id == gdf.iloc[idx]["name"]
        assert agent.age == gdf.iloc[idx]["age"]
        assert agent.geometry == gdf.iloc[idx]["geometry"]
