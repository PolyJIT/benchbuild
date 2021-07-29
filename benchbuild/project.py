"""Project

A project in benchbuild is an abstract representation of a software
system that can live in various stages throughout an experiment.
It defines two extension points for an experiment to attach on, the
compile-time phase and the (optional) run-time phase.

An experiment can intercept the compilation phase of a project and perform
any experiment that requires the source artifacts as input.

Furthermore, it is possible to intercept a project's run-time pahse with
a measurement.

The project definition ensures that all experiments run through the same
series of commands in both phases and that all experiments run inside
a separate build directory in isolation of one another.
"""
import copy
import logging
import typing as tp
import uuid
from abc import abstractmethod
from functools import partial
from os import getenv

import attr
import yaml
from plumbum import local
from plumbum.path.local import LocalPath
from pygtrie import StringTrie

from benchbuild import extensions, source
from benchbuild.environments.domain.declarative import ContainerImage
from benchbuild.settings import CFG
from benchbuild.source import primary, Git
from benchbuild.utils import db, run, unionfs
from benchbuild.utils.requirements import Requirement
from benchbuild.utils.revision_ranges import RevisionRange

LOG = logging.getLogger(__name__)

MaybeGroupNames = tp.Optional[tp.List[str]]
ProjectNames = tp.List[str]
VariantContext = source.VariantContext
Sources = tp.List[source.FetchableSource]
ContainerDeclaration = tp.Union[ContainerImage,
                                tp.List[tp.Tuple[RevisionRange,
                                                 ContainerImage]]]

__REGISTRATION_SEPARATOR = '/'
__REGISTRATION_OPTIONALS = ['/', '-']


class ProjectRegistry(type):
    """Registry for benchbuild projects."""

    projects = StringTrie()

    def __new__(
        mcs: tp.Type['Project'], name: str, bases: tp.Tuple[type, ...],
        attrs: tp.Dict[str, tp.Any]
    ) -> tp.Any:
        """Register a project in the registry."""
        cls = super(ProjectRegistry, mcs).__new__(mcs, name, bases, attrs)
        name = attrs["NAME"] if "NAME" in attrs else cls.NAME
        domain = attrs["DOMAIN"] if "DOMAIN" in attrs else cls.DOMAIN
        group = attrs["GROUP"] if "GROUP" in attrs else cls.GROUP

        defined_attrs = all(bool(attr) for attr in [name, domain, group])

        if bases and defined_attrs:
            key = f'{name}/{group}'
            ProjectRegistry.projects[key] = cls

        return cls


class ProjectDecorator(ProjectRegistry):
    """
    Decorate the interface of a project with the in_builddir decorator.

    This is just a small safety net for benchbuild users, because we make
    sure to run every project method in the project's build directory.
    """

    decorated_methods = ["redirect", "compile", "run_tests"]

    def __init__(cls, name, bases, attrs):
        unionfs_deco = None
        if CFG["unionfs"]["enable"]:
            rw_dir = str(CFG["unionfs"]["rw"])
            unionfs_deco = partial(unionfs.unionfs, rw=rw_dir)
        config_deco = run.store_config

        methods = ProjectDecorator.decorated_methods
        for key, value in attrs.items():
            if (key in methods) and hasattr(cls, key):
                wrapped_fun = value
                wrapped_fun = config_deco(wrapped_fun)

                if unionfs_deco is not None:
                    wrapped_fun = unionfs_deco()(wrapped_fun)

                wrapped_fun = run.in_builddir('.')(wrapped_fun)
                setattr(cls, key, wrapped_fun)

        super(ProjectDecorator, cls).__init__(name, bases, attrs)


