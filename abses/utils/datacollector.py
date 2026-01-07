#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""数据收集器"""

from __future__ import annotations

import logging
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Sequence,
    cast,
)

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from abses.agents.actor import Actor
    from abses.agents.sequences import ActorsList
    from abses.core.model import MainModel
    from abses.core.time_driver import TimeDriver

from abses.utils.tracker import TrackerProtocol

try:
    from typing import TypeAlias
except ImportError:
    from typing_extensions import TypeAlias

Reporter: TypeAlias = Callable[..., Any]
ReporterDict: TypeAlias = Dict[str, Reporter]
ReportType: TypeAlias = Literal["model", "agents", "final"] | str

logger = logging.getLogger(__name__)


def _getattr_to_reporter(
    attribute_name: str,
) -> Callable[..., Any]:
    """获取属性的报告函数"""

    def attr_reporter(obj: Actor | MainModel):
        return getattr(obj, attribute_name, None)

    return attr_reporter


def _func_reporter(reporter: Sequence) -> Callable[..., Any]:
    """函数报告器

    Args:
        reporter: Sequence of [func], [func, args], or [func, args, kwargs]

    Returns:
        A callable that applies func with the bound args/kwargs
    """
    func = reporter[0]
    params = reporter[1] if len(reporter) > 1 else ()
    kwargs_dict = reporter[2] if len(reporter) > 2 else {}

    def func_reporter(agent: Actor):
        return func(agent, *params, **kwargs_dict)

    return func_reporter


def clean_to_reporter(
    reporter: Reporter,
    *args,
    **kwargs,
) -> Callable[..., Any]:
    """将字符串转换为函数

    Args:
        reporter: Can be:
            - str: attribute name to get from object
            - list/tuple: [func, args] or [func, args, kwargs]
            - callable: function to call (args/kwargs bound if provided)

    Returns:
        A callable reporter function
    """
    if isinstance(reporter, str):
        reporter = _getattr_to_reporter(attribute_name=reporter)
    elif isinstance(reporter, (list, tuple)):
        # Expect [func], [func, args], or [func, args, kwargs]
        if not (1 <= len(reporter) <= 3):
            raise ValueError(
                "List/tuple reporter must be [func], [func, args], or [func, args, kwargs]."
            )
        reporter = _func_reporter(reporter)
    elif callable(reporter):
        # Only bind args/kwargs if they were provided
        if args or kwargs:
            reporter = _func_reporter([reporter, args, kwargs])
        else:
            reporter = _func_reporter([reporter])
    return reporter


