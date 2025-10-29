#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""
这个模块储存一些
"""

from functools import wraps
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Literal,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    overload,
)

import numpy as np
from matplotlib import pyplot as plt
from scipy import ndimage

from abses.utils.regex import CAMEL_NAME

try:
    from typing import TypeAlias
except ImportError:
    from typing_extensions import TypeAlias

F = TypeVar("F", bound=Callable[..., Any])

# Separate type aliases for better overload typing
AttrFilter: TypeAlias = str | bool | Iterable[str]
IncludeMap: TypeAlias = Dict[str, str]
IncludeFlag: TypeAlias = AttrFilter | IncludeMap


def get_buffer(
    array: np.ndarray,
    radius: int = 1,
    moor: bool = False,
    annular: bool = False,
) -> np.ndarray:
    """Get a buffer around the array.

    Parameters:
        array:
            The array to get buffer from.
        radius:
            The radius of the buffer.
        moor:
            If True, use moor connectivity (8 neighbors include Diagonal pos).
            Otherwise use von Neumann (4 neighbors).
        annular:
            If True, return an annular buffer.
            e.g., if radius is 2, the result will be a ring with radius 1-2.

    Raises:
        ValueError:
            If radius is not positive or not int type.

    Returns:
        The buffer mask array.
    """
    if radius <= 0 or not isinstance(radius, int):
        raise ValueError(f"Radius must be positive int, not {radius}.")
    connectivity = 2 if moor else 1
    struct = ndimage.generate_binary_structure(2, connectivity)
    result = ndimage.binary_dilation(array, structure=struct, iterations=radius)
    if annular and radius > 1:
        interior = ndimage.binary_dilation(
            array, structure=struct, iterations=radius - 1
        )
        return result & np.invert(interior)
    return result


def make_list(element: Any, keep_none: bool = False) -> List:
    """Turns element into a list of itself if it is not of type list or tuple."""

    if element is None and not keep_none:
        element = []  # Convert none to empty list
    if not isinstance(element, (list, tuple, set, np.ndarray)):
        element = [element]
    elif isinstance(element, (tuple, set)):
        element = list(element)

    return element


def iter_apply_func_to(elements: str) -> Callable:
    """
    A decorator broadcasting function to all elements if available.

    Parameters:
        elements:
            attribute name where object store iterable elements.
            All element in this iterable object will call the decorated function.

    Returns:
        The decorated class method.
    """

    def broadcast(func: Callable) -> Callable:
        def broadcast_func(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            if not hasattr(self, elements):
                return result
            elements_attr = getattr(self, elements)
            # Handle dict: iterate over values instead of keys
            if isinstance(elements_attr, dict):
                elements_iter = elements_attr.values()
            else:
                elements_iter = elements_attr
            for element in elements_iter:
                getattr(element, func.__name__)(*args, **kwargs)
            return result

        return broadcast_func

    return broadcast


def camel_to_snake(name: str) -> str:
    """Convert camel name to snake name.

    Parameters:
        name:
            The name to convert.

    Returns:
        The converted name.
    """
    # https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
    return CAMEL_NAME.sub("_", name).lower()


def with_axes(
    decorated_func: Optional[F] = None, figsize: Tuple[int, int] = (6, 4)
) -> Callable[..., Any]:
    """装饰一个函数/方法，如果该方法接受一个参数叫'ax'并且为None，为其增加一个默认的绘图布。

    Parameters:
        decorated_func:
            被装饰的函数，检查是否有参数传递给装饰器，若没有则返回装饰器本身。
        figsize:
            图片画布的大小，默认宽度为6，高度为4。

    Returns:
        被装饰的函数
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            ax = kwargs.get("ax", None)
            if ax is None:
                _, ax = plt.subplots(figsize=figsize)
                kwargs["ax"] = ax
                result = func(*args, **kwargs)
                return result
            else:
                return func(*args, **kwargs)

        return wrapper

    # 检查是否有参数传递给装饰器，若没有则返回装饰器本身
    return decorator(decorated_func) if decorated_func else decorator


