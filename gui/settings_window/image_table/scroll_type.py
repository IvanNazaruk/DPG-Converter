from functools import cache
from typing import TYPE_CHECKING

import dearpygui.dearpygui as dpg

import fonts
from DPG_modules.Addons import CheckBoxSlider, dpg_callback, ImageSizeInput
from DPG_modules.Addons import dpg_handler
from DPG_modules.Animations.dpg.scroll import ScrollYAnimation
from Resources.settings import FullWindowScrollBar
from ._placeholders import SelectableImageListSetting, SettingImageList, SettingImageListCell
from ...image_table import cell_size

if TYPE_CHECKING:
    from .. import Window

__all__ = ["AddScrollTypeSetting"]


class MiniWindow(SettingImageList):
    window_padding = (0, 0)
    space_between_cells = 0


class MiniImageList(SettingImageList):
    window_padding = (5, 5)
    space_between_cells = 8

    def get_theme(self):
        if self._theme is None:
            with dpg.theme() as self._theme:
                with dpg.theme_component(dpg.mvAll, parent=self._theme) as theme_component:
                    dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 0, category=dpg.mvThemeCat_Core, parent=theme_component)
                    dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, self.window_padding[0], self.window_padding[1], category=dpg.mvThemeCat_Core, parent=theme_component)
                    dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0, 0, category=dpg.mvThemeCat_Core, parent=theme_component)
                    dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 0, self.space_between_cells, category=dpg.mvThemeCat_Core, parent=theme_component)
                    dpg.add_theme_style(dpg.mvStyleVar_CellPadding, 0, 0, category=dpg.mvThemeCat_Core, parent=theme_component)
        return self._theme


def create_interface():
    with dpg.tab_bar():
        with dpg.tab(label='IToI') as tab:
            pass
        with dpg.tab(label='IToI'):
            pass
        with dpg.tab(label='IToI'):
            pass
    with dpg.group(parent=tab):
        with dpg.group():
            dpg.add_spacer(height=5)
            with dpg.table(header_row=False, clipper=True):
                dpg.add_table_column()
                dpg.add_table_column(width_fixed=True)
                with dpg.table_row():
                    CheckBoxSlider().create()
                    ImageSizeInput(1920, 1080)
            with dpg.table(header_row=False, clipper=True):
                dpg.add_table_column()
                dpg.add_table_column(width_fixed=True)
                with dpg.table_row():
                    dpg.add_button(label=" " * 6)
                    with dpg.group(horizontal=True):
                        dpg.add_button(label=" " * 6)
                        dpg.add_spacer(width=fonts.font_size // 2)
                        dpg.add_button(label=" " * 6)
                        dpg.add_spacer(width=fonts.font_size // 2)
                        dpg.add_button(label=" " * 6)
        dpg.add_spacer(height=5)
        dpg.add_separator()
        dpg.add_spacer(height=1)
        image_list = MiniImageList()
        dpg.add_spacer(height=MiniImageList.space_between_cells // 2, parent=image_list.window)
        for _ in range(5):
            image_list.append(SettingImageListCell(image_list))
        return image_list


@cache
def get_invisible_child_window_theme():
    with dpg.theme() as theme:
        with dpg.theme_component(dpg.mvAll, parent=theme) as theme_component:
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 0, category=dpg.mvThemeCat_Core, parent=theme_component)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0, 0, category=dpg.mvThemeCat_Core, parent=theme_component)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0, 0, category=dpg.mvThemeCat_Core, parent=theme_component)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 0, 0, category=dpg.mvThemeCat_Core, parent=theme_component)
            dpg.add_theme_style(dpg.mvStyleVar_CellPadding, 0, 0, category=dpg.mvThemeCat_Core, parent=theme_component)
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (0, 0, 0, 0), category=dpg.mvThemeCat_Core, parent=theme_component)
    return theme


class AddScrollTypeSetting(SelectableImageListSetting):
    scroll_animations: list[ScrollYAnimation]
    windows: list[MiniWindow]

    def __init__(self, settings_window: 'Window'):
        super().__init__(settings_window)
        self.scroll_animations = []
        mini_window_height = int(cell_size * 4.5)
        with dpg.table(header_row=False, clipper=True, parent=self.group) as self.table:
            dpg.add_table_column()
            dpg.add_table_column()
            with dpg.table_row():
                with dpg.group():
                    self.mini_window = MiniWindow()
                    with dpg.group(parent=self.mini_window.window):
                        self.first_window_image_list = create_interface()
                    dpg.configure_item(self.mini_window.window, height=mini_window_height)
                    self.windows.append(self.mini_window)

                with dpg.group():
                    self.mini_window = MiniWindow()
                    with dpg.group(parent=self.mini_window.window):
                        image_list = create_interface()
                        dpg.set_item_height(image_list.window, image_list.get_all_height())

                    dpg.configure_item(self.mini_window.window, height=mini_window_height)
                    self.windows.append(self.mini_window)

        with dpg.item_handler_registry() as handler:
            dpg.add_item_visible_handler(callback=self._update_child_window)
        dpg.bind_item_handler_registry(self.group, handler)

        dpg_handler.add_mouse_release_callback(self.click_callback)
        index = int(FullWindowScrollBar.value)
        dpg.bind_item_theme(self.windows[index].window, self.windows[index].get_selected_theme())

        self.child_window = dpg.add_child_window(pos=[0, 0], height=int(cell_size * 4.5), parent=self.group, show=True)
        dpg.bind_item_theme(self.child_window, get_invisible_child_window_theme())

    def selected(self, index: int):
        super().selected(index)
        FullWindowScrollBar.set(bool(index))

    @dpg_callback()
    def _update_child_window(self):
        pos = dpg.get_item_pos(self.group)
        dpg.set_item_pos(self.child_window, pos=pos)
        for _ in range(3):
            dpg.split_frame()

        self._create_animations()

        for animation in self.scroll_animations:
            if not animation.PAUSED:
                return

        for animation in self.scroll_animations:
            animation.start()

    def _create_animations(self):
        if len(self.scroll_animations) != 0:
            return
        scroll_y_animation = ScrollYAnimation(self.first_window_image_list.window, 0)
        scroll_y_animation.add_pause_point(1.5)
        scroll_y_animation.add_point(int(dpg.get_y_scroll_max(self.first_window_image_list.window)), 2.5, (.56, .28, .56, .84))
        scroll_y_animation.add_pause_point(0.6)
        scroll_y_animation.add_point(0, 2.5, (.56, .28, .56, .84))
        self.scroll_animations.append(scroll_y_animation)

        scroll_y_animation = ScrollYAnimation(self.mini_window.window, 0)
        scroll_y_animation.add_pause_point(1.5)
        scroll_y_animation.add_point(int(dpg.get_y_scroll_max(self.windows[-1].window)), 2.5, (.56, .28, .56, .84))
        scroll_y_animation.add_pause_point(0.6)
        scroll_y_animation.add_point(0, 2.5, (.56, .28, .56, .84))
        self.scroll_animations.append(scroll_y_animation)
