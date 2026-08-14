#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""Cross-process reproducibility regression tests.

These MUST run in subprocesses with varying `PYTHONHASHSEED`. The bugs they
guard against (identity-hashed `set`s leaking into user-visible ordering) are
invisible within a single process: the offending order is stable for the
lifetime of one interpreter and only varies between runs.

See https://github.com/SongshGeoLab/ABSESpy/issues/164
"""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

# Each value exercises a different string-hash randomisation; "random" lets
# CPython pick a fresh one per process.
HASH_SEEDS = ("0", "1", "random")


def run_in_subprocess(script: str, hash_seed: str) -> str:
    """Run `script` in a fresh interpreter under a given PYTHONHASHSEED."""
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = hash_seed
    # Keep the child's import path identical to the parent's.
    env["PYTHONPATH"] = os.pathsep.join(
        [str(REPO_ROOT), env.get("PYTHONPATH", "")]
    ).rstrip(os.pathsep)
    result = subprocess.run(
        [sys.executable, "-c", textwrap.dedent(script)],
        capture_output=True,
        text=True,
        env=env,
        cwd=REPO_ROOT,
        check=False,
        timeout=300,
    )
    if result.returncode != 0:
        pytest.fail(f"subprocess failed (PYTHONHASHSEED={hash_seed}):\n{result.stderr}")
    return result.stdout.strip()


def collect_outputs(script: str) -> list[str]:
    """Run the same script once per hash seed and return the outputs."""
    return [run_in_subprocess(script, seed) for seed in HASH_SEEDS]


LINKS_SCRIPT = """
    from abses import Actor, MainModel

    model = MainModel(seed=42)
    actors = model.agents.new(Actor, num=10)
    hub = actors[0]
    for name in ("test", "alpha", "beta", "gamma"):
        for a in actors[1:]:
            hub.link.to(a, name)

    linked = hub.link.get("test")
    print("ORDER", [a.unique_id for a in linked])
    print("CHOICE", [a.unique_id for a in linked.random.choice(size=3, as_list=True)])
    print("OWNING", hub.link.owning())
    print("GRAPH", [n.unique_id for n in model.human.get_graph("test").nodes])
"""


class TestLinkOrderReproducibility:
    """`link.get()` order must not depend on object memory addresses."""

    def test_link_order_is_identical_across_processes(self):
        """Same seed, different processes and hash seeds -> identical output."""
        outputs = collect_outputs(LINKS_SCRIPT)
        assert len(set(outputs)) == 1, (
            "link ordering varies across processes:\n" + "\n---\n".join(outputs)
        )

    def test_link_order_follows_creation_order(self):
        """Links come back in the order `link.to()` created them."""
        output = run_in_subprocess(LINKS_SCRIPT, "0")
        order_line = next(
            line for line in output.splitlines() if line.startswith("ORDER")
        )
        # actors[0] is the hub (unique_id 1); it linked to 2..10 in order.
        assert order_line == f"ORDER {list(range(2, 11))}"

    def test_owning_follows_registration_order(self):
        """`link.owning()` follows link-type registration order."""
        output = run_in_subprocess(LINKS_SCRIPT, "0")
        owning_line = next(
            line for line in output.splitlines() if line.startswith("OWNING")
        )
        assert owning_line == "OWNING ('test', 'alpha', 'beta', 'gamma')"

    def test_random_choice_on_links_is_reproducible(self):
        """`link.get(...).random.choice(...)` matches across processes.

        Asserted on its own line so a sampling regression is distinguishable
        from an ordering regression.
        """
        choices = [
            next(
                line
                for line in run_in_subprocess(LINKS_SCRIPT, seed).splitlines()
                if line.startswith("CHOICE")
            )
            for seed in HASH_SEEDS
        ]
        assert len(set(choices)) == 1, choices


MODEL_SCRIPT = """
    from examples.schelling.model import Schelling

    params = {
        "model": {
            "width": 10,
            "height": 10,
            "density": 0.8,
            "homophily": 3,
            "radius": 1,
        },
        "SchellingAgent": {"minority_prob": 0.5},
    }
    model = Schelling(parameters=params, seed=42)
    # Bounded: Schelling only clears `running` once every agent is happy,
    # which is not guaranteed for every seed.
    model.run_model(steps=20)
    print("TICK", model.time.tick)
    print("POS", sorted((a.unique_id, a.at.indices) for a in model.agents))
"""


class TestModelTrajectoryReproducibility:
    """A whole model run must be reproducible from its seed alone."""

    def test_same_seed_gives_identical_trajectory(self):
        """Schelling with a fixed seed ends in the same state every time."""
        outputs = collect_outputs(MODEL_SCRIPT)
        assert len(set(outputs)) == 1, (
            "model trajectory varies across processes:\n" + "\n---\n".join(outputs)
        )
