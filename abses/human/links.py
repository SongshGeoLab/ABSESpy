#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""Actor, PatchCell can be used to create links."""

from __future__ import annotations

import contextlib
from abc import abstractmethod
from functools import cached_property
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Set,
    Tuple,
    Union,
    overload,
)

import numpy as np
import pandas as pd
from loguru import logger

with contextlib.suppress(ImportError):
    import networkx as nx

from abses.agents.sequences import ActorsList
from abses.utils.errors import ABSESpyError
from abses.utils.func import make_list

if TYPE_CHECKING:
    from abses import MainModel
    from abses.agents.actor import Actor
    from abses.core.protocols import LinkContainerProtocol
    from abses.core.types import Direction, LinkingNode, TargetName, UniqueID


def get_node_unique_id(node: Any) -> UniqueID:
    """Gets a unique ID for a node when importing actors from graph.

    Args:
        node: The node to get unique ID for.

    Returns:
        str or int: The unique ID for the node.

    Raises:
        Warning: If using repr() for non-string/int node types.
    """
    if not isinstance(node, (str, int)):
        logger.warning(f"Using repr for '{type(node)}' unique ID to create actor.")
        return repr(node)
    return node


class _LinkContainer:
    """容器类，用于管理节点之间的链接。

    使用唯一 ID 作为键来存储链接，提高检索效率。

    Attributes:
        _back_links: 存储入向链接的字典。
        _links: 存储出向链接的字典。
        _cached_networks: 存储缓存的网络图的字典。
        _node_cache: 存储节点对象的缓存，以便通过 ID 快速检索。
    """

    def __init__(self, model=None) -> None:
        self._back_links: Dict[str, Dict[UniqueID, Set[UniqueID]]] = {}
        self._links: Dict[str, Dict[UniqueID, Set[UniqueID]]] = {}
        self._cached_networks: Dict[str, object] = {}
        self._node_cache: Dict[UniqueID, LinkingNode] = {}

    def _cache_node(self, node: LinkingNode) -> UniqueID:
        """缓存节点并返回其唯一 ID。"""
        node_id = node.unique_id
        self._node_cache[node_id] = node
        return node_id

    def _get_node(self, node_id: UniqueID) -> LinkingNode:
        """从缓存中获取节点。"""
        return self._node_cache[node_id]

    @property
    def links(self) -> Tuple[str, ...]:
        """获取特定类型的链接。"""
        return tuple(self._links.keys())

    def _add_a_link_name(self, link_name: str) -> None:
        """添加一个链接类型。"""
        self._links[link_name] = {}
        self._back_links[link_name] = {}

    def owns_links(
        self, node: LinkingNode, direction: Direction = "out"
    ) -> Tuple[str, ...]:
        """获取特定节点参与的所有链接类型。

        Args:
            node: 要检查链接的节点。
            direction: 要检查的链接方向:
                - "out": 出向链接
                - "in": 入向链接
                - None: 两个方向

        Returns:
            链接类型名称的元组。

        Raises:
            ValueError: 如果方向无效。
        """
        node_id = node.unique_id
        if direction == "out":
            data = self._links
        elif direction == "in":
            data = self._back_links
        elif direction is None:
            links_in = self.owns_links(node, direction="in")
            links_out = self.owns_links(node, direction="out")
            return tuple(set(links_in) | set(links_out))
        else:
            raise ValueError(f"Invalid direction '{direction}'.")
        links = {link for link, agents in data.items() if node_id in agents}
        return tuple(links)

    @overload
    def get_graph(self, link_name: str, directions: bool = False) -> "nx.Graph": ...

    @overload
    def get_graph(self, link_name: str, directions: bool = True) -> "nx.DiGraph": ...

    def get_graph(
        self, link_name: str, directions: bool = False
    ) -> "nx.Graph | nx.DiGraph":
        """将指定类型的链接转换为 networkx 图。

        Args:
            link_name: 要转换的链接类型。
            directions: 如果为 True，返回有向图。如果为 False，返回无向图。

        Returns:
            networkx Graph 或 DiGraph 对象。

        Raises:
            ImportError: 如果未安装 networkx。
        """
        if "nx" not in globals():
            raise ImportError("You need to install networkx to use this function.")
        creating_using = nx.DiGraph if directions else nx.Graph

        # 将 ID 映射回节点对象
        links_dict = {}
        for source_id, target_ids in self._links[link_name].items():
            source_node = self._get_node(source_id)
            links_dict[source_node] = {
                self._get_node(target_id) for target_id in target_ids
            }

        graph = nx.from_dict_of_lists(links_dict, creating_using)
        self._cached_networks[link_name] = graph
        return graph

    def _register_link(
        self, link_name: str, source: LinkingNode, target: LinkingNode
    ) -> None:
        """注册一个链接。"""
        source_id = self._cache_node(source)
        target_id = self._cache_node(target)

        if link_name not in self._links:
            self._add_a_link_name(link_name)
        if source_id not in self._links[link_name]:
            self._links[link_name][source_id] = set()
        if target_id not in self._back_links[link_name]:
            self._back_links[link_name][target_id] = set()

    def has_link(
        self, link_name: str, source: LinkingNode, target: LinkingNode
    ) -> Tuple[bool, bool]:
        """检查源节点和目标节点之间是否存在链接。

        Args:
            link_name: 要检查的链接类型。
            source: 源节点。
            target: 目标节点。

        Returns:
            (has_outgoing, has_incoming) 布尔值的元组，其中:
                - has_outgoing: 如果从源到目标存在链接，则为 True
                - has_incoming: 如果从目标到源存在链接，则为 True

        Raises:
            KeyError: 如果 link_name 不存在。
        """
        if link_name not in self.links:
            raise KeyError(f"No link named {link_name}.")

        source_id = source.unique_id
        target_id = target.unique_id

        data = self._links[link_name]
        to = False if source_id not in data else target_id in data.get(source_id, [])
        by = False if target_id not in data else source_id in data.get(target_id, [])
        return to, by

    def add_a_link(
        self,
        link_name: str,
        source: LinkingNode,
        target: LinkingNode,
        mutual: bool = False,
    ) -> None:
        """在节点之间创建新链接。

        Args:
            link_name: 要创建的链接类型。
            source: 源节点。
            target: 目标节点。
            mutual: 如果为 True，则在两个方向上创建链接。
        """
        self._register_link(link_name, source, target)

        source_id = source.unique_id
        target_id = target.unique_id

        self._links[link_name][source_id].add(target_id)
        self._back_links[link_name][target_id].add(source_id)
        if mutual:
            self.add_a_link(link_name, target=source, source=target, mutual=False)

    def remove_a_link(
        self,
        link_name: str,
        source: LinkingNode,
        target: LinkingNode,
        mutual: bool = False,
    ) -> None:
        """移除特定链接。

        Parameters:
            link_name:
                链接的名称。
            source:
                源节点。
            target:
                目标节点。
            mutual:
                是否互相删除链接。

        Raises:
            ABSESpyError:
                如果从源到目标的链接不存在。
        """
        if not self.has_link(link_name, source, target)[0]:
            raise ABSESpyError(f"Link from {source} to {target} not found.")

        source_id = source.unique_id
        target_id = target.unique_id

        self._links[link_name].get(source_id, set()).remove(target_id)
        self._back_links[link_name].get(target_id, set()).remove(source_id)
        if mutual:
            self.remove_a_link(link_name, target=source, source=target, mutual=False)

    def _clean_link_name(self, link_name: Optional[str | Iterable[str]]) -> List[str]:
        """清理链接名称。"""
        if link_name is None:
            link_name = self.links
        if isinstance(link_name, str):
            link_name = [link_name]
        if not isinstance(link_name, Iterable):
            raise TypeError(f"{link_name} is not an iterable.")
        return list(link_name)

    def clean_links_of(
        self,
        node: LinkingNode,
        link_name: Optional[str] = None,
        direction: Direction = None,
    ) -> None:
        """移除与节点关联的所有链接。

        Args:
            node: 要清理链接的节点。
            link_name: 要清理的链接类型。如果为 None，则清理所有类型。
            direction: 要清理的链接方向:
                - "in": 入向链接
                - "out": 出向链接
                - None: 两个方向

        Raises:
            ValueError: 如果方向无效。
        """
        node_id = node.unique_id

        if direction == "in":
            data = self._back_links
            another_data = self._links
        elif direction == "out":
            data = self._links
            another_data = self._back_links
        elif direction is None:
            self.clean_links_of(node, link_name, direction="in")
            self.clean_links_of(node, link_name, direction="out")
            return
        else:
            raise ValueError(
                f"Invalid direction {direction}, please choose from 'in' or 'out'."
            )
        for name in self._clean_link_name(link_name):
            to_clean = data[name].pop(node_id, set())
            for another_node_id in to_clean:
                another_data[name][another_node_id].remove(node_id)

    def linked(
        self,
        node: LinkingNode,
        link_name: Optional[str] = None,
        direction: Direction = None,
        default: Any = ...,
    ) -> Set[LinkingNode]:
        """获取链接的节点。

        Parameters:
            node:
                要获取链接节点的节点。
            link_name:
                链接的名称。
                如果为 None，则获取所有类型的链接。
            direction:
                链接的方向（'in' 或 'out'）。

        Raises:
            ValueError:
                如果方向不是 'in' 或 'out'。

        Returns:
            与输入节点链接的 Actors 或 PatchCells。
        """
        node_id = node.unique_id
        link_names = self._clean_link_name(link_name=link_name)

        if direction == "in":
            data = self._back_links
        elif direction == "out":
            data = self._links
        elif direction is None:
            in_links = self.linked(node, link_name, direction="in")
            out_links = self.linked(node, link_name, direction="out")
            return in_links | out_links
        else:
            raise ValueError(f"Invalid direction {direction}")

        linked_ids: Set[UniqueID] = set()
        for name in link_names:
            if name not in data and default is not ...:
                continue
            linked_ids = linked_ids.union(data[name].get(node_id, set()))

        # 将 ID 转换回节点对象
        return {self._get_node(node_id) for node_id in linked_ids}

    def _check_is_node(
        self,
        node: UniqueID | LinkingNode,
        mapping_dict: Optional[Dict[UniqueID, Actor]] = None,
    ) -> LinkingNode:
        if mapping_dict:
            unique_id = get_node_unique_id(node)
            node = mapping_dict[unique_id]
        if not isinstance(node, _LinkNode):
            raise TypeError(f"Invalid node type {type(node)}, mapping: {mapping_dict}.")
        return node

    def add_links_from_graph(
        self,
        graph: "nx.Graph",
        link_name: str,
        mapping_dict: Optional[Dict[UniqueID, Actor]] = None,
        mutual: Optional[bool] = None,
    ) -> None:
        """从图中添加链接。"""
        if mutual is None:
            mutual = not isinstance(graph, nx.DiGraph)
        if mapping_dict is None:
            mapping_dict = {}
        edges = 0
        for source, targets in nx.to_dict_of_lists(graph).items():
            source = self._check_is_node(source, mapping_dict)
            for target in targets:
                target = self._check_is_node(target, mapping_dict)
                self.add_a_link(link_name, source, target, mutual=mutual)
                edges += 1
        logger.info(f"Imported links {edges} links from graph {graph}.")


