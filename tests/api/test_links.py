#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""测试链接"""

from functools import cached_property
from typing import List, Optional, Set
from unittest.mock import Mock

import pytest
from omegaconf import DictConfig

from abses.core.model import MainModel
from abses.core.protocols import ActorProtocol, Observer
from abses.human.links import _LinkContainer, _LinkNode, _LinkProxy
from abses.utils.errors import ABSESpyError


class MockObserver(Observer):
    """模拟观察者"""


class MockNode(_LinkNode, MockObserver):
    """用于测试的节点类

    继承 MockObserver 以满足 Observer 协议
    """

    _next_id = 0  # 类变量，用于生成唯一ID

    def __init__(self, model: MainModel, name: str = "test"):
        self.model = model
        self.name = name
        self._alive = True
        self._links: Set[str] = set()
        # 为每个实例分配唯一ID
        self.unique_id = MockNode._next_id
        MockNode._next_id += 1

    @property
    def alive(self) -> bool:
        return self._alive

    def die(self):
        """模拟死亡"""
        self._alive = False

    def _target_is_me(self, target: Optional[str]) -> bool:
        """检查目标是否是我自己。"""
        return target is None or target == "self"

    @cached_property
    def link(self) -> _LinkProxy:
        """重写link属性，确保使用正确的container"""
        proxy = _LinkProxy(self, self.model)
        # 确保proxy.human是container而不是model.human
        if hasattr(self.model, "human") and isinstance(
            self.model.human, _LinkContainer
        ):
            proxy.human = self.model.human
        return proxy


@pytest.fixture
def mock_model():
    """创建模拟的主模型"""
    model = Mock()
    model.settings = DictConfig({"test": {}})
    return model


@pytest.fixture
def container(mock_model):
    """创建链接容器"""
    container = _LinkContainer(mock_model)
    # 确保model.human指向container
    mock_model.human = container
    return container


@pytest.fixture
def nodes(mock_model) -> List[MockNode]:
    """创建测试节点"""
    return [MockNode(mock_model, f"node_{i}") for i in range(3)]


@pytest.fixture
def tres_nodes(mock_model) -> List[MockNode]:
    """创建三个测试节点"""
    return [MockNode(mock_model, f"node_{i}") for i in range(3)]


class TestLinkContainer:
    """测试链接容器"""

    def test_link_add(self, nodes: List[MockNode], container: _LinkContainer):
        """测试添加链接

        场景：
        1. 添加单向链接
        2. 验证链接存在
        """
        node_1, node_2, _ = nodes
        container.add_a_link("test", node_1, node_2)
        assert "test" in container.links
        assert any(container.has_link("test", node_1, node_2))

    @pytest.mark.parametrize(
        "mutual, expected",
        [
            (True, (False, False)),
            (False, (False, True)),
        ],
    )
    def test_link_delete(
        self,
        nodes: List[MockNode],
        container: _LinkContainer,
        mutual: bool,
        expected: tuple,
    ):
        """测试删除链接

        场景：
        1. 删除互相链接
        2. 删除单向链接
        """
        node_1, node_2, _ = nodes
        container.add_a_link("test", node_1, node_2, mutual=True)
        container.remove_a_link("test", node_1, node_2, mutual=mutual)
        assert container.has_link("test", node_1, node_2) == expected

    @pytest.mark.parametrize(
        "direction, expected",
        [
            ("in", (True, False)),
            ("out", (False, True)),
            (None, (False, False)),
        ],
    )
    def test_clean_links(
        self,
        nodes: List[MockNode],
        container: _LinkContainer,
        direction: str,
        expected: tuple,
    ):
        """测试清理链接

        场景：
        1. 清理入向链接
        2. 清理出向链接
        3. 清理所有链接
        """
        node_1, node_2, _ = nodes
        container.add_a_link("test", node_1, node_2, mutual=True)
        container.clean_links_of(node_1, "test", direction=direction)
        assert container.has_link("test", node_1, node_2) == expected


class TestNetworkx:
    """Test linking nodes into networkx."""

    def test_converting_to_networkx(
        self, tres_nodes: List[ActorProtocol], container: _LinkContainer
    ):
        """Test converting to networkx."""
        # arrange
        node_1, node_2, node_3 = tres_nodes
        container.add_a_link("test", node_1, node_2, mutual=True)
        container.add_a_link("test", node_2, node_3, mutual=True)

        # act
        graph = container.get_graph("test")

        # assert
        assert set(graph.nodes) == set(tres_nodes)
        assert graph.number_of_edges() == 2


