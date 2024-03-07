import dearpygui.dearpygui as dpg
from loguru import logger

from ui import CalculatorWindow


logger.add("error.log", format="{time} {level} {message}", level="ERROR")


def main():

    dpg.create_context()

    with dpg.viewport_menu_bar():
        with dpg.menu(label="Menu"):
            dpg.add_menu_item(label="Calculator", callback=lambda: CalculatorWindow().add)

    dpg.create_viewport(title='Node Editor Example')
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.maximize_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == '__main__':
    main()
