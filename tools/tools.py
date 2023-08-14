from __future__ import annotations

import dearpygui.dearpygui as dpg


def get_local_mouse_pos(dpg_item: int | str) -> list[int, int]:  # TODO: Refactor this
    mouse_pos: list[int, int] = list(dpg.get_mouse_pos(local=False))
    all_parents: list[int | str] = []
    parent = dpg_item
    while True:
        parent = dpg.get_item_parent(parent)
        object_type = dpg.get_item_info(parent)['type']
        if object_type in ('mvAppItemType::mvChildWindow', 'mvAppItemType::mvWindowAppItem'):
            all_parents.append(parent)
            if object_type == 'mvAppItemType::mvWindowAppItem':
                break

    object_type = dpg.get_item_info(dpg_item)['type']
    if object_type in ('mvAppItemType::mvChildWindow', 'mvAppItemType::mvWindowAppItem'):
        all_parents.append(dpg_item)

    item_pos = [0, 0]
    for parent in all_parents:
        item_pos = [x + y for x, y in zip(item_pos, dpg.get_item_pos(parent))]
    mouse_pos[0] = mouse_pos[0] - item_pos[0]
    mouse_pos[1] = mouse_pos[1] - item_pos[1]
    for window in all_parents:
        mouse_pos[0] += dpg.get_x_scroll(window)
        mouse_pos[1] += dpg.get_y_scroll(window)
    return mouse_pos


def get_window(dpg_item: int | str) -> int | str:
    while True:
        if not dpg.does_item_exist(dpg_item):
            return 0
        if dpg.get_item_info(dpg_item)['type'] == 'mvAppItemType::mvWindowAppItem':
            return dpg_item
        dpg_item = dpg.get_item_parent(dpg_item)
