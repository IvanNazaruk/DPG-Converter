import dearpygui.dearpygui as dpg

import fonts
from .image_table import AddNewFileAddToEndSetting, AddScrollTypeSetting
from .other import OtherSetting
from .theme import ThemeSetting


class Window:
    window: int

    def __init__(self):
        with dpg.window(label="Settings", modal=True, min_size=[fonts.font_size * 16, fonts.font_size * 5],
                        height=fonts.font_size * 15, show=False, autosize=True) as self.window:
            with dpg.tab_bar() as self.tab_bar:
                with dpg.tab(label='Theme'):
                    ThemeSetting(self)
                with dpg.tab(label='Table'):
                    AddNewFileAddToEndSetting(self)
                    AddScrollTypeSetting(self)
                with dpg.tab(label='Other'):
                    OtherSetting(self)
