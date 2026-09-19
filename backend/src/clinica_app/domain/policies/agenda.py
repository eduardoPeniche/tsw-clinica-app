from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from enum import Enum
from typing import Iterable
from zoneinfo import ZoneInfo

from clinica_app.domain.exceptions import ValidacionDominioError
from clinica_app.domain.entities import Cita, EstadoCita


class EstadoSlot(str, Enum):
    LIBRE = "libre"
    NO_DISPONIBLE = "no_disponible"
    OCUPADO = "ocupado"


@dataclass(frozen=True)
class SlotDisponibilidad:
    inicio: time
    fin: time
    estado: EstadoSlot


@dataclass(frozen=True)
class DisponibilidadAgenda:
    fecha: date
    zona_horaria: str
    slots: list[SlotDisponibilidad]
    slot_recomendado: time | None


@dataclass(frozen=True)
class PoliticaAgenda:
    dias_atencion: frozenset[int]
    hora_apertura: time
    hora_cierre: time
    duracion_cita: timedelta
    zona_horaria: ZoneInfo

    def normalizar_y_validar(self, fecha_hora: datetime) -> datetime:
        fecha_local = self._en_zona_de_clinica(fecha_hora)

        if fecha_local.weekday() not in self.dias_atencion:
            raise ValidacionDominioError("La clínica atiende únicamente de lunes a viernes.")
        if fecha_local.second or fecha_local.microsecond:
            raise ValidacionDominioError("Las citas deben iniciar en un slot exacto de 30 minutos.")

        apertura = datetime.combine(fecha_local.date(), self.hora_apertura, self.zona_horaria)
        cierre = datetime.combine(fecha_local.date(), self.hora_cierre, self.zona_horaria)
        if fecha_local < apertura or fecha_local + self.duracion_cita > cierre:
            raise ValidacionDominioError("La cita debe estar dentro del horario de atención: 09:00 a 17:00.")

        minutos_desde_apertura = int((fecha_local - apertura).total_seconds() // 60)
        duracion_en_minutos = int(self.duracion_cita.total_seconds() // 60)
        if minutos_desde_apertura % duracion_en_minutos:
            raise ValidacionDominioError("Las citas sólo pueden iniciar cada 30 minutos.")

        return fecha_local

    def fin_de_cita(self, fecha_hora: datetime) -> datetime:
        return fecha_hora + self.duracion_cita

    def disponibilidad_en_fecha(
        self,
        fecha: date,
        citas: Iterable[Cita],
        ahora: datetime | None = None,
    ) -> DisponibilidadAgenda:
        if fecha.weekday() not in self.dias_atencion:
            return DisponibilidadAgenda(fecha, str(self.zona_horaria), [], None)

        ahora = self._en_zona_de_clinica(ahora or datetime.now(self.zona_horaria))
        apertura = datetime.combine(fecha, self.hora_apertura, self.zona_horaria)
        cierre = datetime.combine(fecha, self.hora_cierre, self.zona_horaria)
        citas_activas = [cita for cita in citas if cita.estado is not EstadoCita.CANCELADA]
        slots: list[SlotDisponibilidad] = []
        inicio = apertura

        while inicio + self.duracion_cita <= cierre:
            fin = inicio + self.duracion_cita
            estado = self._estado_del_slot(inicio, fin, citas_activas, ahora)
            slots.append(SlotDisponibilidad(inicio.time(), fin.time(), estado))
            inicio = fin

        recomendacion = self._slot_recomendado(fecha, slots, ahora)
        return DisponibilidadAgenda(fecha, str(self.zona_horaria), slots, recomendacion)

    def _estado_del_slot(
        self,
        inicio: datetime,
        fin: datetime,
        citas_activas: Iterable[Cita],
        ahora: datetime,
    ) -> EstadoSlot:
        if inicio < ahora:
            return EstadoSlot.NO_DISPONIBLE
        if any(self._se_traslapan(inicio, fin, cita.fecha_hora) for cita in citas_activas):
            return EstadoSlot.OCUPADO
        return EstadoSlot.LIBRE

    def _slot_recomendado(
        self,
        fecha: date,
        slots: Iterable[SlotDisponibilidad],
        ahora: datetime,
    ) -> time | None:
        for slot in slots:
            if slot.estado is not EstadoSlot.LIBRE:
                continue
            inicio = datetime.combine(fecha, slot.inicio, self.zona_horaria)
            if fecha > ahora.date() or (fecha == ahora.date() and inicio >= ahora):
                return slot.inicio
        return None

    def _se_traslapan(self, inicio: datetime, fin: datetime, inicio_existente: datetime) -> bool:
        inicio_existente = self._en_zona_de_clinica(inicio_existente)
        fin_existente = self.fin_de_cita(inicio_existente)
        return inicio_existente < fin and inicio < fin_existente

    def _en_zona_de_clinica(self, fecha_hora: datetime) -> datetime:
        if fecha_hora.tzinfo is None:
            return fecha_hora.replace(tzinfo=self.zona_horaria)
        return fecha_hora.astimezone(self.zona_horaria)
