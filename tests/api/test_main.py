#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

import pytest
from omegaconf import DictConfig

from abses.core.model import MainModel


class TestMain:
    """Test MainModel"""

    @pytest.fixture(name="model")
    def fixture_main_model(self, main_config):
        """测试用模型"""
        return MainModel(parameters=main_config)

    def test_model_attrs(self, model: MainModel, main_config: DictConfig):
        """测试模型的默认属性"""
        # params 里 1 被 testing.yaml 第一层的 3 覆盖
        # 这个应该出现在
        assert repr(model) == "<[v0] MainModel(NEW)>"
        assert isinstance(model.settings, DictConfig)
        assert model.params == main_config.model
        assert model.time.strftime("%Y") == "2000"
        assert model.run_id is None
        model2 = MainModel(parameters=main_config, run_id=1)
        assert model2.run_id == 1

    def test_time_go(self, model: MainModel):
        """测试模型运行"""
        model.step()
        assert model.time.year == 2001

    def test_run_a_model(self, main_config):
        """测试运行模型"""
        # arrange
        model = MainModel(parameters=main_config)
        # act
        model.run_model()

    def test_run_a_tick_model(self, farmer_cls):
        """测试运行一个 tick 的模型"""

        class TestModel(MainModel):
            """用来测试，每步都创建几个主体。"""

            def step(self) -> None:
                self.agents.new(num=self.time.tick)
                self.agents.new(farmer_cls, num=2)

        model = TestModel(logging="tick")
        model.run_model(steps=20)