def set_null_values(arr: np.ndarray, mask: np.ndarray):
    """
    Set null values in an array based on a boolean mask and the array's data type.

    Parameters:
        arr:
            The input array that can contain float or strings.
        mask:
            A boolean array where True indicates that a null value should be set.

    Returns:
        The modified array with null values set.
        Note: Integer arrays will be upcast to float to support NaN values.
    """
    if arr.shape != mask.shape:
        raise ValueError(f"Mismatching shape {mask.shape} and {arr.shape}.")
    # Check if the dtype is float or integer
    if arr.dtype.kind in {"f", "i"}:
        # Integer arrays must be upcast to float to support NaN
        if arr.dtype.kind == "i":
            arr = arr.astype(float, copy=True)
        null_value = np.nan
    # Unicode string
    elif arr.dtype.kind == "U":
        null_value = ""
    # # Byte string
    elif arr.dtype.kind == "S":
        null_value = b""
    else:
        raise ValueError(f"Unsupported data type {arr.dtype}")
    arr[mask] = null_value
    return arr


@overload
def clean_attrs(
    all_attrs: Iterable[str],
    include: Optional[AttrFilter],
    exclude: Optional[Iterable[str]] = None,
) -> List[str]: ...


@overload
def clean_attrs(
    all_attrs: Iterable[str],
    include: IncludeMap,
    exclude: Optional[Iterable[str]] = None,
) -> Dict[str, str]: ...


def clean_attrs(
    all_attrs: Iterable[str],
    include: Optional[IncludeFlag] = True,
    exclude: Optional[Iterable[str]] = None,
) -> List[str] | Dict[str, str]:
    """
    Clean attributes based on include and exclude lists.

    Parameters:
        all_attrs:
            All attributes to clean.
        include:
            Attributes to include.
        exclude:
            Attributes to exclude.

    Returns:
        The cleaned attributes.
    """
    if isinstance(include, dict):
        attrs = clean_attrs(all_attrs, list(include.keys()), exclude)
        return {attr: include[attr] for attr in attrs}
    if isinstance(include, bool):
        include = all_attrs if include else None
    selected = set(all_attrs) & set(make_list(include))
    if exclude:
        selected -= set(make_list(exclude))
    return list(selected)


def search_unique_key(
    to_search: Sequence[str],
    valid_keys: Sequence[str],
    default: Optional[str] = None,
    when_multiple: Literal["error", "first", "last", "all"] = "error",
) -> str | Sequence[str] | None:
    """
    Get the unique key from the possible keys.

    Parameters:
        to_search:
            The keys to search.
        valid_keys:
            The possible keys.
        default:
            The default key if no match is found.
        when_multiple:
            What to do if multiple keys are found.

    Examples:
        >>> search_unique_key(
            to_search=["b", "c", "d"],
            valid_keys=["a", "b"],
        )
        "b"
        >>> search_unique_key(
            to_search=["a", "b", "c"],
            valid_keys=["a", "b"],
            when_multiple="error",
        )
        ValueError("Multiple keys found: ['a', 'b']")
        >>> search_unique_key(
            to_search=["a", "b", "c"],
            valid_keys=["a", "b"],
            when_multiple="first",
        )
        "a"

    Returns:
        The unique key.
    """
    if len(to_search) == 0:
        return default

    # 将可迭代对象转换为集合以提高查找效率
    valid_keys_set = set(valid_keys)

    # 找出所有匹配的键
    matched_keys = [key for key in to_search if key in valid_keys_set]

    # 如果没有找到匹配的键，返回默认值
    if not matched_keys:
        return default

    # 如果只找到一个匹配的键，直接返回
    if len(matched_keys) == 1:
        return matched_keys[0]

    # 处理找到多个匹配键的情况
    if when_multiple == "error":
        raise ValueError(f"Multiple keys found: {matched_keys}")
    elif when_multiple == "first":
        return matched_keys[0]
    elif when_multiple == "last":
        return matched_keys[-1]
    elif when_multiple == "all":
        return matched_keys
    raise ValueError(f"Invalid value for when_multiple: {when_multiple}")


def get_only_item(agents: Sequence[Any], default: Optional[Any] = ...) -> Any:
    """Select one agent"""
    if len(agents) == 0:
        if default is ...:
            raise ValueError("No agent found.")
        return default
    if len(agents) == 1:
        return agents[0]
    raise ValueError("More than one agent.")
