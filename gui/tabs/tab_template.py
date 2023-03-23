import time
import traceback
from abc import ABC, abstractmethod
from pathlib import Path

import dearpygui.dearpygui as dpg

import settings
from DearPyGui_Addons import dpg_callback
from DearPyGui_Animations.dpg.scroll import ScrollYAnimation
from DearPyGui_ImageController import ENABLE_LOADING
from ..draggable_list import DraggableList
from ..load_window import load_window_tqdm, use_load_window


class AddFileTab(ABC):
    window: int = None
    image_list: DraggableList
    scroll_bar_animation: ScrollYAnimation

    def __init__(self, main_window: int | str):
        self.main_window = main_window
        self.scroll_bar_animation = ScrollYAnimation(0, 0)

    @abstractmethod
    def add_file(self, file_path: Path):
        ...

    @dpg_callback(sender=True)
    @use_load_window
    def load_files(self, path_list: list[str]):
        ENABLE_LOADING.clear()  # FIXME
        start_time = time.time()

        def create_animation(duration: float):
            self.scroll_bar_animation.delete()
            if settings.AutoScrollToNewElement.get():
                window = self.image_list.window
                if settings.FullWindowScrollBar.get():
                    window = self.main_window

                if settings.AddToEnd.get():
                    start_value = int(dpg.get_y_scroll(window))
                    if settings.FullWindowScrollBar.get():
                        dpg.split_frame(delay=0)
                        end_value = int(dpg.get_y_scroll_max(window))
                    else:
                        end_value = self.image_list.get_all_height() - dpg.get_item_rect_size(window)[1]
                else:
                    start_value = int(dpg.get_y_scroll(window))
                    end_value = 0
                    if end_value == start_value:
                        return
                self.scroll_bar_animation = ScrollYAnimation(window, start_value) \
                    .add_point(end_value, duration, (.42, 0, .58, 1)) \
                    .start()

        create_animation(0.6)

        for path in load_window_tqdm(path_list):
            try:
                self.add_file(path)
            except Exception:
                traceback.print_exc()
            if settings.AddToEnd.get():
                if time.time() - start_time > 0.8:
                    start_time = time.time()
                    create_animation(0.6)

        if settings.AddToEnd.get():
            create_animation(0.35)

        ENABLE_LOADING.set()  # FIXME