class _LinkProxy:
    """用于管理节点上链接的代理类。

    提供创建、检查和移除链接的便捷方法。

    使用节点的唯一 ID 来优化链接操作。

    Attributes:
        node: 此代理管理链接的节点。
        model: 主模型实例。
        human: 链接容器实例。
    """

    def __init__(self, node: _LinkNode, model: MainModel) -> None:
        self.node: _LinkNode = node
        self.model: MainModel = model
        self.human: LinkContainerProtocol = model.human
        # 确保节点已缓存
        self.human._cache_node(node)

    def __contains__(self, link_name: str) -> bool:
        """检查链接是否存在。"""
        return link_name in self.human.links

    def __eq__(self, __value: object) -> bool:
        """检查链接是否等于一组字符串。"""
        if not isinstance(__value, Iterable):
            return NotImplemented
        return set(__value) == set(self.owning())

    def __repr__(self) -> str:
        return str(self.owning())

    def owning(self, direction: Direction = None) -> Tuple[str, ...]:
        """此对象拥有的链接。

        Parameters:
            direction:
                链接的方向（'in' 或 'out'）。
                如果为 None，则返回出向链接和入向链接。

        Returns:
            此对象拥有的链接。
        """
        return self.human.owns_links(self.node, direction=direction)

    def get(
        self,
        link_name: Optional[Union[str, List[str]]] = None,
        direction: Optional[str] = None,
        default: Any = ...,
    ) -> ActorsList:
        """获取链接的节点。

        Args:
            link_name: 要获取的链接类型。如果为 None，则获取所有类型。
            direction: 要获取的链接方向:
                - "out": 出向链接
                - "in": 入向链接
                - None: 两个方向
            default: 如果未找到链接类型，则返回的值。

        Returns:
            链接节点的列表。
        """
        agents = self.human.linked(
            self.node, link_name, direction=direction, default=default
        )

        # 确保agents是可迭代的
        if hasattr(agents, "__iter__"):
            return ActorsList(self.model, agents)
        else:
            # 如果是Mock对象或其他不可迭代对象，返回空列表
            return ActorsList(self.model, [])

    def has(
        self, link_name: str, node: Optional[LinkingNode] = None
    ) -> Tuple[bool, bool]:
        """检查当前节点是否有特定类型的链接，或者是否与另一个节点有链接。

        Parameters:
            link_name:
                要检查的链接类型。
            node:
                要检查是否与当前节点有链接的节点。
                如果为 None，则检查当前节点是否有任何链接。

        Returns:
            tuple:
                两个布尔值的元组。
                如果从我到其他存在链接，则第一个元素为 True。
                如果从其他到我存在链接，则第二个元素为 True。
        """
        if node is None:
            try:
                has_in = link_name in self.owning("in")
                has_out = link_name in self.owning("out")
            except TypeError:
                # 如果owning返回的不是可迭代对象，则假设没有链接
                has_in = False
                has_out = False
            return has_out, has_in

        # 直接调用human.has_link并确保返回元组
        result = self.human.has_link(link_name, self.node, node)
        # 如果结果不是元组，则创建一个默认元组
        if not isinstance(result, tuple):
            return (False, False)
        return result

    def to(self, node: LinkingNode, link_name: str, mutual: bool = False) -> None:
        """创建到另一个节点的出向链接。

        Args:
            node: 要链接到的目标节点。
            link_name: 要创建的链接类型。
            mutual: 如果为 True，则在两个方向上创建链接。
        """
        self.human.add_a_link(
            link_name=link_name, source=self.node, target=node, mutual=mutual
        )

    def by(self, node: LinkingNode, link_name: str, mutual: bool = False) -> None:
        """使此节点被另一个节点链接。

        Parameters:
            node:
                要链接的节点。
            link_name:
                链接的名称。
            mutual:
                链接是否是互相的。默认为 False。
        """
        self.human.add_a_link(
            link_name=link_name, source=node, target=self.node, mutual=mutual
        )

    def unlink(self, node: LinkingNode, link_name: str, mutual: bool = False):
        """移除我和另一个节点之间的链接。

        Parameters:
            node:
                要解除链接的节点。
            link_name:
                链接的名称。
            mutual:
                是否互相删除链接。默认为 False。

        Raises:
            ABSESpyError:
                如果从源到目标的链接不存在。
        """
        # 检查链接是否存在
        has_in, has_out = self.has(link_name, node)
        if not has_in and not has_out:
            from abses.utils.errors import ABSESpyError

            raise ABSESpyError(
                f"Link '{link_name}' between {self.node} and {node} not found."
            )

        self.human.remove_a_link(
            link_name=link_name, source=self.node, target=node, mutual=mutual
        )

    def clean(self, link_name: Optional[str] = None, direction: Direction = None):
        """清理此节点的所有相关链接。

        Parameters:
            link_name:
                链接的名称。
                如果为 None，则清理节点的所有相关链接。
            direction:
                链接的方向（'in' 或 'out'）。
                如果为 None，则清理两个方向（出向链接和入向链接）。

        Raises:
            ValueError:
                如果方向不是 'in' 或 'out'。
        """
        self.human.clean_links_of(self.node, link_name=link_name, direction=direction)


