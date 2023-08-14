from __future__ import annotations

import time
from threading import Thread
from typing import Any, Callable, Optional

import dearpygui.dearpygui as dpg
from DearPyGui_DragAndDrop import DROPEFFECT, set_drop_effect
from tqdm.auto import tqdm as base_tqdm

import DPG_modules.Theme as dpg_theme
from DPG_modules.Addons import dpg_handler
from DPG_modules.Animations import StyleAnimation, StyleColorAnimation
from DPG_modules.Animations.animator.value import FloatValueAnimationABC, IntValueAnimationABC


class ThreadWithReturnValue(Thread):
    _kwargs = None
    _args = None
    _target = None

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, daemon: bool = False):
        if kwargs is None:
            kwargs = {}
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,
                                        **self._kwargs)

    def join(self, timeout: float = None):
        super().join(timeout)
        return self._return

    @property
    def result(self):
        return self._return


class LoadWindowPositionAnimation(IntValueAnimationABC):
    def set_value(self, value: int):
        window_size = dpg.get_item_rect_size(LoadWindow.window)
        center = dpg.get_viewport_client_width() / 2, dpg.get_viewport_client_height() / 2

        center = [int(center[0] - window_size[0] / 2), int(center[1] - window_size[1] / 2)]
        center[1] = int(center[1] * 0.75 + value)
        LoadWindow.start_y_pos = value
        dpg.configure_item(LoadWindow.window, pos=center)


class ProgressBarAnimation(FloatValueAnimationABC):
    def set_value(self, value: float):
        dpg.set_value(LoadWindow.progress_bar, value)