@attr.s
class Project(metaclass=ProjectDecorator):
    """Abstract class for benchbuild projects.

    A project is an arbitrary software system usable by benchbuild in
    experiments.
    Subclasses of Project are registered automatically by benchbuild, if
    imported in the same interpreter session. For this to happen, you must list
    the in the settings under plugins -> projects.

    A project implementation *must* provide the following method:
        compile: Downloads & Compiles the source.

    A project implementation *may* provide the following functions:
        run_tests: Wrap any binary that has to be run under the
            runtime_extension wrapper and execute an implementation defined
            set of run-time tests.
        clean: Clean the project's build directory. Defaults to
            recursive 'rm' on the build directory and can be disabled
            by setting the environment variable ``BB_CLEAN=false``.

    Raises:
        AttributeError: Class definition raises an attribute error, if
            the implementation does not provide a value for the attributes
            `NAME`, `DOMAIN`, and `GROUP`
        TypeError: Validation of properties may throw a TypeError.

    Attributes:
        name (str, optional):
            The name of this project. Defaults to `NAME`.
        domain (str, optional):
            The application domain of this project. Defaults to `DOMAIN`.
        group (str, optional):
            The group this project belongs to. Defaults to `GROUP`.
        container (benchbuild.utils.container.Container, optional):
            A uchroot compatible container that we can use for this project.
            Defaults to `benchbuild.utils.container.Gentoo`.
        requirements (:obj:`list` of :obj:`Requirement`)
            A list of specific requirements that are used to configure the
            execution environment.
        version (str, optional):
            A version information for this project. Defaults to `VERSION`.
        builddir (str, optional):
            The build directory for this project. Auto generated, if not set.
        cflags (:obj:`list` of :obj:`str`, optional)
            A list of cflags used, for compilation of this project.
        ldflags (:obj:`list` of :obj:`str`, optional)
            A list of ldflags used, for compilation of this project.
        run_uuid (uuid.UUID, optional):
            An UUID that identifies all binaries executed by a single run of
            this project. In the database schema this is named the 'run_group'.
        compiler_extension (Callable[str, iterable[str], RunInfo], optional):
            A composable extension that will be used in place of the real
            compiler. Defaults to running the compiler with a timeout command
            wrapped around it.
        runtime_extension (Callable[str, iterable[str], RunInfo], optional):
            A composable extension that will be used in place of any binary
            this project
            wants to execute. Which binaries to replace is defined by the
            implementation using `benchbuild.utils.wrapping.wrap`.
            Defaults to None.
    """
    CONTAINER: tp.ClassVar[ContainerDeclaration] = ContainerImage()
    DOMAIN: tp.ClassVar[str] = ""
    GROUP: tp.ClassVar[str] = ""
    NAME: tp.ClassVar[str] = ""
    REQUIREMENTS: tp.ClassVar[tp.List[Requirement]] = []
    SOURCE: tp.ClassVar[Sources] = []

    def __new__(cls, *args, **kwargs):
        """Create a new project instance and set some defaults."""
        del args, kwargs

        new_self = super(Project, cls).__new__(cls)
        mod_ident = f'{cls.__name__} @ {cls.__module__}'
        if not cls.NAME:
            raise AttributeError(
                f'{mod_ident} does not define a NAME class attribute.'
            )
        if not cls.DOMAIN:
            raise AttributeError(
                f'{mod_ident} does not define a DOMAIN class attribute.'
            )
        if not cls.GROUP:
            raise AttributeError(
                f'{mod_ident} does not define a GROUP class attribute.'
            )

        return new_self

    variant: VariantContext = attr.ib()

    @variant.default
    def __default_variant(self) -> VariantContext:
        return source.default(*type(self).SOURCE)

    name: str = attr.ib(
        default=attr.Factory(lambda self: type(self).NAME, takes_self=True)
    )

    domain: str = attr.ib(
        default=attr.Factory(lambda self: type(self).DOMAIN, takes_self=True)
    )

    group: str = attr.ib(
        default=attr.Factory(lambda self: type(self).GROUP, takes_self=True)
    )

    container: ContainerImage = attr.ib(default=attr.Factory(ContainerImage))

    cflags: tp.List[str] = attr.ib(default=attr.Factory(list))

    ldflags: tp.List[str] = attr.ib(default=attr.Factory(list))

    run_uuid: uuid.UUID = attr.ib()

    @run_uuid.default
    def __default_run_uuid(self):  # pylint: disable=no-self-use
        run_group = getenv("BB_DB_RUN_GROUP", None)
        if run_group:
            return uuid.UUID(run_group)
        return uuid.uuid4()

    @run_uuid.validator
    def __check_if_uuid(self, _: tp.Any, value: uuid.UUID) -> None:  # pylint: disable=no-self-use
        if not isinstance(value, uuid.UUID):
            raise TypeError("{attribute} must be a valid UUID object")

    builddir: local.path = attr.ib(
        default=attr.Factory(
            lambda self: local.path(str(CFG["build_dir"])) / self.id / self.
            run_uuid,
            takes_self=True
        )
    )

    source: Sources = attr.ib(
        default=attr.Factory(lambda self: type(self).SOURCE, takes_self=True)
    )

    primary_source: str = attr.ib()

    @primary_source.default
    def __default_primary_source(self) -> str:
        return source.primary(*self.source).key

    compiler_extension = attr.ib(
        default=attr.Factory(extensions.MissingExtension, takes_self=False)
    )

    runtime_extension = attr.ib(default=None)

    def __attrs_post_init__(self) -> None:
        db.persist_project(self)

        # select container image
        if isinstance(type(self).CONTAINER, ContainerImage):
            self.container = tp.cast(
                ContainerImage, copy.deepcopy(type(self).CONTAINER)
            )
        else:
            if not isinstance(primary(*self.SOURCE), Git):
                raise AssertionError(
                    "Container selection by version is only allowed if the"
                    "primary source is a git repository."
                )
            version = self.version_of_primary
            for rev_range, image in type(self).CONTAINER:
                if version in rev_range:
                    self.container = copy.deepcopy(image)
                    break

    @abstractmethod
    def run_tests(self) -> None:
        """
        Run the tests of this project.

        Clients override this method to provide customized run-time tests.

        Args:
            experiment: The experiment we run this project under
            run: A function that takes the run command.
        """

    def clean(self) -> None:
        """Clean the project build directory."""
        builddir_p = local.path(self.builddir)
        builddir_p.delete()

    def clone(self) -> 'Project':
        """Create a deepcopy of ourself."""
        new_p = copy.deepcopy(self)
        new_p.run_uuid = uuid.uuid4()
        return new_p

    @abstractmethod
    def compile(self) -> None:
        """Compile the project."""

    @property
    def id(self) -> str:
        version_str = source.to_str(*tuple(self.variant.values()))
        return f'{self.name}-{self.group}@{version_str}'

    def prepare(self) -> None:
        """Prepare the build diretory."""
        builddir_p = local.path(self.builddir)
        if not builddir_p.exists():
            builddir_p.mkdir()

    def redirect(self) -> None:
        """Redirect execution to a containerized benchbuild instance."""
        LOG.error("Redirection not supported by project.")

    def source_of(self, name: str) -> tp.Optional[str]:
        """
        Retrieve source for given index name.

        First we try to find the given source in the configured variant index.
        If unsuccessful, we try to find them in our configured sources. The
        second variant picks up all sources that did not take part in
        version expansion.

        Args:
            project (Project): The project to access.
            name (str): Local name of the source .

        Returns:
            (Optional[FetchableSource]): A source representing this variant.
        """
        variant = self.variant
        if name in variant:
            return str(self.builddir / variant[name].owner.local)

        all_sources = source.sources_as_dict(*self.source)
        if name in all_sources:
            return str(self.builddir / all_sources[name].local)

        return None

    def version_of(self, name: str) -> tp.Optional[str]:
        """
        Retrieve source for given index name.

        Args:
            project (Project): The project to access.
            name (str): Local name of the source .

        Returns:
            (Optional[FetchableSource]): A source representing this variant.
        """
        variant = self.variant
        if name in variant:
            return str(variant[name])
        return None

    @property
    def version_of_primary(self) -> str:
        """
        Get version of the primary source.
        """
        version_str = self.version_of(self.primary_source)
        if not version_str:
            raise ValueError('You are expected to have a primary_source.')
        return version_str

    @property
    def source_of_primary(self) -> str:
        """
        Get source of the primary source.
        """
        source_str = self.source_of(self.primary_source)
        if not source_str:
            raise ValueError('You are expected to have a primary_source.')
        return source_str


