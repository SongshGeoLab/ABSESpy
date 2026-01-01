#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : ABSESpy Team
from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional

from omegaconf import DictConfig

from abses.utils.errors import ConfigurationError
from abses.utils.logging import logger
from abses.utils.tracker import TrackerProtocol
from abses.utils.tracker.default import DefaultTracker

if TYPE_CHECKING:
    from abses.core.model import MainModel


def _to_plain(cfg: DictConfig) -> Dict:
    """Convert DictConfig to plain dict safely."""
    from omegaconf import OmegaConf

    return OmegaConf.to_container(cfg, resolve=True)


def prepare_tracker_run_name(
    tracker_cfg: DictConfig | Dict,
    model_name: str,
    version: str,
    run_id: Optional[int],
) -> str:
    """Prepare tracker run name from configuration or use default.

    Args:
        tracker_cfg: Tracker configuration.
        model_name: Name of the model.
        version: Version of the model.
        run_id: Optional run ID.

    Returns:
        Formatted run name.
    """
    template_vars = {
        "model_name": model_name,
        "run_id": str(run_id) if run_id is not None else "",
        "version": version,
    }

    run_name_template = tracker_cfg.get("run_name", None)
    if not run_name_template:
        return f"{model_name}_run_{run_id}" if run_id is not None else model_name

    try:
        run_name = run_name_template.format(**template_vars)
        return run_name.replace("__", "_").strip("_")
    except (KeyError, ValueError):
        logger.warning(
            f"Failed to format run_name template '{run_name_template}', using as-is."
        )
        return run_name_template


def prepare_tracker_tags(
    tracker_cfg: DictConfig | Dict,
    model_name: str,
    version: str,
    run_id: Optional[int],
) -> Dict[str, str]:
    """Prepare tracker tags from configuration or use default.

    Args:
        tracker_cfg: Tracker configuration.
        model_name: Name of the model.
        version: Version of the model.
        run_id: Optional run ID.

    Returns:
        Dictionary of tags.
    """
    from omegaconf import OmegaConf

    template_vars = {
        "model_name": model_name,
        "run_id": str(run_id) if run_id is not None else "",
        "version": version,
    }

    tags_config = tracker_cfg.get("tags", None)
    if not tags_config:
        tags = {"model": model_name, "version": version}
        if run_id is not None:
            tags["run_id"] = str(run_id)
        return tags

    # Convert to plain dict if needed
    if isinstance(tags_config, DictConfig):
        tags = OmegaConf.to_container(tags_config, resolve=True)
    else:
        tags = dict(tags_config)

    if not isinstance(tags, dict):
        return {"model": model_name, "version": version}

    processed_tags = {}
    for k, v in tags.items():
        if isinstance(v, str) and ("{" in v and "}" in v):
            try:
                processed_tags[k] = v.format(**template_vars)
            except (KeyError, ValueError):
                logger.warning(f"Failed to format tag '{k}' value '{v}', using as-is.")
                processed_tags[k] = v
        else:
            processed_tags[k] = v

    return processed_tags


def start_tracker_run(
    tracker: Optional[TrackerProtocol],
    tracker_cfg: DictConfig | Dict,
    model_name: str,
    version: str,
    run_id: Optional[int],
    model_params: DictConfig | Dict,
) -> None:
    """Start tracker run and log parameters.

    Args:
        tracker: Tracker backend instance (None for no-op).
        tracker_cfg: Tracker configuration.
        model_name: Name of the model.
        version: Version of the model.
        run_id: Optional run ID.
        model_params: Model parameters to log as hyperparameters.
    """
    if tracker is None:
        return

    from omegaconf import OmegaConf

    run_name = prepare_tracker_run_name(tracker_cfg, model_name, version, run_id)
    tags = prepare_tracker_tags(tracker_cfg, model_name, version, run_id)
    tracker.start_run(run_name=run_name, tags=tags)

    # Log model parameters as hyperparameters
    if isinstance(tracker_cfg, DictConfig):
        cfg_dict = OmegaConf.to_container(tracker_cfg, resolve=True)
    else:
        cfg_dict = dict(tracker_cfg)

    log_params = cfg_dict.get("log_params", True)
    if log_params and hasattr(tracker, "log_params"):
        if isinstance(model_params, DictConfig):
            params_dict = OmegaConf.to_container(model_params, resolve=True)
        else:
            params_dict = dict(model_params)
        if isinstance(params_dict, dict):
            tracker.log_params(params_dict)


def create_tracker(
    config: Optional[DictConfig | Dict] = None, model: Optional["MainModel"] = None
) -> TrackerProtocol:
    """Create tracker backend from configuration and optionally start run.

    If a model instance is provided, the tracker run will be automatically started
    with appropriate run name, tags, and hyperparameters.

    Args:
        config: Tracker configuration (DictConfig or dict).
        model: Current model instance. If provided, tracker run will be started automatically.

    Returns:
        An implementation of TrackerProtocol.

    Raises:
        ConfigurationError: If backend is unknown or missing dependencies.
    """
    backend = None
    cfg_dict: Dict[str, Dict] = {}
    if config is not None and config:  # Check for both None and empty
        if isinstance(config, DictConfig):
            backend = config.get("backend", None)
            cfg_dict = _to_plain(config)
        elif isinstance(config, dict):
            backend = config.get("backend", None)
            cfg_dict = config

    if backend in (None, "default"):
        tracker = DefaultTracker()
    elif backend == "aim":
        try:
            from abses.utils.tracker.aim_tracker import AimTracker
        except ImportError as exc:
            raise ConfigurationError(
                "Aim tracker selected but aim is not installed. "
                "Install with: pip install aim"
            ) from exc
        tracker = AimTracker(cfg_dict.get("aim", {}))
    elif backend == "mlflow":
        try:
            from abses.utils.tracker.mlflow_tracker import MLflowTracker
        except ImportError as exc:
            raise ConfigurationError(
                "MLflow tracker selected but mlflow is not installed. "
                "Install with: pip install mlflow"
            ) from exc
        tracker = MLflowTracker(cfg_dict.get("mlflow", {}))
    else:
        logger.warning(
            "Unknown tracker backend '%s', falling back to default.", backend
        )
        tracker = DefaultTracker()

    # Start tracker run if model is provided
    if model is not None:
        start_tracker_run(
            tracker=tracker,
            tracker_cfg=config or {},
            model_name=model.name,
            version=model.version,
            run_id=model._run_id,
            model_params=model.params,
        )

    return tracker


def prepare_collector_config(tracker_cfg: DictConfig | Dict | None) -> Dict:
    """Prepare configuration for DataCollector from tracker config.

    Removes backend key and converts DictConfig to plain dict.

    Args:
        tracker_cfg: Tracker configuration (may be DictConfig, dict, or None).

    Returns:
        Plain dict suitable for DataCollector reports parameter.
    """
    from omegaconf import DictConfig, OmegaConf

    if tracker_cfg is None:
        return {}

    if isinstance(tracker_cfg, DictConfig):
        collector_cfg = OmegaConf.to_container(tracker_cfg, resolve=True)
    elif isinstance(tracker_cfg, dict):
        collector_cfg = tracker_cfg.copy()
    else:
        collector_cfg = {}

    if isinstance(collector_cfg, dict) and "backend" in collector_cfg:
        collector_cfg.pop("backend", None)

    return collector_cfg or {}
