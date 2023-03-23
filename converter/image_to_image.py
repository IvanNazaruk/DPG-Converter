import os
import traceback
from dataclasses import dataclass
from functools import lru_cache
from typing import TYPE_CHECKING

from PIL import Image

from .conrtoller import Controller, ImageStore
from .conrtoller import get_safely_file_name, output_path
from .status import Status

if TYPE_CHECKING:
    from gui.tabs.ImageToImage.image_table_cell import ImageToDraggableListCell


@lru_cache
def get_output_formats_dict():
    not_supported_formats = [
        "BLP",
        "BUFR",
        "FITS",
        "GRIB",
        "HDF5",
        "MSP",
        "PALM",
        "WMF",
        "XBM",
    ]

    all_formats = {value: key for key, value in Image.registered_extensions().items()}
    supported_formats = {}

    for _format in Image.SAVE:
        if _format in not_supported_formats:
            continue
        try:
            supported_formats[_format] = all_formats[_format]
        except KeyError:
            pass
            # print('Not supported format: {}'.format(_format))

    supported_formats["PNG"] = ".png"
    return supported_formats


@lru_cache
def get_name_all_output_formats():
    return tuple(get_output_formats_dict().keys())


@dataclass
class ImageToImageStore(ImageStore):
    image: Image
    dpg_cell: 'ImageToDraggableListCell' = None


class ImageToImage(Controller):
    queue: dict[id, ImageToImageStore] = {}

    @classmethod
    def _processing(cls, image_store: ImageToImageStore) -> bool:
        cell = image_store.dpg_cell
        if cell.cell_group is None:
            return False
        image = image_store.image
        new_size = cell.image_size_input.get_value()
        new_format = cell.format_combolist.get_value()
        file_extension = get_output_formats_dict()[new_format]

        filename = "output"
        if hasattr(image, "filename"):
            filename = os.path.basename(image.filename)

        filename, ext = os.path.splitext(filename)
        path = os.path.join(output_path, cls.session_name, f"{filename}{file_extension}")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        path = get_safely_file_name(path)

        new_image = image.resize(new_size, Image.NEAREST)  # noqa
        new_image.save(path, format=new_format)
        del new_image, image
        image_store.output_path = path
        return True

    @classmethod
    def processing(cls, image_store: ImageToImageStore):
        cell = image_store.dpg_cell
        cell.status = Status.PROCESSING
        for _ in range(3):
            try:
                cls._processing(image_store)
                cell.status = Status.DONE
                return
            except Exception:
                traceback.print_exc()
        cell.status = Status.WAITING
