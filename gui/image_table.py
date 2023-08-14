from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar

import dearpygui.dearpygui as dpg

import fonts as dpg_font
import tools
from DPG_modules.Addons import dpg_handler
from gui.load_window import load_window_tqdm
from Resources.settings import FullWindowScrollBar
from tools import get_local_mouse_pos

cell_border_size = 3
cell_size = dpg_font.font_size * 2 + int(cell_border_size * 1.5)


class ImageListCell(ABC):
    image_list: ImageList
    cell_group: int | str = None
    theme_group: int | str = None
    window: int | str = None

    _theme: int = None
    _selected_theme: int = None
    _handler: int = None

    @classmethod
    def get_theme(cls):
        if cls._theme is None:
            with dpg.theme() as cls._theme:
                with dpg.theme_component(dpg.mvAll, parent=cls._theme) as theme_component:
                    dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, cell_border_size, category=dpg.mvThemeCat_Core, parent=theme_component)
                    dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0, 0, category=dpg.mvThemeCat_Core, parent=theme_component)
                    dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0, 0, category=dpg.mvThemeCat_Core, parent=theme_component)
                    dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 0, 0, category=dpg.mvThemeCat_Core, parent=theme_component)
                    dpg.add_theme_style(dpg.mvStyleVar_CellPadding, 0, 0, category=dpg.mvThemeCat_Core, parent=theme_component)
        return cls._theme

    @classmethod
    def get_selected_theme(cls):
        if cls._selected_theme is None:
            with dpg.theme() as cls._selected_theme:
                with dpg.theme_component(dpg.mvAll, parent=cls._selected_theme) as theme_component:
                    dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, cell_border_size, category=dpg.mvThemeCat_Core, parent=theme_component)
                    dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0, 0, category=dpg.mvThemeCat_Core, parent=theme_component)
                    dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0, 0, category=dpg.mvThemeCat_Core, parent=theme_component)
                    dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 0, 0, category=dpg.mvThemeCat_Core, parent=theme_component)
                    dpg.add_theme_style(dpg.mvStyleVar_CellPadding, 0, 0, category=dpg.mvThemeCat_Core, parent=theme_component)
                with dpg.theme_component(dpg.mvChildWindow, parent=cls._selected_theme) as theme_component:
                    dpg.add_theme_color(dpg.mvThemeCol_Border, (60, 230, 230), category=dpg.mvThemeCat_Core, parent=theme_component)
        return cls._selected_theme

    def __init__(self, image_list: ImageList):
        self.image_list = image_list

    def __pre_create__(self, cell_group: int | str):
        self.cell_group = cell_group
        self.theme_group = dpg.add_group(parent=cell_group)
        self.window = dpg.add_child_window(width=-1, height=cell_size, parent=self.theme_group, show=False)
        self.create(self.window)
        dpg.bind_item_theme(self.window, self.get_theme())
        dpg.show_item(self.window)

    @abstractmethod
    def create(self, window: int | str) -> None:
        ...

    def selected(self):
        dpg.bind_item_theme(self.window, self.get_selected_theme())

    def unselected(self):
        dpg.bind_item_theme(self.window, self.get_theme())

    def __del__(self):
        self.delete()

    def delete(self):
        if self.cell_group is None:
            return

        try:
            dpg.delete_item(self.cell_group)
        except Exception:
            pass
        finally:
            self.cell_group = None  # noqa


ImageListCellType = TypeVar("ImageListCellType", bound=ImageListCell)


