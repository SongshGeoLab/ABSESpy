#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from typing import Type

import pytest

from abses.core.base import BaseModule, BaseSubSystem, State


class ConcreteModule(BaseModule):
    """用于测试的具体模块类"""

    pass


class ConcreteSubSystem(BaseSubSystem):
    """用于测试的具体子系统类"""

    def create_module(self, module_cls: Type[BaseModule], **kwargs) -> BaseModule:
        module = module_cls(self.model, **kwargs)
        self.add_module(module)
        assert module.name in self.modules
        return module


class TestSubSystemInitialization:
    """测试子系统初始化"""

    @pytest.fixture
    def subsystem(self, mock_model):
        """创建基础子系统"""
        return ConcreteSubSystem(model=mock_model, name="test_system")

    def test_initial_state(self, subsystem):
        """测试初始状态

        场景：
        1. 验证模块集合为空
        2. 验证初始状态为 NEW
        3. 验证名称设置
        """
        assert isinstance(subsystem.modules, dict)
        assert len(subsystem.modules) == 0
        assert subsystem.state == State.NEW
        assert subsystem.name == "test_system"

    def test_default_name(self, mock_model):
        """测试默认名称

        场景：
        1. 不提供名称时使用类名
        """
        subsystem = ConcreteSubSystem(model=mock_model)
        assert subsystem.name == "ConcreteSubSystem"


class TestModuleManagement:
    """测试模块管理功能"""

    @pytest.fixture
    def subsystem(self, mock_model):
        return ConcreteSubSystem(model=mock_model)

    @pytest.mark.parametrize("module_count", [1, 2, 5])
    def test_multiple_module_creation(self, subsystem, module_count):
        """测试创建多个模块

        场景：
        1. 创建单个模块
        2. 创建多个模块
        3. 验证模块数量
        """
        modules = [
            subsystem.create_module(ConcreteModule, name=f"module_{i}")
            for i in range(module_count)
        ]
        assert len(subsystem.modules) == module_count
        assert all(m.name in subsystem.modules for m in modules)

    def test_duplicate_module_names(self, subsystem):
        """测试重复模块名称

        场景：
        1. 尝试创建同名模块
        2. 验证唯一性检查
        """
        subsystem.create_module(ConcreteModule, name="test")
        with pytest.raises(ValueError):
            subsystem.create_module(ConcreteModule, name="test")

    def test_invalid_module_type(self, subsystem):
        """测试无效模块类型

        场景：
        1. 尝试创建非 BaseModule 子类
        2. 验证类型检查
        """
        with pytest.raises(TypeError):
            subsystem.create_module(object)


class TestStateManagement:
    """测试状态管理功能"""

    @pytest.fixture
    def populated_subsystem(self, mock_model):
        """创建包含多个模块的子系统"""
        sys = ConcreteSubSystem(model=mock_model)
        sys.create_module(ConcreteModule, name="module1")
        sys.create_module(ConcreteModule, name="module2")
        return sys

    @pytest.mark.parametrize(
        "state_sequence",
        [
            [State.INIT, State.READY, State.COMPLETE],
            [State.INIT, State.COMPLETE],
        ],
    )
    def test_state_propagation(self, populated_subsystem, state_sequence):
        """测试状态传播

        场景：
        1. 完整状态序列
        2. 跳过中间状态
        3. 验证所有模块状态同步
        """
        for state in state_sequence:
            populated_subsystem.set_state(state)
            assert all(m.state == state for m in populated_subsystem.modules.values())


class TestLifecycleMethods:
    """测试生命周期方法"""

    @pytest.fixture
    def lifecycle_system(self, mock_model):
        """创建用于生命周期测试的系统"""
        sys = ConcreteSubSystem(model=mock_model)
        sys.create_module(ConcreteModule, name="test1")
        sys.create_module(ConcreteModule, name="test2")
        sys._initialize()
        return sys

    def test_setup_method(self, lifecycle_system):
        """测试设置方法

        场景：
        1. 调用 setup
        2. 验证系统和模块状态
        """
        lifecycle_system._setup()
        assert lifecycle_system.state == State.READY
        assert all(m.state == State.READY for m in lifecycle_system.modules.values())

    def test_step_method(self, lifecycle_system):
        """测试步进方法

        场景：
        1. 完成设置后步进
        2. 验证系统和模块状态
        """
        lifecycle_system._setup()
        lifecycle_system._step()
        assert lifecycle_system.state == State.READY
        assert all(m.state == State.READY for m in lifecycle_system.modules.values())

    def test_end_method(self, lifecycle_system):
        """测试结束方法

        场景：
        1. 完成运行后结束
        2. 验证系统和模块状态
        """
        lifecycle_system._setup()
        lifecycle_system._step()
        lifecycle_system._end()
        assert lifecycle_system.state == State.COMPLETE
        assert all(m.state == State.COMPLETE for m in lifecycle_system.modules.values())


class TestOpeningBehavior:
    """测试开启状态行为"""

    @pytest.fixture
    def system_with_modules(self, mock_model):
        sys = ConcreteSubSystem(model=mock_model)
        sys.create_module(ConcreteModule, name="m1")
        sys.create_module(ConcreteModule, name="m2")
        return sys

    @pytest.mark.parametrize(
        "module_states",
        [
            ([True, True], True),  # 全开启
            ([False, False], False),  # 全关闭
            ([True, False], True),  # 部分开启
        ],
    )
    def test_opening_states(self, system_with_modules, module_states):
        """测试开启状态逻辑

        场景：
        1. 所有模块开启
        2. 所有模块关闭
        3. 部分模块开启
        """
        states, expected = module_states
        for module, state in zip(system_with_modules.modules.values(), states):
            module._open = state
        assert system_with_modules.opening is expected

    def test_empty_system_opening(self, mock_model):
        """测试空系统的开启状态

        场景：
        1. 验证空系统的开启状态
        """
        system = ConcreteSubSystem(model=mock_model)
        assert not system.opening
