"""Smoke-test an installed abses wheel through its public API only (#154).

The test suite runs against the source checkout, where files the wheel
leaves out are still on disk. CI runs this script with `python -I` from a
directory outside the checkout, against a clean environment holding just
the built wheel, so a file missing from the wheel fails here.
"""

from pathlib import Path

import abses
from abses import MainModel, load_data
from abses.utils.data import DATA_LIST

package_dir = Path(abses.__file__).resolve().parent
assert "site-packages" in package_dir.parts, f"not the installed wheel: {package_dir}"

for name in DATA_LIST:
    path = load_data(name)
    assert path.is_file(), f"{name} is missing from the wheel: {path}"

# Build modules the two common ways, against whatever mesa / mesa-geo a
# fresh install resolves to (#179), then run one step.
model = MainModel()
grid = model.nature.create_module(shape=(3, 3), name="grid")
assert grid.array_cells.shape == (3, 3)
farmland = model.nature.create_module(
    raster_file=load_data("farmland.tif"), name="farmland"
)
assert farmland.array_cells.size > 0
model.run_model(steps=1)

print(f"abses {abses.__version__} wheel OK: {len(DATA_LIST)} datasets, modules built")
