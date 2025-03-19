#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    Type,
    final,
)

from omegaconf import DictConfig

from abses.utils.func import iter_apply_func_to
from abses.utils.regex import is_snake_name

from .primitives import State
from .protocols import (
    ActorsListProtocol,
    AgentsContainerProtocol,
    DynamicVariableProtocol,
    MainModelProtocol,
    ModelElement,
    ModuleProtocol,
    Observable,
    Observer,
    StateManagerProtocol,
    SubSystemProtocol,
    TimeDriverProtocol,
    VariableProtocol,
)


class BaseVariable(ABC, VariableProtocol):
    """基础变量实现"""


class BaseDynamicVariable(DynamicVariableProtocol):
    """Time dependent variable

    A time dependent function will take the model time driver as
    an input and return its value. The function can also take other
    variables as inputs. The function can be defined as a static
    method of a class or a function.
    """

    def __init__(
        self,
        name: str,
        obj: BaseModelElement,
        data: Any,
        function: Callable,
        **kwargs,
    ) -> None:
        self._name: str = name
        self._obj: BaseModelElement = obj
        self._data: Any = data
        self._function: Callable = function
        self._cached_data: Any = None
        self.attrs = kwargs
        self.now()

    def __str__(self) -> str:
        return f"<{self.name}: {type(self.now())}>"

    def __repr__(self) -> str:
        return str(self)

    @property
    def name(self) -> str:
        """Get the name of the variable

        Returns
        -------
        name: str
        """
        return self._name

    @property
    def obj(self) -> BaseModelElement:
        """Returns a base object instance

        Returns:
            obj:
                BaseModelElement
        """
        return self._obj

    @obj.setter
    def obj(self, obj: BaseModelElement):
        if not isinstance(obj, BaseModelElement):
            raise TypeError("Only accept observer object")
        self._obj = obj

    @property
    def data(self) -> Any:
        """Returns unused data

        Returns:
            data:
                Any
        """
        return self._data

    @property
    def function(self) -> Callable:
        """Get the function that calculates the variable

        Returns:
            function:
                Callable
        """
        return self._function

    @property
    def time(self) -> TimeDriverProtocol:
        """Get the model time driver

        Returns:
            time:
                abses.time.TimeDriver
        """
        return self.obj.time

    def get_required_attributes(self, function: Callable) -> List[str]:
        """Get the function required attributes

        Returns:
            required_attributes:
                list[str]
        """
        # Get the source code of the function
        source_code = inspect.getsource(function)
        return [attr for attr in ["data", "obj", "time", "name"] if attr in source_code]

    def now(self) -> Any:
        """Return the dynamic variable function's output

        Returns:
            The dynamic data value now.
        """
        required_attrs = self.get_required_attributes(self.function)
        args = {attr: getattr(self, attr) for attr in required_attrs}
        result = self.function(**args)
        self._cached_data = result
        return result

    @property
    def cache(self) -> Any:
        """Return the dynamic variable's cache"""
        return self._cached_data


class BaseObserver(ABC, Observer):
    """基础观察者实现"""

    @abstractmethod
    def update(self, subject: Observable, *args: Any, **kwargs: Any) -> None:
        """当被观察对象发生变化时调用"""
        pass


class BaseObservable(ABC, Observable):
    """基础可观察对象实现"""

    def __init__(self) -> None:
        self._observers: Set[Observer] = set()

    @property
    def observers(self) -> Set[Observer]:
        return self._observers

    @property
    def variables(self) -> Dict[str, VariableProtocol]:
        """获取可观察对象的变量"""
        return {}

    def attach(self, observer: Observer) -> None:
        """添加观察者"""
        self._observers.add(observer)

    def detach(self, observer: Observer) -> None:
        """移除观察者"""
        self._observers.discard(observer)

    def notify(self, *args: Any, **kwargs: Any) -> None:
        """通知所有观察者"""
        for observer in self._observers:
            observer.update(self, *args, **kwargs)


