import dearpygui.dearpygui as dpg

import DPG_modules.Theme as dpg_theme


class StatusValue:
    _theme: int = None
    child_bg_color: int
    blend_alpha: int = 255

    color: tuple[int, int, int, int] = (0, 0, 0, 0)

    @classmethod
    def get_theme(cls) -> int:
        if cls._theme is None:
            cls._theme = cls.create_theme()
        return cls._theme

    @classmethod
    def create_theme(cls) -> int:
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvChildWindow, parent=theme) as theme_component:
                dpg.add_theme_color(dpg.mvThemeCol_Border, cls.color, category=dpg.mvThemeCat_Core, parent=theme_component)
                cls.child_bg_color = dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (0, 0, 0, 0), category=dpg.mvThemeCat_Core, parent=theme_component)
            with dpg.theme_component(dpg.mvAll, parent=theme) as theme_component:
                dpg.add_theme_color(dpg.mvThemeCol_Border, cls.color, category=dpg.mvThemeCat_Core, parent=theme_component)

            dpg_theme.subscribe_color_theme_change(dpg.mvThemeCol_ChildBg, cls.set_child_bg_color)
        return theme

    @classmethod
    def set_child_bg_color(cls, bg_color: tuple[int, int, int, int]):
        *bg_color, bg_alpha = bg_color
        alpha = cls.blend_alpha / 255.0
        blend_color = [int((1 - alpha) * bg_color[i] + alpha * cls.color[i]) for i in range(3)]
        blend_color += [bg_alpha]
        # print('blend_color:', blend_color)
        dpg.set_value(cls.child_bg_color, blend_color)


class WAITING(StatusValue):
    color = (0, 0, 0, 0)
    blend_alpha = 0

    @classmethod
    def create_theme(cls) -> int:
        return dpg.add_theme()


class IN_QUEUE(StatusValue):
    color = (139, 0, 255, 225)
    blend_alpha = 40


class PROCESSING(StatusValue):
    color = (60, 230, 230, 255)
    blend_alpha = 40


class DONE(StatusValue):
    color = (0, 250, 0, 225)
    blend_alpha = 40


class Status:
    WAITING = WAITING
    IN_QUEUE = IN_QUEUE
    PROCESSING = PROCESSING
    DONE = DONE
