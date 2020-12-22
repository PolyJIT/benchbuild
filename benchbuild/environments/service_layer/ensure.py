from . import unit_of_work


class ImageNotFound(Exception):
    pass


def image_exists(
    image_name: str, uow: unit_of_work.AbstractUnitOfWork
) -> None:
    image = uow.registry.get_image(image_name)
    if not image:
        raise ImageNotFound(image_name)
