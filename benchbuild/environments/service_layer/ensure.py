from . import unit_of_work


class ImageNotFound(Exception):
    pass


def image_exists(image_name: str, uow: unit_of_work.ImageUnitOfWork) -> None:
    image = uow.registry.find(image_name)
    if not image:
        raise ImageNotFound(image_name)


def container_image_exists(
    image_name: str, uow: unit_of_work.ContainerUnitOfWork
) -> None:
    image = uow.registry.find_image(image_name)
    if not image:
        raise ImageNotFound(image_name)
