"""
Defines commonly required data streams.
"""
from typing import Iterable, Tuple

import rx
import rx.operators as ops
from rx.core.typing import Observable

from benchbuild import source
from benchbuild.typing import ProjectT, VariantContext, VariantTuple


def from_projects(projects: Iterable[ProjectT]) -> Observable:
    """
    Emit a stream of project classes and an associated variant context.

    Args:
        projects: An iterable of project classes, commonly obtained via cli.

    Returns:
        An observable stream of (ProjectT, VariantContext)
    """
    project_stream = rx.from_iterable(projects)

    def add_variants(prj: ProjectT) -> rx.Observable:
        variants = source.product(prj.SOURCE)
        return rx.combine_latest(rx.return_value(prj),
                                 rx.from_iterable(variants))

    def variant_to_context(
            prj: ProjectT,
            var: VariantTuple) -> Tuple[VariantContext, ProjectT]:
        return (prj, source.variants.context(var))

    return project_stream.pipe(
        ops.flat_map(add_variants),
        ops.starmap(variant_to_context),
    )
