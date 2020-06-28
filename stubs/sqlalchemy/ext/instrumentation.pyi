from ..orm.instrumentation import ClassManager, InstrumentationFactory
from typing import Any, Optional

INSTRUMENTATION_MANAGER: str

def find_native_user_instrumentation_hook(cls): ...

instrumentation_finders: Any

class ExtendedInstrumentationRegistry(InstrumentationFactory):
    def unregister(self, class_: Any) -> None: ...
    def manager_of_class(self, cls: Any): ...
    def state_of(self, instance: Any): ...
    def dict_of(self, instance: Any): ...

class InstrumentationManager:
    def __init__(self, class_: Any) -> None: ...
    def manage(self, class_: Any, manager: Any) -> None: ...
    def dispose(self, class_: Any, manager: Any) -> None: ...
    def manager_getter(self, class_: Any): ...
    def instrument_attribute(self, class_: Any, key: Any, inst: Any) -> None: ...
    def post_configure_attribute(self, class_: Any, key: Any, inst: Any) -> None: ...
    def install_descriptor(self, class_: Any, key: Any, inst: Any) -> None: ...
    def uninstall_descriptor(self, class_: Any, key: Any) -> None: ...
    def install_member(self, class_: Any, key: Any, implementation: Any) -> None: ...
    def uninstall_member(self, class_: Any, key: Any) -> None: ...
    def instrument_collection_class(self, class_: Any, key: Any, collection_class: Any): ...
    def get_instance_dict(self, class_: Any, instance: Any): ...
    def initialize_instance_dict(self, class_: Any, instance: Any) -> None: ...
    def install_state(self, class_: Any, instance: Any, state: Any) -> None: ...
    def remove_state(self, class_: Any, instance: Any) -> None: ...
    def state_getter(self, class_: Any): ...
    def dict_getter(self, class_: Any): ...

class _ClassInstrumentationAdapter(ClassManager):
    def __init__(self, class_: Any, override: Any) -> None: ...
    def manage(self) -> None: ...
    def dispose(self) -> None: ...
    def manager_getter(self): ...
    def instrument_attribute(self, key: Any, inst: Any, propagated: bool = ...) -> None: ...
    def post_configure_attribute(self, key: Any) -> None: ...
    def install_descriptor(self, key: Any, inst: Any) -> None: ...
    def uninstall_descriptor(self, key: Any) -> None: ...
    def install_member(self, key: Any, implementation: Any) -> None: ...
    def uninstall_member(self, key: Any) -> None: ...
    def instrument_collection_class(self, key: Any, collection_class: Any): ...
    def initialize_collection(self, key: Any, state: Any, factory: Any): ...
    def new_instance(self, state: Optional[Any] = ...): ...
    def setup_instance(self, instance: Any, state: Optional[Any] = ...): ...
    def teardown_instance(self, instance: Any) -> None: ...
    def has_state(self, instance: Any): ...
    def state_getter(self): ...
    def dict_getter(self): ...
