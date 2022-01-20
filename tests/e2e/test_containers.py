import typing as tp
from functools import partial

import pytest
from plumbum import ProcessExecutionError

from benchbuild.environments.adapters.podman import (
    remove_container,
    ContainerCreateError,
)
from benchbuild.environments.domain import declarative as decl
from benchbuild.environments.domain import commands, events
from benchbuild.environments.service_layer import messagebus, handlers
from benchbuild.environments.service_layer import unit_of_work as uow
from benchbuild.settings import CFG
from benchbuild.utils import settings
from benchbuild.utils.cmd import cp, which


@pytest.fixture
def config():
    settings.setup_config(CFG)
    yield CFG
    settings.setup_config(CFG)


@pytest.fixture
def image_uow() -> uow.ImageUnitOfWork:
    return uow.BuildahImageUOW()


@pytest.fixture
def container_uow() -> uow.ContainerUnitOfWork:
    return uow.PodmanContainerUOW()


@pytest.fixture
def publish(image_uow,
            container_uow) -> tp.Callable[[messagebus.Message], None]:
    evt_handlers = {
        events.LayerCreated: [],
        events.ImageCreated: [],
        events.ContainerCreated: [],
        events.ContainerStartFailed: [],
        events.ContainerStarted: [],
        events.LayerCreationFailed: [],
        events.DebugImageKept: [],
        events.ImageCreationFailed: []
    }

    cmd_handlers = {
        commands.CreateImage:
            handlers.bootstrap(handlers.create_image, image_uow),
        commands.CreateBenchbuildBase:
            handlers.bootstrap(handlers.create_benchbuild_base, image_uow),
        commands.RunProjectContainer:
            handlers.bootstrap(handlers.run_project_container, container_uow),
        commands.ExportImage:
            handlers.bootstrap(handlers.export_image_handler, image_uow),
        commands.ImportImage:
            handlers.bootstrap(handlers.import_image_handler, image_uow),
        commands.DeleteImage:
            handlers.bootstrap(handlers.delete_image_handler, image_uow),
    }

    yield partial(messagebus.handle, cmd_handlers, evt_handlers)

    images = list(image_uow.registry.images.values())
    for image in images:
        image_uow.registry.remove(image)

    containers = list(container_uow.registry.containers.values())
    for container in containers:
        remove_container(container.container_id)


@pytest.fixture
def true_image() -> decl.ContainerImage:

    def prepare_container() -> None:
        true_path = which('true').strip()
        cp(true_path, 'true')

    return decl.ContainerImage() \
        .from_('scratch') \
        .context(prepare_container) \
        .workingdir('/') \
        .entrypoint('/true')


@pytest.fixture
def no_entrypoint() -> decl.ContainerImage:

    def prepare_container() -> None:
        true_path = which('true').strip()
        cp(true_path, 'true')

    return decl.ContainerImage() \
        .from_('scratch') \
        .context(prepare_container) \
        .workingdir('/') \
        .command('/true')


def test_image_creation(true_image, publish, image_uow) -> None:
    name = 'benchbuild-e2e-test_image_creation'

    maybe_image = image_uow.registry.find(name)
    assert maybe_image is None

    cmd = commands.CreateImage(name, true_image)
    publish(cmd)
    maybe_image = image_uow.registry.find(name)

    assert maybe_image is not None


def test_image_run_no_args(true_image, publish) -> None:
    name = 'benchbuild-e2e-test_image_run'

    cmd = commands.CreateImage(name, true_image)
    publish(cmd)

    run_cmd_no_args = commands.RunProjectContainer(name, name, '/')
    try:
        publish(run_cmd_no_args)
    except ContainerCreateError:
        assert False, "RunProjectContainer was unable to create a container."
    except ProcessExecutionError:
        assert False, "RunProjectContainer raised an unexpected exception"


def test_image_run_args(true_image, publish) -> None:
    name = 'benchbuild-e2e-test_image_run'

    cmd = commands.CreateImage(name, true_image)
    publish(cmd)

    run_cmd_args = commands.RunProjectContainer(
        name, name, '/', ('arg1', 'arg2')
    )
    try:
        publish(run_cmd_args)
    except ContainerCreateError:
        assert False, "RunProjectContainer was unable to create a container."
    except ProcessExecutionError:
        assert False, "RunProjectContainer raised an unexpected exception"


def test_interactive_without_entrypoint(no_entrypoint, publish, config) -> None:
    name = 'benchbuild-e2e-test_interactive_without_entrypoint'

    cmd = commands.CreateImage(name, no_entrypoint)
    publish(cmd)

    run_cmd_args = commands.RunProjectContainer(
        name, name, '/', ('arg1', 'arg2')
    )
    config["container"]["interactive"] = True
    try:
        publish(run_cmd_args)
    except ContainerCreateError:
        assert False, "RunProjectContainer was unable to create a container."
    except ProcessExecutionError:
        assert False, "RunProjectContainer raised an unexpected exception"
