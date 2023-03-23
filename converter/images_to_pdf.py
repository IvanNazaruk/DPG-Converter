import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from PIL.Image import Image

from converter.conrtoller import get_safely_file_name, ImageStore, output_path
from gui.load_window import load_window_tqdm

if TYPE_CHECKING:
    from gui.tabs.ImagesToPDF.draggable_list_cell import ImagesToPDFListCell


@dataclass
class ImagesToPDFStore(ImageStore):
    image: Image
    dpg_cell: 'ImagesToPDFListCell' = None


class ImagesToPDF:
    @classmethod
    def start(cls, image_stores: list[ImagesToPDFStore]) -> Path:
        session_name = datetime.now().strftime("%d.%m %H.%M")
        all_images = []
        image_store: ImagesToPDFStore
        for image_store in load_window_tqdm(image_stores):
            img: Image = image_store.image.convert('RGB')
            img = img.resize(image_store.dpg_cell.image_size_input.get_value())  # noqa
            all_images.append(img)

        filename = 'output.pdf'
        filename, file_extension = os.path.splitext(filename)
        path = os.path.join(output_path, session_name, f"{filename}{file_extension}")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        path = get_safely_file_name(path)

        all_images[0].save(path, save_all=True, append_images=all_images[1::])

        image: Image
        for image in all_images:  # noqa
            del image
        del all_images
        return path
