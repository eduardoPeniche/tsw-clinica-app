import type { components } from './generated/schema';

export type Paciente = components['schemas']['PacienteOutput'];
export type PacienteInput = components['schemas']['PacienteInput'];
export type Medico = components['schemas']['MedicoOutput'];
export type MedicoInput = components['schemas']['MedicoInput'];
export type Cita = components['schemas']['CitaOutput'];
export type CitaInput = components['schemas']['CitaInput'];
export type DisponibilidadAgenda = components['schemas']['DisponibilidadAgendaOutput'];

export class ApiError extends Error {
	constructor(
		public readonly status: number,
		message: string,
	) {
		super(message);
		this.name = 'ApiError';
	}
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
	const response = await fetch(`/api${path}`, {
		...init,
		headers: {
			'Content-Type': 'application/json',
			...init.headers,
		},
	});

	if (!response.ok) {
		const payload: unknown = await response.json().catch(() => null);
		const message =
			typeof payload === 'object' &&
			payload !== null &&
			'detail' in payload &&
			typeof payload.detail === 'string'
				? payload.detail
				: `La solicitud falló con estado ${response.status}.`;

		throw new ApiError(response.status, message);
	}

	return response.status === 204 ? (undefined as T) : ((await response.json()) as T);
}

function json(body: unknown): Pick<RequestInit, 'body' | 'method'> {
	return { body: JSON.stringify(body), method: 'POST' };
}

export const api = {
	pacientes: {
		crear: (data: PacienteInput) => request<Paciente>('/pacientes', json(data)),
		listar: () => request<Paciente[]>('/pacientes'),
		obtener: (id: string) => request<Paciente>(`/pacientes/${id}`),
		actualizar: (id: string, data: PacienteInput) =>
			request<Paciente>(`/pacientes/${id}`, { ...json(data), method: 'PUT' }),
		eliminar: (id: string) => request<void>(`/pacientes/${id}`, { method: 'DELETE' }),
	},
	medicos: {
		crear: (data: MedicoInput) => request<Medico>('/medicos', json(data)),
		listar: () => request<Medico[]>('/medicos'),
		obtener: (id: string) => request<Medico>(`/medicos/${id}`),
		actualizar: (id: string, data: MedicoInput) =>
			request<Medico>(`/medicos/${id}`, { ...json(data), method: 'PUT' }),
		eliminar: (id: string) => request<void>(`/medicos/${id}`, { method: 'DELETE' }),
	},
	citas: {
		crear: (data: CitaInput) => request<Cita>('/citas', json(data)),
		cancelar: (id: string) => request<Cita>(`/citas/${id}/cancelacion`, { method: 'PATCH' }),
		consultarDisponibilidad: (medicoId: string, fecha: string) =>
			request<DisponibilidadAgenda>(
				`/medicos/${medicoId}/disponibilidad?fecha=${encodeURIComponent(fecha)}`,
			),
		listarPorMedico: (medicoId: string, fecha?: string) => {
			const query = fecha ? `?fecha=${encodeURIComponent(fecha)}` : '';
			return request<Cita[]>(`/medicos/${medicoId}/citas${query}`);
		},
		listarPorPaciente: (pacienteId: string) => request<Cita[]>(`/pacientes/${pacienteId}/citas`),
	},
};
