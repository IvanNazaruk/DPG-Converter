import time
import traceback
from pathlib import Path

import dearpygui.dearpygui as dpg
from PIL import Image

import fonts
from Resources import settings
from converter import Status
from converter.conrtoller import get_unsupported_load_formats
from converter.images_to_pdf import ImagesToPDF
from converter.images_to_pdf import ImagesToPDFStorage
from converter.tools import open_file_in_explorer
from DPG_modules.Addons import CheckBoxSlider, get_alpha_theme
from DPG_modules.Addons import ImageSizeInput
from .image_table_cell import ImagesToPDFListCell, LoadSettings
from ..image_table import ImageList
from ..load_window import load_window_tqdm, use_load_window
from ..tab_template import AddFileTab


class Window(AddFileTab):
    window: int = None
    image_list: ImageList
    settings: LoadSettings

    def update_settings(self):
        self.size_input.set_enabled(self.set_size_check_box.get_value())
        theme = 0
        if not self.set_size_check_box.get_value():
            theme = get_alpha_theme(0.25)
        dpg.bind_item_theme(self.update_button, theme)
        if self.set_size_check_box.get_value():
            self.settings.size = self.size_input.get_value()
        else:
            self.settings.size = None

    def __init__(self, main_window: int | str):
        super().__init__(main_window)
        self.settings = LoadSettings()
        with dpg.group() as self.window:
            with dpg.table(header_row=False, clipper=True):
                dpg.add_table_column()
                dpg.add_table_column(width_fixed=True)
                with dpg.table_row():
                    dpg.add_spacer()
                    with dpg.group(horizontal=True):
                        dpg.add_text('Size:')
                        self.set_size_check_box = CheckBoxSlider(callback=lambda *args: self.update_settings())
                        self.set_size_check_box.create(True)
                        self.size_input = ImageSizeInput(width=1920, height=1080,
                                                         use_frame_padding=True, callback=self.update_settings)
            with dpg.table(header_row=False, clipper=True):
                dpg.add_table_column()
                dpg.add_table_column(width_fixed=True)
                with dpg.table_row():
                    with dpg.group(horizontal=True):
                        dpg.add_button(label='Clear all', callback=self.clear_all_image_list)
                    with dpg.group(horizontal=True):
                        # dpg.add_button(label='Stop', callback=self.stop_all_cells)
                        # dpg.add_spacer(width=fonts.font_size // 2)
                        dpg.add_button(label='Start', callback=self.start_all_cells)
                        dpg.add_spacer(width=fonts.font_size // 2)
                        self.update_button = dpg.add_button(label='Update', callback=self.update_all_cells)

            self.image_list = ImageList()
        self.update_settings()

    @use_load_window
    def clear_all_image_list(self):
        self.image_list.remove_all()
        dpg.split_frame()
        self.image_list.update_settings()

    @use_load_window
    def start_all_cells(self):
        image_stores = []
        cell: ImagesToPDFListCell
        for cell in load_window_tqdm(self.image_list.all_cells):
            image_stores.append(cell.image_store)
            cell.status = Status.PROCESSING
        if len(image_stores) == 0:
            return
        try:
            path = ImagesToPDF.start(image_stores)
            for image_store in image_stores:
                image_store.dpg_cell.status = Status.DONE
            open_file_in_explorer(path)
            time.sleep(0.3)
        except Exception:
            traceback.print_exc()
            for image_store in image_stores:
                image_store.dpg_cell.status = Status.WAITING

    @use_load_window
    def update_all_cells(self):
        cell: ImagesToPDFListCell
        for cell in load_window_tqdm(self.image_list.all_cells):
            cell.set_settings(self.settings)

    def add_file(self, file_path: Path):
        image = Image.open(file_path)
        if image.format in get_unsupported_load_formats():
            del image
            return
        image_store = ImagesToPDFStorage(None, image)
        cell = ImagesToPDFListCell(self.image_list, image_store, self.settings)
        if settings.AddToEnd.get():
            self.image_list.append(cell)
        else:
            self.image_list.insert(0, cell)
