import urwid
from typing import Any, Optional

class TreeWidgetError(RuntimeError): ...

class TreeWidget(urwid.WidgetWrap):
    indent_cols: int = ...
    unexpanded_icon: Any = ...
    expanded_icon: Any = ...
    is_leaf: Any = ...
    expanded: bool = ...
    def __init__(self, node: Any) -> None: ...
    def selectable(self): ...
    def get_indented_widget(self): ...
    def update_expanded_icon(self) -> None: ...
    def get_indent_cols(self): ...
    def get_inner_widget(self): ...
    def load_inner_widget(self): ...
    def get_node(self): ...
    def get_display_text(self): ...
    def next_inorder(self): ...
    def prev_inorder(self): ...
    def keypress(self, size: Any, key: Any): ...
    def mouse_event(self, size: Any, event: Any, button: Any, col: Any, row: Any, focus: Any): ...
    def first_child(self): ...
    def last_child(self): ...

class TreeNode:
    def __init__(self, value: Any, parent: Optional[Any] = ..., key: Optional[Any] = ..., depth: Optional[Any] = ...) -> None: ...
    def get_widget(self, reload: bool = ...): ...
    def load_widget(self): ...
    def get_depth(self): ...
    def get_index(self): ...
    def get_key(self): ...
    def set_key(self, key: Any) -> None: ...
    def change_key(self, key: Any) -> None: ...
    def get_parent(self): ...
    def load_parent(self) -> None: ...
    def get_value(self): ...
    def is_root(self): ...
    def next_sibling(self): ...
    def prev_sibling(self): ...
    def get_root(self): ...

class ParentNode(TreeNode):
    def __init__(self, value: Any, parent: Optional[Any] = ..., key: Optional[Any] = ..., depth: Optional[Any] = ...) -> None: ...
    def get_child_keys(self, reload: bool = ...): ...
    def load_child_keys(self) -> None: ...
    def get_child_widget(self, key: Any): ...
    def get_child_node(self, key: Any, reload: bool = ...): ...
    def load_child_node(self, key: Any) -> None: ...
    def set_child_node(self, key: Any, node: Any) -> None: ...
    def change_child_key(self, oldkey: Any, newkey: Any) -> None: ...
    def get_child_index(self, key: Any): ...
    def next_child(self, key: Any): ...
    def prev_child(self, key: Any): ...
    def get_first_child(self): ...
    def get_last_child(self): ...
    def has_children(self): ...

class TreeWalker(urwid.ListWalker):
    focus: Any = ...
    def __init__(self, start_from: Any) -> None: ...
    def get_focus(self): ...
    def set_focus(self, focus: Any) -> None: ...
    def get_next(self, start_from: Any): ...
    def get_prev(self, start_from: Any): ...

class TreeListBox(urwid.ListBox):
    def keypress(self, size: Any, key: Any): ...
    def unhandled_input(self, size: Any, input: Any): ...
    def collapse_focus_parent(self, size: Any) -> None: ...
    def move_focus_to_parent(self, size: Any) -> None: ...
    def focus_home(self, size: Any) -> None: ...
    def focus_end(self, size: Any) -> None: ...