class TestLinkProxy:
    """Test linking methods in proxy."""

    @pytest.mark.parametrize(
        "links, mutual, to_or_by, expected",
        [
            (("test", "test1", "test2"), True, "to", (True, True)),
            (("test", "test1", "test2"), False, "to", (True, False)),
            (("test", "test", "test2"), False, "to", (True, False)),
            (("test", "test1", "test1"), True, "to", (True, True)),
            (("test", "test1", "test2"), True, "by", (True, True)),
            (("test", "test1", "test2"), False, "by", (False, True)),
            (("test", "test", "test2"), False, "by", (False, True)),
            (("test", "test1", "test1"), True, "by", (True, True)),
        ],
    )
    def test_link_to_or_by(
        self,
        tres_nodes: List[ActorProtocol],
        links,
        mutual,
        to_or_by,
        container: _LinkContainer,
        expected,
    ):
        """Test linking to"""
        # arrange
        a1, a2, a3 = tres_nodes
        link1, link2, link3 = links

        # act
        getattr(a1.link, to_or_by)(a2, link1, mutual=mutual)
        getattr(a1.link, to_or_by)(a3, link2, mutual=mutual)
        getattr(a2.link, to_or_by)(a3, link3, mutual=mutual)

        # assert
        assert a1.link == {link1, link2}
        assert a2.link == {link1, link3}
        assert a3.link == {link2, link3}
        assert set(container.links) == {link1, link2, link3}
        assert container.has_link(link1, a1, a2) == expected
        assert container.has_link(link2, a1, a3) == expected
        assert container.has_link(link3, a2, a3) == expected

    @pytest.mark.parametrize(
        "mutual, to_or_by, expected",
        [
            (True, "to", (True, True)),
            (False, "to", (True, False)),
            (True, "by", (True, True)),
            (False, "by", (False, True)),
        ],
    )
    def test_has(
        self,
        tres_nodes: List[ActorProtocol],
        mutual,
        to_or_by,
        expected,
        container: _LinkContainer,
    ):
        """Test that if a node has a link, or has link with another node."""
        # arrange
        node1, node2, _ = tres_nodes

        # 确保node1.link.human是container
        if hasattr(node1, "link") and hasattr(node1.link, "human"):
            node1.link.human = container

        getattr(node1.link, to_or_by)(node2, "test", mutual=mutual)
        # act / assert
        assert node1.link.has("test", node2) == expected
        assert node1.link.has("test") == expected

    @pytest.mark.parametrize(
        "to_or_by, mutuals, link_name, direction, expected",
        [
            (("to", "to"), (True, True), "t2", "out", (True, False)),
            (("by", "to"), (False, True), "t2", "out", (False, False)),
            (("by", "to"), (True, True), "t2", "out", (True, False)),
            (("by", "to"), (False, True), "t2", "in", (True, False)),
            (("by", "to"), (False, True), ["t2", "t3"], "in", (True, True)),
            (("by", "to"), (False, True), ["t2", "t3"], "out", (False, True)),
            (("by", "to"), (True, True), ["t2", "t3"], "in", (True, True)),
            (("by", "to"), (True, True), ["t2", "t3"], "out", (True, True)),
        ],
    )
    def test_get_link(
        self,
        tres_nodes: List[ActorProtocol],
        to_or_by,
        mutuals,
        expected,
        link_name,
        direction,
        container: _LinkContainer,
    ):
        """testing get linked actors / cells."""
        # arrange
        node1, node2, node3 = tres_nodes

        # 确保node1.link.human是container
        if hasattr(node1, "link") and hasattr(node1.link, "human"):
            node1.link.human = container

        tob2, tob3 = to_or_by
        m2, m3 = mutuals

        # 添加调试信息
        print("\nDebug info before link calls:")
        print(f"node1.unique_id: {node1.unique_id}")
        print(f"node2.unique_id: {node2.unique_id}")
        print(f"node3.unique_id: {node3.unique_id}")

        getattr(node1.link, tob2)(node2, link_name="t2", mutual=m2)
        getattr(node1.link, tob3)(node3, link_name="t3", mutual=m3)

        # 添加调试信息
        print("\nDebug info after link calls:")
        print(f"node1.link.human._links: {node1.link.human._links}")
        print(f"node1.link.human._back_links: {node1.link.human._back_links}")
        print(f"node1.link.has('t2'): {node1.link.has('t2')}")
        print(f"node1.link.has('t3'): {node1.link.has('t3')}")

        # act
        results = node1.link.get(link_name=link_name, direction=direction)

        # 添加调试信息
        print("\nDebug info after get call:")
        print(f"Results: {results}")

        # assert
        if isinstance(link_name, list):
            assert len(results) == sum(expected)
        else:
            assert len(results) == (1 if any(expected) else 0)

    def test_bad_get(self, tres_nodes: List[ActorProtocol], container: _LinkContainer):
        """Test that the get method raises an error if the link is not found."""
        # arrange
        node1, _, _ = tres_nodes

        # 确保node1.link.human是container
        if hasattr(node1, "link") and hasattr(node1.link, "human"):
            node1.link.human = container

        # act / assert
        with pytest.raises(KeyError, match="test"):
            node1.link.get("test")

    @pytest.mark.parametrize(
        "link_name, direction, expected_2, expected_3",
        [
            ("test2", "in", (True, False), (True, True)),
            ("test2", "out", (False, True), (True, True)),
            ("test2", None, (False, False), (True, True)),
            (["test2", "test3"], "in", (True, False), (True, False)),
            (["test2", "test3"], "out", (False, True), (False, True)),
            (["test2", "test3"], None, (False, False), (False, False)),
            (None, None, (False, False), (False, False)),
        ],
    )
    def test_clean(
        self,
        tres_nodes: List[ActorProtocol],
        link_name,
        direction,
        expected_2,
        expected_3,
        container: _LinkContainer,
    ):
        """testing delete all links."""
        # arrange
        node1, node2, node3 = tres_nodes

        # 确保node1.link.human是container
        if hasattr(node1, "link") and hasattr(node1.link, "human"):
            node1.link.human = container

        # 添加调试信息
        print("\nDebug info before to() calls:")
        print(f"node1.unique_id: {node1.unique_id}")
        print(f"node2.unique_id: {node2.unique_id}")
        print(f"node3.unique_id: {node3.unique_id}")

        node1.link.to(node2, "test2", True)
        node1.link.to(node3, "test3", True)

        # 添加调试信息
        print("\nDebug info after to() calls:")
        print(f"node1.link.human._links: {node1.link.human._links}")
        print(f"node1.link.human._back_links: {node1.link.human._back_links}")
        print(f"node1.link.has('test2'): {node1.link.has('test2')}")
        print(f"node1.link.has('test3'): {node1.link.has('test3')}")

        # act
        node1.link.clean(link_name=link_name, direction=direction)

        # 添加调试信息
        print("\nDebug info after clean() call:")
        print(f"node1.link.human._links: {node1.link.human._links}")
        print(f"node1.link.human._back_links: {node1.link.human._back_links}")
        print(f"node1.link.has('test2'): {node1.link.has('test2')}")
        print(f"node1.link.has('test3'): {node1.link.has('test3')}")

        # assert
        assert node1.link.has("test2") == expected_2
        assert node1.link.has("test3") == expected_3

    @pytest.mark.parametrize(
        "mutual, expected",
        [
            (False, (False, True)),
            (True, (False, False)),
        ],
    )
    def test_unlink(
        self,
        tres_nodes: List[ActorProtocol],
        expected,
        mutual,
        container: _LinkContainer,
    ):
        """testing delete a specific link."""
        # arrange
        node1, node2, node3 = tres_nodes

        # 确保node1.link.human是container
        if hasattr(node1, "link") and hasattr(node1.link, "human"):
            node1.link.human = container

        # 添加调试信息
        print("\nDebug info before to() call:")
        print(f"node1.unique_id: {node1.unique_id}")
        print(f"node2.unique_id: {node2.unique_id}")

        node1.link.to(node2, "test", mutual=True)

        # 添加调试信息
        print("\nDebug info after to() call:")
        print(f"node1.link.human._links: {node1.link.human._links}")
        print(f"node1.link.human._back_links: {node1.link.human._back_links}")
        print(f"node1.link.has('test', node2): {node1.link.has('test', node2)}")

        # act
        node1.link.unlink(node2, "test", mutual=mutual)
        with pytest.raises(ABSESpyError, match="not found."):
            node1.link.unlink(node3, "test", mutual=True)
        # assert
        assert node1.link.has("test", node2) == expected
