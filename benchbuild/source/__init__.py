# pylint: disable=useless-import-alias
"""
Declarative API for downloading sources required by benchbuild.
"""
from .base import FetchableSource as FetchableSource
from .base import Expandable as Expandable
from .base import ContextAwareSource as ContextAwareSource
from .base import ContextEnumeratorFn as ContextEnumeratorFn
from .base import Variant as Variant
from .base import Revision as Revision
from .base import RevisionStr as RevisionStr
from .base import NestedVariants as NestedVariants
from .base import nosource as nosource
from .base import primary as primary
from .base import secondaries as secondaries
from .base import product as product
from .base import enumerate_revisions as enumerate_revisions
from .base import revision_from_str as revision_from_str
from .base import sources_as_dict as sources_as_dict
from .base import to_str as to_str
from .git import Git as Git
from .git import GitSubmodule as GitSubmodule
from .http import HTTP as HTTP
from .http import HTTPMultiple as HTTPMultiple
from .http import HTTPUntar as HTTPUntar
from .versions import BaseVersionFilter as BaseVersionFilter
from .versions import SingleVersionFilter as SingleVersionFilter
