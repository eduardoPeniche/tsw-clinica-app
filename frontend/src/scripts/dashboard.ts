import {
	api,
	ApiError,
	type Cita,
	type DisponibilidadAgenda,
	type Medico,
	type Paciente,
} from '../lib/api/client';

const pacientesBody = byId<HTMLTableSectionElement>('pacientes-body');
const medicosBody = byId<HTMLTableSectionElement>('medicos-body');
const citasBody = byId<HTMLTableSectionElement>('citas-body');
const pacienteForm = byId<HTMLFormElement>('paciente-form');
const medicoForm = byId<HTMLFormElement>('medico-form');
const citaForm = byId<HTMLFormElement>('cita-form');
const citaPaciente = byId<HTMLSelectElement>('cita-paciente');
const citaMedico = byId<HTMLSelectElement>('cita-medico');
const citaFecha = byId<HTMLInputElement>('cita-fecha');
const citaFechas = byId<HTMLDivElement>('cita-fechas');
const citaFechaAnterior = byId<HTMLButtonElement>('cita-fecha-anterior');
const citaFechaSiguiente = byId<HTMLButtonElement>('cita-fecha-siguiente');
const citaHora = byId<HTMLInputElement>('cita-hora');
const citaSlots = byId<HTMLDivElement>('cita-slots');
const notice = byId<HTMLParagraphElement>('notice');

let pacientes: Paciente[] = [];
let medicos: Medico[] = [];
const CLINIC_TIME_ZONE = 'America/Merida';
const VISIBLE_BUSINESS_DAYS = 5;
let dateOffset = 0;

type DateTimeParts = {
	day: string;
	hour: string;
	minute: string;
	month: string;
	second: string;
	year: string;
};

function byId<T extends HTMLElement>(id: string): T {
	const element = document.getElementById(id);
	if (!element) throw new Error(`No se encontró #${id}.`);
	return element as T;
}

function value(data: FormData, key: string): string {
	return String(data.get(key) ?? '').trim();
}

function clinicDateTimeParts(value: Date | string): DateTimeParts {
	const parts = new Intl.DateTimeFormat('en-US', {
		day: '2-digit',
		hour: '2-digit',
		hourCycle: 'h23',
		hour12: false,
		minute: '2-digit',
		month: '2-digit',
		second: '2-digit',
		timeZone: CLINIC_TIME_ZONE,
		year: 'numeric',
	}).formatToParts(new Date(value));

	return Object.fromEntries(
		parts.filter((part) => part.type !== 'literal').map((part) => [part.type, part.value]),
	) as DateTimeParts;
}

function clinicDate(value: Date | string): string {
	const parts = clinicDateTimeParts(value);
	return `${parts.year}-${parts.month}-${parts.day}`;
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
	renderFechasDeAtencion();
}

function renderFechasDeAtencion(): Array<{ label: string; value: string }> {
	const today = clinicDateTimeParts(new Date());
	const cursor = new Date(Date.UTC(Number(today.year), Number(today.month) - 1, Number(today.day)));
	const dayFormatter = new Intl.DateTimeFormat('es-MX', { day: 'numeric', timeZone: 'UTC' });
	const monthFormatter = new Intl.DateTimeFormat('es-MX', { month: 'short', timeZone: 'UTC' });
	const weekdayFormatter = new Intl.DateTimeFormat('es-MX', {
		timeZone: 'UTC',
		weekday: 'short',
	});
	const fechas: Array<{ label: string; value: string }> = [];
	let diasLaborablesRecorridos = 0;

	while (fechas.length < VISIBLE_BUSINESS_DAYS) {
		const dayOfWeek = cursor.getUTCDay();
		if (dayOfWeek !== 0 && dayOfWeek !== 6) {
			if (diasLaborablesRecorridos >= dateOffset) {
				fechas.push({
					label: `${weekdayFormatter.format(cursor).replace('.', '')} ${dayFormatter.format(cursor)} ${monthFormatter.format(cursor).replace('.', '')}`,
					value: cursor.toISOString().slice(0, 10),
				});
			}
			diasLaborablesRecorridos += 1;
		}
		cursor.setUTCDate(cursor.getUTCDate() + 1);
	}

	if (!fechas.some((fecha) => fecha.value === citaFecha.value)) {
		citaFecha.value = fechas[0].value;
	}
	citaFechas.replaceChildren();
	for (const fecha of fechas) {
		const button = document.createElement('button');
		button.type = 'button';
		button.className = 'date-pill';
		button.dataset.date = fecha.value;
		button.textContent = fecha.label;
		button.classList.toggle('date-pill-selected', fecha.value === citaFecha.value);
		button.setAttribute('aria-pressed', String(fecha.value === citaFecha.value));
		button.addEventListener('click', () => seleccionarFecha(fecha.value));
		citaFechas.append(button);
	}
	citaFechaAnterior.disabled = dateOffset === 0;
	return fechas;
}

