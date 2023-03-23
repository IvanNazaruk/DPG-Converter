import configparser
import os
from typing import Type

import darkdetect

import DearPyGui_Theme as dpg_theme
from DearPyGui_Addons.dpg_callback import dpg_callback
from .settings import *
from .statics import application_path

file_name = 'settings.ini'
file_path = os.path.join(application_path, 'settings', file_name)

all_settings: dict[str, dict[str, Type[SettingValue]]] = {
    'Theme': {
        'UseSystemColor': UseSystemColor,
        'LightTheme': LightTheme,
        'DarkTheme': DarkTheme,
        'CustomTheme': CustomTheme,
        'DarkTitleBar': DarkTitleBar,
    },
    'Table': {
        'AddToEnd': AddToEnd,
        'FullWindowScrollBar': FullWindowScrollBar,
    },
    'Other': {
        'MaxTooltipImageWidth': MaxTooltipImageWidth,
        'MaxTooltipImageHeight': MaxTooltipImageHeight,
        'AutoScrollToNewElement': AutoScrollToNewElement,
    }
}


@dpg_callback()
def save_settings():
    config = configparser.ConfigParser()
    for category_name in all_settings.keys():
        setting_category = {}
        for setting_name, setting in all_settings[category_name].items():
            setting_category[setting_name] = setting.get()
        config[category_name] = setting_category

    with open(file_path, 'w') as configfile:
        config.write(configfile)


def convert_str_by_type(string: str, example_value: Any):  # TODO: Perhaps this should be rewritten to something normal
    # print(f'"Converting "{string}" to {type(example_value)}"')
    string = str(string)
    value_type = type(example_value)
    if value_type is str:
        return string
    elif value_type is bool:
        if string.lower() == 'true':
            return True
        if string.lower() == 'false':
            return False
        if string == '1':
            return True
        if string == '0':
            return False
    elif value_type is int:
        return int(string)
    elif value_type is float:
        return float(string)
    raise ValueError


def load_settings():
    if not os.path.exists(file_path):
        return
    config = configparser.ConfigParser()
    config.read(file_path)
    for category_name in all_settings.keys():
        try:
            category = config[category_name]
        except KeyError:
            continue
        for setting_name, setting in all_settings[category_name].items():
            try:
                setting.set(
                    convert_str_by_type(category[setting_name], setting.get())
                )
            except KeyError:
                continue
            except ValueError:
                continue


def start_up():
    if UseSystemColor.get():
        if darkdetect.isDark():
            theme_name = DarkTheme.get()
        else:
            theme_name = LightTheme.get()
    else:
        theme_name = CustomTheme.get()

    theme = dpg_theme.get_theme_by_name(theme_name)
    dpg_theme.CurrentTheme.set(theme, fast=True)
