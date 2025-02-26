#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/


from datetime import datetime

import pendulum
import pytest
from pendulum import DateTime

from abses.core.primitives import VALID_DT_ATTRS
from abses.utils.time import is_positive_int, parse_datetime, parse_duration


class TestIsValidTimeUnit:
    """测试时间单位验证函数 is_positive_int"""

    @pytest.mark.parametrize(
        "value, expected",
        [
            (0, True),  # 零是有效的
            (1, True),  # 正整数是有效的
            (100, True),  # 大正整数是有效的
            (-1, False),  # 负数是无效的
            (1.5, False),  # 浮点数是无效的
            ("1", False),  # 字符串是无效的
            (None, False),  # None是无效的
        ],
    )
    def test_valid_time_unit_check(self, value, expected):
        """测试不同输入值的有效性检查"""
        assert is_positive_int(value) == expected

    def test_raise_error_when_invalid(self):
        """测试当raise_error=True时，无效值会引发ValueError"""
        with pytest.raises(ValueError):
            is_positive_int(-1, raise_error=True)

    def test_no_raise_error_when_valid(self):
        """测试当raise_error=True时，有效值不会引发错误"""
        try:
            result = is_positive_int(5, raise_error=True)
            assert result is True
        except ValueError:
            pytest.fail("Unexpected ValueError raised for valid input")


class TestParseDateTime:
    """测试日期时间解析函数 parse_datetime"""

    @pytest.fixture
    def sample_datetime(self):
        """返回一个示例datetime对象"""
        return pendulum.datetime(2023, 1, 1, 12, 0, 0)

    def test_datetime_input(self, sample_datetime):
        """测试输入已经是datetime对象的情况"""
        result = parse_datetime(sample_datetime)
        assert isinstance(result, DateTime)

    @pytest.mark.parametrize(
        "date_string, expected",
        [
            ("2023-01-01", datetime(2023, 1, 1)),  # 标准日期格式
            ("2023/01/01", datetime(2023, 1, 1)),  # 斜杠分隔的日期
            (
                "2023-01-01 12:30:45",
                datetime(2023, 1, 1, 12, 30, 45),
            ),  # 带时间的日期
            ("20230101", datetime(2023, 1, 1)),  # 紧凑格式
            ("Jan 1, 2023", datetime(2023, 1, 1)),  # 英文月份格式
        ],
    )
    def test_string_input(self, date_string, expected):
        """测试各种字符串格式的日期时间输入"""
        result = parse_datetime(date_string)
        assert result == pendulum.instance(expected, tz=None)
        assert isinstance(result, DateTime)

    def test_invalid_input(self):
        """测试无效输入类型引发TypeError"""
        invalid_inputs = [123, None, [], {}]
        for invalid in invalid_inputs:
            with pytest.raises((TypeError, ValueError)):
                parse_datetime(invalid)

    def test_invalid_date_string(self):
        """测试无效的日期字符串格式"""
        with pytest.raises(Exception):  # 可能会引发不同类型的异常
            parse_datetime("not-a-date")


class TestParseDuration:
    """测试持续时间解析函数 parse_duration"""

    def test_valid_duration(self):
        """测试有效的持续时间参数"""
        kwargs = {"days": 1, "hours": 2, "minutes": 30}
        result = parse_duration(kwargs)
        expected = pendulum.duration(days=1, hours=2, minutes=30)
        assert result == expected
        assert isinstance(result, pendulum.Duration)

    def test_zero_duration(self):
        """测试零持续时间"""
        kwargs = {"days": 0, "hours": 0, "seconds": 0}
        result = parse_duration(kwargs)
        expected = pendulum.duration()
        assert result == expected

    def test_empty_kwargs(self):
        """测试空参数字典"""
        result = parse_duration({})
        assert result is None

    def test_invalid_unit(self):
        """测试无效的时间单位"""
        kwargs = {"days": 1, "invalid_unit": 5}
        with pytest.raises(KeyError) as excinfo:
            parse_duration(kwargs)
        assert "invalid_unit" in str(excinfo.value)

    def test_negative_value(self):
        """测试负值时间单位"""
        kwargs = {"days": -1}
        with pytest.raises(KeyError) as excinfo:
            parse_duration(kwargs)
        assert "days" in str(excinfo.value)

    def test_non_integer_value(self):
        """测试非整数时间单位值"""
        kwargs = {"days": "1"}
        with pytest.raises(KeyError) as excinfo:
            parse_duration(kwargs)
        assert "days" in str(excinfo.value)

    @pytest.mark.parametrize("unit", VALID_DT_ATTRS)
    def test_all_valid_units(self, unit):
        """测试所有有效的时间单位"""
        kwargs = {unit: 1}
        result = parse_duration(kwargs)
        expected = pendulum.duration(**{unit: 1})
        assert result == expected
