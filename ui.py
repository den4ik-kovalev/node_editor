from __future__ import annotations
from random import randint

import dearpygui.dearpygui as dpg

from database import db
from library.node_editor import NodeEditor, Node, NodeFreezer
from library.window import Window
from library.value_editor import IntInput, StrCombobox


class NumberNode(Node):

    def __init__(self) -> None:
        super(NumberNode, self).__init__(label="Number", inputs=[], outputs_count=1)
        int_input = IntInput(width=100)
        self.add_param("number", int_input)

    @property
    def value(self) -> int:
        return self.params_dict["number"] or 0

    def copy(self) -> NumberNode:
        return NumberNode()


class OperatorNode(Node):

    def __init__(self) -> None:
        super(OperatorNode, self).__init__(label="Operator", inputs=["1", "2"], outputs_count=1)
        combobox = StrCombobox(["+", "-", "*", "/"], width=100)
        self.add_param("operation", combobox)

    @property
    def value(self) -> float:

        parents = self.parents
        parent_1, parent_2 = next(parents), next(parents)
        operation = self.params_dict["operation"]
        
        if operation == "+":
            return parent_1.value + parent_2.value
        elif operation == "-":
            return parent_1.value - parent_2.value
        elif operation == "*":
            return parent_1.value * parent_2.value
        elif operation == "/":
            return parent_1.value / parent_2.value

    def copy(self) -> OperatorNode:
        return OperatorNode()


class ResultNode(Node):

    def __init__(self) -> None:
        super(ResultNode, self).__init__(label="Result", inputs=[""], outputs_count=0)
        with dpg.stage():
            btn_result = dpg.add_button(
                label="=", width=100, height=30, callback=self._on_btn_result_click
            )
            self._text_result = dpg.add_text("Empty")
        self.add_widget(btn_result)
        self.add_widget(self._text_result)
        
    def copy(self) -> ResultNode:
        return ResultNode()

    def _on_btn_result_click(self) -> None:
        if not list(self.parents):
            return
        parent = next(self.parents)
        try:
            result = parent.value
            dpg.configure_item(self._text_result, default_value=str(result))
            self.paint(0, 128, 0)
        except Exception:
            dpg.configure_item(self._text_result, default_value="Error")
            self.paint(128, 0, 0)


class CalculatorWindow(Window):

    def __init__(self) -> None:

        with dpg.stage() as self._stage:

            self._tag = dpg.add_window(
                label="Calculator",
                width=dpg.get_viewport_client_width(),
                height=dpg.get_viewport_client_height() - 20,
                no_move=True,
                on_close=self._on_close
            )

            self._node_editor = NodeEditor()
            self._node_editor.add(parent=self._tag)

            with dpg.handler_registry():
                self._delete_kph = dpg.add_key_press_handler(
                    key=dpg.mvKey_Delete,
                    callback=self._node_editor.delete_selection
                )

            with dpg.menu_bar(parent=self._tag):

                with dpg.menu(label="Edit"):
                    dpg.add_menu_item(
                        label="Clear",
                        callback=self._node_editor.clear
                    )

                with dpg.menu(label="Nodes"):
                    dpg.add_menu_item(
                        label="Number",
                        callback=self._on_add_number_node
                    )
                    dpg.add_menu_item(
                        label="Operator",
                        callback=self._on_add_operator_node
                    )
                    dpg.add_menu_item(
                        label="Result",
                        callback=self._on_add_result_node
                    )

                with dpg.menu(label="Presets") as self._presets_menu:
                    dpg.add_menu_item(
                        label="Save",
                        callback=self._on_save_preset
                    )

                    rows = db.select_node_editor_states_info()
                    if rows:
                        dpg.add_separator()

                    for row in rows:
                        with dpg.menu(label=row["name"]):
                            dpg.add_menu_item(
                                label="Load",
                                callback=self._on_load_preset,
                                user_data=row["rowid"]
                            )
                            dpg.add_menu_item(
                                label="Delete",
                                callback=self._on_delete_preset,
                                user_data=row["rowid"]
                            )

    def _on_close(self) -> None:
        dpg.delete_item(self._delete_kph)

    def _on_add_number_node(self) -> None:
        node = NumberNode()
        self._node_editor.add_node(node)

    def _on_add_operator_node(self) -> None:
        node = OperatorNode()
        self._node_editor.add_node(node)

    def _on_add_result_node(self) -> None:
        node = ResultNode()
        self._node_editor.add_node(node)

    def _on_save_preset(self) -> None:

        preset_name = str(randint(0, 1000))
        state = NodeFreezer.get_editor_state(self._node_editor)
        rowid = db.insert_node_editor_state(preset_name, state)

        with dpg.menu(parent=self._presets_menu, label=preset_name):
            dpg.add_menu_item(
                label="Load",
                callback=self._on_load_preset,
                user_data=rowid
            )
            dpg.add_menu_item(
                label="Delete",
                callback=self._on_delete_preset,
                user_data=rowid
            )

    def _on_load_preset(self, sender, app_data, rowid: int) -> None:
        row = db.select_node_editor_state(rowid)
        state = row["state"]
        NodeFreezer.restore_editor_state(self._node_editor, state)

    def _on_delete_preset(self, sender, app_data, rowid: int) -> None:
        db.delete_node_editor_state(rowid)
        dpg.delete_item(dpg.get_item_parent(sender))
