import os
from dataclasses import dataclass
from pathlib import Path

import dearpygui.dearpygui as dpg

import converter
from converter import open_file_in_explorer_with_load_window
from converter.images_to_pdf import ImagesToPDFStore
from converter.status import Status, StatusValue
from DearPyGui_Addons import get_alpha_theme, get_text_size, ImageSizeInput
from DearPyGui_ImageController import ImageViewer, TooltipImageViewer
from ...draggable_list import cell_size, DraggableList
from ...draggable_list import DraggableListCell


@dataclass
class LoadSettings:
    size: list[int, int] = None


class ImagesToPDFListCell(DraggableListCell):
    image_viewer: ImageViewer
    file_path: Path | str
    file_name: str

    delete_button: int

    image_size_input: ImageSizeInput
    tooltip_image_viewer: TooltipImageViewer

    _status = Status.WAITING

    @property
    def status(self) -> StatusValue:
        return self._status

    @status.setter
    def status(self, value: StatusValue):
        if self._status == value:
            return
        self._status = value
        if self.cell_group is None:
            return
        self._update_status()

    def _update_status(self):
        dpg.configure_item(self.delete_button, enabled=True)
        match status := self.status:
            case Status.WAITING:
                self.image_size_input.set_enabled(True)
            case Status.IN_QUEUE:
                self.image_size_input.set_enabled(False)
            case Status.PROCESSING:
                self.image_size_input.set_enabled(False)
                dpg.configure_item(self.delete_button, enabled=False)
            case Status.DONE:
                self.image_size_input.set_enabled(True)
            case _:
                raise ValueError(f'Unknown status: {status}')
        dpg.bind_item_theme(self.theme_group, self.status.get_theme())

    def __init__(self, image_list: 'DraggableList', image_store: ImagesToPDFStore, settings: LoadSettings):
        super().__init__(image_list)
        self.load_settings = settings
        self.image_store = image_store
        self.image_store.dpg_cell = self

        self.image_list = image_list
        self.image_viewer = ImageViewer(self.image_store.image)
        self.output_width = self.image_store.image.width
        self.output_height = self.image_store.image.height

        if hasattr(self.image_store.image, "filename"):
            self.file_path = self.image_store.image.filename
            self.file_name = os.path.basename(self.file_path)
            self.tooltip_image = self.file_path
        else:
            self.file_path = "{IN_RAM}"
            self.file_name = "{IN_RAM}"
            self.tooltip_image = self.image_store.image

    def __pre_create__(self, cell_group: int | str):
        super().__pre_create__(cell_group)

    def create(self, window):
        # print('test:', self.window, window)
        with dpg.table(header_row=False, clipper=True, parent=window) as table:
            dpg.add_table_column(parent=table)
            dpg.add_table_column(width_fixed=True, parent=table)
            with dpg.table_row(parent=table) as row:
                # 1-st Column
                with dpg.group(horizontal=True, parent=row) as group:
                    self.delete_button = dpg.add_button(label="X", width=int(get_text_size(" X ")[0]), height=-1,
                                                        callback=lambda: self.image_list.remove(self), parent=group)
                    dpg.add_spacer(width=4, parent=group)
                    self.image_viewer.create(width=cell_size, height=cell_size, parent=group)
                    dpg.add_spacer(width=8, parent=group)
                    with dpg.group(parent=group) as file_group:
                        file_name = self.file_name
                        if len(file_name) > 21:
                            file_name = file_name[:9:] + '...' + file_name[-9::]
                        _ = dpg.add_text(f'{file_name}', parent=file_group)
                        dpg.bind_item_theme(_, get_alpha_theme(0.6))
                        with dpg.group(horizontal=True, parent=file_group) as resize_info_group:
                            dpg.add_text(f'{self.image_store.image.width}×{self.image_store.image.height}', parent=resize_info_group)
                            dpg.add_spacer(width=16, parent=resize_info_group)
                            dpg.add_text(f'{self.image_store.image.format}', parent=resize_info_group)
                # 2-st Column
                with dpg.group(parent=row, horizontal=True):
                    with dpg.group() as resize_row:
                        dpg.add_text(parent=resize_row)
                        with dpg.group(horizontal=True, parent=resize_row) as resize_group:
                            dpg.add_spacer(width=16, parent=resize_group)
                            width, height = self.image_store.image.width, self.image_store.image.height
                            if self.load_settings.size is not None:
                                width, height = self.load_settings.size
                            self.image_size_input = ImageSizeInput(width, height,
                                                                   callback=self.image_settings_changed, parent=resize_group)
                            dpg.add_spacer(width=8, parent=resize_group)

                    self.tooltip_image_viewer = TooltipImageViewer(self.image_viewer._view_window,  # noqa
                                                                   self.tooltip_image)

    def image_settings_changed(self):
        if self.status == Status.DONE:
            self.status = Status.WAITING

    def set_settings(self, settings: LoadSettings):
        if self.status == Status.PROCESSING:
            return

        self.image_settings_changed()
        if settings.size is not None:
            self.image_size_input.set_value(settings.size)

    def on_convert_click(self):
        match self.status:
            case Status.WAITING:
                self.status = Status.IN_QUEUE
                converter.ImageToImage.add_to_queue(self.image_store)
            case Status.IN_QUEUE:
                if converter.ImageToImage.remove_from_queue(self.image_store):
                    self.status = Status.WAITING
            case Status.PROCESSING:
                pass
            case Status.DONE:
                # print('open_image:', self.image_store.output_path)
                if os.path.exists(self.image_store.output_path):
                    open_file_in_explorer_with_load_window(self.image_store.output_path)
                else:
                    self.status = Status.WAITING
                    self.on_convert_click()

    def selected(self):
        dpg.configure_item(self.delete_button, enabled=False)
        super().selected()

    def unselected(self):
        self._update_status()
        super().unselected()

    def delete(self):
        if self.cell_group is None:
            return

        if self.status == Status.IN_QUEUE:
            converter.ImageToImage.remove_from_queue(self.image_store)
        del self.image_store.image
        del self.image_store

        super().delete()

        self.image_viewer.delete()
        self.image_size_input.delete()
        self.tooltip_image_viewer.delete()
