# Author: olekristensen
from __future__ import annotations

from typing import Optional, Sequence

import dearpygui.dearpygui as dpg

name = """ledSynthmaster"""
styles: dict[int, Sequence[float]] = {
    dpg.mvStyleVar_Alpha: [1.0],
    dpg.mvStyleVar_WindowPadding: [15.0, 15.0],
    dpg.mvStyleVar_WindowRounding: [5.0],
    dpg.mvStyleVar_WindowBorderSize: [1.0],
    dpg.mvStyleVar_WindowMinSize: [32.0, 32.0],
    dpg.mvStyleVar_WindowTitleAlign: [0.0, 0.5],
    dpg.mvStyleVar_ChildRounding: [0.0],
    dpg.mvStyleVar_ChildBorderSize: [1.0],
    dpg.mvStyleVar_PopupRounding: [0.0],
    dpg.mvStyleVar_PopupBorderSize: [1.0],
    dpg.mvStyleVar_FramePadding: [5.0, 5.0],
    dpg.mvStyleVar_FrameRounding: [4.0],
    dpg.mvStyleVar_FrameBorderSize: [0.0],
    dpg.mvStyleVar_ItemSpacing: [12.0, 8.0],
    dpg.mvStyleVar_ItemInnerSpacing: [8.0, 6.0],
    dpg.mvStyleVar_CellPadding: [4.0, 2.0],
    dpg.mvStyleVar_IndentSpacing: [25.0],
    dpg.mvStyleVar_ScrollbarSize: [15.0],
    dpg.mvStyleVar_ScrollbarRounding: [9.0],
    dpg.mvStyleVar_GrabMinSize: [5.0],
    dpg.mvStyleVar_GrabRounding: [3.0],
    dpg.mvStyleVar_TabRounding: [4.0],
    dpg.mvStyleVar_ButtonTextAlign: [0.5, 0.5],
    dpg.mvStyleVar_SelectableTextAlign: [0.0, 0.0],
}
colors: dict[int, Sequence[int, int, int, Optional[int]]] = {
    dpg.mvThemeCol_Text: [102, 99, 96, 255],
    dpg.mvThemeCol_TextDisabled: [102, 99, 96, 196],
    dpg.mvThemeCol_WindowBg: [234, 232, 224, 178],
    dpg.mvThemeCol_ChildBg: [234, 232, 224, 178],
    dpg.mvThemeCol_PopupBg: [234, 232, 224, 178],
    dpg.mvThemeCol_Border: [214, 211, 204, 165],
    dpg.mvThemeCol_BorderShadow: [234, 232, 224, 0],
    dpg.mvThemeCol_FrameBg: [255, 249, 242, 255],
    dpg.mvThemeCol_FrameBgHovered: [252, 255, 102, 198],
    dpg.mvThemeCol_FrameBgActive: [66, 255, 0, 255],
    dpg.mvThemeCol_TitleBg: [255, 249, 242, 255],
    dpg.mvThemeCol_TitleBgActive: [63, 255, 0, 255],
    dpg.mvThemeCol_TitleBgCollapsed: [255, 249, 242, 191],
    dpg.mvThemeCol_MenuBarBg: [255, 249, 242, 119],
    dpg.mvThemeCol_ScrollbarBg: [255, 249, 242, 255],
    dpg.mvThemeCol_ScrollbarGrab: [0, 0, 0, 53],
    dpg.mvThemeCol_ScrollbarGrabHovered: [229, 232, 0, 198],
    dpg.mvThemeCol_ScrollbarGrabActive: [63, 255, 0, 255],
    dpg.mvThemeCol_CheckMark: [63, 255, 0, 204],
    dpg.mvThemeCol_SliderGrab: [0, 0, 0, 35],
    dpg.mvThemeCol_SliderGrabActive: [63, 255, 0, 255],
    dpg.mvThemeCol_Button: [0, 0, 0, 35],
    dpg.mvThemeCol_ButtonHovered: [252, 255, 56, 219],
    dpg.mvThemeCol_ButtonActive: [63, 255, 0, 255],
    dpg.mvThemeCol_Header: [63, 255, 0, 193],
    dpg.mvThemeCol_HeaderHovered: [63, 255, 0, 219],
    dpg.mvThemeCol_HeaderActive: [63, 255, 0, 255],
    dpg.mvThemeCol_Separator: [0, 0, 0, 81],
    dpg.mvThemeCol_SeparatorHovered: [63, 255, 0, 198],
    dpg.mvThemeCol_SeparatorActive: [63, 255, 0, 255],
    dpg.mvThemeCol_ResizeGrip: [0, 0, 0, 10],
    dpg.mvThemeCol_ResizeGripHovered: [63, 255, 0, 198],
    dpg.mvThemeCol_ResizeGripActive: [63, 255, 0, 255],
    dpg.mvThemeCol_Tab: [45, 89, 147, 219],
    dpg.mvThemeCol_TabHovered: [66, 150, 249, 204],
    dpg.mvThemeCol_TabActive: [50, 104, 173, 255],
    dpg.mvThemeCol_TabUnfocused: [17, 26, 37, 247],
    dpg.mvThemeCol_TabUnfocusedActive: [34, 66, 108, 255],
    dpg.mvThemeCol_PlotLines: [102, 99, 96, 160],
    dpg.mvThemeCol_PlotLinesHovered: [63, 255, 0, 255],
    dpg.mvThemeCol_PlotHistogram: [102, 99, 96, 160],
    dpg.mvThemeCol_PlotHistogramHovered: [63, 255, 0, 255],
    dpg.mvThemeCol_TableHeaderBg: [48, 48, 51, 255],
    dpg.mvThemeCol_TableBorderStrong: [79, 79, 89, 255],
    dpg.mvThemeCol_TableBorderLight: [58, 58, 63, 255],
    dpg.mvThemeCol_TableRowBg: [0, 0, 0, 0],
    dpg.mvThemeCol_TableRowBgAlt: [255, 255, 255, 15],
    dpg.mvThemeCol_TextSelectedBg: [63, 255, 0, 109],
    dpg.mvThemeCol_DragDropTarget: [255, 255, 0, 229],
    dpg.mvThemeCol_NavHighlight: [66, 150, 249, 255],
    dpg.mvThemeCol_NavWindowingHighlight: [255, 255, 255, 178],
    dpg.mvThemeCol_NavWindowingDimBg: [204, 204, 204, 51],
    dpg.mvThemeCol_ModalWindowDimBg: [255, 249, 242, 186],
}
clear_color = colors.get(dpg.mvThemeCol_WindowBg, (0, 0, 0))