from typing import TYPE_CHECKING

import numpy as np
import pytest

from abses import Actor, MainModel, PatchCell

if TYPE_CHECKING:
    pass


class DummyActor(Actor):
    """Minimal actor for testing evaluate."""

    def setup(self) -> None:
        self.price = 10.0


class SimpleModel(MainModel):
    """Minimal model with a small grid for evaluate tests."""

    def setup(self) -> None:
        self.nature.create_module(cell_cls=PatchCell, name="grid", shape=(3, 3))
        # place a single actor
        a = self.agents.new(DummyActor, 1)
        a.apply(lambda x: x.move.to(self.nature.grid[1, 1][0]))


@pytest.fixture()
def model() -> SimpleModel:
    """Create a minimal model for tests and run setup to populate state."""
    m = SimpleModel(parameters={})
    m.setup()
    return m


@pytest.fixture()
def actor(model: SimpleModel) -> DummyActor:
    """Get the only actor from model."""
    return model.actors[0]  # type: ignore[index]


class TestEvaluateScores:
    @pytest.mark.parametrize(
        "candidates, scorer, dtype, expected",
        [
            pytest.param(
                [1, 2, 3],
                lambda a, x: x * 2,
                float,
                np.array([2.0, 4.0, 6.0]),
                id="list-candidates",
            ),
            pytest.param(
                np.array([1, 2, 3]),
                lambda a, x: x + 1,
                float,
                np.array([2.0, 3.0, 4.0]),
                id="numpy-candidates",
            ),
        ],
    )
    def test_returns_scores_array(
        self, actor: DummyActor, candidates, scorer, dtype, expected
    ) -> None:
        """It should return an ndarray of scores when how=None."""
        scores = actor.evaluate(candidates, scorer, dtype=dtype)
        assert isinstance(scores, np.ndarray)
        np.testing.assert_allclose(scores, expected)


class TestEvaluateSelection:
    def test_how_max_returns_candidate(self, actor: DummyActor) -> None:
        """how='max' returns the candidate with maximum score."""
        candidates = ["a", "bbb", "cc"]
        best = actor.evaluate(candidates, lambda a, s: len(s), how="max")
        assert best == "bbb"

    def test_how_min_returns_candidate(self, actor: DummyActor) -> None:
        """how='min' returns the candidate with minimum score."""
        candidates = [5, 2, 9]
        best = actor.evaluate(candidates, lambda a, x: x, how="min")
        assert best == 2

    def test_empty_candidates_returns_none(self, actor: DummyActor) -> None:
        """Empty candidate set returns None when selecting."""
        best = actor.evaluate([], lambda a, x: 0, how="max")
        assert best is None


class TestEvaluateRollback:
    def test_preserve_attrs_rolls_back(self, actor: DummyActor) -> None:
        """preserve_attrs should restore attributes after scoring."""
        orig = actor.price
        _ = actor.evaluate(
            [20.0],
            lambda a, p: (setattr(a, "price", p) or a.price),
            preserve_attrs=("price",),
        )
        assert actor.price == orig

    def test_preserve_position_rolls_back(
        self, model: SimpleModel, actor: DummyActor
    ) -> None:
        """preserve_position should restore position after scoring."""
        start_cell = actor.at
        target = model.nature.grid[0, 0][0]
        _ = actor.evaluate(
            [target], lambda a, c: (a.move.to(c) or 1), preserve_position=True
        )
        assert actor.at is start_cell


class TestEvaluateActorsList:
    def test_with_actorslist_candidates(
        self, model: SimpleModel, actor: DummyActor
    ) -> None:
        """Supports ActorsList input and returns best candidate with how."""
        cells = model.nature.grid[0:2, 0:2]
        best = actor.evaluate(
            cells, lambda a, c: -abs(c.pos[0] - 1) - abs(c.pos[1] - 1), how="max"
        )
        assert best in list(cells)


class TestEvaluateDtypes:
    @pytest.mark.parametrize("dtype", [int, float])
    def test_dtype_coercion(self, actor: DummyActor, dtype) -> None:
        """Result array should respect requested dtype when how=None."""
        scores = actor.evaluate([1, 2, 3], lambda a, x: x, dtype=dtype)
        assert isinstance(scores, np.ndarray)
        assert scores.dtype == np.dtype(dtype)


class TestEvaluateEmptyInputs:
    def test_empty_list_scores(self, actor: DummyActor) -> None:
        """Empty list with how=None returns empty ndarray."""
        arr = actor.evaluate([], lambda a, x: 0, dtype=float)
        assert isinstance(arr, np.ndarray)
        assert arr.size == 0

    def test_empty_actorslist_scores_and_select(
        self, model: SimpleModel, actor: DummyActor
    ) -> None:
        """Empty ActorsList: returns empty ndarray for how=None; None for selection."""
        empty_cells = model.nature.grid[0:0, 0:0]
        arr = actor.evaluate(empty_cells, lambda a, c: 0, dtype=float)
        assert isinstance(arr, np.ndarray)
        assert arr.size == 0
        best = actor.evaluate(empty_cells, lambda a, c: 0, how="max")
        assert best is None


class TestEvaluateRollbackCombined:
    def test_preserve_both_attrs_and_position(
        self, model: SimpleModel, actor: DummyActor
    ) -> None:
        """Preserve both attribute(s) and position simultaneously during scoring."""
        start_cell = actor.at
        orig_price = actor.price
        target = model.nature.grid[2, 2][0]
        _ = actor.evaluate(
            [target],
            lambda a, c: (
                setattr(a, "price", 99.0)
                or a.move.to(c)
                or (a.price + (1 if a.at is c else 0))
            ),
            preserve_position=True,
            preserve_attrs=("price",),
            dtype=float,
        )
        # rolled back
        assert actor.at is start_cell
        assert actor.price == orig_price


class TestEvaluateExceptionSafety:
    def test_exception_rolls_back_state(
        self, model: SimpleModel, actor: DummyActor
    ) -> None:
        """Even if scorer raises, rollback must restore state; exception propagates."""
        start_cell = actor.at
        orig_price = actor.price
        target = model.nature.grid[0, 2][0]
        with pytest.raises(RuntimeError):
            _ = actor.evaluate(
                [target],
                lambda a, c: (
                    setattr(a, "price", 77.0)
                    or a.move.to(c)
                    or (_ for _ in ()).throw(RuntimeError("boom"))
                ),
                preserve_position=True,
                preserve_attrs=("price",),
                dtype=float,
            )
        assert actor.at is start_cell
        assert actor.price == orig_price


class TestEvaluateDeterminism:
    def test_equal_scores_returns_first(self, actor: DummyActor) -> None:
        """When scores tie, selection should return the first occurrence (numpy behavior)."""
        candidates = ["aa", "bb", "cc"]
        best = actor.evaluate(candidates, lambda a, s: 2, how="max")
        assert best == candidates[0]
