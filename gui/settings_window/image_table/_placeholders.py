from abc import ABC, abstractmethod
from functools import cache
from typing import TYPE_CHECKING
from typing import TypeVar

import dearpygui.dearpygui as dpg

from DearPyGui_Addons.ctypes_utils import GetNowCursorType
from DearPyGui_Addons.get_local_mouse_pos import get_local_mouse_pos
from DearPyGui_Theme import subscribe_color_theme_change
from ...draggable_list import DraggableList, DraggableListCell

if TYPE_CHECKING:
    from .. import Window

__all__ = ["SettingDraggableListCell", "SettingDraggableList", "SelectableSettingDraggableList"]


class SettingDraggableListCell(DraggableListCell):
    _theme_border_color: int = None

    @classmethod
    def _update_border_color(cls, color: list[int]):
        dpg.set_value(cls._theme_border_color, color)

    @classmethod
    def get_theme(cls):
        if cls._theme is None:
            cls._theme = super().get_theme()
            with dpg.theme_component(dpg.mvChildWindow, parent=cls._theme) as theme_component:
                cls._theme_border_color = dpg.add_theme_color(dpg.mvThemeCol_Border, (0, 0, 0, 0), category=dpg.mvThemeCat_Core, parent=theme_component)
            subscribe_color_theme_change(dpg.mvThemeCol_Border, cls._update_border_color)
        return cls._theme

    def create(self, window: int | str) -> None:
        dpg.bind_item_theme(self.theme_group, self.get_theme())


class SettingDraggableList(DraggableList):
    DISABLE_DRAG = True
    window_padding = (10, 10)

    def update_settings(self):
        pass

    @cache
    def get_selected_theme(self):
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvAll, parent=theme) as theme_component:
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, self.window_padding[0], self.window_padding[1], category=dpg.mvThemeCat_Core, parent=theme_component)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0, 0, category=dpg.mvThemeCat_Core, parent=theme_component)
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 0, self.space_between_cells, category=dpg.mvThemeCat_Core, parent=theme_component)
                dpg.add_theme_style(dpg.mvStyleVar_CellPadding, 0, 0, category=dpg.mvThemeCat_Core, parent=theme_component)
            with dpg.theme_component(dpg.mvChildWindow, parent=theme) as theme_component:
                dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 3, category=dpg.mvThemeCat_Core, parent=theme_component)
                dpg.add_theme_color(dpg.mvThemeCol_Border, (0, 250, 0, 225), category=dpg.mvThemeCat_Core, parent=theme_component)
        return theme


_SettingDraggableListType = TypeVar("_SettingDraggableListType", bound=SettingDraggableList)


class SelectableSettingDraggableList(ABC):
    settings_window: 'Window'
    windows: list[_SettingDraggableListType]
    group: int | str

    def __init__(self, settings_window: 'Window'):
        self.settings_window = settings_window
        self.windows: list[_SettingDraggableListType] = []
        self.group = dpg.add_group()

    def click_callback(self):
        if len(self.windows) == 0:
            return
        if GetNowCursorType() != 65539:  # 65539 - default cursor
            return
        if not dpg.is_item_shown(self.settings_window.window):
            return
        if not dpg.is_item_visible(self.group):
            return
        # If the click was above or to the left of the first (left) window
        first_window_mouse_pos = get_local_mouse_pos(self.windows[0].window)
        if first_window_mouse_pos[0] < 0 or first_window_mouse_pos[1] < 0:
            return

        # If the click was further than the height of the window
        window_size = dpg.get_item_rect_size(self.windows[0].window)
        first_window_mouse_pos[1] -= window_size[1]
        if first_window_mouse_pos[1] > 0:
            return
        # if the click is inside the window
        first_window_mouse_pos[0] -= window_size[0]
        if first_window_mouse_pos[0] < 0:
            self.selected(0)
            return

        # Checking the remaining windows
        for i, setting_child_window in enumerate(self.windows[1::]):
            window_mouse_local_pos = get_local_mouse_pos(setting_child_window.window)
            if window_mouse_local_pos[0] < 0:
                return
            window_size = dpg.get_item_rect_size(setting_child_window.window)
            window_mouse_local_pos[0] -= window_size[0]
            if window_mouse_local_pos[0] < 0:
                self.selected(i + 1)
                return

    @abstractmethod
    def selected(self, index: int):
        for i, setting_child_window in enumerate(self.windows):
            theme = setting_child_window.get_theme()
            if i == index:
                theme = setting_child_window.get_selected_theme()
            dpg.bind_item_theme(setting_child_window.window, theme)
