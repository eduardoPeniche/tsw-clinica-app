class RecursoNoEncontradoError(LookupError):
    """Indica que una operación requiere un recurso que no existe."""


class HorarioNoDisponibleError(ValueError):
    """Indica que el médico ya tiene una cita activa en el horario solicitado."""
