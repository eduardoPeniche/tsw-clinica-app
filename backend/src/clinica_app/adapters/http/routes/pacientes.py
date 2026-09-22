from uuid import UUID

from fastapi import APIRouter, Response, status

from clinica_app.adapters.http.dependencies import ContainerDep
from clinica_app.adapters.http.schemas.paciente import PacienteInput, PacienteOutput

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])


def _output(paciente: object) -> PacienteOutput:
    return PacienteOutput.model_validate(paciente, from_attributes=True)


@router.post("", response_model=PacienteOutput, status_code=status.HTTP_201_CREATED)
def crear(data: PacienteInput, services: ContainerDep) -> PacienteOutput:
    return _output(services.crear_paciente.ejecutar(**data.model_dump()))


@router.get("", response_model=list[PacienteOutput])
def listar(services: ContainerDep) -> list[PacienteOutput]:
    return [_output(item) for item in services.listar_pacientes.ejecutar()]


@router.get("/{paciente_id}", response_model=PacienteOutput)
def obtener(paciente_id: UUID, services: ContainerDep) -> PacienteOutput:
    return _output(services.obtener_paciente.ejecutar(paciente_id))


@router.put("/{paciente_id}", response_model=PacienteOutput)
def actualizar(
    paciente_id: UUID, data: PacienteInput, services: ContainerDep
) -> PacienteOutput:
    return _output(
        services.actualizar_paciente.ejecutar(paciente_id, **data.model_dump())
    )


@router.delete("/{paciente_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(paciente_id: UUID, services: ContainerDep) -> Response:
    services.eliminar_paciente.ejecutar(paciente_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
