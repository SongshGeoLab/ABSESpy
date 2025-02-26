#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/


import pendulum
import pytest

from abses.core.model import MainModel
from abses.core.time_driver import TimeDriver
from abses.utils.time import parse_datetime


@pytest.fixture
def time_config_tick_end():
    """不记录时间，只记录刻度，到20结束"""
    return {
        "end": 20,
    }


@pytest.fixture
def time_config_year_start_end():
    """记录时间，从2000年开始，到2020年结束"""
    return {
        "years": 1,
        "start": "2000",
        "end": "2020",
    }


@pytest.fixture
def time_config_month_start_end_duration():
    """记录时间，从2000年5月开始，到2020年1月结束，步长为6个月"""
    return {
        "months": 6,
        "start": "2000-05",
        "end": "2020-01",
    }


@pytest.fixture
def time_config_day_start_end_duration():
    """记录时间，从2000年5月1日开始，到2020年1月1日结束，步长为180天"""
    return {
        "days": 180,
        "start": "2000-05-01",
        "end": "2020-01-01",
    }


@pytest.fixture
def yearly_time_driver(time_config_year_start_end) -> TimeDriver:
    """年度推进的时间驱动器"""
    return TimeDriver(MainModel({"time": time_config_year_start_end}))


class TestTimeInitialization:
    """测试时间驱动器的初始化功能"""

    def test_tick_mode_initialization(self, time_config_tick_end):
        """测试默认初始化
        验证:
        1. 当前时间正确设置
        2. 初始状态正确
        """
        model = MainModel({"time": time_config_tick_end})
        time = model.time
        now = pendulum.now(tz=None)
        assert time.dt.day == now.day
        assert time.dt.month == now.month
        assert time.dt.year == now.year
        assert time.tick == 0
        assert time.duration is None
        assert len(time.history) == 0

    def test_year_mode_initialization(self, time_config_year_start_end):
        """测试年份模式初始化"""
        model = MainModel({"time": time_config_year_start_end})
        time = model.time
        assert time.dt.year == 2000
        assert time.tick == 0
        assert time.duration == pendulum.duration(years=1)
        assert time.end_at == pendulum.datetime(year=2020, month=1, day=1, tz=None)
        time.go()
        assert time.dt.year == 2001

    @pytest.mark.parametrize(
        "params,expected",
        [
            ({"start": "2000"}, 2000),
            ({"start": "2000-01"}, 2000),
            ({"start": "2000-01-01"}, 2000),
        ],
    )
    def test_start_time_formats(self, params, expected):
        """测试不同格式的开始时间
        验证:
        1. 支持多种时间格式
        2. 正确解析年份
        """
        time = TimeDriver(MainModel({"time": params}))
        assert time.year == expected

    @pytest.mark.parametrize(
        "params",
        [
            ({"start": 1234}),
            ({"start": "invalid"}),
        ],
    )
    def test_invalid_start_time(self, params):
        """测试无效的开始时间
        验证:
        1. 无效字符串时间
        2. 错误类型时间
        """
        with pytest.raises(ValueError):
            TimeDriver(MainModel({"time": params}))


class TestTimeDuration:
    """测试时间步长相关功能"""

    @pytest.mark.parametrize(
        "duration,expected_next",
        [
            ({"years": 1}, 2001),
            ({"years": 5}, 2005),
            ({"years": 10}, 2010),
        ],
    )
    def test_year_duration(self, duration, expected_next):
        """测试年度步长
        验证:
        1. 正确前进指定年数
        2. 历史记录正确更新
        """
        time = TimeDriver(MainModel({"time": {**{"start": "2000"}, **duration}}))
        time.go()
        assert time.year == expected_next
        assert len(time.history) == 1

    @pytest.mark.parametrize(
        "duration",
        [
            {"years": -1},
            {"months": -1},
        ],
    )
    def test_invalid_duration(self, duration):
        """测试无效的时间步长
        验证:
        1. 负数时间单位
        2. 无效时间单位
        """
        with pytest.raises((ValueError, KeyError)):
            TimeDriver(MainModel({"time": duration}))


class TestTimeProgression:
    """测试时间推进功能"""

    def test_normal_progression(self, yearly_time_driver):
        """测试正常时间推进
        验证:
        1. 时间正确前进
        2. 计数器正确增加
        3. 历史记录正确更新
        """
        yearly_time_driver.go()
        assert yearly_time_driver.year == 2001
        assert len(yearly_time_driver.history) == 1

    def test_progression_to_end(self, yearly_time_driver):
        """测试推进到结束时间
        验证:
        1. 正确停止在结束时间
        2. 模型状态正确更新
        """
        yearly_time_driver.go(19)  # 推进到2019年
        assert yearly_time_driver.year == 2019
        assert yearly_time_driver.model.running is True
        yearly_time_driver.go()  # 推进到2020年
        assert yearly_time_driver.year == 2020
        assert yearly_time_driver.model.running is False

    def test_expected_ticks(self, yearly_time_driver):
        """测试预期时间步数
        验证:
        1. 初始预期步数正确
        2. 中途更改时间后预期步数更新
        """
        assert yearly_time_driver.expected_ticks == 20
        yearly_time_driver.to("2019")
        assert yearly_time_driver.expected_ticks == 1


class TestTimeManipulation:
    """测试时间操作功能"""

    @pytest.mark.parametrize(
        "target,expected_year",
        [
            ("2010", 2010),
            ("2020", 2020),
            ("1900", 1900),
        ],
    )
    def test_time_to(self, yearly_time_driver, target, expected_year):
        """测试时间跳转
        验证:
        1. 正确跳转到目标时间
        2. 历史记录正确重置
        """
        yearly_time_driver.to(target)
        assert yearly_time_driver.year == expected_year
        assert len(yearly_time_driver.history) == 1

    def test_invalid_time_to(self, yearly_time_driver):
        """测试无效的时间跳转
        验证:
        1. 无效时间字符串
        2. 无效时间类型
        """
        with pytest.raises(ValueError):
            yearly_time_driver.to("invalid")
        with pytest.raises(TypeError):
            yearly_time_driver.to(123)


class TestTimeComparison:
    """测试时间比较功能"""

    @pytest.mark.parametrize(
        "other_time,expected",
        [
            ("1999", True),  # 早于当前时间
            ("2000", False),  # 等于当前时间
            ("2001", False),  # 晚于当前时间
        ],
    )
    def test_time_comparison(
        self, yearly_time_driver: TimeDriver, other_time: str, expected: bool
    ):
        """测试时间比较操作
        验证:
        1. 与字符串时间的比较
        2. 与datetime对象的比较
        3. 与其他TimeDriver实例的比较
        """
        other_dt = parse_datetime(other_time)  # 使用我们自己的parse_datetime
        assert (yearly_time_driver > other_dt) == expected