class ABSESpyDataCollector:
    """ABSESpyDataCollector, adapted from DataCollector of `mesa`."""

    def __init__(
        self,
        reports: Dict[ReportType, Dict[str, Reporter]] | None = None,
        tracker: Optional[TrackerProtocol] = None,
        run_id: Optional[int] = None,
    ):
        """Initialize data collector.

        Args:
            reports: Reporters configuration.
            tracker: Optional tracker backend.
            run_id: Optional run id.
        """
        reports = reports or {}
        self.tracker = tracker
        self.run_id = run_id
        self.model_reporters: Dict[str, Reporter] = {}
        self.final_reporters: Dict[str, Reporter] = {}
        self.agent_reporters: Dict[str, Dict[str, Reporter]] = {}

        self._agent_records: Dict[str, List[pd.DataFrame]] = {}
        self.model_vars: Dict[str, List[Any]] = {}

        self.add_reporters("model", reports.get("model", {}))
        self.add_reporters("agents", reports.get("agents", {}))
        self.add_reporters("final", reports.get("final", {}))

    def add_reporters(
        self,
        item: ReportType,
        reporters: ReporterDict,
    ) -> None:
        """Add a dictionary of new reporters."""
        # 处理列表？
        # if isinstance(reporters, (tuple, list)):
        #     reporters = {name: name for name in reporters}
        if item == "model":
            for name, reporter in reporters.items():
                self._new_model_reporter(name=name, reporter=reporter)
            return
        if item == "final":
            for name, reporter in reporters.items():
                self.final_reporters[name] = clean_to_reporter(reporter)
            return
        if item == "agents":
            for breed, tmp_reporters in reporters.items():
                self.add_reporters(
                    item=breed, reporters=cast(ReporterDict, tmp_reporters)
                )
            return
        for name, reporter in reporters.items():
            self._new_agent_reporter(breed=item, name=name, reporter=reporter)

    def _add_run_id_to_data(
        self, data: pd.DataFrame | Dict[str, Any]
    ) -> pd.DataFrame | Dict[str, Any]:
        if self.run_id is not None:
            data["run_id"] = self.run_id
        return data

    def _new_model_reporter(self, name: str, reporter: Reporter) -> None:
        """Add a new model-level reporter to collect data.

        Parameters:
            name:
                Name of the model level variable to collect.
            reporter:
                Attribute string,
                or function object that returns the variable.
        """
        self.model_reporters[name] = clean_to_reporter(reporter)
        self.model_vars[name] = []

    def _record_a_breed_of_agents(
        self, time: TimeDriver, breed: str, agents: ActorsList[Actor]
    ) -> None:
        """记录某一组的数据"""
        result = {
            "AgentID": agents.array("unique_id"),
            "Step": np.repeat(time.tick, len(agents)),
            "Time": np.repeat(time.dt, len(agents)),
        }
        for name, reporter in self.agent_reporters[breed].items():
            result[name] = agents.apply(reporter)
        self._agent_records[breed].append(result)

    def _record_agents(self, model: MainModel) -> None:
        """记录所有的Agents"""
        for breed in model.agent_types:
            breed = breed.__name__
            if breed not in self.agent_reporters:
                continue
            if breed not in self._agent_records:
                self._agent_records[breed] = []
            agents = model.agents[breed]
            self._record_a_breed_of_agents(model.time, breed, agents)

    def _new_agent_reporter(self, breed: str, name: str, reporter: Reporter) -> None:
        """添加新的 Agent Reporter"""
        if breed not in self.agent_reporters:
            self.agent_reporters[breed] = {}
        self.agent_reporters[breed][name] = clean_to_reporter(reporter=reporter)

    def get_model_vars_dataframe(self):
        """Create a pandas DataFrame from the model variables.

        The DataFrame has one column for each model variable, and the index is
        (implicitly) the model tick.
        """
        # Check if self.model_reporters dictionary is empty, if so raise warning
        if not self.model_reporters:
            logger.warning(
                "No model reporters have been definedreturning empty DataFrame."
            )
        df = pd.DataFrame(self.model_vars)
        df = self._add_run_id_to_data(df)
        return df

    def get_agent_vars_dataframe(self, breed: Optional[str] = None) -> pd.DataFrame:
        """获取某种 Agents 的 DataFrame"""
        if breed is None:
            return {
                breed: self.get_agent_vars_dataframe(breed)
                for breed in self.agent_reporters
            }
        if not self.agent_reporters:
            logger.warning("No agent reporters have been defined in the DataCollector.")
        if results := self._agent_records.get(breed):
            df = pd.concat([pd.DataFrame(res) for res in results])
        else:
            logger.warning(f"No agent records found for breed {breed}.")
            df = pd.DataFrame()
        df = self._add_run_id_to_data(data=df)
        return df

    def get_final_vars_report(self, model: MainModel) -> Dict[str, Any]:
        """Report at the end of this model.

        Returns:
            A dictionary mapping variable names to their computed values.
        """
        if not self.final_reporters:
            logger.info("No final reporters have been defined.")
            return {}
        results = {var: func(model) for var, func in self.final_reporters.items()}
        self._add_run_id_to_data(results)
        if self.tracker is not None:
            self.tracker.log_final_metrics(results)
        return results

    def collect(self, model: MainModel):
        """Collect all the data for the given model object."""

        if self.model_reporters:
            model_snapshot = {}
            for var, func in self.model_reporters.items():
                value = func(model)
                self.model_vars[var].append(value)
                model_snapshot[var] = value
            if self.tracker is not None:
                self.tracker.log_model_vars(model_snapshot, step=model.time.tick)

        if self.agent_reporters:
            self._record_agents(model)
            if self.tracker is not None:
                for breed, records in self._agent_records.items():
                    if not records:
                        continue
                    latest_df = pd.DataFrame(records[-1])
                    agent_vars = {
                        col: latest_df[col].tolist()
                        for col in latest_df.columns
                        if col not in ("AgentID", "Step", "Time")
                    }
                    self.tracker.log_agent_vars(breed, agent_vars, step=model.time.tick)
