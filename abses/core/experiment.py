#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""This file is for multiple-run experiment."""

from __future__ import annotations

import copy
import inspect
import itertools
import logging
import os
import random
from copy import deepcopy
from numbers import Number
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
)

try:
    from typing import TypeAlias
except ImportError:
    from typing_extensions import TypeAlias

import numpy as np
import pandas as pd
from hydra import compose, initialize
from hydra.core.global_hydra import GlobalHydra
from hydra.core.hydra_config import HydraConf, HydraConfig
from joblib import Parallel, delayed
from omegaconf import DictConfig, OmegaConf
from tqdm.auto import tqdm

from abses.core.job_manager import ExperimentManager
from abses.core.model import MainModel
from abses.utils.exp_logging import EXP_LOGGER_NAME, setup_exp_logger
from abses.utils.log_parser import get_file_config, get_log_mode

# Use experiment-level logger, separate from model run loggers
logger = logging.getLogger(EXP_LOGGER_NAME)

Configurations: TypeAlias = DictConfig | str | Dict[str, Any]
T = TypeVar("T")
HookFunc: TypeAlias = Callable[[MainModel, Optional[int], Optional[int]], Any]

if TYPE_CHECKING:
    from abses.core.protocols import MainModelProtocol


def _parse_path(relative_path: str) -> Path:
    """Parse the path of the configuration file.
    Convert the relpath of current work space to the relpath of this script.
    """
    # 目标绝对路径
    abs_config_file_path = (Path(os.getcwd()) / relative_path).resolve()
    if not abs_config_file_path.is_file():
        raise FileNotFoundError(f"File {abs_config_file_path} not found.")
    # 返回相对于本脚本的路径
    current_file_path = Path(__file__).parent.resolve()
    return relative_path_from_to(current_file_path, abs_config_file_path)


def convert_to_python_type(value: Any) -> Any:
    """Convert numpy types to python native types.
    This function is mainly for `OmegaConfig` module to handle the parameters.
    """
    # If generic one value.
    if isinstance(value, np.generic):
        return value.item()
    # If array
    if isinstance(value, np.ndarray):
        # Optionally convert arrays to list if necessary
        return value.tolist()
    return value


def relative_path_from_to(from_path: Path, to_path: Path) -> Path:
    """Calculate the relative path from one path to another.

    Args:
        from_path: Starting path
        to_path: Target path

    Returns:
        Relative path from from_path to to_path
    """
    return Path(
        os.path.relpath(Path(to_path).resolve(), start=Path(from_path).resolve())
    )


def run_single(
    model_cls: Type[MainModelProtocol],
    cfg: DictConfig,
    key: Tuple[int, int],
    seed: Optional[int] = None,
    hooks: Optional[Dict[str, HookFunc]] = None,
    **kwargs,
) -> Tuple[Tuple[int, int], Optional[int], pd.DataFrame]:
    """Run model once, return the key, seed, and results.

    Args:
        key:
            The key of the experiment.
        seed:
            The seed of the experiment.
        hooks:
            The hooks to run after the model is run.
    """
    job_id, run_id = key
    model = model_cls(
        parameters=cfg,
        run_id=run_id,
        seed=seed,
        **kwargs,
    )
    model.run_model()
    results = model.datacollector.get_final_vars_report(model)
    if hooks is not None:
        for hook_name, hook_func in hooks.items():
            logger.info(f"Running hook {hook_name}.")
            _call_hook_with_optional_args(
                hook_func, model, job_id=job_id, run_id=run_id
            )
    return key, seed, results


