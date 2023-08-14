import time
from functools import cache
from typing import TYPE_CHECKING

import dearpygui.dearpygui as dpg

from .themes import THEME
from ..Addons.dpg_callback import dpg_callback
from ..Animations import StyleAnimation, StyleColorAnimation
from ..Animations.animator.list import IntListAnimation
from ..Animations.animator.value import FloatValueAnimation

if TYPE_CHECKING:
    from ..Animations.loop import AnimatorType

__all__ = [
    "global_theme", "global_theme_component",
    "all_styles", "all_colors",
    "CurrentTheme", "initialize",
    "get_current_theme_name", "get_theme_by_name", "get_theme_names",
    "add_theme_picker"
]

global_theme: int = None  # noqa
global_theme_component: int = None  # noqa

all_styles: dict[int, int] = {}
all_colors: dict[int, int] = {}


class CurrentTheme:
    theme: THEME = THEME.COMFY
    changing_progress: float = 0

    @classmethod
    def set(cls, theme: THEME, *, fast: bool = False):
        if theme == cls.get():
            return
        duration = 0 if fast else 0.3
        _change_theme(theme, duration)
        cls.theme = theme

    @classmethod
    def get(cls) -> THEME:
        return cls.theme


@dpg_callback(sender=True)
def _change_theme(theme: THEME, duration: float):
    if None in (global_theme, global_theme_component):
        return
    all_animations: list[AnimatorType] = []

    for dpg_id, style in theme.value.styles.items():
        tag = all_styles.get(dpg_id)
        if tag is None:
            tag = dpg.add_theme_style(dpg_id, *style, category=dpg.mvThemeCat_Core,
                                      parent=global_theme_component)  # noqa
            all_styles[dpg_id] = tag

        anim = StyleAnimation(tag, dpg.get_value(tag))
        anim.add_point(style, duration, (.55, -0.01, .4, 1))
        all_animations.append(anim)

    for dpg_id, color in theme.value.colors.items():
        tag = all_colors.get(dpg_id)
        if tag is None:
            tag = dpg.add_theme_color(dpg_id, color, category=dpg.mvThemeCat_Core,
                                      parent=global_theme_component)  # noqa
            all_colors[dpg_id] = tag

        anim = StyleColorAnimation(tag, dpg.get_value(tag))
        anim.add_point(color, duration, (.55, -0.01, .4, 1))
        all_animations.append(anim)

    anim = IntListAnimation(list(map(lambda x: int(x * 255), dpg.get_viewport_clear_color())),
                            lambda _color: dpg.configure_viewport(0, clear_color=_color))
    anim.add_point(theme.value.clear_color, duration, (.55, -0.01, .4, 1))
    all_animations.append(anim)

    from .runtime_changes import update_theme_callback
    anim = FloatValueAnimation(0, update_theme_callback)
    anim.add_point(1, duration)
    all_animations.append(anim)
    for anim in all_animations:
        anim.start()

    if duration > 0:
        time.sleep(duration)
        dpg.split_frame()

    for anim in all_animations:
        if not anim.PAUSED:
            anim.pause()
            anim.__pre_set_value__(anim.points[-1].value)
            anim.delete()

    del all_animations
    if duration > 0:
        dpg.split_frame()
        dpg.split_frame()
    else:
        update_theme_callback(1)


def initialize() -> int:
    """
    :return: global theme
    """
    global global_theme, global_theme_component

    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll) as global_theme_component:
            for dpg_id, style in CurrentTheme.get().value.styles.items():
                tag = dpg.add_theme_style(dpg_id, *style, category=dpg.mvThemeCat_Core)
                all_styles[dpg_id] = tag

            for dpg_id, color in CurrentTheme.get().value.colors.items():
                tag = dpg.add_theme_color(dpg_id, color, category=dpg.mvThemeCat_Core)  # noqa
                all_colors[dpg_id] = tag

    class TempTheme:
        class value:
            name = "StartupTheme"
            colors = THEME.LIGHT.value.colors
            styles = CurrentTheme.get().value.styles
            clear_color = THEME.LIGHT.value.clear_color

    new_theme = CurrentTheme.get()
    CurrentTheme.set(TempTheme, fast=True)  # noqa
    CurrentTheme.set(new_theme)
    return global_theme


def get_current_theme_name() -> str:
    return str(CurrentTheme.get().name)


def get_theme_by_name(theme_name: str) -> THEME:
    return getattr(THEME, theme_name)


@cache
def get_theme_names() -> tuple[str]:
    return tuple(str(theme.name) for theme in THEME)


def add_theme_picker() -> int:
    return dpg.add_combo(
        items=get_theme_names(),
        default_value=get_current_theme_name(),
        callback=lambda _, value: CurrentTheme.set(get_theme_by_name(value)),
    )
