from typing import Any

import dearpygui.dearpygui as dpg
from DearPyGui_DragAndDrop import DragAndDrop, DragAndDropDataObject

from . import ImagesToPDF
from . import ImageToImage
from . import settings_window


class MainWindow(DragAndDrop):
    window: int = None
    tabs: dict[int, Any] = {}
    settings_window: settings_window.Window

    def __init__(self):
        super().__init__()
        with dpg.window() as self.window:
            with dpg.tab_bar() as self.tab_bar:
                dpg.add_tab_button(label="[S]", callback=lambda: dpg.show_item(self.settings_window.window))
                with dpg.tab(label='ImageToImage') as tab:
                    self.tabs[tab] = ImageToImage.Window(self.window)
                with dpg.tab(label='ImagesToPDF') as tab:
                    self.tabs[tab] = ImagesToPDF.Window(self.window)
        self.settings_window = settings_window.Window()

    def Drop(self, path_list: DragAndDropDataObject, _):
        if path_list is None:
            return
        path_list: list[str]
        if isinstance(path_list, str):
            path_list = [path_list]

        path_list = path_list
        # print(dpg.get_value(self.tab_bar), self.tabs)
        processing_window = self.tabs[dpg.get_value(self.tab_bar)]
        processing_window.load_files(path_list)
