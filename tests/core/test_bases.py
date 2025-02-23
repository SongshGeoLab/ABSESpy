#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from pathlib import Path
from unittest.mock import Mock, PropertyMock

import pytest
from omegaconf import DictConfig, OmegaConf

from abses.core.base import (
    BaseMainModel,
    BaseModelElement,
    BaseModule,
    BaseObservable,
    BaseObserver,
    State,
)


class MockObserver(BaseObserver):
    """用于测试的观察者类"""

    def __init__(self):
        self.update_called = False
        self.last_observable = None

    def update(self, observable):
        self.update_called = True
        self.last_observable = observable


class TestBaseObservable:
    """测试基础可观察类"""

    @pytest.fixture
    def observable(self):
        """创建一个基础可观察对象"""
        return BaseObservable()

    @pytest.fixture
    def observer(self):
        """创建一个模拟观察者"""
        return MockObserver()

    def test_attach_observer(self, observable, observer):
        """测试添加观察者

        场景：
        1. 添加一个新观察者
        2. 重复添加同一个观察者
        """
        # 添加观察者
        observable.attach(observer)
        assert observer in observable._observers

        # 重复添加同一个观察者不应该产生重复
        observable.attach(observer)
        assert len(observable._observers) == 1

    def test_detach_observer(self, observable, observer):
        """测试移除观察者

        场景：
        1. 移除已存在的观察者
        2. 移除不存在的观察者
        """
        # 添加然后移除观察者
        observable.attach(observer)
        observable.detach(observer)
        assert observer not in observable._observers

        # 移除不存在的观察者不应该抛出异常
        observable.detach(observer)

    @pytest.mark.parametrize("num_observers", [0, 1, 3])
    def test_notify_observers(self, observable, num_observers):
        """测试通知观察者

        场景：
        1. 通知多个观察者
        2. 没有观察者时的通知
        3. 确保所有观察者都被通知到
        """
        # 创建多个观察者
        observers = [MockObserver() for _ in range(num_observers)]
        for obs in observers:
            observable.attach(obs)

        # 发送通知
        observable.notify()

        # 验证所有观察者都收到通知
        for obs in observers:
            assert obs.update_called
            assert obs.last_observable == observable

    def test_notify_with_no_observers(self, observable):
        """测试没有观察者时的通知行为

        场景：
        1. 空观察者列表时的通知
        """
        # 不应该抛出异常
        observable.notify()


class TestBaseModelElement:
    """测试基础模型元素类"""

    @pytest.fixture
    def mock_model(self):
        """创建模拟的主模型，包含基本设置"""
        model = Mock()
        settings = DictConfig(
            {
                "test_element": {"param1": "value1", "param2": 42},
                "empty_element": {},
            }
        )
        type(model).settings = PropertyMock(return_value=settings)
        return model

    @pytest.fixture
    def element(self, mock_model):
        """创建一个基本的模型元素实例"""

        class ConcreteModelElement(BaseModelElement):
            pass

        return ConcreteModelElement(model=mock_model, name="test_element")

    @pytest.mark.parametrize(
        "name,expected_name",
        [
            ("custom_name", "custom_name"),  # 显式指定名称
            (None, "ConcreteModelElement"),  # 默认使用类名小写
        ],
    )
    def test_element_name(self, mock_model, name, expected_name):
        """测试模型元素名称属性

        场景：
        1. 显式指定名称
        2. 未指定名称时使用类名
        """

        class ConcreteModelElement(BaseModelElement):
            pass

        element = ConcreteModelElement(model=mock_model, name=name)
        assert element.name == expected_name

    def test_model_property(self, mock_model):
        """测试模型属性

        场景：
        1. 确保返回正确的模型实例
        2. 确保模型实例不可修改
        """
        element = BaseModelElement(model=mock_model)
        assert element.model == mock_model
        # 确保 model 属性不可修改
        with pytest.raises(AttributeError):
            element.model = Mock()

    @pytest.mark.parametrize(
        "element_name,expected_params",
        [
            ("test_element", {"param1": "value1", "param2": 42}),  # 存在的配置
            ("empty_element", {}),  # 空配置
            ("non_existent", {}),  # 不存在的配置
        ],
    )
    def test_params_property(self, mock_model, element_name, expected_params):
        """测试参数属性

        场景：
        1. 获取已配置的参数
        2. 获取空配置的参数
        3. 获取不存在配置的参数
        4. 确保所有组件共享同一配置源
        """
        element1 = BaseModelElement(mock_model, "test_element")
        element2 = BaseModelElement(mock_model, "test_element")

        # 确保两个实例共享相同的配置
        assert element1.params is element2.params

        # 测试不存在的配置返回空 DictConfig
        element3 = BaseModelElement(mock_model, "non_existent")
        assert isinstance(element3.params, DictConfig)
        assert not element3.params

    def test_model_required(self):
        """测试模型参数必需性

        场景：
        1. 创建元素时必须提供模型实例
        """
        with pytest.raises(TypeError):
            BaseModelElement()  # 不提供 model 参数应该引发错误

    def test_immutable_properties(self, element):
        """测试属性不可变性

        场景：
        1. 确保所有属性都是只读的
        """
        with pytest.raises(AttributeError):
            element.name = "new_name"
        with pytest.raises(AttributeError):
            element.params = {}
        with pytest.raises(AttributeError):
            element.model = Mock()

    def test_dict_config_conversion(self, mock_model):
        """测试 DictConfig 转换

        场景：
        1. 确保返回的参数是 DictConfig 类型
        2. 确保空参数也是 DictConfig 类型
        """
        element = BaseModelElement(mock_model, "test_element")
        assert isinstance(element.params, DictConfig)

        element_empty = BaseModelElement(mock_model, "non_existent")
        assert isinstance(element_empty.params, DictConfig)


