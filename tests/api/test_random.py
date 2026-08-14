#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

import numpy as np
import pytest
from numpy import isclose

from abses import Actor, MainModel
from abses.agents.sequences import ActorsList
from abses.utils.errors import ABSESpyError


class TestRandomActorsList:
    """测试主体列表的随机"""

    @pytest.fixture(name="main")
    def mock_main(self):
        """有随机种子的测试模型"""
        return MainModel(seed=0)

    def test_link(self, main):
        """测试随机互相连接"""
        # arrange
        actors = main.agents.new(Actor, num=3)

        # act
        linked_combs = actors.random.link("test")

        # assert
        assert len(linked_combs) == 3
        assert actors[1] in actors[0].link.get("test")
        assert actors[2] in actors[0].link.get("test")

    @pytest.mark.parametrize(
        "actors_num, p, expected_p",
        [
            (2, [0, 0], [0.5, 0.5]),
            (2, [-1, 0], [0.5, 0.5]),
            (2, [np.nan, np.nan], [0.5, 0.5]),
            (2, [np.nan, np.nan], [0.5, 0.5]),
            (2, [np.nan, 3], [0, 1]),
            (1, [np.nan], [1]),
            (1, [-1], [1]),
            (2, [3, 2], [0.6, 0.4]),
        ],
        ids=[
            ("Zero values"),
            ("Negative-Zero values"),
            ("Nan values"),
            ("Nan-negative values"),
            ("Nan-positive values"),
            ("One NaN value"),
            ("One negative value"),
            ("Normal values"),
        ],
    )
    def test_clean_p(self, main: MainModel, actors_num, p, expected_p):
        """测试清理概率"""
        # arrange
        agents = main.agents.new(Actor, num=actors_num)
        agents.update("test", p)

        # act
        possibilities = agents.random.clean_p(prob="test")

        # assert
        assert np.allclose(possibilities, expected_p)
        assert np.sum(possibilities) == 1

    @pytest.mark.parametrize(
        "num, size, replace",
        [
            (0, 2, True),
            (1, 2, False),
        ],
    )
    def test_bad_choose(self, main: MainModel, num, size, replace):
        """测试不能选取的一些情况"""
        agents = main.agents.new(Actor, num=num)

        # act / assert
        with pytest.raises(ABSESpyError):
            agents.random.choice(size=size, replace=replace)

    @pytest.mark.parametrize(
        "size, p, replace, expected",
        [
            (2, [0.1, 0.4], False, [0, 1]),
            (2, [np.nan, 1], True, [1, 1]),
            (1, [np.nan, 1], False, [1]),
            (2, [0, 1], False, [0, 1]),
        ],
        ids=[
            "choose all two",
            "expected two, but only one to choose",
            "only one to choose",
            "double_check choosing",
        ],
    )
    def test_random_choose(self, main: MainModel, size, p, replace, expected):
        """测试从列表中随机抽取"""
        # arrange
        agents: ActorsList = main.agents.new(Actor, num=2)

        # act
        chosen = agents.random.choice(
            size=size,
            prob=p,
            as_list=True,
            replace=replace,
            double_check=True,
        )

        # assert
        assert chosen == [agents[i] for i in expected]

    @pytest.mark.parametrize(
        "p, expected",
        [
            ([0.99, -1], 0),
            ([np.nan, 1], 1),
        ],
        ids=[
            "choose the first one",
            "choose the second one",
        ],
    )
    def test_random_choose_one(self, main: MainModel, p, expected):
        """测试从列表中随机抽取"""
        # TODO 为什么之前从不报错，随机种子有问题？
        # arrange
        agents = main.agents.new(Actor, num=2)

        # act
        chosen = agents.random.choice(prob=p, as_list=False)

        # assert
        assert isinstance(chosen, Actor)
        assert chosen is agents[expected]

    @pytest.mark.parametrize(
        "value, num",
        [
            (4, 1),
            (4, 2),
            (4, 3),
        ],
    )
    def test_random_assign(self, main: MainModel, num, value):
        """测试随机分配"""
        # arrange
        agents = main.agents.new(Actor, num=num)
        agents.apply(lambda a: setattr(a, "test", 0))

        # act
        values = agents.random.assign(
            value=value, attr="test", when_empty="raise exception"
        )

        # assert
        assert isclose(agents.array("test").sum(), value)
        assert isclose(values.sum(), value)


class TestSharedRandomStream:
    """`.random` must share the model's seeded RNG, not re-seed its own.

    `.random` builds a new `ListRandom` on every access. It used to seed that
    object from `model._seed`, which froze every method inherited from
    `random.Random` -- `shuffle()` returned the same order forever, so the
    canonical mesa activation pattern never actually shuffled.
    """

    @pytest.fixture(name="main")
    def mock_main(self):
        """有随机种子的测试模型"""
        return MainModel(seed=42)

    def test_consecutive_draws_advance(self, main: MainModel):
        """Repeated draws must differ -- the stream advances."""
        # arrange
        actors = main.agents.new(Actor, num=6)

        # act
        draws = [actors.random.random() for _ in range(5)]

        # assert
        assert len(set(draws)) == len(draws)

    def test_consecutive_shuffles_differ(self, main: MainModel):
        """`shuffle()` must not return the same order every call."""
        # arrange
        actors = main.agents.new(Actor, num=8)

        # act
        orders = [tuple(a.unique_id for a in actors.shuffle()) for _ in range(5)]

        # assert
        assert len(set(orders)) > 1

    @staticmethod
    def _draw(seed: int) -> list:
        """Draw a fixed sequence from a freshly seeded model."""
        model = MainModel(seed=seed)
        actors = model.agents.new(Actor, num=6)
        return [actors.random.randint(0, 1000) for _ in range(5)]

    def test_same_seed_reproduces_draws(self):
        """Two models with the same seed produce the same draw sequence."""
        assert self._draw(7) == self._draw(7)

    def test_different_seeds_diverge(self):
        """Different seeds produce different draw sequences."""
        assert self._draw(7) != self._draw(8)

    def test_seed_is_a_method_not_an_int(self, main: MainModel):
        """`self.seed = seed` used to shadow the inherited `Random.seed`."""
        # arrange
        actors = main.agents.new(Actor, num=2)

        # act / assert
        assert callable(actors.random.seed)

    def test_seeding_the_list_warns_and_does_not_reset_the_model(self, main: MainModel):
        """`ListRandom.seed()` must warn rather than silently do nothing."""
        # arrange
        actors = main.agents.new(Actor, num=6)
        before = actors.random.random()

        # act
        with pytest.warns(UserWarning, match="cannot be re-seeded"):
            actors.random.seed(123)

        # assert -- the stream kept advancing instead of restarting
        assert actors.random.random() != before
