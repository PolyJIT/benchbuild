from typing import Any

loc: Any

class NullTranslation:
    def gettext(self, str: Any): ...
    def ngettext(self, str1: Any, strN: Any, n: Any): ...

def get_translation_for(package_name: Any): ...

local_dir: Any