class BaseModelElement(ABC, ModelElement):
    """基础模型元素实现"""

    def __init__(self, model: MainModelProtocol, name: Optional[str] = None) -> None:
        self._model = model
        self._name = name
        self._dynamic_variables: Dict[str, DynamicVariableProtocol] = {}
        self._updated_ticks: List[int] = []

    @property
    def model(self) -> MainModelProtocol:
        return self._model

    @model.setter
    def model(self, model: MainModelProtocol) -> None:
        pass

    @property
    def name(self) -> str:
        """获取组件的名称"""
        if self._name is None:
            return self.__class__.__name__
        if not isinstance(self._name, str):
            raise ValueError(f"Name must be a string, but got {type(self._name)}")
        if not is_snake_name(self._name):
            raise ValueError(f"Name '{self._name}' is not a valid name.")
        return self._name

    @property
    def params(self) -> DictConfig:
        """获取组件的参数配置
        如果组件名称对应的配置不存在，返回空配置
        """
        return self.model.settings.get(self.name, DictConfig({}))

    p = params

    @property
    def tick(self) -> int:
        """Returns the current tick."""
        return self.model.steps

    @property
    def time(self) -> TimeDriverProtocol:
        """Returns the current time."""
        return self.model.time

    @property
    def dynamic_variables(self) -> Dict[str, DynamicVariableProtocol]:
        """Returns read-only model's dynamic variables.

        Returns:
            Dict[str, Any]:
                Dictionary of model's dynamic variables.
        """
        return self._dynamic_variables

    def add_dynamic_variable(
        self, name: str, data: Any, function: Callable, **kwargs
    ) -> None:
        """Adds new dynamic variable.

        Parameters:
            name:
                Name of the variable.
            data:
                Data source for callable function.
            function:
                Function to calculate the dynamic variable.
        """
        var = BaseDynamicVariable(
            obj=self,
            name=name,
            data=data,
            function=function,
            **kwargs,
        )
        self._dynamic_variables[name] = var

    def dynamic_var(self, attr_name: str) -> Any:
        """Returns output of a dynamic variable.

        Parameters:
            attr_name:
                Dynamic variable's name.
        """
        if self.time.tick in self._updated_ticks:
            return self._dynamic_variables[attr_name].cache
        return self._dynamic_variables[attr_name].now()


class BaseStateManager(ABC, StateManagerProtocol):
    """基础状态管理器实现"""

    def __init__(self) -> None:
        self._state = State.NEW
        self._open = True

    @property
    def state(self) -> State:
        """获取模块的状态"""
        return self._state

    @state.setter
    def state(self, state: State) -> None:
        """设置模块的状态"""
        self._state = state

    @property
    def opening(self) -> bool:
        """获取模块是否开启"""
        return self._open

    def set_state(self, state: State) -> None:
        """设置模块状态"""
        if state == self._state:
            raise ValueError(f"Setting state repeat: {self.state}!")
        if state < self._state:
            raise ValueError(f"State cannot retreat from {self.state} to {state}!")
        self._state = state

    def reset(self, opening: bool = True) -> None:
        """重置模块"""
        self._state = State.NEW
        self._open = opening

    def initialize(self) -> None:
        """初始化模块"""
        pass

    def setup(self) -> None:
        """设置模块"""
        pass

    def step(self) -> None:
        """步进模块"""
        pass

    def end(self) -> None:
        """结束模块"""
        pass


class BaseModule(BaseModelElement, BaseStateManager, Observer, ModuleProtocol, ABC):
    """基础模块实现"""

    def __init__(
        self,
        model: MainModelProtocol,
        *,
        name: Optional[str] = None,
    ) -> None:
        BaseModelElement.__init__(self, model, name)
        BaseStateManager.__init__(self)

    def __repr__(self) -> str:
        flag = "open" if self.opening else "closed"
        return f"<{self.name}: {flag}>"

    def __str__(self) -> str:
        return self.name

    @final
    def _initialize(self):
        """
        Initialization before handle parameters.
        """
        # Wrap the user-defined step method
        self._user_setup = self.setup
        self.setup = self._setup
        self._user_step = self.step
        self.step = self._step
        self._user_end = self.end
        self.end = self._end
        self.set_state(State.INIT)
        self.initialize()

    @final
    def _setup(self, *args, **kwargs):
        """
        Initialization after handle parameters.
        """
        self._user_setup(*args, **kwargs)
        self.set_state(State.READY)

    @final
    def _step(self, *args, **kwargs):
        """
        Called every time step.
        """
        self._user_step(*args, **kwargs)

    @final
    def _end(self, *args, **kwargs):
        """
        Called at the end of the simulation.
        """
        self._user_end(*args, **kwargs)
        self.set_state(State.COMPLETE)


