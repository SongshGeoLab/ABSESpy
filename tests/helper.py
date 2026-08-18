#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

import os

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


class PidReportingMod(MainModel):
    """Reports the OS process it ran in, so parallelism is observable.

    `run_single` executes in a worker process and only its reported vars travel
    back, so a final reporter on this attribute is how a test can see which
    process each repeat actually ran in.
    """

    @property
    def worker_pid(self) -> int:
        """PID of the process running this model."""
        return os.getpid()