class ConcreteMainModel(BaseMainModel):
    """用于测试的具体主模型类"""

    pass


class TestBaseMainModel:
    """测试基础主模型类"""

    @pytest.fixture
    def base_params(self) -> DictConfig:
        """创建基础参数配置"""
        return OmegaConf.create(
            {
                "name": "test_model",
                "version": "1.0.0",
                "outpath": "/test/path",
                "model": {"param1": "value1", "param2": 42},
                "ds": {"dataset1": {"path": "path1"}, "dataset2": {"path": "path2"}},
            }
        )

    @pytest.fixture
    def mock_experiment(self):
        """创建模拟实验对象"""
        return Mock()

    @pytest.mark.parametrize(
        "params,kwargs,expected_name",
        [
            (DictConfig({"name": "explicit_name"}), {}, "explicit_name"),
            (DictConfig({}), {"name": "kwarg_name"}, "kwarg_name"),
            (DictConfig({}), {}, "ConcreteMainModel"),  # 默认使用类名
            (
                DictConfig({"name": "param_name"}),
                {"name": "kwarg_name"},
                "kwarg_name",
            ),  # kwargs优先
        ],
    )
    def test_model_name(self, params, kwargs, expected_name):
        """测试模型名称属性

        场景：
        1. 从参数中获取显式名称
        2. 从kwargs中获取名称
        3. 使用默认类名
        4. 测试参数优先级
        """
        model = ConcreteMainModel(parameters=params, **kwargs)
        assert model.name == expected_name

    @pytest.mark.parametrize(
        "path_config,expected_path",
        [
            ("/custom/path", Path("/custom/path")),
            (None, Path.cwd() / "ConcreteMainModel"),  # 默认路径
            ("relative/path", Path("relative/path")),
        ],
    )
    def test_outpath(self, path_config, expected_path):
        """测试输出路径属性

        场景：
        1. 自定义绝对路径
        2. 默认路径（当前目录/模型名）
        3. 相对路径
        """
        params = DictConfig({"outpath": path_config} if path_config is not None else {})
        model = ConcreteMainModel(parameters=params)
        assert model.outpath == expected_path

    def test_experiment_integration(self, mock_experiment):
        """测试实验集成

        场景：
        1. 带实验初始化
        2. 不带实验初始化
        """
        model_with_exp = ConcreteMainModel(experiment=mock_experiment)
        assert model_with_exp.exp == mock_experiment

        model_without_exp = ConcreteMainModel()
        assert model_without_exp.exp is None

    def test_version_handling(self):
        """测试版本处理

        场景：
        1. 指定版本
        2. 未指定版本
        """
        model_with_version = ConcreteMainModel(
            parameters=DictConfig({"version": "1.0.0"})
        )
        assert model_with_version.version == "1.0.0"

        model_without_version = ConcreteMainModel()
        assert model_without_version.version is None

    def test_datasets_access(self, base_params):
        """测试数据集访问

        场景：
        1. 访问已配置的数据集
        2. 访问空数据集配置
        3. 测试数据集别名(ds)
        """
        model = ConcreteMainModel(parameters=base_params)
        assert "dataset1" in model.datasets
        assert "dataset2" in model.datasets
        assert model.datasets == model.ds  # 测试别名

        empty_model = ConcreteMainModel()
        assert isinstance(empty_model.datasets, DictConfig)
        assert not empty_model.datasets  # 空配置

    def test_params_access(self, base_params):
        """测试参数访问

        场景：
        1. 访问模型参数
        2. 访问空参数配置
        """
        model = ConcreteMainModel(parameters=base_params)
        assert model.params["param1"] == "value1"
        assert model.params["param2"] == 42

        empty_model = ConcreteMainModel()
        assert isinstance(empty_model.params, DictConfig)
        assert not empty_model.params

    def test_settings_merge(self):
        """测试设置合并

        场景：
        1. 基础参数与kwargs合并
        2. 嵌套参数合并
        3. 参数覆盖
        """
        base = DictConfig({"a": 1, "nested": {"x": 1}})
        kwargs = {"a": 2, "nested.y": 2, "new": 3}

        model = ConcreteMainModel(parameters=base, **kwargs)
        assert model.settings.a == 2  # 覆盖已存在的参数
        assert model.settings.nested.x == 1  # 保持已存在的嵌套参数
        assert model.settings.nested.y == 2  # 添加新的嵌套参数
        assert model.settings.new == 3  # 添加新参数

    def test_rng_seed_handling(self):
        """测试随机数生成器和种子处理

        场景：
        1. 指定种子，验证可重复性
        2. 不同种子产生不同结果
        3. 默认随机种子
        """
        # 测试种子的可重复性
        model1 = ConcreteMainModel(seed=42)
        model2 = ConcreteMainModel(seed=42)
        assert model1.random.random() == model2.random.random()

        # 测试不同种子产生不同结果
        model3 = ConcreteMainModel(seed=43)
        assert model1.random.random() != model3.random.random()

        # 测试默认随机种子
        model4 = ConcreteMainModel()
        model5 = ConcreteMainModel()
        # 默认种子应该产生不同的结果
        assert model4.random.random() != model5.random.random()


