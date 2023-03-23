import subprocess
import time
from pathlib import Path

from gui.load_window import use_load_window


@use_load_window
def open_file_in_explorer_with_load_window(file_path: Path):
    open_file_in_explorer(file_path)
    time.sleep(0.7)


def open_file_in_explorer(file_path: Path):
    subprocess.run(["explorer", "/select,", file_path])
