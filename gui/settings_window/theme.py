import threading
from typing import TYPE_CHECKING

import darkdetect
import dearpygui.dearpygui as dpg

from DPG_modules.Addons import CheckBoxSlider, ComboList
from DPG_modules.Addons.title_bar import set_dark_mode
from DPG_modules.Animations.dpg.style import StyleAnimation
from DPG_modules.Theme import CurrentTheme
from DPG_modules.Theme import get_theme_by_name, get_theme_names
from Resources.settings import CustomTheme, DarkTheme, DarkTitleBar, LightTheme, UseSystemColor

if TYPE_CHECKING:
    from . import Window


class ThemeSetting:
    def __init__(self, settings_window: 'Window'):
        self.settings_window = settings_window
        with dpg.group(horizontal=True):
            dpg.add_text("Use system color:")
            self.use_system_color_theme = CheckBoxSlider(callback=self.disable_custom_theme)
            self.use_system_color_theme.create(UseSystemColor.get())
        with dpg.group(horizontal=True) as self.system_theme_group:
            dpg.add_text("Light:")
            self.light_theme_combo_list = ComboList(get_theme_names(), default_value=LightTheme.get(),
                                                    callback=self.update_theme, use_frame_padding=True)
            dpg.add_text("Dark:")
            self.dark_theme_combo_list = ComboList(get_theme_names(), default_value=DarkTheme.get(),
                                                   callback=self.update_theme, use_frame_padding=True)
        with dpg.group() as self.custom_theme_group:
            with dpg.group(horizontal=True):
                dpg.add_text("Custom theme:")
                self.current_theme_combo_list = ComboList(get_theme_names(), CustomTheme.get(),
                                                          callback=self.update_theme, use_frame_padding=True)
            with dpg.group(horizontal=True):
                dpg.add_text("Dark title bar:")
                self.dark_mode_checkbox = dpg.add_checkbox(default_value=DarkTitleBar.get(), callback=self.update_theme)

        # Animations
        with dpg.theme() as theme:
            with dpg.theme_component():
                alpha_style = dpg.add_theme_style(dpg.mvStyleVar_Alpha, 0)
        dpg.bind_item_theme(self.system_theme_group, theme)
        self.system_theme_group_animation = StyleAnimation(alpha_style, [0.25])
        self.system_theme_group_animation.add_point([1], self.use_system_color_theme.ANIMATION_DURATION, (.55, -0.01, .4, 1))
        with dpg.theme() as theme:
            with dpg.theme_component():
                alpha_style = dpg.add_theme_style(dpg.mvStyleVar_Alpha, 0)
        dpg.bind_item_theme(self.custom_theme_group, theme)
        self.custom_theme_group_animation = StyleAnimation(alpha_style, [0.25])
        self.custom_theme_group_animation.add_point([1], self.use_system_color_theme.ANIMATION_DURATION, (.55, -0.01, .4, 1))
        #########################

        self.disable_custom_theme(UseSystemColor.get())
        threading.Thread(target=darkdetect.listener, args=(lambda *args, **kwargs: self.update_theme(),), daemon=True).start()

    def disable_custom_theme(self, disabled: bool):
        self.system_theme_group_animation.set_reverse(not disabled)
        self.custom_theme_group_animation.set_reverse(disabled)
        if self.system_theme_group_animation.PAUSED:
            self.system_theme_group_animation.start()
        if self.custom_theme_group_animation.PAUSED:
            self.custom_theme_group_animation.start()

        self.light_theme_combo_list.set_enabled(disabled)
        self.dark_theme_combo_list.set_enabled(disabled)
        self.current_theme_combo_list.set_enabled(not disabled)
        dpg.configure_item(self.dark_mode_checkbox, enabled=not disabled)

        UseSystemColor.set(disabled)

        self.update_theme()

    @staticmethod
    def change_theme(theme_name: str):
        CurrentTheme.set(get_theme_by_name(theme_name))

    def update_theme(self):
        if self.use_system_color_theme.VALUE:
            is_dark = darkdetect.isDark()
            if is_dark:
                new_theme_name = self.dark_theme_combo_list.get_value()
            else:
                new_theme_name = self.light_theme_combo_list.get_value()
            # self.current_theme_combo_list.set_value(new_theme_name)
            # dpg.set_value(self.dark_mode_checkbox, is_dark)
            self.change_theme(new_theme_name)
            set_dark_mode(is_dark)
        else:
            self.change_theme(self.current_theme_combo_list.get_value())
            set_dark_mode(dpg.get_value(self.dark_mode_checkbox))

        LightTheme.set(self.light_theme_combo_list.get_value())
        DarkTheme.set(self.dark_theme_combo_list.get_value())

        CustomTheme.set(self.current_theme_combo_list.get_value())
        DarkTitleBar.set(dpg.get_value(self.dark_mode_checkbox))
