#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""
测试 logging 相关功能。

测试内容：
1. 配置解析功能 (log_parser.py)
2. 日志设置功能 (log_config.py)
3. 实验日志设置 (exp_logging.py)
4. 模型日志设置 (logging.py)
5. 集成测试：完整的日志流程
"""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path

import pytest
from omegaconf import OmegaConf

from abses import MainModel
from abses.core.experiment import Experiment
from abses.utils.exp_logging import EXP_LOGGER_NAME, setup_exp_logger
from abses.utils.log_config import (
    DEFAULT_DATEFMT,
    DEFAULT_FORMAT,
    DEFAULT_LEVEL,
    create_console_handler,
    create_file_handler,
    determine_log_file_path,
    setup_abses_logger,
)
from abses.utils.log_parser import (
    get_file_config,
    get_log_mode,
    get_mesa_config,
    get_stdout_config,
)
from abses.utils.logging import setup_model_logger


class TestLogParser:
    """测试配置解析功能"""

    def test_get_log_mode_default(self) -> None:
        """测试获取默认日志模式"""
        cfg = {}
        assert get_log_mode(cfg) == "once"

    def test_get_log_mode_from_config(self) -> None:
        """测试从配置中获取日志模式"""
        cfg = {"log": {"mode": "separate"}}
        assert get_log_mode(cfg) == "separate"

        cfg = {"log": {"mode": "merge"}}
        assert get_log_mode(cfg) == "merge"

    def test_get_stdout_config_enabled(self) -> None:
        """测试获取启用的 stdout 配置"""
        cfg = {
            "log": {
                "run": {
                    "stdout": {
                        "enabled": True,
                        "level": "DEBUG",
                        "format": "[%(levelname)s] %(message)s",
                        "datefmt": "%Y-%m-%d",
                    }
                }
            }
        }
        stdout_cfg = get_stdout_config(cfg, "run")
        assert stdout_cfg["enabled"] is True
        assert stdout_cfg["level"] == "DEBUG"
        assert stdout_cfg["format"] == "[%(levelname)s] %(message)s"
        assert stdout_cfg["datefmt"] == "%Y-%m-%d"

    def test_get_stdout_config_disabled(self) -> None:
        """测试获取禁用的 stdout 配置"""
        cfg = {"log": {"run": {"stdout": {"enabled": False}}}}
        stdout_cfg = get_stdout_config(cfg, "run")
        assert stdout_cfg == {}

    def test_get_file_config_enabled(self) -> None:
        """测试获取启用的文件配置"""
        cfg = {
            "log": {
                "run": {
                    "file": {
                        "enabled": True,
                        "name": "test_model",
                        "level": "WARNING",
                        "format": "[%(levelname)s] %(message)s",
                        "rotation": "1 day",
                        "retention": "10 days",
                    }
                }
            }
        }
        file_cfg = get_file_config(cfg, "run")
        assert file_cfg["enabled"] is True
        assert file_cfg["name"] == "test_model"
        assert file_cfg["level"] == "WARNING"
        assert file_cfg["rotation"] == "1 day"
        assert file_cfg["retention"] == "10 days"

    def test_get_file_config_defaults(self) -> None:
        """测试文件配置的默认值"""
        cfg = {"log": {"run": {"file": {"enabled": True}}}}
        file_cfg = get_file_config(cfg, "run")
        assert file_cfg["name"] == "model"  # Default name for run
        assert file_cfg["level"] == DEFAULT_LEVEL
        assert file_cfg["format"] == DEFAULT_FORMAT
        assert file_cfg["datefmt"] == DEFAULT_DATEFMT

    def test_get_mesa_config(self) -> None:
        """测试获取 Mesa 配置"""
        cfg = {"log": {"run": {"mesa": {"level": "DEBUG", "format": "%(message)s"}}}}
        mesa_cfg = get_mesa_config(cfg, "run")
        assert mesa_cfg["level"] == "DEBUG"
        assert mesa_cfg["format"] == "%(message)s"

    def test_get_mesa_config_defaults(self) -> None:
        """测试 Mesa 配置的默认值"""
        cfg = {"log": {"run": {}}}
        mesa_cfg = get_mesa_config(cfg, "run")
        assert mesa_cfg["level"] is None
        assert mesa_cfg["format"] is None


class TestLogConfig:
    """测试日志配置功能"""

    def test_create_console_handler_defaults(self) -> None:
        """测试创建控制台处理器（使用默认值）"""
        handler = create_console_handler()
        assert handler.level == logging.getLevelName(DEFAULT_LEVEL)
        assert isinstance(handler, logging.StreamHandler)

    def test_create_console_handler_custom(self) -> None:
        """测试创建自定义控制台处理器"""
        handler = create_console_handler(
            level="DEBUG", fmt="%(message)s", datefmt="%Y-%m-%d"
        )
        assert handler.level == logging.DEBUG
        formatter = handler.formatter
        assert formatter._fmt == "%(message)s"
        assert formatter.datefmt == "%Y-%m-%d"

    def test_create_file_handler_defaults(self, tmp_path: Path) -> None:
        """测试创建文件处理器（使用默认值）"""
        log_file = tmp_path / "test.log"
        handler = create_file_handler(log_file)
        assert handler.level == logging.getLevelName(DEFAULT_LEVEL)
        assert isinstance(handler, logging.FileHandler)

    def test_create_file_handler_custom(self, tmp_path: Path) -> None:
        """测试创建自定义文件处理器"""
        log_file = tmp_path / "test.log"
        handler = create_file_handler(
            log_file, level="WARNING", fmt="%(message)s", datefmt="%Y-%m-%d"
        )
        assert handler.level == logging.WARNING
        formatter = handler.formatter
        assert formatter._fmt == "%(message)s"
        assert formatter.datefmt == "%Y-%m-%d"

    def test_determine_log_file_path_once_mode(self, tmp_path: Path) -> None:
        """测试确定日志文件路径（once 模式）"""
        # First repeat should create file
        path = determine_log_file_path(
            outpath=tmp_path, log_name="test", logging_mode="once", repeat_id=1
        )
        assert path == tmp_path / "test.log"

        # Subsequent repeats should return None
        path = determine_log_file_path(
            outpath=tmp_path, log_name="test", logging_mode="once", repeat_id=2
        )
        assert path is None

    def test_determine_log_file_path_separate_mode(self, tmp_path: Path) -> None:
        """测试确定日志文件路径（separate 模式）"""
        path1 = determine_log_file_path(
            outpath=tmp_path, log_name="test", logging_mode="separate", repeat_id=1
        )
        assert path1 == tmp_path / "test_1.log"

        path2 = determine_log_file_path(
            outpath=tmp_path, log_name="test", logging_mode="separate", repeat_id=2
        )
        assert path2 == tmp_path / "test_2.log"

    def test_determine_log_file_path_merge_mode(self, tmp_path: Path) -> None:
        """测试确定日志文件路径（merge 模式）"""
        path1 = determine_log_file_path(
            outpath=tmp_path, log_name="test", logging_mode="merge", repeat_id=1
        )
        assert path1 == tmp_path / "test.log"

        path2 = determine_log_file_path(
            outpath=tmp_path, log_name="test", logging_mode="merge", repeat_id=2
        )
        assert path2 == tmp_path / "test.log"  # Same file

    def test_setup_abses_logger_console_only(self) -> None:
        """测试设置 ABSESpy 日志器（仅控制台）"""
        logger = setup_abses_logger(
            name="test_logger", console=True, console_level="DEBUG"
        )
        assert logger.name == "test_logger"
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.StreamHandler)

    def test_setup_abses_logger_file_only(self, tmp_path: Path) -> None:
        """测试设置 ABSESpy 日志器（仅文件）"""
        log_file = tmp_path / "test.log"
        logger = setup_abses_logger(
            name="test_logger", console=False, file_path=log_file, file_level="WARNING"
        )
        assert logger.name == "test_logger"
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.FileHandler)
        assert log_file.exists()


class TestExpLogging:
    """测试实验日志功能"""

    def test_setup_exp_logger_stdout_only(self, tmp_path: Path) -> None:
        """测试设置实验日志器（仅控制台）"""
        cfg = OmegaConf.create(
            {
                "outpath": str(tmp_path),
                "log": {
                    "exp": {
                        "stdout": {"enabled": True, "level": "INFO"},
                        "file": {"enabled": False},
                    }
                },
            }
        )
        logger = setup_exp_logger(cfg)
        assert logger.name == EXP_LOGGER_NAME
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.StreamHandler)

    def test_setup_exp_logger_file_only(self, tmp_path: Path) -> None:
        """测试设置实验日志器（仅文件）"""
        cfg = OmegaConf.create(
            {
                "outpath": str(tmp_path),
                "log": {
                    "exp": {
                        "stdout": {"enabled": False},
                        "file": {
                            "enabled": True,
                            "name": "experiment.log",
                            "level": "INFO",
                        },
                    }
                },
            }
        )
        logger = setup_exp_logger(cfg)
        assert logger.name == EXP_LOGGER_NAME
        # When stdout is disabled, only file handler should be added
        assert len(logger.handlers) == 1
        # Check that file handler exists
        file_handlers = [
            h for h in logger.handlers if isinstance(h, logging.FileHandler)
        ]
        assert len(file_handlers) == 1
        assert (tmp_path / "experiment.log").exists()

    def test_setup_exp_logger_both(self, tmp_path: Path) -> None:
        """测试设置实验日志器（控制台和文件）"""
        cfg = OmegaConf.create(
            {
                "outpath": str(tmp_path),
                "log": {
                    "exp": {
                        "stdout": {"enabled": True, "level": "DEBUG"},
                        "file": {
                            "enabled": True,
                            "name": "experiment.log",
                            "level": "INFO",
                        },
                    }
                },
            }
        )
        logger = setup_exp_logger(cfg)
        assert logger.name == EXP_LOGGER_NAME
        assert len(logger.handlers) == 2

    def test_setup_exp_logger_separate_mode(self, tmp_path: Path) -> None:
        """测试 separate 模式下的实验日志器"""
        cfg = OmegaConf.create(
            {
                "outpath": str(tmp_path),
                "log": {
                    "mode": "separate",
                    "run": {"file": {"name": "model"}},
                    "exp": {"file": {"enabled": True}},
                },
            }
        )
        _ = setup_exp_logger(cfg)  # Setup logger
        # In separate mode, exp log should use run.file.name if not explicitly set
        assert (tmp_path / "model.log").exists()


class TestModelLogging:
    """测试模型日志功能"""

    def test_setup_model_logger_console_only(self, tmp_path: Path) -> None:
        """测试设置模型日志器（仅控制台）"""
        logger, mesa_logger, mesa_upper_logger = setup_model_logger(
            name="test_model",
            level="INFO",
            outpath=None,  # No outpath to disable file logging
            console=True,
            console_level="DEBUG",
            logging_mode="once",
        )
        assert logger.name == "abses"
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.StreamHandler)

    def test_setup_model_logger_file_only(self, tmp_path: Path) -> None:
        """测试设置模型日志器（仅文件）"""
        logger, mesa_logger, mesa_upper_logger = setup_model_logger(
            name="test_model",
            level="INFO",
            outpath=tmp_path,
            console=False,
            logging_mode="once",
            repeat_id=1,
        )
        assert logger.name == "abses"
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.FileHandler)
        assert (tmp_path / "test_model.log").exists()

    def test_setup_model_logger_custom_format(self, tmp_path: Path) -> None:
        """测试设置模型日志器（自定义格式）"""
        logger, mesa_logger, mesa_upper_logger = setup_model_logger(
            name="test_model",
            level="INFO",
            outpath=tmp_path,
            console=True,
            console_format="%(levelname)s: %(message)s",
            console_datefmt="%Y-%m-%d",
            file_format="[%(asctime)s] %(message)s",
            file_datefmt="%H:%M:%S",
            logging_mode="once",
            repeat_id=1,
        )
        # Check that handlers have correct formatters
        console_handler = next(
            (h for h in logger.handlers if isinstance(h, logging.StreamHandler)), None
        )
        assert console_handler is not None
        # Check format (may include datefmt in the format string)
        assert "%(levelname)s" in console_handler.formatter._fmt
        assert "%(message)s" in console_handler.formatter._fmt

        # Check file handler if it exists
        file_handler = next(
            (h for h in logger.handlers if isinstance(h, logging.FileHandler)), None
        )
        if file_handler is not None:
            assert "%(asctime)s" in file_handler.formatter._fmt
            assert "%(message)s" in file_handler.formatter._fmt


class TestLoggingIntegration:
    """测试日志功能的集成测试"""

    @pytest.fixture
    def temp_dir(self) -> Path:
        """创建临时目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_experiment_logging_integration(self, temp_dir: Path) -> None:
        """测试实验日志的完整流程"""
        cfg = OmegaConf.create(
            {
                "outpath": str(temp_dir),
                "log": {
                    "mode": "separate",
                    "exp": {
                        "stdout": {"enabled": True, "level": "INFO"},
                        "file": {"enabled": True, "name": "experiment.log"},
                    },
                    "run": {
                        "stdout": {"enabled": False},
                        "file": {
                            "enabled": True,
                            "name": "model",
                            "level": "INFO",
                        },
                    },
                },
            }
        )

        # Setup experiment logger
        exp_logger = setup_exp_logger(cfg)

        try:
            # Check handlers
            file_handlers = [
                h for h in exp_logger.handlers if isinstance(h, logging.FileHandler)
            ]
            if file_handlers:
                # Get the actual file path from the handler
                actual_file_path = Path(file_handlers[0].baseFilename)
                exp_logger.info("Experiment started")
                # Force flush to ensure file is written
                file_handlers[0].flush()
                # Verify the actual file exists
                assert actual_file_path.exists(), (
                    f"Log file not found at {actual_file_path}. Files in temp_dir: {list(temp_dir.iterdir())}"
                )
            else:
                # No file handler was created, which might be expected in some cases
                # But in this test we expect one
                assert False, f"No file handler found. Handlers: {exp_logger.handlers}"
        finally:
            # Close all handlers to release file handles (required on Windows)
            for handler in exp_logger.handlers[:]:
                handler.close()
                exp_logger.removeHandler(handler)

    def test_model_logging_integration(self, temp_dir: Path) -> None:
        """测试模型日志的完整流程"""
        _ = {
            "outpath": str(temp_dir),
            "log": {
                "mode": "once",
                "run": {
                    "stdout": {"enabled": True, "level": "INFO"},
                    "file": {
                        "enabled": True,
                        "name": "model",
                        "level": "INFO",
                    },
                },
            },
        }

        # Setup model logger
        logger, mesa_logger, mesa_upper_logger = setup_model_logger(
            name="model",
            level="INFO",
            outpath=temp_dir,
            console=True,
            logging_mode="once",
            repeat_id=1,
        )
        try:
            logger.info("Model started")

            # Verify model log file exists
            assert (temp_dir / "model.log").exists()
        finally:
            # Close all handlers to release file handles (required on Windows)
            for log in [logger, mesa_logger, mesa_upper_logger]:
                for handler in log.handlers[:]:
                    handler.close()
                    log.removeHandler(handler)

    def test_logging_modes(self, temp_dir: Path) -> None:
        """测试不同的日志模式"""
        # Test once mode
        path1 = determine_log_file_path(
            outpath=temp_dir, log_name="model", logging_mode="once", repeat_id=1
        )
        path2 = determine_log_file_path(
            outpath=temp_dir, log_name="model", logging_mode="once", repeat_id=2
        )
        assert path1 == temp_dir / "model.log"
        assert path2 is None

        # Test separate mode
        path1 = determine_log_file_path(
            outpath=temp_dir, log_name="model", logging_mode="separate", repeat_id=1
        )
        path2 = determine_log_file_path(
            outpath=temp_dir, log_name="model", logging_mode="separate", repeat_id=2
        )
        assert path1 == temp_dir / "model_1.log"
        assert path2 == temp_dir / "model_2.log"

        # Test merge mode
        path1 = determine_log_file_path(
            outpath=temp_dir, log_name="model", logging_mode="merge", repeat_id=1
        )
        path2 = determine_log_file_path(
            outpath=temp_dir, log_name="model", logging_mode="merge", repeat_id=2
        )
        assert path1 == temp_dir / "model.log"
        assert path2 == temp_dir / "model.log"

    def test_experiment_with_logging(self, temp_dir: Path) -> None:
        """测试实验运行时的日志功能"""
        # Clean ExperimentManager singleton to avoid conflicts with other tests
        from abses.core.job_manager import ExperimentManager

        # Save and reset the singleton instance
        original_instance = getattr(ExperimentManager, "_instance", None)
        ExperimentManager._instance = None

        try:
            cfg = OmegaConf.create(
                {
                    "outpath": str(temp_dir),
                    "time": {"end": 2},  # Add time config to avoid errors
                    "log": {
                        "mode": "once",
                        "exp": {
                            "stdout": {"enabled": True, "level": "INFO"},
                            "file": {"enabled": True},
                        },
                        "run": {
                            "stdout": {"enabled": False},
                            "file": {"enabled": True, "name": "model"},
                        },
                    },
                }
            )

            class TestModel(MainModel):
                def setup(self):
                    pass

                def step(self):
                    pass

            # Create and run experiment
            exp = Experiment.new(TestModel, cfg)

            # Get the actual outpath used by experiment
            actual_outpath = exp.outpath

            exp.batch_run(repeats=2, display_progress=False)

            # Verify log files exist
            # Files are created in exp.outpath, not necessarily temp_dir
            exp_log = actual_outpath / "experiment.log"
            model_log = actual_outpath / "model.log"
            assert exp_log.exists(), (
                f"Experiment log not found at {exp_log}. Files in {actual_outpath}: {list(actual_outpath.iterdir()) if actual_outpath.exists() else 'directory does not exist'}"
            )
            assert model_log.exists(), (
                f"Model log not found at {model_log}. Files in {actual_outpath}: {list(actual_outpath.iterdir()) if actual_outpath.exists() else 'directory does not exist'}"
            )
        finally:
            # Close all log handlers to release file handles (required on Windows)
            for logger_name in ["abses.core.experiment", "abses", "mesa", "MESA"]:
                log = logging.getLogger(logger_name)
                for handler in log.handlers[:]:
                    handler.close()
                    log.removeHandler(handler)
            # Restore the original instance
            ExperimentManager._instance = original_instance
