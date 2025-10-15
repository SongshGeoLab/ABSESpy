# 安装

## 使用 pip 安装 <small>推荐</small> { #with-pip data-toc-label="with pip" }

`ABSESpy` 作为 [Python 包] 发布，可以使用 `pip` 或您喜欢的 PyPI 包管理器安装，理想情况下使用[虚拟环境]。打开终端并使用以下命令安装 `ABSESpy`：

=== "最新版本"

    ``` sh
    pip install abses
    ```

这将自动安装所有[依赖项]的兼容版本。

!!! tip "提示"

    如果您之前没有使用 Python 的经验，我们推荐阅读
    [使用 Python 的 pip 管理项目依赖]，这是一个很好的 Python 包管理机制介绍，
    可以帮助您解决遇到的错误。

## 从源代码安装

可以直接从 [GitHub] 克隆仓库来使用 `ABSESpy`，如果您想使用最新版本，可以将仓库克隆到项目根目录的子文件夹中：

```sh
git clone https://github.com/SongshGeoLab/ABSESpy abses
```

接下来，安装框架及其依赖项：

```sh
pip install -e abses
```

<!-- Links -->
  [Python 包]: https://pypi.org/project/abses/
  [虚拟环境]: https://realpython.com/what-is-pip/#using-pip-in-a-python-virtual-environment
  [使用 Python 的 pip 管理项目依赖]: https://realpython.com/what-is-pip/
  [依赖项]: ../home/dependencies.md
  [GitHub]: https://github.com/SongshGeoLab/ABSESpy

