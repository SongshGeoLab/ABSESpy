#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/
"""测试列表"""

import numpy as np
import pytest

from abses import MainModel
from abses.agents.actor import Actor
from abses.agents.sequences import ActorsList
from tests.helper import create_actors_with_metric


class TestSequences:
    """Test Sequence"""

    def test_sequences_attributes(self, model, farmer_cls):
        """测试容器的属性"""
        # arrange
        actors5 = model.agents.new(Actor, 5)
        farmers3 = model.agents.new(farmer_cls, 3)
        actors5.test = 1
        farmers3.test = -1
        mixed_actors = ActorsList(model=model, objs=[*actors5, *farmers3])

        # act / assert
        assert isinstance(actors5, ActorsList)
        assert repr(mixed_actors) == "<ActorsList: (5)Actor; (3)Farmer>"
        assert mixed_actors.to_dict() == {"Actor": actors5, "Farmer": farmers3}
        assert mixed_actors.select(agent_type=farmer_cls) == farmers3

    @pytest.mark.parametrize(
        "than, expected_num",
        [
            (-1.0, 5),
            (0.0, 4),
            (2.0, 2),
            (3.0, 1),
        ],
    )
    def test_sequences_better(self, model: MainModel, than, expected_num):
        """Test that sequences"""
        # arrange
        others = create_actors_with_metric(model, 5)

        # act
        better = others.better("test", than=than)
        # assert
        assert len(better) == expected_num

    def test_apply(self, model: MainModel):
        """Test that applying a function."""
        # assert
        actors = create_actors_with_metric(model, 3)
        # act
        results = actors.apply(lambda x: x.test + 1)
        expected = actors.array("test") + 1
        # assert
        np.testing.assert_array_equal(results, expected)

    @pytest.mark.parametrize(
        "num, index, how, expected",
        [
            (3, 1, "item", 1),
            (1, 0, "only", 0),
        ],
    )
    def test_item(self, model: MainModel, num, index, how, expected):
        """Test that the item function."""
        # arrange
        actors = model.agents.new(Actor, num=num)
        expected = actors[expected]
        # act
        result = actors.item(index=index, how=how)
        # assert
        assert result == expected

    @pytest.mark.parametrize(
        "how, num, index, error, to_match",
        [
            ("not a method", 3, 1, ValueError, "Invalid how method"),
            ("only", 2, 0, ValueError, "More than one agent."),
            ("only", 0, 0, ValueError, "No agent found."),
        ],
    )
    def test_bad_item(self, model: MainModel, how, num, index, error, to_match):
        """Test that the item function raises an error."""
        # arrange
        actors = model.agents.new(Actor, num=num)
        # act / assert
        with pytest.raises(error, match=to_match):
            actors.item(index=index, how=how)
