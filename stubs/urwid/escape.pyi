from typing import Any

within_double_byte: Any
SO: str
SI: str
IBMPC_ON: str
IBMPC_OFF: str
DEC_TAG: str
DEC_SPECIAL_CHARS: str
ALT_DEC_SPECIAL_CHARS: str
DEC_SPECIAL_CHARMAP: Any
SAFE_ASCII_DEC_SPECIAL_RE: Any
DEC_SPECIAL_RE: Any

class MoreInputRequired(Exception): ...

def escape_modifier(digit: Any): ...

input_sequences: Any

class KeyqueueTrie:
    data: Any = ...
    def __init__(self, sequences: Any) -> None: ...
    def add(self, root: Any, s: Any, result: Any): ...
    def get(self, keys: Any, more_available: Any): ...
    def get_recurse(self, root: Any, keys: Any, more_available: Any): ...
    def read_mouse_info(self, keys: Any, more_available: Any): ...
    def read_cursor_position(self, keys: Any, more_available: Any): ...

MOUSE_RELEASE_FLAG: int
MOUSE_MULTIPLE_CLICK_MASK: int
MOUSE_MULTIPLE_CLICK_FLAG: int
MOUSE_DRAG_FLAG: int
input_trie: Any

def process_keyqueue(codes: Any, more_available: Any): ...

ESC: str
CURSOR_HOME: Any
CURSOR_HOME_COL: str
APP_KEYPAD_MODE: Any
NUM_KEYPAD_MODE: Any
SWITCH_TO_ALTERNATE_BUFFER: Any
RESTORE_NORMAL_BUFFER: Any
REPORT_STATUS: Any
REPORT_CURSOR_POSITION: Any
INSERT_ON: Any
INSERT_OFF: Any

def set_cursor_position(x: Any, y: Any): ...
def move_cursor_right(x: Any): ...
def move_cursor_up(x: Any): ...
def move_cursor_down(x: Any): ...

HIDE_CURSOR: Any
SHOW_CURSOR: Any
MOUSE_TRACKING_ON: Any
MOUSE_TRACKING_OFF: Any
DESIGNATE_G1_SPECIAL: Any
ERASE_IN_LINE_RIGHT: Any
