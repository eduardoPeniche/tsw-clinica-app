from uuid import UUID

from fastapi import APIRouter, status

from clinica_app.adapters.http.dependencies import ContainerDep
from clinica_app.adapters.http.schemas.cita import CitaInput, CitaOutput

router = APIRouter(tags=["Citas"])


def _output(cita: object) -> CitaOutput:
    return CitaOutput.model_validate(cita, from_attributes=True)


@router.post("/citas", response_model=CitaOutput, status_code=status.HTTP_201_CREATED)
def crear(data: CitaInput, services: ContainerDep) -> CitaOutput:
    return _output(services.crear_cita.ejecutar(**data.model_dump()))


@router.patch("/citas/{cita_id}/cancelacion", response_model=CitaOutput)
def cancelar(cita_id: UUID, services: ContainerDep) -> CitaOutput:
    return _output(services.cancelar_cita.ejecutar(cita_id))


@router.get("/medicos/{medico_id}/citas", response_model=list[CitaOutput])
def listar_por_medico(medico_id: UUID, services: ContainerDep) -> list[CitaOutput]:
    return [_output(item) for item in services.listar_citas_por_medico.ejecutar(medico_id)]


@router.get("/pacientes/{paciente_id}/citas", response_model=list[CitaOutput])
def listar_por_paciente(paciente_id: UUID, services: ContainerDep) -> list[CitaOutput]:
    return [_output(item) for item in services.listar_citas_por_paciente.ejecutar(paciente_id)]
