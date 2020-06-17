"""
Declarative API for downloading sources required by benchbuild.
"""
from .base import BaseSource, default, product
from .git import Git
from .http import HTTP
