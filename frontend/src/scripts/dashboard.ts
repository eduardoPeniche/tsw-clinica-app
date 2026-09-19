import { api, ApiError, type Cita, type Medico, type Paciente } from '../lib/api/client';

const pacientesBody = byId<HTMLTableSectionElement>('pacientes-body');
const medicosBody = byId<HTMLTableSectionElement>('medicos-body');
const citasBody = byId<HTMLTableSectionElement>('citas-body');
const pacienteForm = byId<HTMLFormElement>('paciente-form');
const medicoForm = byId<HTMLFormElement>('medico-form');
const citaForm = byId<HTMLFormElement>('cita-form');
const citaPaciente = byId<HTMLSelectElement>('cita-paciente');
const citaMedico = byId<HTMLSelectElement>('cita-medico');
const notice = byId<HTMLParagraphElement>('notice');

let pacientes: Paciente[] = [];
let medicos: Medico[] = [];

function byId<T extends HTMLElement>(id: string): T {
	const element = document.getElementById(id);
	if (!element) throw new Error(`No se encontró #${id}.`);
	return element as T;
}

function value(data: FormData, key: string): string {
	return String(data.get(key) ?? '').trim();
}

function showNotice(message: string, isError = false): void {
	notice.textContent = message;
	notice.hidden = false;
	notice.classList.toggle('error', isError);
}

function showError(error: unknown): void {
	showNotice(
		error instanceof ApiError ? error.message : 'No fue posible completar la operación.',
		true,
	);
}

function clearRows(body: HTMLTableSectionElement): void {
	body.replaceChildren();
}

function emptyRow(body: HTMLTableSectionElement, message: string, columns: number): void {
	const row = body.insertRow();
	const cell = row.insertCell();
	cell.colSpan = columns;
	cell.className = 'empty';
	cell.textContent = message;
}

function cell(row: HTMLTableRowElement, text: string): HTMLTableCellElement {
	const result = row.insertCell();
	result.textContent = text;
	return result;
}

function button(label: string, action: string, id: string, danger = false): HTMLButtonElement {
	const result = document.createElement('button');
	result.type = 'button';
	result.className = `button button-small${danger ? ' button-danger' : ' button-secondary'}`;
	result.dataset.action = action;
	result.dataset.id = id;
	result.textContent = label;
	return result;
}

function renderPacientes(): void {
	clearRows(pacientesBody);
	if (!pacientes.length) return emptyRow(pacientesBody, 'Aún no hay pacientes registrados.', 4);
	for (const paciente of pacientes) {
		const row = pacientesBody.insertRow();
		cell(row, paciente.nombre);
		cell(row, paciente.fecha_nacimiento);
		cell(row, paciente.contacto);
		const actions = cell(row, '');
		actions.className = 'row-actions';
		actions.append(
			button('Editar', 'editar', paciente.id),
			button('Eliminar', 'eliminar', paciente.id, true),
		);
	}
}

function renderMedicos(): void {
	clearRows(medicosBody);
	if (!medicos.length) return emptyRow(medicosBody, 'Aún no hay médicos registrados.', 3);
	for (const medico of medicos) {
		const row = medicosBody.insertRow();
		cell(row, medico.nombre);
		cell(row, medico.especialidad);
		const actions = cell(row, '');
		actions.className = 'row-actions';
		actions.append(
			button('Editar', 'editar', medico.id),
			button('Eliminar', 'eliminar', medico.id, true),
		);
	}
}

function options(
	select: HTMLSelectElement,
	items: Array<{ id: string; label: string }>,
	placeholder: string,
): void {
	const selected = select.value;
	select.replaceChildren(new Option(placeholder, ''));
	for (const item of items) select.add(new Option(item.label, item.id));
	select.value = items.some((item) => item.id === selected) ? selected : (items[0]?.id ?? '');
}

function renderSelects(): void {
	options(
		citaPaciente,
		pacientes.map((item) => ({ id: item.id, label: item.nombre })),
		'Selecciona un paciente',
	);
	const doctorOptions = medicos.map((item) => ({
		id: item.id,
		label: `${item.nombre} · ${item.especialidad}`,
	}));
	options(citaMedico, doctorOptions, 'Selecciona un médico');
}

function renderCitas(citas: Cita[]): void {
	clearRows(citasBody);
	if (!citas.length) return emptyRow(citasBody, 'No hay citas para este médico.', 4);
	for (const cita of citas) {
		const row = citasBody.insertRow();
		const paciente = pacientes.find((item) => item.id === cita.paciente_id);
		cell(row, paciente?.nombre ?? cita.paciente_id);
		cell(
			row,
			new Intl.DateTimeFormat('es-MX', { dateStyle: 'medium', timeStyle: 'short' }).format(
				new Date(cita.fecha_hora),
			),
		);
		const estado = cell(row, '');
		const badge = document.createElement('span');
		badge.className = `estado${cita.estado === 'cancelada' ? ' estado-cancelada' : ''}`;
		badge.textContent = cita.estado;
		estado.append(badge);
		const actions = cell(row, '');
		if (cita.estado !== 'cancelada') {
			actions.className = 'row-actions';
			actions.append(button('Cancelar', 'cancelar', cita.id, true));
		}
	}
}

