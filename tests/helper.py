#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from abses import Actor, MainModel


class RandomAddingMod(MainModel):
    """测试类"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_var = 0

    def random_step(self):
        """测试步骤"""
        return self.random.randint(0, 10)

    def step(self):
        """测试步骤"""
        self.test_var += self.random_step()


def create_actors_with_metric(model: MainModel, n: int):
    """Create actors with a test metric."""
    actors = model.agents.new(Actor, n)
    for i, actor in enumerate(actors):
        actor.test = float(i)
    return actors
