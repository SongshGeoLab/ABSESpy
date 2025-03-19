#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

import numpy as np
import pytest


class TestHumanAttributes:
    @pytest.fixture(name="human")
    def human(self, model):
        return model.human

    def test_human_attributes(self, human, farmer_cls, admin_cls):
        """测试人类模块的属性"""
        assert len(human.actors) == 0
        human.agents.new(farmer_cls, 5)
        human.agents.new(admin_cls, 5)
        assert len(human.agents) == 10


def test_human_define(model, farmer_cls, admin_cls):
    """测试人口的定义"""
    human = model.human
    farmers = human.agents.new(farmer_cls, 5)
    admins = model.agents.new(admin_cls, 5)

    farmers.update("test", np.arange(5))
    admins.update("test", np.arange(5))

    test = human.create_module("test", agent_type=farmer_cls)
    assert "test" in human.collections
    assert "test" == test.name
    assert test.agents == farmers