ProjectT = tp.Type[Project]


def __split_project_input__(
    project_input: str
) -> tp.Tuple[str, tp.Optional[str]]:
    split_input = project_input.rsplit('@', maxsplit=1)
    first = split_input[0]
    second = split_input[1] if len(split_input) > 1 else None

    return (first, second)


def discovered() -> tp.Dict[str, ProjectT]:
    """Return all discovered projects."""
    return dict(ProjectRegistry.projects)


def __add_single_filter__(project: ProjectT, version: str) -> ProjectT:

    sources = project.SOURCE
    victim = sources[0]
    victim = source.SingleVersionFilter(victim, version)
    sources[0] = victim

    project.SOURCE = sources
    return project


def __add_indexed_filters__(
    project: ProjectT, versions: tp.List[str]
) -> ProjectT:
    sources = project.SOURCE
    for i in range(min(len(sources), len(versions))):
        sources[i] = source.SingleVersionFilter(sources[i], versions[i])

    project.SOURCE = sources
    return project


def __add_named_filters__(
    project: ProjectT, versions: tp.Dict[str, str]
) -> ProjectT:
    sources = project.SOURCE
    named_sources: tp.Dict[str, source.base.FetchableSource] = {
        s.key: s for s in sources
    }
    for k, v in versions.items():
        if k in named_sources:
            victim: source.base.FetchableSource = named_sources[k]
            victim = source.SingleVersionFilter(victim, v)
            named_sources[k] = victim
    sources = list(named_sources.values())

    project.SOURCE = sources
    return project


