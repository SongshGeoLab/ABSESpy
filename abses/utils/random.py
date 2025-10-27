#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""在列表中随机操作主体"""

from __future__ import annotations

from itertools import combinations
from random import Random
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
    Union,
    overload,
)

import numpy as np

from abses.utils.errors import ABSESpyError
from abses.utils.func import make_list

if TYPE_CHECKING:
    from abses.agents.actor import Actor
    from abses.agents.sequences import ActorsList
    from abses.core.protocols import ActorProtocol, MainModelProtocol
    from abses.core.types import WHEN_EMPTY


class ListRandom(Random):
    """Create a random generator from an `ActorsList`.

    Inherits from Python's Random class to provide Mesa-compatible shuffle() method.
    Extends Random with ABSESpy-specific methods for working with actors.
    """

    def __init__(self, model: MainModelProtocol, actors: Iterable[Any]) -> None:
        # Get seed from model and ensure it's a valid type
        if hasattr(model, "_seed"):
            seed = model._seed
            # Ensure seed is a valid type for Random
            if seed is not None and not isinstance(
                seed, (int, float, str, bytes, bytearray)
            ):
                seed = None
        else:
            seed = None

        # Initialize parent Random with seed
        super().__init__(seed)

        self.model = model
        self.actors = self._to_actors_list(actors)
        self.rng = model.rng if model.rng else np.random.default_rng()
        self.seed = seed

    def _to_actors_list(self, objs: Iterable) -> ActorsList:
        from abses.agents.sequences import ActorsList

        return ActorsList(self.model, objs=objs)

    def _when_empty(self, when_empty: WHEN_EMPTY, operation: str = "choice") -> None:
        if when_empty not in ("raise exception", "return None"):
            raise ValueError(f"Unknown value for `when_empty` parameter: {when_empty}")
        if when_empty == "raise exception":
            raise ABSESpyError(
                f"Random operating '{operation}' on an empty `ActorsList`."
            )

    def clean_p(self, prob: Union[np.ndarray, str]) -> np.ndarray:
        """Clean the probabilities.
        Any negative values, NaN values, or zeros will be recognized as in-valid probabilities.
        For all valid probabilities, normalize them into a prob-array (the sum is equal to 1.0).

        Parameters:
            prob:
                An array-like numbers of probabilities.

        Returns:
            The probabilities after cleaned.

        Example:
        ```
        >>> clean_p([0, 0])
        >>> [0.5, 0.5]

        >>> clean_p([-1, np.nan])
        >>> [0.5, 0.5]

        >>> clean_p([3, 2])
        >>> [0.6, 0.4]
        ```
        """
        if isinstance(prob, str):
            prob = self.actors.array(attr=prob)
        else:
            prob = np.array(make_list(prob))
        length = len(prob)
        prob = np.nan_to_num(prob)
        prob[prob < 0] = 0.0
        total = prob.sum()
        prob = prob / total if total else np.repeat(1 / length, length)
        return prob

    @overload
    def choice(
        self,
        size: int = 1,
        prob: np.ndarray | None = None,
        replace: bool = False,
        as_list: bool = True,
        when_empty: WHEN_EMPTY = "raise exception",
    ) -> ActorsList[ActorProtocol]: ...

    @overload
    def choice(
        self,
        size: int = 1,
        prob: np.ndarray | None = None,
        replace: bool = False,
        as_list: bool = False,
        when_empty: WHEN_EMPTY = "raise exception",
    ) -> ActorProtocol | ActorsList[ActorProtocol]: ...

    def choice(
        self,
        size: int = 1,
        prob: np.ndarray | None | str = None,
        replace: bool = False,
        as_list: bool = False,
        when_empty: WHEN_EMPTY = "raise exception",
        double_check: bool = False,
    ) -> Optional[ActorProtocol | ActorsList[ActorProtocol] | list]:
        """Randomly choose one or more actors from the current self object."""
        instances_num = len(self.actors)
        if instances_num == 0:
            self._when_empty(when_empty=when_empty)
            return None
        if not isinstance(size, int):
            raise ValueError(f"{size} isn't an integer size.")
        if instances_num < size and not replace:
            raise ABSESpyError(f"Trying to choose {size} actors from {self.actors}.")
        # 有概率的时候，先清理概率
        if prob is not None:
            prob = self.clean_p(prob=prob)
            valid_prob = prob.astype(bool)
            # 特别处理有概率的主体数量不足预期的情况
            if valid_prob.sum() < size and not replace:
                return self._when_p_not_enough(double_check, prob, size, as_list)
            # 如果只有一个有效概率且需要重复选择，直接返回对应的 actor
            if valid_prob.sum() == 1 and replace and size > 1:
                idx = np.where(valid_prob)[0][0]
                chosen = [self.actors[idx]] * size
                return chosen if as_list else self._to_actors_list(chosen)
        # 其他情况就正常随机选择
        indices = np.arange(len(self.actors))
        chosen_indices = self.rng.choice(indices, size=size, replace=replace, p=prob)
        # 如果不允许重复，按索引排序
        if not replace:
            chosen_indices.sort()
        chosen = [self.actors[i] for i in chosen_indices]
        return (
            chosen[0]
            if size == 1 and not as_list
            else (chosen if as_list else self._to_actors_list(chosen))
        )

    def _when_p_not_enough(self, double_check, prob, size, as_list):
        """处理概率不足的情况"""
        if not double_check:
            raise ABSESpyError(
                f"Only {(prob > 0).sum()} entities have possibility, "
                f"but {size} entities are expected. "
                "Please check the probability settings.\n"
                "If you want to choose with replacement, set `replace=True`.\n"
                "If you want to choose with equal probability, set `prob=None`.\n"
                "If you want to choose the valid entities firstly, "
                "and then choose others equally, set `double_check=True'`."
            )
        # 获取有效和无效的概率索引
        valid_indices = np.where(prob > 0)[0]
        invalid_indices = np.where(prob <= 0)[0]

        # 选择所有有效概率的实体
        first_chosen = [self.actors[i] for i in valid_indices]
        remain_size = size - len(first_chosen)

        # 从无效概率的实体中随机选择剩余数量
        if remain_size > 0:
            others = [self.actors[i] for i in invalid_indices]
            second_chosen = list(self.rng.choice(others, remain_size, replace=False))
            first_chosen.extend(second_chosen)

        # 按原始列表中的顺序排序
        result = sorted(first_chosen, key=lambda x: self.actors.index(x))
        return result if as_list else self._to_actors_list(result)

    def new(
        self,
        actor_cls: Type[Actor],
        actor_attrs: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> ActorsList[Actor]:
        """Randomly creating new agents for a given actor type."""
        if actor_attrs is None:
            actor_attrs = {}
        cells = self.choice(as_list=True, **kwargs)
        # Ensure we operate on an ActorsList for chaining operations like `.apply()`
        cells = self._to_actors_list(cells)
        objs = cells.apply(
            lambda c: c.agents.new(breed_cls=actor_cls, singleton=True, **actor_attrs)
        )
        return self._to_actors_list(objs)

    def link(
        self, link: str, p: float = 1.0, mutual: bool = True
    ) -> List[Tuple[Actor, Actor]]:
        """Random build links between actors.

        Parameters:
            link:
                Name of the link.
            p:
                Probability to generate a link.

        Returns:
            A list of tuple, in each tuple, there are two actors who got linked.

        Example:
            ```
            # generate three actors
            actors = model.agents.new(Actor, 3)
            # with `probability=1`, all possible actor-actor links would be generated.
            >>> actors.random.link('test', p=1)
            >>> a1, a2, a3 = actors
            >>> assert a1.link.get('test) == [a2, a3]
            >>> assert a2.link.get('test) == [a1, a3]
            >>> assert a3.link.get('test) == [a1, a2]
            ```
        """
        linked_combs = []
        for source, target in list(combinations(self.actors, 2)):
            if self.rng.random() < p:
                source.link.to(target, link_name=link, mutual=mutual)
                linked_combs.append((source, target))
        return linked_combs

    def assign(
        self,
        value: float | int,
        attr: str,
        when_empty: WHEN_EMPTY = "raise exception",
    ) -> np.ndarray:
        """Randomly assign a value to each actor."""
        num = len(self.actors)
        if num == 0:
            self._when_empty(when_empty=when_empty, operation="assign")
            return np.array([])
        if num == 1:
            values = np.array([value])
        else:
            # 生成 n-1 个随机切割点
            cuts = np.sort(self.rng.uniform(0, value, num - 1))
            # 将 0 和总面积 X 添加到切割点数组中，方便计算每段区间长度
            full_range = np.append(np.append(0, cuts), value)
            # 计算每个区间的长度，即为每个对象的分配面积
            values = np.diff(full_range)
        # 将分配的值赋予每个对象
        self.actors.update(attr, values)
        return values