class BaseSubSystem(BaseModule, SubSystemProtocol, ABC):
    """基础子系统实现"""

    def __init__(self, model: MainModelProtocol, name: Optional[str] = None) -> None:
        super().__init__(model, name=name)
        self._modules: Set[BaseModule] = set()
        self._major_layer: Optional[BaseModule] = None

    @property
    def agents(self) -> AgentsContainerProtocol:
        """获取子系统中的所有代理"""
        return self.model.agents

    @property
    def actors(self) -> ActorsListProtocol:
        """获取子系统中的所有演员"""
        return self.agents.select("on_earth")

    @property
    def modules(self) -> Set[BaseModule]:
        """获取子系统中的所有模块"""
        return self._modules

    @property
    def opening(self) -> bool:
        """获取子系统是否开启"""
        return any(module.opening for module in self.modules)

    @property
    def is_empty(self) -> bool:
        """获取子系统是否为空"""
        return len(self.modules) == 0

    @iter_apply_func_to("modules")
    def set_state(self, state: State):
        return super().set_state(state)

    @iter_apply_func_to("modules")
    def _initialize(self):
        self.initialize()
        super().set_state(State.INIT)

    @iter_apply_func_to("modules")
    def _setup(self):
        self.setup()
        super().set_state(State.READY)

    @iter_apply_func_to("modules")
    def _step(self):
        self.step()

    @iter_apply_func_to("modules")
    def _end(self):
        self.end()
        super().set_state(State.COMPLETE)

    def __repr__(self) -> str:
        flag = "open" if self.opening else "closed"
        return f"<{self.name} ({str(self.major_layer)}): {flag}>"

    def __getattr__(self, name: str) -> Any:
        """Delegates attribute access to major_layer when not found in BaseNature.

        Args:
            name: Name of the attribute being accessed.

        Returns:
            Value of the attribute from major_layer.

        Raises:
            AttributeError: If no major layer is set or attribute not found.
        """
        try:
            return super().__getattribute__(name)
        except AttributeError as e:
            if self._major_layer is None:
                raise AttributeError(
                    f"Attribute '{name}' not found in {self.__class__.__name__},"
                    "and no major layer is set."
                ) from e
            try:
                return getattr(self._major_layer, name)
            except AttributeError as e2:
                raise AttributeError(
                    f"Attribute '{name}' not found in either BaseNature or major layer ({self._major_layer.name})"
                ) from e2

    @property
    def major_layer(self) -> Optional[BaseModule]:
        """Primary raster layer of the nature module.

        Returns:
            The current major layer, or None if not set.
        """
        return self._major_layer

    @major_layer.setter
    def major_layer(self, layer: BaseModule) -> None:
        """Sets the major layer for this nature module.

        Args:
            layer: PatchModule instance to set as major layer.

        Raises:
            TypeError: If layer is not a PatchModule instance.

        Note:
            If the layer has a CRS different from nature's current CRS,
            nature's CRS will be updated to match.
        """
        if layer not in self.modules:
            raise ValueError(f"{layer} is not in {self}.")
        self._major_layer = layer

    def add_module(self, module: BaseModule):
        """Add a module."""
        was_empty = bool(self.is_empty)
        # check name
        self.model.add_name(module.name, check="unique")
        # attach to model
        self.attach(module)
        # add to modules
        self.modules.add(module)
        if was_empty:
            self.major_layer = module
        return module

    @abstractmethod
    def create_module(
        self,
        module_cls: Type[BaseModule],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Create a module."""
        module = module_cls(model=self.model, *args, **kwargs)
        self.add_module(module)
        return module
