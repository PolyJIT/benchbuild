# pylint: disable=useless-import-alias
"""
Declarative API for downloading sources required by benchbuild.
"""
from .base import FetchableSource as FetchableSource
from .base import Variant as Variant
from .base import VariantContext as VariantContext
from .base import context as context
from .base import default as default
from .base import nosource as nosource
from .base import primary as primary
from .base import product as product
from .base import sources_as_dict as sources_as_dict
from .base import to_str as to_str
from .git import Git as Git
from .git import GitSubmodule as GitSubmodule
from .http import HTTP as HTTP
from .versions import BaseVersionFilter as BaseVersionFilter
from .versions import BaseVersionGroup as BaseVersionGroup
from .versions import SingleVersionFilter as SingleVersionFilter
