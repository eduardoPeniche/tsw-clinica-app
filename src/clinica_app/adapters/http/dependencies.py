from typing import Annotated

from fastapi import Depends

from clinica_app.container import ApplicationContainer, build_container

_container = build_container()


def get_container() -> ApplicationContainer:
    return _container


ContainerDep = Annotated[ApplicationContainer, Depends(get_container)]
