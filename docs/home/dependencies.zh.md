
**`ABSESpy` 框架基于许多优秀的开源项目：**

| 包            | 版本              | 用途                                   |
|---------------|-------------------|----------------------------------------|
| python        | ">=3.11,<3.14"    | 开发使用的核心编程语言                 |
| netcdf4       | ">=1.6"           | 读写 NetCDF 和 HDF5 文件               |
| hydra-core    | ">=1.3,<1.4"      | 管理应用程序配置                       |
| mesa          | ">=3.1.0"         | 智能体调度与核心工具                   |
| mesa-geo      | ">=0.9.1"         | 空间显式图层与栅格支持                 |
| xarray        | ">=2023"          | 处理标记的多维数组                     |
| fiona         | ">1.8"            | 读写矢量数据（shapefiles 等）          |
| rioxarray     | ">=0.13"          | 操作栅格数据和 xarray                  |
| pendulum      | ">=3.0.0"         | 时间控制                               |
| geopandas     | ">=0,<1"          | shapefile 地理数据操作                 |

### Mesa / mesa-geo 兼容性说明

`ABSESpy` 在 `pyproject.toml` 中对 `mesa` 与 `mesa-geo` 仅声明**下界**，以便下游项目按需升级。不同 `mesa-geo` 版本在栅格初始化顺序上的差异在代码中处理（例如 `abses/space/mesa_raster_compat.py` 与 `PatchModule`）。

CI 在 Ubuntu 上运行**依赖兼容**任务：分别安装声明的最低版本与当前 PyPI 最新版本，再跑空间相关回归测试。这不保证未来任意大版本 `mesa-geo` 都无需改动，但能尽早发现破坏性变更。

若升级 `mesa` / `mesa-geo` 后在 `PatchModule` 或栅格初始化阶段报错，请记录 `pip show mesa mesa-geo`（或 `uv pip list`）中的版本并附上完整 traceback 提 issue。

!!! Warning "警告"

    上表可能不是最新的，请参考 `pyproject.toml` 文件中的完整依赖项及其版本。