def __add_filters__(project: ProjectT, version_str: str) -> ProjectT:
    """
    Add a set of version filters to this project's source.

    The version_str argument will be used to make an educated guess about
    the filters required.

    Example:
        benchbuild/bzip2@3.5 -> A single version filter will be wrapped around
            source.
        benchbuild/bzip2@[3.5,1.0] -> Each element of the input list will
            generate a version filter that wraps the same index in the
            project's source.
    """
    version_in = yaml.safe_load(version_str)
    if not project.SOURCE:
        return project

    def csv(in_str: tp.Union[tp.Any, str]) -> bool:
        if isinstance(in_str, str):
            return len(in_str.split(',')) > 1
        return False

    is_csv = csv(version_in)
    is_scalar = isinstance(version_in, (str, int))

    if not is_csv and is_scalar:
        return __add_single_filter__(project, str(version_in))

    if isinstance(version_in, list) or is_csv:
        version_in = version_in.split(',') if is_csv else version_in
        return __add_indexed_filters__(project, version_in)

    if isinstance(version_in, dict):
        if not all(version_in.values()):
            return __add_indexed_filters__(project, list(version_in.keys()))
        return __add_named_filters__(project, version_in)

    raise ValueError('not sure what this version input')


ProjectIndex = tp.Mapping[str, ProjectT]


def populate(
    projects_to_filter: ProjectNames,
    group: MaybeGroupNames = None
) -> ProjectIndex:
    """
    Populate the list of projects that belong to this experiment.

    Args:
        projects_to_filter (list(Project)):
            List of projects we want to assign to this experiment.
            We intersect the list of projects with the list of supported
            projects to get the list of projects that belong to this
            experiment.
        group (list(str)):
            In addition to the project filter, we provide a way to filter
            whole groups.
    Returns:
        a dictionary of (project name, project class) pairs.
    """
    prjs = discovered()

    def normalize_key(key: str) -> str:
        newkey = key
        for opt in __REGISTRATION_OPTIONALS:
            newkey = newkey.replace(opt, __REGISTRATION_SEPARATOR, 1)
        return newkey

    p2f = projects_to_filter

    if projects_to_filter:
        prjs = {}
        p2f = [normalize_key(k) for k in projects_to_filter]

        for filter_project in set(p2f):
            project_str, version = __split_project_input__(filter_project)
            try:
                selected = ProjectRegistry.projects.items(prefix=project_str)
                for name, prj_cls in selected:
                    if version:
                        prj_cls = __add_filters__(prj_cls, version)
                    prjs.update({name: prj_cls})
            except KeyError:
                pass

    if group:
        groupkeys = set(group)
        prjs = {
            name: cls for name, cls in prjs.items() if cls.GROUP in groupkeys
        }

    populated = {
        x: prjs[x] for x in prjs if prjs[x].DOMAIN != "debug" or x in p2f
    }
    return populated


def build_dir(e, p) -> LocalPath:
    return local.path(str(CFG['build_dir'])) / str(e.name) / str(p.id)
