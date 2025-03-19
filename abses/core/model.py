#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""
The main modelling framework of ABSESpy.
"""

from __future__ import annotations

import functools
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Optional,
    Set,
    Tuple,
    Type,
)

from mesa import Model
from omegaconf import DictConfig

from abses import __version__
from abses.agents.container import _ModelAgentsContainer
from abses.core.base import BaseStateManager
from abses.core.primitives import DEFAULT_INIT_ORDER, DEFAULT_RUN_ORDER
from abses.core.protocols import (
    ActorsListProtocol,
    ExperimentProtocol,
    HumanSystemProtocol,
    NatureSystemProtocol,
)
from abses.core.time_driver import TimeDriver
from abses.human.human import BaseHuman
from abses.space.nature import BaseNature
from abses.utils.args import merge_parameters
from abses.utils.datacollector import ABSESpyDataCollector
from abses.utils.logging import (
    formatter,
    log_session,
    logger,
    setup_logger_info,
)

if TYPE_CHECKING:
    from mesa.model import RNGLike, SeedLike

    from abses.core.types import (
        HowCheckName,
        SubSystemName,
    )


class MainModel(Model, BaseStateManager):
    """Base class of a main ABSESpy model.

    A MainModel instance represents the core simulation environment that coordinates
    human and natural subsystems.

    Attributes:
        name: Name of the model (defaults to lowercase class name).
        settings: Structured parameters for all model components. Allows nested access
            like model.nature.params.parameter_name.
        human: The Human subsystem module.
        nature: The Nature subsystem module.
        time: Time driver controlling simulation progression.
        params: Model parameters (alias: .p).
        run_id: Identifier for current model run (useful in batch runs).
        agents: Container for all active agents. Provides methods for agent management.
        actors: List of all agents currently on the earth (in a PatchCell).
        outpath: Directory path for model outputs.
        version: Current version of the model.
        datasets: Available datasets (alias: .ds).
        plot: Visualization interface for the model.
    """

    def __init__(
        self,
        parameters: DictConfig = DictConfig({}),
        human_class: Type[HumanSystemProtocol] = BaseHuman,
        nature_class: Type[NatureSystemProtocol] = BaseNature,
        run_id: Optional[int] = None,
        seed: Optional[int] = None,
        rng: Optional[RNGLike | SeedLike] = None,
        experiment: Optional[ExperimentProtocol] = None,
        **kwargs: Optional[Any],
    ) -> None:
        """Initializes a new MainModel instance.

        Args:
            parameters: Configuration dictionary for model parameters.
            human_class: Class to use for human subsystem (defaults to BaseHuman).
            nature_class: Class to use for nature subsystem (defaults to BaseNature).
            run_id: Identifier for this model run.
            outpath: Directory path for model outputs.
            experiment: Associated experiment instance.
            **kwargs: Additional model parameters.

        Raises:
            AssertionError: If human_class or nature_class are not valid subclasses.
        """
        self._names: Set[str] = set()
        Model.__init__(self, seed=seed, rng=rng)
        BaseStateManager.__init__(self)
        self._exp = experiment
        self._run_id: Optional[int] = run_id
        self._settings = merge_parameters(parameters, **kwargs)
        self._time = TimeDriver(model=self)  # type: ignore[abstract]
        self._setup_subsystems(human_class, nature_class)
        self._agents_handler = _ModelAgentsContainer(
            model=self, max_len=kwargs.get("max_agents", None)
        )
        self.datacollector: ABSESpyDataCollector = ABSESpyDataCollector(
            parameters.get("reports", {})
        )
        self.do_each("_initialize", order=DEFAULT_INIT_ORDER)

    @functools.cached_property
    def name(self) -> str:
        """获取主模型的名称"""
        default_name = self.__class__.__name__
        return self.settings.get("name", default_name)

    @functools.cached_property
    def outpath(self) -> Path:
        """获取主模型的输出路径"""
        path = self.settings.get("outpath", None)
        if path is None:
            return Path.cwd() / self.name
        return Path(path)

    @functools.cached_property
    def version(self) -> str:
        """获取主模型的版本"""
        return str(self.settings.get("version", "v0"))

    @property
    def steps(self) -> int:
        """获取主模型的步数"""
        return self._steps

    @steps.setter
    def steps(self, steps: int) -> None:
        """设置主模型的步数"""
        self._steps = steps
        if steps > 0:
            self.time.go(steps)

    def __deepcopy__(self, memo):
        return self

    def __repr__(self) -> str:
        return f"<[{self.version}] {self.name}({self.state.name})>"

    def _logging_begin(self) -> None:
        """Logging the beginning of the model."""
        # settings = OmegaConf.to_container(self._settings)
        msg = (
            f"Model: {self.__class__.__name__}\n"
            f"ABSESpy version: {__version__}\n"
            f"Outpath: {self.outpath}\n"
            # f"Model parameters: {json.dumps(settings, indent=4)}\n"
        )
        # logger.bind(data=self._settings).info("Params:")
        log_session(title="MainModel", msg=msg)

    def _logging_step(self) -> None:
        if not self.agent_types:
            return
        agents = self._agents_handler.select({"_birth_tick": self.time.tick})
        agents_dict = agents.to_dict()
        lst = [f"{len(lst)} {breed}" for breed, lst in agents_dict.items()]
        msg = f"\nIn [tick {self.time.tick - 1}]:\nCreated " + ", ".join(lst) + ""
        logger.bind(no_format=True).info(msg)

    def _setup_subsystems(
        self,
        human_class: Type[HumanSystemProtocol] = BaseHuman,
        nature_class: Type[NatureSystemProtocol] = BaseNature,
    ) -> None:
        """设置子系统

        Args:
            human_class: 人类子系统类
            nature_class: 自然子系统类
        """
        # 使用默认实现
        self._human = human_class(self)
        self._nature = nature_class(self)

    def do_each(
        self,
        func: str | Callable,
        order: Tuple[SubSystemName, ...] = DEFAULT_RUN_ORDER,
        **kwargs: Any,
    ) -> Dict[SubSystemName, Any]:
        """执行每个子系统

        Args:
            func: 函数名或可调用对象
            order: 子系统顺序
            **kwargs: 其他参数
        """
        _obj = {"model": self, "nature": self.nature, "human": self.human}
        result = {}
        for name in order:
            if name not in _obj:
                raise ValueError(f"{name} is not a valid component.")
            if isinstance(func, str):
                callable_func = getattr(_obj[name], func)
            else:
                callable_func = func
            if not callable(callable_func):
                raise ValueError(f"{name}.{func} is not callable.")
            callable_func(**kwargs)
            result[name] = _obj[name]
        return result

    def _setup_logger(self, log_cfg: Dict[str, Any]) -> None:
        if not log_cfg:
            return
        name = log_cfg.get("name", "logging")
        rotation = log_cfg.get("rotation", "1 day")
        retention = log_cfg.get("retention", "10 days")
        level = log_cfg.get("level", "INFO")
        name = str(name).replace(".log", "")
        logger.add(
            self.outpath / f"{name}.log",
            retention=retention,
            rotation=rotation,
            level=level,
            format=formatter,
        )
        setup_logger_info(self.exp)
        self._logging_begin()  # logging

    def add_name(self, name: str, check: Optional[HowCheckName] = None) -> None:
        """检查名称是否有效"""
        if check not in ["unique", "exists"] and check is not None:
            raise ValueError(f"Invalid check name method: {check}")
        in_names = name in self._names
        if check == "unique" and in_names:
            raise ValueError(f"Name '{name}' already exists.")
        if check == "exists" and not in_names:
            raise ValueError(f"Name '{name}' does not exist.")
        self._names.add(name)

    @property
    def exp(self) -> Optional[ExperimentProtocol]:
        """Returns the associated experiment."""
        return self._exp

    @property
    def run_id(self) -> int | None:
        """The run id of the current model.
        It's useful in batch run.
        When running a single model, the run id is None.
        """
        return self._run_id

    @property
    def settings(self) -> DictConfig:
        """Structured configuration for all model components.

        Allows nested parameter access. Example:
        If settings = {'nature': {'test': 3}},
        Access via:
        - model.nature.params.test
        - model.nature.p.test

        Returns:
            DictConfig containing all model settings.
        """
        return self._settings

    @property
    def agents(self) -> _ModelAgentsContainer:
        """Container managing all agents in the model.

        Provides methods for:
        - Accessing agents: agents.select()
        - Creating agents: agents.new(Actor, num=3)
        - Registering agent types: agents.register(Actor)
        - Triggering events: agents.trigger()

        Returns:
            The model's agent container instance.
        """
        return self._agents_handler

    @property
    def actors(self) -> ActorsListProtocol:
        """List of all agents currently on the earth.

        Returns:
            ActorsList containing all agents in PatchCells.
        """
        return self.agents.select("on_earth")

    @property
    def human(self) -> HumanSystemProtocol:
        """The Human subsystem."""
        return self._human

    social = human

    @property
    def nature(self) -> NatureSystemProtocol:
        """The Nature subsystem."""
        return self._nature

    space = nature

    @property
    def time(self) -> TimeDriver:
        """The time driver & controller"""
        return self._time

    @property
    def params(self) -> DictConfig:
        """The global parameters of this model."""
        return self.settings.get("model", DictConfig({}))

    # alias for model's parameters
    p = params

    @property
    def datasets(self) -> DictConfig:
        """Available datasets for the model.

        Returns:
            DictConfig containing dataset configurations.
        """
        return self.settings.get("ds", DictConfig({}))

    # alias for model's datasets
    ds = datasets

    def run_model(
        self,
        steps: Optional[int] = None,
        order: Tuple[SubSystemName, ...] = DEFAULT_RUN_ORDER,
    ) -> None:
        """Executes the model simulation.

        Runs through the following phases:
        1. Setup phase (model.setup())
        2. Step phase (model.step()) - repeated
        3. End phase (model.end())

        Args:
            steps: Number of steps to run. If None, runs until self.running is False.
        """
        run_times = 0
        self.do_each("setup", order=order)
        while self.running is True:
            self.time.go()
            self.do_each("step", order=order)
            run_times += 1
            if steps is not None and run_times >= steps:
                break
        self.do_each("end", order=order)

    def setup(self) -> None:
        """Users can custom what to do when the model is setup and going to start running."""

    def step(self) -> None:
        """A step of the model.
        By default, collect data at each step.
        """
        self.datacollector.collect(self)

    def end(self) -> None:
        """Users can custom what to do when the model is end."""

    # def summary(self, verbose: bool = False) -> pd.DataFrame:
    #     """Generates a summary report of the model's current state.

    #     Args:
    #         verbose: If True, includes additional details about model and agent variables.

    #     Returns:
    #         DataFrame containing model statistics and state information.
    #     """
    #     print(f"Using ABSESpy version: {self.version}")
    #     # Basic reports
    #     to_report = {"name": self.name, "state": self.state, "tick": self.time.tick}
    #     for breed in self.agents_by_type:
    #         to_report[breed] = self.agents.has(breed)
    #     if verbose:
    #         to_report["model_vars"] = self.datacollector.model_reporters.keys()
    #         to_report["agent_vars"] = self.datacollector.agent_reporters.keys()
    #     return pd.Series(to_report)