async function cargarCitas(): Promise<void> {
	if (!citaMedico.value) return renderCitas([]);
	try {
		renderCitas(await api.citas.listarPorMedico(citaMedico.value));
	} catch (error) {
		renderCitas([]);
		showError(error);
	}
}

async function refresh(): Promise<void> {
	try {
		[pacientes, medicos] = await Promise.all([api.pacientes.listar(), api.medicos.listar()]);
		renderPacientes();
		renderMedicos();
		renderSelects();
		await cargarCitas();
	} catch (error) {
		showError(error);
	}
}

pacienteForm.addEventListener('submit', async (event) => {
	event.preventDefault();
	const data = new FormData(pacienteForm);
	const input = {
		nombre: value(data, 'nombre'),
		fecha_nacimiento: value(data, 'fecha_nacimiento'),
		contacto: value(data, 'contacto'),
	};
	try {
		const id = value(data, 'id');
		await (id ? api.pacientes.actualizar(id, input) : api.pacientes.crear(input));
		pacienteForm.reset();
		showNotice(id ? 'Paciente actualizado.' : 'Paciente creado.');
		await refresh();
	} catch (error) {
		showError(error);
	}
});

medicoForm.addEventListener('submit', async (event) => {
	event.preventDefault();
	const data = new FormData(medicoForm);
	const input = { nombre: value(data, 'nombre'), especialidad: value(data, 'especialidad') };
	try {
		const id = value(data, 'id');
		await (id ? api.medicos.actualizar(id, input) : api.medicos.crear(input));
		medicoForm.reset();
		showNotice(id ? 'Médico actualizado.' : 'Médico creado.');
		await refresh();
	} catch (error) {
		showError(error);
	}
});

citaForm.addEventListener('submit', async (event) => {
	event.preventDefault();
	const data = new FormData(citaForm);
	try {
		await api.citas.crear({
			paciente_id: value(data, 'paciente_id'),
			medico_id: value(data, 'medico_id'),
			fecha_hora: value(data, 'fecha_hora'),
		});
		citaForm.reset();
		showNotice('Cita agendada.');
		await refresh();
	} catch (error) {
		showError(error);
	}
});

pacientesBody.addEventListener('click', async (event) => {
	const target = (event.target as Element).closest<HTMLButtonElement>('button[data-action]');
	if (!target) return;
	const paciente = pacientes.find((item) => item.id === target.dataset.id);
	if (!paciente) return;
	if (target.dataset.action === 'editar') {
		pacienteForm.elements.namedItem('id')!.value = paciente.id;
		pacienteForm.elements.namedItem('nombre')!.value = paciente.nombre;
		pacienteForm.elements.namedItem('fecha_nacimiento')!.value = paciente.fecha_nacimiento;
		pacienteForm.elements.namedItem('contacto')!.value = paciente.contacto;
		showNotice('Editando paciente.');
		return;
	}
	if (!confirm(`¿Eliminar a ${paciente.nombre}?`)) return;
	try {
		await api.pacientes.eliminar(paciente.id);
		showNotice('Paciente eliminado.');
		await refresh();
	} catch (error) {
		showError(error);
	}
});

medicosBody.addEventListener('click', async (event) => {
	const target = (event.target as Element).closest<HTMLButtonElement>('button[data-action]');
	if (!target) return;
	const medico = medicos.find((item) => item.id === target.dataset.id);
	if (!medico) return;
	if (target.dataset.action === 'editar') {
		medicoForm.elements.namedItem('id')!.value = medico.id;
		medicoForm.elements.namedItem('nombre')!.value = medico.nombre;
		medicoForm.elements.namedItem('especialidad')!.value = medico.especialidad;
		showNotice('Editando médico.');
		return;
	}
	if (!confirm(`¿Eliminar a ${medico.nombre}?`)) return;
	try {
		await api.medicos.eliminar(medico.id);
		showNotice('Médico eliminado.');
		await refresh();
	} catch (error) {
		showError(error);
	}
});

citasBody.addEventListener('click', async (event) => {
	const target = (event.target as Element).closest<HTMLButtonElement>(
		'button[data-action="cancelar"]',
	);
	if (!target || !confirm('¿Cancelar esta cita?')) return;
	try {
		await api.citas.cancelar(target.dataset.id!);
		showNotice('Cita cancelada.');
		await cargarCitas();
	} catch (error) {
		showError(error);
	}
});

citaMedico.addEventListener('change', cargarCitas);

void refresh();
