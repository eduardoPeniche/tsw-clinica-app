from uuid import UUID

from fastapi import APIRouter, Response, status

from clinica_app.adapters.http.dependencies import ContainerDep
from clinica_app.adapters.http.schemas.medico import MedicoInput, MedicoOutput

router = APIRouter(prefix="/medicos", tags=["Médicos"])


def _output(medico: object) -> MedicoOutput:
    return MedicoOutput.model_validate(medico, from_attributes=True)


@router.post("", response_model=MedicoOutput, status_code=status.HTTP_201_CREATED)
def crear(data: MedicoInput, services: ContainerDep) -> MedicoOutput:
    return _output(services.crear_medico.ejecutar(**data.model_dump()))


@router.get("", response_model=list[MedicoOutput])
def listar(services: ContainerDep) -> list[MedicoOutput]:
    return [_output(item) for item in services.listar_medicos.ejecutar()]


@router.get("/{medico_id}", response_model=MedicoOutput)
def obtener(medico_id: UUID, services: ContainerDep) -> MedicoOutput:
    return _output(services.obtener_medico.ejecutar(medico_id))


@router.put("/{medico_id}", response_model=MedicoOutput)
def actualizar(
    medico_id: UUID, data: MedicoInput, services: ContainerDep
) -> MedicoOutput:
    return _output(services.actualizar_medico.ejecutar(medico_id, **data.model_dump()))


@router.delete("/{medico_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(medico_id: UUID, services: ContainerDep) -> Response:
    services.eliminar_medico.ejecutar(medico_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
