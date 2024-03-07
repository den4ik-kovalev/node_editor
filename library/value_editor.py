from abc import abstractmethod, ABC
from enum import Enum, EnumMeta
from typing import Any, Callable, Optional

import dearpygui.dearpygui as dpg


class ValueEditor(ABC):

    @abstractmethod
    def __init__(self, **kwargs) -> None:
        self._stage: int = ...
        self._tag: int = ...

    @property
    def tag(self) -> int:
        return self._tag

    @property
    def callback(self) -> Optional[Callable]:
        return dpg.get_item_callback(self._tag)

    @callback.setter
    def callback(self, callback: Optional[Callable]) -> None:
        dpg.set_item_callback(self._tag, callback)

    @property
    def value(self) -> Optional[Any]:
        return dpg.get_value(self._tag)

    @value.setter
    def value(self, value: Optional[Any]):
        dpg.set_value(self._tag, value)

    def add(self, parent) -> None:
        dpg.push_container_stack(parent)
        dpg.unstage(self._stage)
        dpg.pop_container_stack()


class IntInput(ValueEditor):

    def __init__(self, **kwargs) -> None:
        with dpg.stage() as self._stage:
            self._tag = dpg.add_input_int(**kwargs)

    @property
    def value(self) -> Optional[int]:
        return dpg.get_value(self._tag)

    @value.setter
    def value(self, value: Optional[int]):
        dpg.set_value(self._tag, value)


class Combobox(ValueEditor):

    def __init__(self, items: list[Any], nullable: bool = False, **kwargs) -> None:

        if nullable and None not in items:
            items.insert(0, None)

        if kwargs.get("default_value") is None:
            if nullable:
                kwargs["default_value"] = self._value_to_str(None)
            else:
                kwargs["default_value"] = self._value_to_str(items[0])
        else:
            kwargs["default_value"] = self._value_to_str(kwargs["default_value"])

        kwargs["items"] = [self._value_to_str(i) for i in items]

        with dpg.stage() as self._stage:
            self._tag = dpg.add_combo(**kwargs)

    @property
    def value(self) -> Optional[Any]:
        return self._value_from_str(dpg.get_value(self._tag))

    @value.setter
    def value(self, value: Optional[Any]):
        dpg.set_value(self._tag, self._value_to_str(value))

    @staticmethod
    def _value_to_str(value: Optional[Any]) -> str:
        return str(value)

    @abstractmethod
    def _value_from_str(self, value_str: str) -> Optional[Any]:
        ...


class StrCombobox(Combobox):

    def _value_from_str(self, value_str: str) -> Optional[Any]:
        if value_str == "None":
            return None
        return value_str
