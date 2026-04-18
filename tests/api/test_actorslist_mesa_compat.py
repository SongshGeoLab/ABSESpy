#!/usr/bin/env python3
# -*-coding:utf-8 -*-
"""Regression tests for ActorsList vs mesa AgentSet MRO.

mesa 3.5 added ``typing.Generic`` to ``AgentSet.__bases__``. If ``ActorsList``
is declared as ``class ActorsList(Generic[A], AgentSet)`` Python cannot
linearize the MRO and ``import abses`` fails. Keep ``AgentSet`` first to stay
compatible across mesa 3.1–3.5+.
"""

from __future__ import annotations

import typing

from mesa.agent import AgentSet


def test_actorslist_subclasses_agentset() -> None:
    """ActorsList must remain a real AgentSet subclass."""
    from abses.agents.sequences import ActorsList

    assert issubclass(ActorsList, AgentSet)


def test_actorslist_stays_generic() -> None:
    """Generic parameterization ``ActorsList[Actor]`` must still work."""
    from abses.agents.actor import Actor
    from abses.agents.sequences import ActorsList

    parameterized = ActorsList[Actor]
    assert typing.get_origin(parameterized) is ActorsList


def test_agentset_first_in_bases() -> None:
    """Guard against regressing to ``(Generic[A], AgentSet)`` base order."""
    from abses.agents.sequences import ActorsList

    assert ActorsList.__bases__[0] is AgentSet
