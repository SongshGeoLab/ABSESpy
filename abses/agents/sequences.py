#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""ActorsList is a sequence of actors.
It's used to manipulate the actors quickly in batch.
"""

from __future__ import annotations

from collections.abc import Iterable
from numbers import Number
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Sized,
    Union,
    cast,
    overload,
)

import numpy as np
from mesa import Agent
from mesa.agent import AgentSet
from numpy.typing import NDArray

from abses.core.protocols import MainModelProtocol
from abses.core.types import A
from abses.utils.func import get_only_item
from abses.utils.random import ListRandom

if TYPE_CHECKING:
    from abses.core.types import HOW_TO_SELECT


class ActorsList(Generic[A], AgentSet):
    """ActorsList 是 AgentSet 的扩展，专门用于处理 Actor 对象。

    主要特点是在返回值时使用 numpy 数组，并保持与 ABSESpy 其他组件的兼容性。
    尽可能使用 AgentSet 的原生方法，减少自定义实现。
    """

    def __init__(
        self,
        model: MainModelProtocol,
        objs: Iterable[A] = (),
    ) -> None:
        """初始化 ActorsList。"""
        super().__init__(objs, random=model.random)
        self._model = model

    def __repr__(self):
        """返回 ActorsList 的字符串表示。"""
        results = [f"({len(v)}){k}" for k, v in self.to_dict().items()]
        return f"<ActorsList: {'; '.join(results)}>"

    @overload
    def __getitem__(self, other: int) -> A: ...

    @overload
    def __getitem__(self, index: slice) -> ActorsList[A]: ...

    def __getitem__(self, index):
        """获取 ActorsList 中的一个 actor 或一个切片。"""
        results = super().__getitem__(index)
        return ActorsList(self._model, results) if isinstance(index, slice) else results

    def _is_same_length(self, length: Sized, rep_error: bool = False) -> bool:
        """Check if the length of input is as same as the number of actors."""
        if not hasattr(length, "__len__"):
            raise ValueError(f"{type(length)} object is not iterable.")
        if len(length) != len(self):
            if rep_error:
                raise ValueError(
                    f"Length of the input {len(length)} mismatch {len(self)} actors."
                )
        return True

    def to_dict(self) -> Dict[str, ActorsList[A]]:
        """将所有 actor 转换为字典，格式为 {breed: ActorsList}。

        使用 AgentSet 的 groupby 方法按照 breed 属性进行分组，提高效率。

        Returns:
            以 breed 为键，对应的 actors 为值的字典。
        """
        # 使用 groupby 按照 breed 属性分组
        grouped = self.groupby(by="breed")

        # 将分组结果转换为 ActorsList
        return {
            breed: ActorsList(self._model, agents)
            for breed, agents in grouped.groups.items()
        }

    def select(
        self,
        filter_func: Callable[[A], bool] | None = None,
        at_most: int | float = float("inf"),
        inplace: bool = False,
        agent_type: Agent | None = None,
    ) -> AgentSet:
        """
        Selects elements from the sequence based on a filter function.

        Args:
            filter_func:
                A callable that takes an agent and returns a boolean value.
                If a dictionary, it will be used as a filter function.
                If a string, it will be used as a filter function.
        """
        if isinstance(filter_func, dict):
            key_value_paris = filter_func

            def filter_func(agent: Agent) -> bool:
                return all(getattr(agent, k) == v for k, v in key_value_paris.items())

        if isinstance(filter_func, str):

            def filter_func(agent: Agent) -> bool:
                # 如果 filter_func 是字符串，则使用该字符串作为过滤条件
                return getattr(agent, filter_func)

        objects = super().select(filter_func, at_most, inplace, agent_type)
        return ActorsList(self._model, objects)

    def better(
        self, metric: str, than: Optional[Union[Number, A]] = None
    ) -> ActorsList[A]:
        """选择比给定值或 actor 更好的 actors。"""
        if isinstance(than, Agent):
            than = than.metric
        return self.select(lambda x: getattr(x, metric) > than)

    def update(self, attr: str, values: Iterable[Any]) -> None:
        """Update the specified attribute of each agent in the sequence with the corresponding value in the given iterable.

        Parameters:
            attr:
                The name of the attribute to update.
            values:
                An iterable of values to update the attribute with. Must be the same length as the sequence.

        Raises:
            ValueError:
                If the length of the values iterable does not match the length of the sequence.
        """
        self._is_same_length(cast(Sized, values), rep_error=True)
        for agent, val in zip(self, values):
            setattr(agent, attr, val)

    def split(self, where: NDArray[Any]) -> List[ActorsList[A]]:
        """将 actors 分成 N+1 组。"""
        split: List[NDArray[Any]] = np.hsplit(np.array(self), where)
        return [ActorsList(self._model, group) for group in split]

    def array(self, attr: str) -> np.ndarray:
        """将所有 actor 的指定属性转换为 numpy 数组。

        Parameters:
            attr: 要转换为 numpy 数组的属性名称。

        Returns:
            包含所有 actor 指定属性的 numpy 数组。
        """
        return np.array(self.get(attr))

    def apply(self, ufunc: Callable, *args: Any, **kwargs: Any) -> np.ndarray:
        """对序列中的所有 actor 应用函数。

        Parameters:
            ufunc: 要应用于每个 actor 的函数。
            *args: 传递给函数的位置参数。
            **kwargs: 传递给函数的关键字参数。

        Returns:
            应用函数到每个 actor 的结果数组。
        """
        return np.array(self.map(ufunc, *args, **kwargs))

    def trigger(self, func_name: str, *args: Any, **kwargs: Any) -> np.ndarray:
        """调用序列中所有 actor 上具有给定名称的方法。

        Parameters:
            func_name: 要在每个 actor 上调用的方法的名称。
            *args: 传递给方法的位置参数。
            **kwargs: 传递给方法的关键字参数。

        Returns:
            在每个 actor 上调用方法的结果数组。
        """
        return np.array(self.map(func_name, *args, **kwargs))

    def item(self, how: HOW_TO_SELECT = "item", index: int = 0) -> Optional[A]:
        """获取一个 agent（如果可能）。"""
        if how == "only":
            return get_only_item(self)
        if how == "item":
            return self[index] if len(self) > index else None
        raise ValueError(f"Invalid how method '{how}'.")

    @property
    def random(self) -> ListRandom:
        """返回一个 ListRandom 实例，用于随机操作。

        Returns:
            ListRandom: 用于随机操作的实例，使用与 AgentSet 相同的随机数生成器。
        """
        return ListRandom(self._model, self)

    @random.setter
    def random(self, random: np.random.Generator) -> None:
        pass
