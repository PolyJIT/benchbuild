from typing import Any

LFANEW_OFFSET: Any
FILE_HEADER_SIZE: Any
SUBSYSTEM_OFFSET: Any
IMAGE_SUBSYSTEM_WINDOWS_GUI: int
IMAGE_SUBSYSTEM_WINDOWS_CUI: int

def get_pe_subsystem(filename: Any): ...