class _BreedDescriptor:
    """A descriptor to get the breed of a node."""

    def __get__(self, _: Any, owner: Any) -> str:
        return owner.__name__ if owner else self.__class__.__name__


class _LinkNode:
    """可链接节点的基类。

    提供管理节点之间属性和链接的核心功能。

    使用唯一 ID 来优化链接的检索和管理。

    Attributes:
        unique_id: 节点的唯一标识符。
        breed: 节点的品种/类型。
        link: 管理链接的代理。
    """

    unique_id: UniqueID = -1
    breed = _BreedDescriptor()

    @abstractmethod
    def _target_is_me(self, target: Optional[TargetName]) -> bool:
        """检查目标是否是我自己。"""

    @classmethod
    def viz_attrs(cls, **kwargs) -> Dict[str, Any]:
        """返回用于可视化的属性。"""
        maker = getattr(cls, "marker", "o")
        return {
            "marker": maker,
            "color": getattr(cls, "color", "black"),
            "alpha": getattr(cls, "alpha", 1.0),
        } | kwargs

    @cached_property
    def link(self) -> _LinkProxy:
        """用于操作链接的代理：

        1. `link.to()`: 创建从此 actor 到另一个的新链接。
        2. `link.by()`: 创建从另一个到此 actor 的新链接。
        3. `link.get()`: 获取此 actor 的链接。
        4. `link.has()`: 检查此 actor 和另一个之间是否存在链接。
        5. `link.unlink()`: 移除此 actor 和另一个之间的链接。
        6. `link.clean()`: 移除此 actor 的所有链接。
        """
        return _LinkProxy(self, getattr(self, "model"))

    def has(self, attr: str, raise_error: bool = False) -> bool:
        """检查当前节点中是否存在属性。

        Args:
            attr:
                要检查的属性的名称。
            raise_error:
                如果为 True，则在属性不存在时引发错误。

        Returns:
            bool:
                如果属性存在，则为 True，否则为 False。
        """
        # 如果属性不是字符串，引发错误。
        if not isinstance(attr, str):
            raise TypeError(f"The attribute to check {attr} is not string.")
        if attr.startswith("_"):
            # 受保护的属性
            flag = False
        else:
            flag = hasattr(self, attr)
        if flag:
            return True
        if raise_error:
            raise AttributeError(f"'{self}' doesn't have attribute '{attr}'.")
        return False

    def _redirect(self, target: Optional[TargetName]) -> _LinkNode:
        """重定向目标。

        Args:
            target:
                要重定向到的目标。

        Returns:
            重定向的目标。
        """
        if self._target_is_me(target):
            return self
        if isinstance(target, str) and any(self.link.has(link_name=target)):
            return self.link.get(link_name=target)
        raise ABSESpyError(f"Unknown target {target}.")

    def _setattr(
        self, attr: str, value: Any, target: Optional[TargetName], new: bool = False
    ) -> None:
        """在当前节点上设置属性。"""
        if attr.startswith("_"):
            raise AttributeError(f"Attribute '{attr}' is protected.")
        if new:
            setattr(self, attr, value)
            return
        if not self.has(attr):
            raise AttributeError(
                f"Attribute '{attr}' not found in {self}, please set 'new=True' to create a new attribute."
            )
        if self._target_is_me(target):
            setattr(self, attr, value)
            return
        raise ABSESpyError(
            f"The target '{target}' is not 'self' set when '{self}' already has attr '{attr}'."
        )

    def get(
        self, attr: str, target: Optional[TargetName] = None, default: Any = ...
    ) -> Any:
        """从此节点或目标获取属性值。

        Args:
            attr: 要获取的属性名称。
            target: 从哪里获取属性：
                - None: 首先尝试自己，然后是默认目标
                - "self": 仅从此节点获取
                - 其他目标: 从链接的目标获取
            default: 如果未找到属性，则返回的值。

        Returns:
            属性值。

        Raises:
            AttributeError: 如果未找到属性且未提供默认值。
        """
        if self._target_is_me(target):
            if default is ...:
                return getattr(self, attr)
            return getattr(self, attr, default)
        if target is not None:
            target_obj = self._redirect(target=target)
            return target_obj.get(attr, target="self", default=default)
        if self.has(attr, raise_error=False):
            return getattr(self, attr)
        if default is not ...:
            return default
        target_obj = self._redirect(target=target)
        try:
            return target_obj.get(attr=attr, target="self", default=default)
        except AttributeError as exc:
            raise AttributeError(
                f"Neither {self} nor {target_obj} has attribute {attr}."
            ) from exc

    def set(
        self,
        attr: str,
        value: Any,
        target: Optional[TargetName] = None,
        new: bool = False,
    ) -> None:
        """在此节点或目标上设置属性值。

        Args:
            attr: 要设置的属性名称。
            value: 要设置的值。
            target: 在哪里设置属性：
                - None: 首先尝试自己，然后是默认目标
                - "self": 仅在此节点上设置
                - 其他目标: 在链接的目标上设置
            new: 如果为 True，允许创建新属性。

        Raises:
            AttributeError: 如果属性不存在且 new=False。
            TypeError: 如果 attr 不是字符串。
            ABSESpyError: 如果目标无效或属性受保护。
        """
        if self._target_is_me(target):
            self._setattr(attr, value, target="self", new=new)
            return
        if target is None and new:
            self._setattr(attr, value, target="self", new=new)
            return
        if target is not None:
            self._redirect(target=target).set(attr, value, target="self", new=new)
            return
        if self.has(attr):
            self._setattr(attr, value, target="self")
            return
        target_obj = self._redirect(target="self")
        if hasattr(target_obj, attr):
            target_obj.set(attr, value, target="self", new=new)
            return
        raise AttributeError(f"Neither {self} nor {target_obj} has attribute '{attr}'.")

    def summary(
        self, coords: bool = False, attrs: Optional[Iterable[str] | str] = None
    ) -> pd.Series:
        """返回对象的摘要。"""
        geo_type = self.get("geo_type")
        if geo_type in ("Point", "Cell"):
            a, b = self.get("coordinate" if coords else "pos")
        else:
            a, b = np.nan, np.nan
        result = {
            "breed": self.breed,
            "geo_type": geo_type,
            "x" if coords else "row": a,
            "y" if coords else "col": b,
        }
        result.update({attr: self.get(attr) for attr in make_list(attrs)})
        return pd.Series(result, name=self.unique_id)


class _LinkNodeCell(_LinkNode):
    """PatchCell"""

    _default_redirect_target = "actor"

    def _target_is_me(self, target: Optional[TargetName]) -> bool:
        """Check if the target is me."""
        return target in ("self", "cell")

    def _redirect(self, target: Optional[TargetName]) -> _LinkNode:
        """By default, redirect to the agents list of this cell."""
        if target == self._default_redirect_target or target is None:
            return self.get("agents", target="self")
        return super()._redirect(target)


class _LinkNodeActor(_LinkNode):
    _default_redirect_target = "cell"

    def _target_is_me(self, target: Optional[TargetName]) -> bool:
        """Check if the target is me."""
        return target in ("self", "actor")

    def _redirect(self, target: Optional[TargetName]) -> _LinkNode:
        """Redirect the target.

        Args:
            target:
                The target to redirect to.

        Returns:
            The redirected target.
        """
        if target == self._default_redirect_target or target is None:
            return self.get("at", target="self")
        return super()._redirect(target)
