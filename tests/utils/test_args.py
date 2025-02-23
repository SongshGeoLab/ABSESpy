#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

import pytest
from omegaconf import DictConfig, OmegaConf

from abses.utils.args import merge_parameters


class TestMergeParameters:
    """测试参数合并功能"""

    @pytest.fixture(scope="function")
    def base_config(self) -> DictConfig:
        """创建基础配置"""
        return OmegaConf.create(
            {
                "simple": "value",
                "nested": {"key1": "value1", "key2": 42},
                "list": [1, 2, 3],
                "empty_dict": {},
            }
        )

    @pytest.mark.parametrize(
        "kwargs, expected",
        [
            # 基本测试：添加新参数
            (
                {"new_param": "new_value"},
                {
                    "simple": "value",
                    "nested": {"key1": "value1", "key2": 42},
                    "list": [1, 2, 3],
                    "empty_dict": {},
                    "new_param": "new_value",
                },
            ),
            # 覆盖已存在的参数
            (
                {"simple": "new_value"},
                {
                    "simple": "new_value",
                    "nested": {"key1": "value1", "key2": 42},
                    "list": [1, 2, 3],
                    "empty_dict": {},
                },
            ),
            # 更新嵌套字典
            (
                {"nested.key1": "updated"},
                {
                    "simple": "value",
                    "nested": {"key1": "updated", "key2": 42},
                    "list": [1, 2, 3],
                    "empty_dict": {},
                },
            ),
            # 添加新的嵌套参数
            (
                {"nested.key3": "new_nested"},
                {
                    "simple": "value",
                    "nested": {"key1": "value1", "key2": 42, "key3": "new_nested"},
                    "list": [1, 2, 3],
                    "empty_dict": {},
                },
            ),
        ],
    )
    def test_basic_merge(self, base_config: DictConfig, kwargs, expected):
        """测试基本的参数合并功能

        场景：
        1. 添加新参数
        2. 覆盖已存在的参数
        3. 更新嵌套字典中的值
        4. 添加新的嵌套参数
        """
        result = merge_parameters(base_config, **kwargs)
        assert OmegaConf.to_container(result) == expected

    @pytest.mark.parametrize(
        "kwargs, expected_structure",
        [
            (
                {"nested.non_existent.key": "value"},
                {
                    "nested": {
                        "non_existent": {"key": "value"},
                        "key1": "value1",
                        "key2": 42,
                    }
                },
            ),
            ({"new.deep.path": 42}, {"new": {"deep": {"path": 42}}}),
        ],
    )
    def test_nested_path_creation(
        self, base_config: DictConfig, kwargs, expected_structure
    ):
        """测试嵌套路径的自动创建

        场景：
        1. 访问不存在的嵌套路径时会自动创建结构
        2. 创建多层嵌套结构
        """
        result = merge_parameters(base_config, **kwargs)
        for key in expected_structure:
            assert key in result
            assert OmegaConf.to_container(result[key]) == expected_structure[key]

    def test_empty_merge(self, base_config: DictConfig):
        """测试空参数合并

        场景：
        1. 不提供任何新参数
        2. 确保原配置不被修改
        """
        result = merge_parameters(base_config)
        assert OmegaConf.to_container(result) == OmegaConf.to_container(base_config)
        assert result is not base_config  # 确保返回新对象

    def test_type_preservation(self, base_config: DictConfig):
        """测试类型保持

        场景：
        1. 确保合并后返回的仍是 DictConfig 类型
        2. 确保嵌套的字典也是 DictConfig 类型
        """
        result = merge_parameters(base_config, new_nested={"key": "value"})
        assert isinstance(result, DictConfig)
        assert isinstance(result.get("new_nested"), DictConfig)

    @pytest.mark.parametrize(
        "value_type, expected",
        [
            ({"int_val": 42}, 42),
            ({"float_val": 3.14}, 3.14),
            ({"bool_val": True}, True),
            ({"none_val": None}, "None"),  # OmegaConf 将 None 转换为字符串
            ({"list_val": [1, 2, 3]}, [1, 2, 3]),
            ({"dict_val": {"key": "value"}}, {"key": "value"}),
        ],
    )
    def test_value_types(self, base_config: DictConfig, value_type, expected):
        """测试不同类型值的合并

        场景：
        1. 整数值
        2. 浮点数值
        3. 布尔值
        4. None 值（会被转换为字符串 'None'）
        5. 列表值
        6. 字典值
        """
        result = merge_parameters(base_config, **value_type)
        key = list(value_type.keys())[0]
        assert OmegaConf.to_container(result)[key] == expected

    def test_immutability(self, base_config: DictConfig):
        """测试原配置不变性

        场景：
        1. 确保原配置在合并后保持不变
        2. 确保返回新的配置对象
        """
        original = OmegaConf.to_container(base_config)
        result = merge_parameters(base_config, new_key="new_value")

        assert OmegaConf.to_container(base_config) == original
        assert result is not base_config
