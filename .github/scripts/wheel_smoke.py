"""Smoke-test an installed abses wheel through its public API only (#154).

The test suite runs against the source checkout, where files the wheel
leaves out are still on disk. CI runs this script with `python -I` from a
directory outside the checkout, against a clean environment holding just
the built wheel, so a file missing from the wheel fails here.
"""

from pathlib import Path

import abses
from abses import load_data
from abses.utils.data import DATA_LIST

package_dir = Path(abses.__file__).resolve().parent
assert "site-packages" in package_dir.parts, f"not the installed wheel: {package_dir}"

for name in DATA_LIST:
    path = load_data(name)
    assert path.is_file(), f"{name} is missing from the wheel: {path}"

print(f"abses {abses.__version__} wheel OK: {len(DATA_LIST)} datasets shipped")