function seleccionarFecha(fecha: string): void {
	citaFecha.value = fecha;
	renderFechasDeAtencion();
	void cargarCitas();
}

function cambiarPaginaDeFechas(direction: -1 | 1): void {
	dateOffset = Math.max(0, dateOffset + direction * VISIBLE_BUSINESS_DAYS);
	const fechas = renderFechasDeAtencion();
	seleccionarFecha(fechas[0].value);
}

function renderSlotsDisponibles(disponibilidad: DisponibilidadAgenda): void {
	citaSlots.replaceChildren();
	for (const slot of disponibilidad.slots) {
		const noDisponible = slot.estado !== 'libre';
		const button = document.createElement('button');
		button.type = 'button';
		button.className = 'slot';
		button.dataset.slot = slot.inicio;
		button.disabled = noDisponible;
		button.textContent = `${slot.inicio} – ${slot.fin}`;
		button.addEventListener('click', () => seleccionarSlot(slot.inicio));
		citaSlots.append(button);
	}
	seleccionarSlot(disponibilidad.slot_recomendado ?? '');
}

function limpiarSlots(): void {
	citaHora.value = '';
	citaSlots.replaceChildren();
}

function seleccionarSlot(inicio: string): void {
	citaHora.value = inicio;
	for (const button of citaSlots.querySelectorAll<HTMLButtonElement>('button[data-slot]')) {
		const seleccionado = button.dataset.slot === inicio;
		button.classList.toggle('slot-selected', seleccionado);
		button.setAttribute('aria-pressed', String(seleccionado));
	}
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
			new Intl.DateTimeFormat('es-MX', {
				dateStyle: 'medium',
				timeStyle: 'short',
				timeZone: CLINIC_TIME_ZONE,
			}).format(new Date(cita.fecha_hora)),
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
	if (!citaMedico.value || !citaFecha.value) {
		renderCitas([]);
		limpiarSlots();
		return;
	}
	try {
		const [citas, disponibilidad] = await Promise.all([
			api.citas.listarPorMedico(citaMedico.value, citaFecha.value),
			api.citas.consultarDisponibilidad(citaMedico.value, citaFecha.value),
		]);
		renderCitas(citas);
		renderSlotsDisponibles(disponibilidad);
	} catch (error) {
		renderCitas([]);
		limpiarSlots();
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
	const fecha = value(data, 'fecha');
	const medicoId = value(data, 'medico_id');
	const hora = value(data, 'hora');
	if (!hora) {
		showNotice('Selecciona un horario disponible.', true);
		return;
	}
	try {
		await api.citas.crear({
			paciente_id: value(data, 'paciente_id'),
			medico_id: medicoId,
			fecha_hora: `${fecha}T${hora}:00`,
		});
		citaForm.reset();
		citaFecha.value = fecha;
		citaMedico.value = medicoId;
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
citaFechaAnterior.addEventListener('click', () => cambiarPaginaDeFechas(-1));
citaFechaSiguiente.addEventListener('click', () => cambiarPaginaDeFechas(1));

void refresh();
