from pathlib import Path

import dearpygui.dearpygui as dpg
from PIL import Image

import converter.image_to_image
import fonts
import settings
from converter import Status
from converter.conrtoller import Controller, get_unsupported_load_formats
from converter.image_to_image import ImageToImageStore
from DearPyGui_Addons import CheckBoxSlider, ComboList, ImageSizeInput
from DearPyGui_Addons import context_manager_decorator
from .draggable_list_cell import ImageToDraggableListCell
from .draggable_list_cell import LoadSettings
from ..tab_template import AddFileTab
from ...draggable_list import DraggableList
from ...load_window import load_window_tqdm, use_load_window


class Window(AddFileTab):
    window: int = None
    image_list: DraggableList
    settings: LoadSettings

    def update_settings(self):
        self.size_input.set_enabled(self.set_size_check_box.get_value())
        if self.set_size_check_box.get_value():
            self.settings.size = self.size_input.get_value()
        else:
            self.settings.size = None
        self.settings.format = self.format_combo_list.get_value()
        self.settings.auto_start = self.auto_start_check_box.get_value()
        # print('Updating settings:', self.settings)

    def __init__(self, main_window: int | str):
        super().__init__(main_window)
        self.settings = LoadSettings()
        with dpg.group() as self.window:
            with dpg.table(header_row=False, clipper=True):
                dpg.add_table_column()
                dpg.add_table_column(width_fixed=True)
                dpg.add_table_column(width_fixed=True)
                with dpg.table_row():
                    with dpg.group(horizontal=True):
                        dpg.add_text("Auto-start:")
                        self.auto_start_check_box = CheckBoxSlider(callback=lambda *args: self.update_settings()) \
                            .create(True)

                    with dpg.group(horizontal=True):
                        dpg.add_text('Size:')
                        self.set_size_check_box = CheckBoxSlider(callback=lambda *args: self.update_settings()) \
                            .create(True)
                        self.size_input = ImageSizeInput(width=1920, height=1080,
                                                         use_frame_padding=True, callback=self.update_settings)
                    with dpg.group(horizontal=True):
                        dpg.add_spacer(width=fonts.font_size // 2)
                        dpg.add_text('Format:')
                        self.format_combo_list = ComboList(converter.image_to_image.get_name_all_output_formats(),
                                                           use_frame_padding=True, callback=self.update_settings)
            with dpg.table(header_row=False, clipper=True):
                dpg.add_table_column()
                dpg.add_table_column(width_fixed=True)
                with dpg.table_row():
                    with dpg.group(horizontal=True):
                        dpg.add_button(label='Clear all', callback=self.clear_all_image_list)
                    with dpg.group(horizontal=True):
                        dpg.add_button(label='Stop', callback=self.stop_all_cells)
                        dpg.add_spacer(width=fonts.font_size // 2)
                        dpg.add_button(label='Start', callback=self.start_all_cells)
                        dpg.add_spacer(width=fonts.font_size // 2)
                        dpg.add_button(label='Update', callback=self.update_all_cells)

            self.image_list = DraggableList()
        self.update_settings()

    @use_load_window
    def update_all_cells(self):
        cell: ImageToDraggableListCell
        for cell in load_window_tqdm(self.image_list.all_cells):
            cell.set_settings(self.settings)

    @use_load_window
    @context_manager_decorator(Controller.ENABLED_EVENT)
    def stop_all_cells(self):
        cell: ImageToDraggableListCell
        for cell in load_window_tqdm(self.image_list.all_cells):
            match cell.status:
                case Status.PROCESSING | Status.DONE:
                    continue
                case Status.IN_QUEUE:
                    if not converter.ImageToImage.remove_from_queue(cell.image_store):
                        continue
            cell.status = Status.WAITING

    @use_load_window
    def start_all_cells(self):
        cell: ImageToDraggableListCell
        for cell in load_window_tqdm(self.image_list.all_cells):
            if cell.status == Status.WAITING:
                cell.status = Status.IN_QUEUE
                converter.ImageToImage.add_to_queue(cell.image_store)

    @use_load_window
    @context_manager_decorator(Controller.ENABLED_EVENT)
    def clear_all_image_list(self):
        self.image_list.remove_all()
        dpg.split_frame()
        self.image_list.update_settings()

    def add_file(self, file_path: Path):
        image = Image.open(file_path)
        if image.format in get_unsupported_load_formats():
            del image
            return
        image_store = ImageToImageStore(None, image)
        cell = ImageToDraggableListCell(self.image_list, image_store, self.settings)
        if settings.AddToEnd.get():
            self.image_list.append(cell)
        else:
            self.image_list.insert(0, cell)
