"""
Defines commonly required data streams.
"""
import copy
from typing import Iterable, Tuple

import rx
from rx.core.typing import Observable

from benchbuild import source
from benchbuild.typing import ExperimentT, ProjectT, VariantContext


def project_stream(project_classes: Iterable[ProjectT]) -> Observable:
    return rx.from_iterable([
        pc(source.variants.context(variant))
        for pc in project_classes
        for variant in source.product(pc.SOURCE)
    ]).pipe(rx.operators.map(copy.deepcopy))


def experiment_stream(experiment_classes: Iterable[ExperimentT]) -> Observable:
    return rx.from_iterable([exp() for exp in experiment_classes
                            ]).pipe(rx.operators.map(copy.deepcopy))
