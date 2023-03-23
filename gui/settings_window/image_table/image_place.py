from typing import TYPE_CHECKING

import dearpygui.dearpygui as dpg

from DearPyGui_Addons import dpg_handler
from DearPyGui_Addons import get_button_is_text_theme
from settings import AddToEnd
from ._placeholders import SelectableSettingDraggableList, SettingDraggableList, SettingDraggableListCell

if TYPE_CHECKING:
    from .. import Window

__all__ = ["AddNewFileAddToEndSetting"]


class NewFilePlaceCell(SettingDraggableListCell):
    def selected(self):
        btn = dpg.add_button(label="NEW", height=-1, width=-1, parent=self.window)
        dpg.bind_item_theme(btn, get_button_is_text_theme())
        super().selected()


class AddNewFileAddToEndSetting(SelectableSettingDraggableList):
    windows: list[SettingDraggableList]

    def __init__(self, settings_window: 'Window'):
        super().__init__(settings_window)
        with dpg.table(header_row=False, clipper=True, parent=self.group):
            dpg.add_table_column()
            dpg.add_table_column()
            with dpg.table_row():
                with dpg.group():
                    self.setting_window = SettingDraggableList()
                    for _ in range(3):
                        self.setting_window.append(NewFilePlaceCell(self.setting_window))
                    self.setting_window.all_cells[0].selected()
                    dpg.configure_item(self.setting_window.window,
                                       height=self.setting_window.get_all_height() - self.setting_window.space_between_cells)
                    self.windows.append(self.setting_window)

                with dpg.group():
                    self.setting_window = SettingDraggableList()
                    for _ in range(3):
                        self.setting_window.append(NewFilePlaceCell(self.setting_window))
                    self.setting_window.all_cells[-1].selected()
                    dpg.configure_item(self.setting_window.window,
                                       height=self.setting_window.get_all_height() - self.setting_window.space_between_cells)
                    self.windows.append(self.setting_window)
        dpg_handler.add_mouse_release_callback(self.click_callback)
        index = int(AddToEnd.get())
        dpg.bind_item_theme(self.windows[index].window, self.windows[index].get_selected_theme())

    def selected(self, index: int):
        super().selected(index)
        AddToEnd.set(bool(index))
