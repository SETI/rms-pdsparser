##########################################################################################
# pdsparser/__init__.pyi
##########################################################################################
"""Type stub for the pdsparser package.

The `src` tree carries no inline annotations, so type information for the public symbols
is published here instead. Every public name is described in this one file, because the
only supported import is ``from pdsparser import ...``; the submodules that define them
are an implementation detail and carry no stubs of their own. Types are taken from the
docstrings.
"""

import builtins
from collections.abc import ItemsView, KeysView, ValuesView
from pathlib import Path
from typing import Any, Literal, TypeAlias

from filecache import FCPath

__version__: str

__all__ = ['expand_structures', 'is_pds3_file', 'read_label', 'read_vax_binary_label',
           'PdsError', 'PdsSyntaxError', 'Pds3Label', 'PdsLabel']

_FilePath: TypeAlias = str | Path | FCPath
_Repairs: TypeAlias = tuple[str, str] | list[tuple[str, str]]

def read_label(filepath: _FilePath, *, chars: int = 4000) -> str: ...
def read_vax_binary_label(filepath: _FilePath) -> str: ...
def expand_structures(content: str, fmt_dirs: _FilePath | list[_FilePath] = ..., *,
                      repairs: _Repairs = ...,
                      label_path: _FilePath | None = None) -> str: ...
def is_pds3_file(filepath: _FilePath) -> bool: ...

class PdsError(Exception): ...
class PdsSyntaxError(SyntaxError, PdsError): ...

class Pds3Label:
    content: str
    dict: builtins.dict[str, Any]
    filepath: FCPath | None
    _filepath: FCPath | None

    def __init__(self, label: str | list[str] | Path | FCPath,
                 method: Literal['strict', 'loose', 'compound', 'fast'] = 'strict', *,
                 expand: bool = False, fmt_dirs: _FilePath | list[_FilePath] = ...,
                 repairs: _Repairs = ..., vax: bool = False, types: bool = False,
                 sources: bool = False, first_suffix: bool = True,
                 _details: bool = False) -> None: ...
    def __getitem__(self, key: str) -> Any: ...
    def __setitem__(self, key: str, value: Any) -> None: ...
    def __len__(self) -> int: ...
    def __contains__(self, key: object) -> bool: ...
    def get(self, key: str, default: Any = None) -> Any: ...
    def items(self) -> ItemsView[str, Any]: ...
    def keys(self) -> KeysView[str]: ...
    def values(self) -> ValuesView[Any]: ...

    # Deprecated API
    def as_dict(self) -> builtins.dict[str, Any]: ...
    @staticmethod
    def from_file(filename: _FilePath) -> Pds3Label: ...
    @staticmethod
    def load_file(filepath: _FilePath) -> list[str]: ...
    @staticmethod
    def from_string(string: str | list[str]) -> Pds3Label: ...

# Deprecated name for the class
PdsLabel = Pds3Label