class LoadWindow:
    window: int
    loading_indicator: int
    progress_bar: int

    __theme: int = None
    bg_theme_color: int
    li_alpha_style: int
    pb_alpha_style: int

    color_animation: StyleColorAnimation
    li_alpha_animation: StyleAnimation
    pb_alpha_animation: StyleAnimation
    pos_animation: LoadWindowPositionAnimation
    progress_bar_animation: ProgressBarAnimation

    duration_animation = 0.35
    bg_alpha: int = 100
    start_y_pos = -150

    @classmethod
    def __get_theme(cls):
        if cls.__theme is None:
            with dpg.theme() as cls.__theme:
                with dpg.theme_component() as theme_component:
                    dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0, 0, category=dpg.mvThemeCat_Core, parent=theme_component)
                    dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0, 0, category=dpg.mvThemeCat_Core, parent=theme_component)
                    dpg.add_theme_style(dpg.mvStyleVar_CellPadding, 0, 0, category=dpg.mvThemeCat_Core, parent=theme_component)
                    dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 0, 0, category=dpg.mvThemeCat_Core, parent=theme_component)
                    cls.bg_theme_color = dpg.add_theme_color(dpg.mvThemeCol_ModalWindowDimBg, (0, 0, 0, cls.bg_alpha), category=dpg.mvThemeCat_Core, parent=theme_component)
                with dpg.theme_component(dpg.mvLoadingIndicator) as theme_component:
                    cls.li_alpha_style = dpg.add_theme_style(dpg.mvStyleVar_Alpha, 0, category=dpg.mvThemeCat_Core, parent=theme_component)
                with dpg.theme_component(dpg.mvProgressBar) as theme_component:
                    cls.pb_alpha_style = dpg.add_theme_style(dpg.mvStyleVar_Alpha, 0, category=dpg.mvThemeCat_Core, parent=theme_component)

                # with dpg.theme_component(dpg.mvButton) as theme_component:
                #     dpg.add_theme_style(dpg.mvStyleVar_Alpha, 0, category=dpg.mvThemeCat_Core, parent=theme_component)

        return cls.__theme

    @classmethod
    def _bg_color_change(cls, color: list[int, int, int, Optional[int]]):
        color = color[:3:]
        color = [255 - channel for channel in color]

        cls.color_animation.start_value = type(cls.color_animation.start_value)(color + [0])
        end_point = cls.color_animation.points[0]
        end_point.value = type(end_point.value)(color + [cls.bg_alpha])

    @classmethod
    def _loading_indicator_color_change(cls, color: list[int, int, int, Optional[int]]):
        color = color[:3:]
        secondary_color = dpg_theme.get_theme_color_value(dpg.mvThemeCol_WindowBg)[:3:]
        dpg.configure_item(cls.loading_indicator, color=color, secondary_color=secondary_color)

    @classmethod
    def create(cls):
        if hasattr(cls, "window"):
            return
        with dpg.window(show=False, modal=True, autosize=True, no_background=True, no_move=True, no_title_bar=True, no_scrollbar=True) as cls.window:
            dpg.bind_item_theme(cls.window, cls.__get_theme())
            cls.loading_indicator = dpg.add_loading_indicator(color=(50, 220, 100), secondary_color=(50, 50, 175), radius=7, )
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=10)
                cls.progress_bar = dpg.add_progress_bar(width=-10, default_value=0)
            # dpg.add_button(label="Hide", callback=cls.hide)

        # Animations
        cls.color_animation = StyleColorAnimation(cls.bg_theme_color, (0, 0, 0, 0))
        cls.color_animation.add_point((0, 0, 0, cls.bg_alpha), cls.duration_animation)

        cls.li_alpha_animation = StyleAnimation(cls.li_alpha_style, [0])
        cls.li_alpha_animation.add_point([1], cls.duration_animation)

        cls.pb_alpha_animation = StyleAnimation(cls.pb_alpha_style, [0])
        cls.pb_alpha_animation.add_point([1.2], cls.duration_animation)

        cls.pos_animation = LoadWindowPositionAnimation(cls.start_y_pos)
        cls.pos_animation.add_point(0, 1, (.19, .16, .01, .94))

        cls.progress_bar_animation = ProgressBarAnimation(0)

        # Themes
        dpg_handler.add_viewport_resize_callback(cls.update_pos)
        dpg_theme.subscribe_color_theme_change(dpg.mvThemeCol_WindowBg, cls._bg_color_change)
        dpg_theme.subscribe_color_theme_change(dpg.mvThemeCol_Text, cls._loading_indicator_color_change)

    @classmethod
    def update_pos(cls):
        window_size = dpg.get_item_rect_size(cls.window)
        center = dpg.get_viewport_client_width() / 2, dpg.get_viewport_client_height() / 2

        center = [int(center[0] - window_size[0] / 2), int(center[1] - window_size[1] / 2)]
        center[1] = int(center[1] * 0.75 + cls.start_y_pos)

        dpg.configure_item(cls.window, pos=center)

    @classmethod
    def run_function(cls, function: Callable[[None], Any]) -> Any | None:
        set_drop_effect(DROPEFFECT.NONE)
        cls.create()
        cls.__pre_show__()
        start_time = time.time()
        thread = ThreadWithReturnValue(target=function, daemon=True)
        thread.start()
        was_shown = False
        while thread.is_alive():
            time.sleep(0.01)
            if time.time() - start_time > 0.15:
                cls.show()
                was_shown = True
                break
        thread.join()
        if was_shown:
            cls.hide()
        else:
            dpg.configure_item(cls.window, show=False)
        set_drop_effect(DROPEFFECT.MOVE)
        return thread.result

    @classmethod
    def __pre_show__(cls):
        dpg.set_value(cls.li_alpha_style, [0])
        dpg.set_value(cls.bg_theme_color, [0, 0, 0, 0])
        dpg.set_value(cls.progress_bar, 0)
        dpg.configure_item(cls.window, show=True)

    @classmethod
    def show(cls):
        cls.__pre_show__()
        dpg.split_frame()
        cls.update_pos()

        animations_list = (cls.color_animation, cls.li_alpha_animation, cls.pb_alpha_animation,
                           cls.pos_animation)
        for animation in animations_list:
            animation.set_reverse(False)
            animation.start()
            animation.update()

    @classmethod
    def hide(cls):
        cls.update_progress_bar(1)
        animations_list = (cls.color_animation, cls.li_alpha_animation, cls.pb_alpha_animation,
                           cls.pos_animation)
        for animation in animations_list:
            animation.set_reverse(True)
            if animation.PAUSED:
                animation.start()

        while True:
            if cls.color_animation.PAUSED:
                break
            time.sleep(0.01)
        for i in range(2):
            dpg.split_frame()
        dpg.configure_item(cls.window, show=False)

    @classmethod
    def update_progress_bar(cls, progress: float, text: str = ""):
        cls.progress_bar_animation.update()
        cls.progress_bar_animation.delete()
        cls.progress_bar_animation = ProgressBarAnimation(dpg.get_value(cls.progress_bar))
        cls.progress_bar_animation.add_point(progress, 0.25, (0, 0, .38, .92))
        cls.progress_bar_animation.start()
        # dpg.configure_item(cls.progress_bar, default_value=progress, label=text)


class load_window_tqdm(base_tqdm):
    def __init__(self, *args, mininterval=0.3, smoothing=1, **kwargs):
        super().__init__(*args, mininterval=mininterval, smoothing=smoothing, disable=True, **kwargs)

    def update(self, n=1, always_callback=False):
        if super().update(n) or always_callback:
            LoadWindow.update_progress_bar(self.format_dict['n'] / self.format_dict['total'],
                                           text=f"{self.format_dict['n']}/{self.format_dict['total']}")


def use_load_window(func):
    def run(*args, **kwargs):
        return LoadWindow.run_function(
            lambda: func(*args, **kwargs)
        )

    return run
