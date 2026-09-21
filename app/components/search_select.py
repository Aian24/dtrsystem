"""
Searchable Select Component — Clean dropdown with persistent search bar inside popup menu
"""
from __future__ import annotations
from typing import Any, Callable, Dict, Iterator, List, Optional, Union
from nicegui.elements.select import Select


class SearchSelect(Select, component='search_select.js'):

    def __init__(self,
                 options: Union[List, Dict], *,
                 label: Optional[str] = None,
                 value: Any = None,
                 on_change: Optional[Callable[..., Any]] = None,
                 multiple: bool = False,
                 clearable: bool = False,
                 validation: Optional[Union[Callable[..., Optional[str]], Dict[str, Callable[..., bool]]]] = None,
                 ) -> None:
        super().__init__(
            options=options,
            label=label,
            value=value,
            on_change=on_change,
            with_input=False,
            multiple=multiple,
            clearable=clearable,
            validation=validation,
        )


def search_select(
    options: Union[List, Dict], *,
    label: Optional[str] = None,
    value: Any = None,
    on_change: Optional[Callable[..., Any]] = None,
    multiple: bool = False,
    clearable: bool = False,
    validation: Optional[Union[Callable[..., Optional[str]], Dict[str, Callable[..., bool]]]] = None,
) -> SearchSelect:
    """Helper function to instantiate a SearchSelect."""
    return SearchSelect(
        options=options,
        label=label,
        value=value,
        on_change=on_change,
        multiple=multiple,
        clearable=clearable,
        validation=validation,
    )
