from typing import TYPE_CHECKING

import dearpygui.dearpygui as dpg

from DearPyGui_Addons import CheckBoxSlider, ImageSizeInput
from settings import AutoScrollToNewElement, MaxTooltipImageHeight, MaxTooltipImageWidth

if TYPE_CHECKING:
    from . import Window


class OtherSetting:
    def __init__(self, settings_window: 'Window'):
        self.settings_window = settings_window
        with dpg.group(horizontal=True):
            dpg.add_text("Tooltip max image size:")
            size = MaxTooltipImageWidth.get(), MaxTooltipImageHeight.get()
            self.tooltip_image_size = ImageSizeInput(width=size[0], height=size[1], use_frame_padding=True,
                                                     callback=self.set_max_tooltip_image_size)
        with dpg.group(horizontal=True):
            dpg.add_text("Scroll to the added image:")
            CheckBoxSlider(callback=AutoScrollToNewElement.set) \
                .create(AutoScrollToNewElement.get())

    def set_max_tooltip_image_size(self):
        size = self.tooltip_image_size.get_value()
        MaxTooltipImageWidth.set(size[0])
        MaxTooltipImageHeight.set(size[1])
