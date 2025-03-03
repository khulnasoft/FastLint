from typing import Any, Callable, List, Optional, Tuple, Type, Union

def construct_format_field_str(fname: str, fspec: str, conv: Optional[str]) -> str: ...
def get_format_args(
    fstr: str,
) -> Union[
    Tuple[List[Tuple[int, Type[str]]], List[Any]],
    Tuple[
        List[
            Union[
                Tuple[int, Type[str]],
                Tuple[int, Type[int]],
                Tuple[int, Type[float]],
            ]
        ],
        List[Any],
    ],
    Tuple[List[Any], List[Tuple[str, Type[str]]]],
]: ...
def infer_positional_format_args(fstr: str) -> str: ...
def split_format_str(
    fstr: str,
) -> Union[List[Tuple[str, str]], List[Union[Tuple[str, str], Tuple[str, None]]]]: ...
def tokenize_format_str(
    fstr: str, resolve_pos: bool = ...
) -> List[Union[str, BaseFormatField]]: ...

class BaseFormatField:
    def __init__(
        self, fname: str, fspec: str = ..., conv: Optional[str] = ...
    ) -> None: ...
    def set_conv(self, conv: Optional[str]) -> None: ...
    def set_fname(self, fname: str) -> None: ...
    def set_fspec(self, fspec: str) -> None: ...

class DeferredValue:
    def __init__(self, func: Callable, cache_value: bool = ...) -> None: ...
    def __str__(self) -> str: ...
    def get_value(self) -> int: ...
