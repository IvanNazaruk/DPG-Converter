import threading

import dearpygui.dearpygui as dpg

dpg.create_context()
dpg.create_viewport(title="Demo WIP", width=900, height=600,
                    x_pos=1920 // 2 - 900 // 2,
                    y_pos=1080 // 2 - 600 // 2)


def main():
    import gui
    main_widow = gui.MainWindow()
    dpg.set_primary_window(main_widow.window, True)
    gui.LoadWindow.create()


import sys

if sys.platform.startswith('win'):
    import ctypes

    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(u'CompanyName.ProductName.SubProduct.VersionInformation')
    ctypes.windll.shcore.SetProcessDpiAwareness(1)

dpg.configure_viewport(0, clear_color=(255, 255, 255))
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.render_dearpygui_frame()

import DearPyGui_DragAndDrop as dpg_dnd

import DPG_modules.Animations as dpg_anim
import DPG_modules.Theme as dpg_theme
from DPG_modules.Addons.title_bar import set_dark_mode
from Resources import fonts, settings

dpg_dnd.initialize()
settings.load_settings()
dpg.bind_font(fonts.load(show=False))
dpg.bind_theme(dpg_theme.initialize())

set_dark_mode(True)
dpg.render_dearpygui_frame()

threading.Thread(target=main, daemon=True).start()
while dpg.is_dearpygui_running():
    dpg_anim.update()
    dpg.render_dearpygui_frame()
dpg.destroy_context()
