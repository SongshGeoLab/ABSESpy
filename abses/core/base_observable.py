#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""
Base classes for the Observer pattern in ABSESpy.

This module contains base implementations for observers and observables.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Set

from abses.core.protocols import Observable, Observer, VariableProtocol


class BaseObserver(ABC, Observer):
    """Base observer implementation.

    Implements the Observer pattern for components that need to
    react to changes in observable subjects.
    """

    @abstractmethod
    def update(self, subject: Observable, *args: Any, **kwargs: Any) -> None:
        """Called when the observed subject changes.

        Args:
            subject: The observable that changed.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        pass


class BaseObservable(ABC, Observable):
    """Base observable implementation.

    Implements the Observable pattern for components that can be observed
    and notify observers of changes.

    Attributes:
        observers: Set of observers watching this object.
        variables: Dictionary of variables that can be tracked.
    """

    def __init__(self) -> None:
        """Initialize the observable with an empty observers set."""
        self._observers: Set[Observer] = set()

    @property
    def observers(self) -> Set[Observer]:
        """Get the set of observers.

        Returns:
            Set of observer objects.
        """
        return self._observers

    @property
    def variables(self) -> Dict[str, VariableProtocol]:
        """Get observable variables.

        Returns:
            Dictionary of variable name to variable protocol.
        """
        return {}

    def attach(self, observer: Observer) -> None:
        """Add an observer.

        Args:
            observer: Observer to add.
        """
        self._observers.add(observer)

    def detach(self, observer: Observer) -> None:
        """Remove an observer.

        Args:
            observer: Observer to remove.
        """
        self._observers.discard(observer)

    def notify(self, *args: Any, **kwargs: Any) -> None:
        """Notify all observers of a change.

        Args:
            *args: Positional arguments to pass to observers.
            **kwargs: Keyword arguments to pass to observers.
        """
        for observer in self._observers:
            observer.update(self, *args, **kwargs)