class Experiment:
    """Experiment class."""

    def __init__(
        self,
        model_cls: Type[MainModelProtocol],
        cfg: Configurations,
        seed: Optional[int] = None,
        **kwargs,
    ):
        self._job_id = 0
        self._extra_kwargs = kwargs
        self._overrides: Dict[str, Any] = {}
        self._base_seed = seed
        self._manager = ExperimentManager(model_cls)
        self.cfg = cfg

        # Setup experiment-level logger (separate from model run loggers)
        # This ensures experiment-level messages don't mix with model run logs
        # Pass DictConfig directly, don't convert to dict (log_parser needs DictConfig)
        self._logger: Optional[logging.Logger] = None
        if isinstance(cfg, DictConfig):
            # Create a copy to avoid modifying original
            cfg_dict = OmegaConf.to_container(cfg, resolve=True)
            if isinstance(cfg_dict, dict):
                cfg_dict["outpath"] = str(self.outpath)  # Convert Path to string
                cfg_copy = OmegaConf.create(cfg_dict)
                self._logger = setup_exp_logger(cfg_copy)
        elif isinstance(cfg, dict):
            # Create a copy to avoid modifying original input
            cfg_copy = cfg.copy()
            cfg_copy["outpath"] = str(self.outpath)  # Convert Path to string
            self._logger = setup_exp_logger(cfg_copy)

    @property
    def model_cls(self) -> Type[MainModelProtocol]:
        """Model class."""
        return self._manager.model_cls

    @property
    def name(self) -> str:
        """Experiment name from configuration.

        Returns:
            Experiment name from exp.name config, or 'experiment' if not set.
        """
        exp_cfg = self._cfg.get("exp", {})
        if isinstance(exp_cfg, (dict, DictConfig)):
            return exp_cfg.get("name", "experiment")
        return "experiment"

    @property
    def logger(self) -> logging.Logger:
        """Experiment-level logger for recording experiment logs.

        Use this logger to write messages to the experiment log file
        (e.g., fire_spread.log) rather than model run logs.

        Example:
            exp.logger.info("Experiment started")
            exp.logger.debug("Processing parameters...")

        Returns:
            The experiment-level logger instance.
        """
        if self._logger is None:
            # Fallback to getting the logger by name
            self._logger = logging.getLogger(EXP_LOGGER_NAME)
        return self._logger

    @property
    def cfg(self) -> DictConfig:
        """Configuration"""
        return self._cfg

    @cfg.setter
    def cfg(self, cfg: DictConfig | str | Path):
        # 如果配置是路径，则利用 Hydra API先清洗配置
        if isinstance(cfg, str):
            cfg = _parse_path(cfg)
        if isinstance(cfg, Path):
            cfg = self._load_hydra_cfg(cfg)
        assert isinstance(cfg, (DictConfig, dict)), (
            f"cfg must be a DictConfig, got {type(cfg)}."
        )
        # Disable struct mode for backward compatibility with projects < 0.8.x
        # This allows dynamic key addition which was supported in older versions
        if isinstance(cfg, DictConfig):
            OmegaConf.set_struct(cfg, False)
        self._cfg = cfg

    def _is_hydra_parallel(self) -> bool:
        """检查是否在 Hydra 并行环境中"""
        if self.is_hydra_job():
            return self.hydra_config.launcher is not None
        return False

    @classmethod
    def new(
        cls, model_cls: Type[MainModelProtocol], cfg: Configurations, **kwargs
    ) -> "Experiment":
        """Create a new experiment for the singleton class `Experiment`.
        This method will delete all currently available exp results and settings.
        Then, it initialize a new instance of experiment.

        Parameters:
            model_cls:
                Using which model class to initialize the experiment.

        Raises:
            TypeError:
                If the model class `model_cls` is not a valid `ABSESpy` model.

        Returns:
            An experiment.
        """
        ExperimentManager(model_cls).clean()
        return cls(model_cls, cfg, **kwargs)

    @property
    def hydra_config(self) -> HydraConf:
        """Hydra runtime configuration object (HydraConf)."""
        if self.is_hydra_job():
            return HydraConfig.get()
        raise RuntimeError("Experiment is not running in Hydra.")

    @property
    def folder(self) -> Path:
        """Output dir path."""
        if self.is_hydra_job():
            return Path(self.hydra_config.run.dir)
        return Path(os.getcwd())

    @property
    def outpath(self) -> Path:
        """Output dir path."""
        if self.is_hydra_job():
            return Path(self.hydra_config.runtime.output_dir)
        return self.folder

    @property
    def overrides(self) -> Dict[str, Any]:
        """Overrides"""
        if not self.is_hydra_job():
            return self._overrides
        overrides_dict = {}
        for item in self.hydra_config.overrides.task:
            if "=" in item:  # 确保是键值对形式的覆盖
                key, value = item.split("=", 1)
                overrides_dict[key] = value
        return overrides_dict

    @overrides.setter
    def overrides(self, current_overrides):
        """Set the overrides."""
        if not isinstance(current_overrides, dict):
            raise TypeError("current_overrides must be a dictionary.")
        self._overrides = current_overrides

    @property
    def job_id(self) -> int:
        """Job id.
        Each job means a combination of the configuration.
        If the experiment is running in Hydra, it will return the hydra's job id.
        """
        if self.is_hydra_job():
            return self.hydra_config.job.get("id", 0)
        return self._job_id

    @staticmethod
    def is_hydra_job() -> bool:
        """Returns True if the experiment is running in Hydra."""
        return GlobalHydra().is_initialized()

    def summary(self) -> pd.DataFrame:
        """Summary of the experiment."""
        return self._manager.get_datasets(seed=bool(self._base_seed))

    def _overriding(
        self,
        cfg: DictConfig | Dict[str, Any],
        overrides: Optional[Dict[str, str | Iterable[Number]]] = None,
    ) -> Iterator[Tuple[DictConfig, Dict[str, Any]]]:
        """Parse the config."""
        if overrides is None:
            if isinstance(cfg, dict):
                cfg = DictConfig(cfg)
            return iter([(cfg, {})])  # type: ignore[return-value]
        if isinstance(cfg, dict):
            cfg = DictConfig(cfg)
        keys, values = zip(*overrides.items())
        values = tuple(convert_to_python_type(val) for val in values)
        combinations = itertools.product(*values)
        for comb in combinations:
            cfg_copy = copy.deepcopy(cfg)
            current_overrides = dict(zip(keys, comb))
            for key, val in current_overrides.items():
                OmegaConf.update(cfg_copy, key=key, value=val, merge=True)
            yield cfg_copy, current_overrides

    def _load_hydra_cfg(
        self,
        cfg_path: Path,
        overrides: Optional[Dict[str, str | Iterable[Number]]] = None,
    ) -> Optional[DictConfig]:
        """Initialize Hydra with overrides and disable struct mode for compatibility.

        Args:
            cfg_path: Path to the configuration file.
            overrides: Optional dictionary of configuration overrides.

        Returns:
            Loaded configuration with struct mode disabled.

        Note:
            Struct mode is disabled to maintain backward compatibility with
            projects from ABSESpy versions < 0.8.x.
        """
        if self.is_hydra_job():
            cfg = HydraConfig.get().cfg
        else:
            with initialize(version_base=None, config_path=str(cfg_path.parent)):
                cfg = compose(config_name=cfg_path.stem, overrides=overrides)

        # Disable struct mode for backward compatibility
        if cfg is not None:
            OmegaConf.set_struct(cfg, False)

        return cfg

    def _get_seed(self, run_id: int, job_id: Optional[int] = None) -> Optional[int]:
        """获取每次运行的随机种子

        使用基础种子初始化随机数生成器，为每次运行生成唯一的随机种子。
        这样可以保证：
        1. 如果基础种子相同，生成的种子序列也相同
        2. 不同的 job_id 和 run_id 组合会得到不同的种子
        3. 种子序列具有更好的随机性

        Args:
            run_id: 重复实验的ID

        Returns:
            如果没有设置基础种子则返回 None，否则返回生成的随机种子
        """
        if self._base_seed is None:
            return None

        if job_id is None:
            job_id = self.job_id
        # 使用基础种子和 job_id 创建随机数生成器
        r = random.Random(self._base_seed + job_id * 1000 + run_id)
        return r.randrange(2**32)

    def _get_logging_mode(self) -> str:
        """Get logging mode from experiment configuration.

        Returns:
            Logging mode: 'once', 'separate', or 'merge'. Defaults to 'once'.
        """
        return get_log_mode(self._cfg)

    def _get_log_file_path(
        self, log_name: str, run_id: int, logging_mode: str
    ) -> Optional[Path]:
        """Get log file path for a specific repeat.

        Args:
            log_name: Base log file name.
            run_id: Repeat ID (1-indexed).
            logging_mode: Logging mode.

        Returns:
            Path to log file, or None if logging should be disabled.
        """
        from abses.utils.log_config import determine_log_file_path

        return determine_log_file_path(
            outpath=self.outpath,
            log_name=log_name,
            logging_mode=logging_mode,
            run_id=run_id,
        )

    def _log_experiment_info(
        self, cfg: DictConfig, repeats: int, logging_mode: str = "once"
    ) -> None:
        """Log experiment-level information to experiment log file.

        Args:
            cfg: Configuration dictionary.
            repeats: Number of repeats.
            logging_mode: The logging mode being used.
        """
        try:
            from abses import __version__
        except ImportError:
            __version__ = "unknown"

        # Get model class name
        model_name = self.model_cls.__name__

        # Log experiment information
        logger.info("=" * 60)
        logger.info("Experiment Information".center(60))
        logger.info("=" * 60)
        logger.info(f"Model: {model_name}")
        logger.info(f"ABSESpy version: {__version__}")
        logger.info(f"Total repeats: {repeats}")
        logger.info(f"Output directory: {self.outpath}")
        logger.info(f"Logging mode: {logging_mode}")
        logger.info("=" * 60)

    def _batch_run_repeats(
        self,
        cfg: DictConfig,
        repeats: int,
        number_process: Optional[int] = None,
        display_progress: bool = True,
    ) -> None:
        """运行重复实验"""
        logging_mode = self._get_logging_mode()
        run_file_cfg = get_file_config(cfg, "run")
        log_name = str(run_file_cfg.get("name", "model")).replace(".log", "")

        # Log experiment-level information to experiment log file
        # Check if exp.file is enabled - if so, log experiment info for all modes
        exp_file_cfg = get_file_config(cfg, "exp")
        if exp_file_cfg:
            # exp.file is enabled, log experiment info
            self._log_experiment_info(cfg, repeats, logging_mode)
            # Also log framework banner to experiment log
            from abses.utils.logging import setup_logger_info

            setup_logger_info(self)
        elif logging_mode == "separate":
            # In separate mode, even if exp.file is disabled, log to experiment log
            self._log_experiment_info(cfg, repeats, logging_mode)
            from abses.utils.logging import setup_logger_info

            setup_logger_info(self)

        # For merge mode, log separator before first repeat
        if logging_mode == "merge" and repeats > 1:
            # Note: This will be logged in the model's logger setup
            pass

        if self._is_hydra_parallel() or number_process == 1:
            # Hydra 并行或指定单进程时，顺序执行
            disable = repeats == 1 or not display_progress
            for run_id in tqdm(
                range(1, repeats + 1),
                disable=disable,
                desc=f"Job {self.job_id} repeats {repeats} times.",
            ):
                # Log separator for merge mode
                if logging_mode == "merge" and run_id > 1:
                    # Note: Separator will be logged in model setup
                    pass

                # Get log file path for this repeat
                log_path = self._get_log_file_path(log_name, run_id, logging_mode)

                # Display log file location for separate mode
                # This should only go to stdout, not to model run log files
                if (
                    display_progress
                    and logging_mode == "separate"
                    and log_path is not None
                ):
                    # Use print instead of logger to avoid writing to model run log files
                    print(f"Repeat {run_id}: Logging to {log_path}")

                run_single(
                    model_cls=self.model_cls,
                    cfg=cfg,
                    key=(self.job_id, run_id),
                    outpath=self.outpath,
                    seed=self._get_seed(run_id),
                    hooks=self._manager.hooks,
                    **self._extra_kwargs,
                )
        else:
            if number_process is None:
                cpu_count = os.cpu_count()
                number_process = max(1, cpu_count or 1 // 2)
                number_process = min(number_process, repeats)

            results = Parallel(
                n_jobs=number_process,
                backend="loky",  # 改用 loky 后端
                verbose=0,
            )(
                delayed(run_single)(
                    model_cls=self.model_cls,
                    cfg=cfg,
                    key=(self.job_id, run_id),
                    outpath=self.outpath,
                    seed=self._get_seed(run_id),
                    hooks=self._manager.hooks,
                    **self._extra_kwargs,
                )
                for run_id in tqdm(
                    range(1, repeats + 1),
                    disable=not display_progress,
                    desc=f"Job {self.job_id} repeats {repeats} times, with {number_process} processes.",
                )
            )
            # 在主进程中批量更新结果
            for key, seed, dataset in results:
                self._manager.update_result(
                    key=key,
                    datasets=dataset,
                    seed=seed,
                    overrides=self.overrides,
                )

    def batch_run(
        self,
        repeats: int = 1,
        parallels: Optional[int] = None,
        display_progress: bool = True,
        overrides: Optional[Dict[str, str | Iterable[Number]]] = None,
    ) -> None:
        """Run the experiment multiple times."""
        self.logger.info(
            f"Running experiment with {repeats} repeats and {parallels} parallels."
        )
        cfg = deepcopy(self._cfg)

        if not overrides:
            # 如果没有覆写，直接运行
            self._batch_run_repeats(cfg, repeats, parallels, display_progress)
            return

        # 获取所有配置组合
        all_configs = list(self._overriding(cfg, overrides))
        # 使用一个总进度条
        for config, overrides_ in tqdm(
            all_configs,
            disable=not display_progress,
            desc=f"{len(all_configs)} jobs (repeats {repeats} times each).",
            position=0,
        ):
            self.overrides = overrides_
            # 内层任务只显示简单信息，不显示进度条
            self._batch_run_repeats(
                config,
                repeats,
                parallels,
                display_progress=False,  # 关闭内层进度条
            )
            self._job_id += 1
        self.overrides = {}

    def add_hooks(
        self,
        hooks: List[HookFunc] | Dict[str, HookFunc] | HookFunc,
    ) -> None:
        """Add hooks to the experiment."""
        if hasattr(hooks, "__call__"):
            hooks = [hooks]
        if isinstance(hooks, (list, tuple)):
            for hook in hooks:
                self._manager.add_a_hook(hook_func=hook)
        elif isinstance(hooks, dict):
            for hook_name, hook_func in hooks.items():
                self._manager.add_a_hook(hook_func=hook_func, hook_name=hook_name)
        else:
            raise TypeError(f"Invalid hooks type: {type(hooks)}.")


def _call_hook_with_optional_args(
    hook_func: Callable,
    model: MainModelProtocol,
    job_id: Optional[int] = None,
    run_id: Optional[int] = None,
) -> Any:
    """根据钩子函数的参数签名动态调用函数

    Args:
        hook_func: 要调用的钩子函数
        model: 模型实例
        job_id: 可选的任务ID
        run_id: 可选的重复实验ID
    """
    sig = inspect.signature(hook_func)
    hook_args = {}

    if "job_id" in sig.parameters:
        hook_args["job_id"] = job_id
    if "run_id" in sig.parameters:
        hook_args["run_id"] = run_id

    return hook_func(model, **hook_args)
