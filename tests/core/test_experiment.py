#!/usr/bin/env python3
# -*-coding:utf-8 -*-

"""测试实验相关功能的模块。
这个模块主要测试:
1. 实验的基本配置加载
2. 实验的运行功能
3. 实验的并行计算
4. 实验的钩子函数
5. 实验结果的收集
"""

import os
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path

import pytest
from hydra import compose, initialize
from hydra.core.global_hydra import GlobalHydra
from hydra.core.hydra_config import HydraConfig
from omegaconf import OmegaConf

from abses import MainModel
from abses.core.experiment import Experiment, launcher_is_parallel
from tests.helper import PidReportingMod, RandomAddingMod


class TestExperimentBasic:
    """测试实验的基本功能"""

    def test_experiment_initialization(self, test_config):
        """测试实验的初始化"""
        exp = Experiment.new(MainModel, test_config)
        assert isinstance(exp, Experiment)
        assert exp.cfg == test_config

        class InvalidModel:
            """测试无效的模型类"""

        with pytest.raises(TypeError):
            Experiment.new(InvalidModel, test_config)

    def test_experiment_run(self, test_config):
        """测试实验的运行"""
        exp = Experiment.new(MainModel, test_config)
        exp.batch_run(repeats=2)
        summary = exp.summary()
        assert len(summary) == 2

    def test_experiment_parallel(self, test_config):
        """测试实验的并行计算"""
        exp = Experiment.new(MainModel, test_config)
        exp.batch_run(repeats=4, parallels=2)
        summary = exp.summary()
        assert len(summary) == 4

    def test_experiment_hooks(self, test_config):
        """测试实验的钩子函数"""

        def test_hook(model):
            model.test_hook_called = True

        exp = Experiment.new(MainModel, test_config)
        exp.add_hooks(test_hook)
        exp.batch_run()

    def test_parameter_override(self, test_config):
        """测试参数覆盖功能"""
        exp = Experiment.new(MainModel, test_config)
        overrides = {"param1": [1, 2], "param2": ["a", "b"]}
        exp.batch_run(overrides=overrides)
        summary = exp.summary()
        assert len(summary) == 4


class TestExperimentRandom:
    """测试实验的随机性控制"""

    pytestmark = pytest.mark.usefixtures("reset_experiment_manager")

    def test_seed_control(self, test_config):
        """测试随机种子控制"""
        # arrange
        exp1 = Experiment.new(RandomAddingMod, test_config, seed=42)
        exp1.batch_run(repeats=3)
        results1 = exp1.summary()

        exp2 = Experiment.new(RandomAddingMod, test_config, seed=42)
        exp2.batch_run(repeats=3)
        results2 = exp2.summary()

        exp3 = Experiment.new(RandomAddingMod, test_config, seed=43)
        exp3.batch_run(repeats=3)
        results3 = exp3.summary()

        # 验证相同种子产生相同结果
        assert results1.equals(results2)
        # 验证不同种子产生不同结果
        assert not results1.equals(results3)


class TestLauncherIsParallel:
    """`launcher_is_parallel` is True only when the launcher really is concurrent.

    Regression for #169: the check used to be `launcher is not None`, but Hydra
    configures a serial BasicLauncher for plain runs and multirun alike, so it
    was always true and `Experiment.batch_run(parallels=...)` never reached its
    parallel branch.
    """

    def test_basic_launcher_is_not_parallel(self):
        """BasicLauncher runs jobs in a `for` loop, which is not parallel."""
        launcher = OmegaConf.create(
            {"_target_": "hydra._internal.core_plugins.basic_launcher.BasicLauncher"}
        )
        assert launcher_is_parallel(launcher) is False

    @pytest.mark.parametrize(
        "target",
        [
            "hydra_plugins.hydra_joblib_launcher.joblib_launcher.JoblibLauncher",
            "hydra_plugins.hydra_submitit_launcher.submitit_launcher.LocalSubmititLauncher",
            "hydra_plugins.hydra_submitit_launcher.submitit_launcher.SlurmSubmititLauncher",
            "hydra_plugins.hydra_ray_launcher.ray_launcher.RayLauncher",
        ],
    )
    def test_plugin_launchers_are_parallel(self, target):
        """Real launcher plugins do run jobs concurrently, so abses must yield."""
        launcher = OmegaConf.create({"_target_": target})
        assert launcher_is_parallel(launcher) is True


@contextmanager
def _inside_hydra_job(launcher_target: str, output_dir: Path):
    """Make the process look like a running Hydra job with the given launcher."""
    GlobalHydra.instance().clear()
    with initialize(version_base=None, config_path="../config"):
        cfg = compose(config_name="test_config.yaml", return_hydra_config=True)
        OmegaConf.set_struct(cfg, False)
        cfg.hydra.launcher = OmegaConf.create({"_target_": launcher_target})
        cfg.hydra.job.id = 0
        cfg.hydra.runtime.output_dir = str(output_dir)
        HydraConfig.instance().set_config(cfg)
        try:
            yield
        finally:
            HydraConfig.instance().cfg = None


class TestNumProcessInsideHydra:
    """`parallels` must still take effect inside a Hydra job (#169).

    Hydra's default BasicLauncher is serial, so abses has to do the
    parallelising itself rather than yielding to the launcher.
    """

    pytestmark = pytest.mark.usefixtures("reset_experiment_manager")

    @pytest.fixture(name="pid_config")
    def pid_reporting_config(self, test_config, tmp_path):
        """A config whose only final report is the process each repeat ran in."""
        cfg = deepcopy(test_config)
        cfg.reports.final = {"worker_pid": "worker_pid"}
        cfg.outpath = str(tmp_path)
        return cfg

    def test_sequential_path_still_records_results(self, pid_config):
        """Running the repeats in-process must not lose their results.

        Only the parallel branch used to feed `run_single`'s return value back
        to the manager, so any sequential run reported an empty summary.
        """
        exp = Experiment.new(PidReportingMod, pid_config)
        exp.batch_run(repeats=3, parallels=1, display_progress=False)

        summary = exp.summary()
        assert len(summary) == 3, f"expected 3 recorded runs, got {len(summary)}"
        assert set(summary["worker_pid"]) == {os.getpid()}

    def test_repeats_span_multiple_processes(self, pid_config, tmp_path):
        """Repeats run in worker processes, not all in the parent."""
        exp = Experiment.new(PidReportingMod, pid_config)
        with _inside_hydra_job(
            "hydra._internal.core_plugins.basic_launcher.BasicLauncher",
            tmp_path,
        ):
            exp.batch_run(repeats=4, parallels=4, display_progress=False)

        summary = exp.summary()
        assert len(summary) == 4, f"expected 4 recorded runs, got {len(summary)}"

        pids = set(summary["worker_pid"])
        assert pids != {os.getpid()}, "every repeat ran in the parent process"
        assert len(pids) > 1, f"all repeats shared one process: {pids}"

    def test_yields_to_a_real_parallel_launcher(self, pid_config, tmp_path):
        """A launcher plugin already parallelises, so abses must not nest."""
        exp = Experiment.new(PidReportingMod, pid_config)
        with _inside_hydra_job(
            "hydra_plugins.hydra_joblib_launcher.joblib_launcher.JoblibLauncher",
            tmp_path,
        ):
            exp.batch_run(repeats=3, parallels=4, display_progress=False)

        summary = exp.summary()
        assert len(summary) == 3, f"expected 3 recorded runs, got {len(summary)}"
        assert set(summary["worker_pid"]) == {os.getpid()}, (
            "abses nested its own workers inside an already-parallel launcher"
        )
