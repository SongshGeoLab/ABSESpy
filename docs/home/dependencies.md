
**`ABSESpy` framework is based on many excellent open-source projects:**

| Package       | Version           | Purpose                                               |
|---------------|-------------------|-------------------------------------------------------|
| python        | ">=3.11,<3.14"    | Core programming language used for development        |
| netcdf4       | ">=1.6"           | To read and write NetCDF and HDF5 files               |
| hydra-core    | ">=1.3,<1.4"      | For managing application configurations               |
| mesa          | ">=3.1.0"         | Agent-based scheduling and core utilities             |
| mesa-geo      | ">=0.9.1"         | Spatially explicit layers and raster support          |
| xarray        | ">=2023"          | To work with labelled multi-dimensional arrays        |
| fiona         | ">1.8"            | For reading and writing vector data (shapefiles, etc) |
| rioxarray     | ">=0.13"          | Operating raster data and xarray                      |
| pendulum      | ">=3.0.0"         | For time control                                      |
| geopandas     | ">=0,<1"          | For shapefile geo-data operating                      |

### Mesa / mesa-geo compatibility

`ABSESpy` declares **lower bounds only** for `mesa` and `mesa-geo` in `pyproject.toml` so downstream projects can upgrade within their own constraints. Raster initialization differences across `mesa-geo` releases are handled in code (e.g. `abses/space/mesa_raster_compat.py` with `PatchModule`).

CI runs a **dependency compatibility** job on Ubuntu that reinstalls the minimum supported `mesa` / `mesa-geo` pair and the latest published releases, then runs spatial regression tests. This does not guarantee every future `mesa-geo` major release will work without changes, but it catches regressions early.

If you upgrade `mesa` / `mesa-geo` and see errors during `PatchModule` / raster setup, check the installed versions (`pip show mesa mesa-geo` or `uv pip list`) and open an issue with the traceback.

!!! Warning

    The above table may not be up-in-date, please refer full dependencies and their versions in the `pyproject.toml` file.
