from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status

from clinica_app.adapters.http.dependencies import ContainerDep
from clinica_app.adapters.http.schemas.cita import (
    CitaInput,
    CitaOutput,
    DisponibilidadAgendaOutput,
    SlotDisponibilidadOutput,
)

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
def listar_por_medico(
    medico_id: UUID,
    services: ContainerDep,
    fecha: Annotated[date | None, Query()] = None,
) -> list[CitaOutput]:
    return [
        _output(item)
        for item in services.listar_citas_por_medico.ejecutar(medico_id, fecha)
    ]


@router.get(
    "/medicos/{medico_id}/disponibilidad",
    response_model=DisponibilidadAgendaOutput,
)
def consultar_disponibilidad(
    medico_id: UUID,
    fecha: Annotated[date, Query()],
    services: ContainerDep,
) -> DisponibilidadAgendaOutput:
    disponibilidad = services.consultar_disponibilidad_medico.ejecutar(medico_id, fecha)
    return DisponibilidadAgendaOutput(
        fecha=disponibilidad.fecha,
        zona_horaria=disponibilidad.zona_horaria,
        slots=[
            SlotDisponibilidadOutput(
                inicio=slot.inicio.strftime("%H:%M"),
                fin=slot.fin.strftime("%H:%M"),
                estado=slot.estado.value,
            )
            for slot in disponibilidad.slots
        ],
        slot_recomendado=(
            disponibilidad.slot_recomendado.strftime("%H:%M")
            if disponibilidad.slot_recomendado
            else None
        ),
    )


@router.get("/pacientes/{paciente_id}/citas", response_model=list[CitaOutput])
def listar_por_paciente(paciente_id: UUID, services: ContainerDep) -> list[CitaOutput]:
    return [_output(item) for item in services.listar_citas_por_paciente.ejecutar(paciente_id)]
