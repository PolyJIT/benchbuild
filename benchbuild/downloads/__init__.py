"""
Declarative API for downloading sources required by benchbuild.
"""
from .git import Git
from .http import HTTP

from .base import default
from .base import product
from .base import BaseSource