class ConcreteModule(BaseModule):
    """用于测试的具体模块类"""

    pass


class TestBaseModule:
    """测试基础模块类"""

    @pytest.fixture
    def mock_model(self):
        """创建模拟的主模型"""
        model = Mock()
        model.settings = DictConfig({"test_module": {"param1": "value1"}})
        return model

    @pytest.fixture
    def module(self, mock_model):
        """创建一个基本的模块实例"""
        return ConcreteModule(model=mock_model, name="test_module")

    def test_initial_state(self, module):
        """测试模块初始状态

        场景：
        1. 验证初始状态为 NEW
        2. 验证初始时模块是开启的
        """
        assert module.state == State.NEW
        assert module.opening is True

    @pytest.mark.parametrize(
        "state_sequence",
        [
            [State.NEW, State.INIT, State.READY, State.COMPLETE],  # 正常状态转换序列
            [State.NEW, State.INIT, State.COMPLETE],  # 跳过 READY 状态
            [State.NEW, State.COMPLETE],  # 直接到完成状态
        ],
    )
    def test_valid_state_transitions(self, module, state_sequence):
        """测试有效的状态转换

        场景：
        1. 完整的状态转换序列
        2. 跳过中间状态
        3. 直接到最终状态
        """
        for new_state in state_sequence[1:]:  # 跳过第一个状态（NEW）
            module.set_state(new_state)
            assert module.state == new_state

    @pytest.mark.parametrize(
        "invalid_sequence",
        [
            (State.INIT, State.NEW),  # 回退到初始状态
            (State.READY, State.INIT),  # 回退到之前状态
            (State.COMPLETE, State.READY),  # 从完成状态回退
        ],
    )
    def test_invalid_state_transitions(self, module, invalid_sequence):
        """测试无效的状态转换

        场景：
        1. 尝试回退到初始状态
        2. 尝试回退到之前状态
        3. 从完成状态回退
        """
        current_state, invalid_state = invalid_sequence
        module.set_state(current_state)
        with pytest.raises(ValueError, match="State cannot retreat"):
            module.set_state(invalid_state)

    def test_repeat_state_setting(self, module):
        """测试重复设置相同状态

        场景：
        1. 尝试重复设置当前状态
        """
        module.set_state(State.INIT)
        with pytest.raises(ValueError, match="Setting state repeat"):
            module.set_state(State.INIT)

    @pytest.mark.parametrize("opening", [True, False])
    def test_reset(self, module, opening):
        """测试模块重置

        场景：
        1. 重置为开启状态
        2. 重置为关闭状态
        3. 验证状态重置为 NEW
        """
        # 先改变状态和开启状态
        module.set_state(State.COMPLETE)
        module._open = not opening  # 设置为与要测试的相反状态

        # 执行重置
        module.reset(opening=opening)

        # 验证重置结果
        assert module.state == State.NEW
        assert module.opening == opening

    def test_state_property_access(self, module):
        """测试状态属性的访问

        场景：
        1. 通过属性访问器获取状态
        2. 通过属性设置器设置状态
        """
        # 测试状态获取
        assert module.state == State.NEW

        # 测试直接设置状态
        module.state = State.INIT
        assert module.state == State.INIT

        # 测试通过 set_state 设置状态
        module.set_state(State.READY)
        assert module.state == State.READY

    @pytest.mark.parametrize(
        "name, expected_name",
        [
            ("custom_name", "custom_name"),
            (None, "ConcreteModule"),
        ],
    )
    def test_module_name_inheritance(self, mock_model, name, expected_name):
        """测试模块名称继承

        场景：
        1. 显式指定名称
        2. 使用默认类名
        """
        named_module = ConcreteModule(mock_model, name=name)
        assert named_module.name == expected_name
