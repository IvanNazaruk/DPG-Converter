import os
import threading
import traceback
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import TypeVar

from PIL import Image

from Resources.settings import application_path

Image.init()

output_path = os.path.join(application_path, "OUTPUT")


@lru_cache
def get_unsupported_load_formats() -> list:
    unsupported_formats = [
        "EPS",
    ]
    return unsupported_formats


def get_safely_file_name(filename):
    base, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(filename):
        filename = f"{base} ({counter}){ext}"
        counter += 1
    return filename


@dataclass
class ImageStore(ABC):
    output_path: Path | str | None


ImageStoreType = TypeVar('ImageStoreType', bound=ImageStore)


class _ENABLED_EVENT(threading.Event):
    def __enter__(self):
        self.clear()

    def __exit__(self, *args, **kwargs):
        self.set()


class Controller(ABC):
    ENABLED_EVENT = _ENABLED_EVENT()
    ENABLED_EVENT.set()

    is_thread_ran: bool = False
    queue: dict[id, ImageStoreType] = {}
    session_name: str = ''

    @classmethod
    def add_to_queue(cls, image_store: ImageStoreType):
        if id(image_store) in cls.queue:
            return

        image_store.output_path = None
        cls.queue[id(image_store)] = image_store
        if cls.is_thread_ran is False:
            cls.is_thread_ran = True
            cls.session_name = datetime.now().strftime("%d.%m %H.%M")
            threading.Thread(target=cls.worker, daemon=True).start()

    @classmethod
    def remove_from_queue(cls, image_store: ImageStoreType) -> bool:
        try:
            del cls.queue[id(image_store)]
            return True
        except Exception:
            traceback.print_exc()
        return False

    @classmethod
    def worker(cls):
        cls.ENABLED_EVENT.wait()
        while len(cls.queue) > 0:
            image_store_id = next(iter(cls.queue))
            image_store = cls.queue.pop(image_store_id)
            cls.processing(image_store)
            cls.ENABLED_EVENT.wait()
        cls.is_thread_ran = False

    @classmethod
    @abstractmethod
    def processing(cls, cell: ImageStoreType):
        ...
