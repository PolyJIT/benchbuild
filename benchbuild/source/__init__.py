# pylint: disable=useless-import-alias
"""
Declarative API for downloading sources required by benchbuild.
"""
from .base import BaseSource as BaseSource
from .base import Variant as Variant
from .base import VariantContext as VariantContext
from .base import context as context
from .base import default as default
from .base import nosource as nosource
from .base import primary as primary
from .base import product as product
from .base import to_str as to_str
from .git import Git as Git
from .http import HTTP as HTTP
from .versions import BaseVersionFilter as BaseVersionFilter
from .versions import BaseVersionGroup as BaseVersionGroup
from .versions import SingleVersionFilter as SingleVersionFilter