class ImageList:
    table: int = None

    DISABLE_DRAG = False

    all_cells: list[ImageListCellType]
    is_now_selected: bool = False
    selected_cell: ImageListCellType | None = None
    selected_cell_pos: list[int, int] | None = None

    temporary_cell: int | None = None
    new_cell_index: int = None

    window_padding: list[int, int] = (50, 10)
    space_between_cells: int = 10
    draggable_dead_zone: int = 5
    start_mouse_pos: list[int, int] | None = None

    _theme = None
    _draggable_theme = None

    def get_theme(self):
        if self._theme is None:
            with dpg.theme() as self._theme:
                with dpg.theme_component(dpg.mvAll, parent=self._theme) as theme_component:
                    dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, self.window_padding[0], self.window_padding[1], category=dpg.mvThemeCat_Core, parent=theme_component)
                    dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0, 0, category=dpg.mvThemeCat_Core, parent=theme_component)
                    dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 0, self.space_between_cells, category=dpg.mvThemeCat_Core, parent=theme_component)
                    dpg.add_theme_style(dpg.mvStyleVar_CellPadding, 0, 0, category=dpg.mvThemeCat_Core, parent=theme_component)
        return self._theme

    def get_draggable_theme(self):
        if self._draggable_theme is None:
            with dpg.theme() as self._draggable_theme:
                with dpg.theme_component(dpg.mvAll, parent=self._draggable_theme) as theme_component:
                    # dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 1, category=dpg.mvThemeCat_Core, parent=theme_component)
                    dpg.add_theme_color(dpg.mvThemeCol_Border, (60, 230, 230, 0), category=dpg.mvThemeCat_Core, parent=theme_component)
                    dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (20, 80, 80), category=dpg.mvThemeCat_Core, parent=theme_component)

        return self._draggable_theme

    def __init__(self):
        self.all_cells = []

        dpg_handler.add_mouse_down_callback(self.mouse_down)
        dpg_handler.add_mouse_release_callback(self.mouse_released)

        with dpg.child_window(height=-1, width=-1) as self.window:
            dpg.bind_item_theme(self.window, self.get_theme())

        FullWindowScrollBar.subscribe(self.update_settings)

    def append(self, cell: ImageListCellType):
        self.all_cells.append(cell)
        self.update_settings()
        with dpg.group(parent=self.window) as cell_group:
            cell.__pre_create__(cell_group)

    def insert(self, index: int, cell: ImageListCellType):
        if len(self.all_cells) == 0:
            return self.append(cell)
        if index >= len(self.all_cells):
            index = len(self.all_cells) - 1

        index_cell: ImageListCellType
        index_cell = self.all_cells[index]
        self.all_cells.insert(index, cell)
        self.update_settings()
        with dpg.group(before=index_cell.cell_group) as cell_group:
            cell.__pre_create__(cell_group)

    def remove_all(self):
        saved_all_cells = self.all_cells.copy()
        self.all_cells.clear()
        dpg.delete_item(self.window, children_only=True)
        cell: ImageListCellType
        for cell in load_window_tqdm(saved_all_cells):
            cell.delete()
        del saved_all_cells

    def remove(self, cell: ImageListCellType | int):
        index: int = cell
        if not isinstance(cell, int):
            index = self.all_cells.index(cell)
        cell = self.all_cells[index]
        del self.all_cells[index]
        cell.delete()

    def get_all_height(self):
        return len(self.all_cells) * cell_size + len(self.all_cells) * self.space_between_cells + self.window_padding[1] * 2

    def update_settings(self):
        height = -1
        if FullWindowScrollBar.value:
            height = self.get_all_height()
        dpg.configure_item(self.window, height=height)

    # Runtime logic
    def update_drag(self, margin_pos: list[int, int]):
        if self.selected_cell is None:
            return

        # Change the position depending on the original position and the position of the mouse
        new_pos = [self.selected_cell_pos[0] + margin_pos[0], self.selected_cell_pos[1] + margin_pos[1]]
        # ============================ ONLY Y POS =====================================
        new_pos = [self.selected_cell_pos[0], new_pos[1]]
        # =============================================================================
        dpg.set_item_pos(self.selected_cell.cell_group, new_pos)

        # Moving the temporary cell
        all_cells = dpg.get_item_children(self.window, slot=1)
        all_cells.remove(self.temporary_cell)
        dpg.move_item(self.temporary_cell, before=all_cells[self.new_cell_index])

    def start_drag(self):
        if self.selected_cell is None:
            return

        # Get the index of the cell to be dragged
        cell_index = self.all_cells.index(self.selected_cell)
        self.selected_cell_pos = dpg.get_item_pos(self.selected_cell.cell_group)

        all_cells = dpg.get_item_children(self.window, slot=1)

        # Create a temporary space so that the elements do not change their position
        # with dpg.mutex():
        if True:
            # Creating a temporary cell
            with dpg.child_window(height=cell_size, before=all_cells[cell_index]) as self.temporary_cell:
                dpg.bind_item_theme(self.temporary_cell, self.get_draggable_theme())

            # Change the position so that the window is on top of all
            dpg.move_item(self.selected_cell.cell_group, parent=self.window)

    def mouse_down(self):
        if self.DISABLE_DRAG:
            return
        # if pressed elsewhere
        if self.is_now_selected and self.selected_cell is None:
            return

        mouse_pos = get_local_mouse_pos(self.window)
        mouse_pos[0] -= self.window_padding[0]
        mouse_pos[1] -= self.window_padding[1]

        # Checking click or drag
        if self.start_mouse_pos is None:
            self.start_mouse_pos = mouse_pos
        margin_mouse_pos = [mouse_pos[0] - self.start_mouse_pos[0], mouse_pos[1] - self.start_mouse_pos[1]]
        if -self.draggable_dead_zone < margin_mouse_pos[0] < self.draggable_dead_zone and \
                -self.draggable_dead_zone < margin_mouse_pos[1] < self.draggable_dead_zone:
            return

        if not self.is_now_selected:
            self.is_now_selected = True
            # If the window is resized
            if tools.GetNowCursorType() != 65539:  # 65539 - default cursor
                return
            # if working in another window (possibly an active window on top of the table)
            if tools.get_window(self.window) != tools.get_window(dpg.get_active_window()):
                return

        cell_space = cell_size + self.space_between_cells

        window_size = dpg.get_item_rect_size(self.window)

        # Check for dragging elsewhere
        if mouse_pos[0] < 0:
            return
        if mouse_pos[0] - window_size[0] + self.window_padding[0] * 2 > 0:
            return  # TODO: fix scroll size
        if (mouse_pos[1] + self.window_padding[1] - dpg.get_y_scroll(self.window)) > window_size[1]:
            return  # TODO: fix scroll

        cell_index = int(mouse_pos[1] // cell_space)
        # Check if there was a click between cells
        if cell_index >= len(self.all_cells) or cell_index < 0:  # click before/after table
            return
        if cell_index != ((mouse_pos[1] + self.space_between_cells) // cell_space):  # click between cells
            if self.selected_cell is not None:
                self.update_drag(margin_mouse_pos)
            return

        if self.selected_cell is None:
            self.selected_cell = self.all_cells[cell_index]
            self.selected_cell.selected()
            self.start_drag()
        self.new_cell_index = cell_index
        self.update_drag(margin_mouse_pos)

    def mouse_released(self):
        self.start_mouse_pos = None
        self.is_now_selected = False
        if not self.selected_cell:
            return

        # with dpg.mutex():
        if True:
            # Deleting the temporary cell
            dpg.delete_item(self.temporary_cell)
            # Replace it with a draggable cell
            all_cells = dpg.get_item_children(self.window, slot=1)
            if self.new_cell_index != len(all_cells) - 1:
                dpg.move_item(self.selected_cell.cell_group, before=all_cells[self.new_cell_index])
            dpg.reset_pos(self.selected_cell.cell_group)

            # Put the cell in its new index
            self.all_cells.pop(self.all_cells.index(self.selected_cell))
            self.all_cells.insert(self.new_cell_index, self.selected_cell)

            # Return the variables to their original values
            self.selected_cell.unselected()
            self.temporary_cell = None
            self.selected_cell = None
            self.selected_cell_pos = None
