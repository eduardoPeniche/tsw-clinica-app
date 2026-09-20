import {
	api,
	ApiError,
	type Cita,
	type DisponibilidadAgenda,
	type Medico,
	type Paciente,
} from '../lib/api/client';

const CLINIC_TIME_ZONE = 'America/Merida';
const pacientesBody = byId<HTMLTableSectionElement>('pacientes-body');
const medicosBody = byId<HTMLTableSectionElement>('medicos-body');
const citasBody = byId<HTMLTableSectionElement>('citas-body');
const pacienteForm = byId<HTMLFormElement>('paciente-form');
const medicoForm = byId<HTMLFormElement>('medico-form');
const citaForm = byId<HTMLFormElement>('cita-form');
const pacienteDialog = byId<HTMLDialogElement>('paciente-dialog');
const medicoDialog = byId<HTMLDialogElement>('medico-dialog');
const citaDialog = byId<HTMLDialogElement>('cita-dialog');
const citaPaciente = byId<HTMLSelectElement>('cita-paciente');
const citaMedico = byId<HTMLInputElement>('cita-medico');
const citaFecha = byId<HTMLInputElement>('cita-fecha');
const citaHora = byId<HTMLInputElement>('cita-hora');
const citaResumen = byId<HTMLParagraphElement>('cita-resumen');
const calendarioMedico = byId<HTMLSelectElement>('calendario-medico');
const calendarRegion = byId<HTMLDivElement>('calendar-region');
const calendarPeriod = byId<HTMLElement>('calendar-period');
const regresarSemana = byId<HTMLButtonElement>('regresar-semana');
const agendaList = byId<HTMLElement>('agenda-list');
const notice = byId<HTMLDivElement>('notice');
const noticeMessage = byId<HTMLSpanElement>('notice-message');
const noticeClose = byId<HTMLButtonElement>('notice-close');

let pacientes: Paciente[] = [];
let medicos: Medico[] = [];
let citasDelDia: Cita[] = [];
let agendaPorFecha = new Map<string, DisponibilidadAgenda>();
let citasPorSlot = new Map<string, Cita>();
let fechaSeleccionada = siguienteDiaLaborable(clinicDate(new Date()));
let vistaCalendario: 'dia' | 'semana' | 'mes' = 'semana';
let noticeTimeout: number | undefined;

function byId<T extends HTMLElement>(id: string): T {
	const element = document.getElementById(id);
	if (!element) throw new Error(`No se encontró #${id}.`);
	return element as T;
}

function value(data: FormData, key: string): string {
	return String(data.get(key) ?? '').trim();
}

function clinicDate(value: Date): string {
	const parts = new Intl.DateTimeFormat('en-CA', {
		timeZone: CLINIC_TIME_ZONE,
		year: 'numeric',
		month: '2-digit',
		day: '2-digit',
	}).formatToParts(value);
	const result = Object.fromEntries(
		parts.filter((part) => part.type !== 'literal').map((part) => [part.type, part.value]),
	);
	return `${result.year}-${result.month}-${result.day}`;
}

function clinicTime(value: Date | string): string {
	const parts = new Intl.DateTimeFormat('en-GB', {
		timeZone: CLINIC_TIME_ZONE,
		hour: '2-digit',
		minute: '2-digit',
		hourCycle: 'h23',
	}).formatToParts(new Date(value));
	const result = Object.fromEntries(
		parts.filter((part) => part.type !== 'literal').map((part) => [part.type, part.value]),
	);
	return `${result.hour}:${result.minute}`;
}

function dateFromIso(iso: string): Date {
	return new Date(`${iso}T12:00:00Z`);
}

function isoDate(date: Date): string {
	return date.toISOString().slice(0, 10);
}

function addDays(iso: string, days: number): string {
	const date = dateFromIso(iso);
	date.setUTCDate(date.getUTCDate() + days);
	return isoDate(date);
}

function siguienteDiaLaborable(iso: string): string {
	const date = dateFromIso(iso);
	if (date.getUTCDay() === 6) return addDays(iso, 2);
	if (date.getUTCDay() === 0) return addDays(iso, 1);
	return iso;
}

function startOfWeek(iso: string): string {
	const date = dateFromIso(iso);
	date.setUTCDate(date.getUTCDate() - ((date.getUTCDay() + 6) % 7));
	return isoDate(date);
}

function visibleDates(): string[] {
	if (vistaCalendario === 'dia') return [fechaSeleccionada];
	if (vistaCalendario === 'semana') {
		const inicio = startOfWeek(fechaSeleccionada);
		return Array.from({ length: 5 }, (_, index) => addDays(inicio, index));
	}
	const date = dateFromIso(fechaSeleccionada);
	const inicio = new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), 1));
	const total = new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth() + 1, 0)).getUTCDate();
	return Array.from({ length: total }, (_, index) =>
		isoDate(new Date(Date.UTC(inicio.getUTCFullYear(), inicio.getUTCMonth(), index + 1))),
	);
}

function showNotice(message: string, isError = false): void {
	if (noticeTimeout) window.clearTimeout(noticeTimeout);
	noticeMessage.textContent = message;
	notice.hidden = false;
	notice.classList.toggle('error', isError);
	notice.setAttribute('role', isError ? 'alert' : 'status');
	noticeTimeout = window.setTimeout(
		() => {
			notice.hidden = true;
		},
		isError ? 8000 : 3500,
	);
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
	const target = row.insertCell();
	target.colSpan = columns;
	target.className = 'empty';
	target.textContent = message;
}

function cell(row: HTMLTableRowElement, text: string): HTMLTableCellElement {
	const target = row.insertCell();
	target.textContent = text;
	return target;
}

function actionButton(
	label: string,
	action: string,
	id: string,
	danger = false,
): HTMLButtonElement {
	const target = document.createElement('button');
	target.type = 'button';
	target.className = `button button-small${danger ? ' button-danger' : ' button-secondary'}`;
	target.dataset.action = action;
	target.dataset.id = id;
	target.textContent = label;
	return target;
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
			actionButton('Editar', 'editar', paciente.id),
			actionButton('Eliminar', 'eliminar', paciente.id, true),
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
			actionButton('Editar', 'editar', medico.id),
			actionButton('Eliminar', 'eliminar', medico.id, true),
		);
	}
}

function renderCitasDelDia(): void {
	clearRows(citasBody);
	if (!citasDelDia.length) return emptyRow(citasBody, 'No hay citas para este día.', 4);
	for (const cita of citasDelDia) {
		const row = citasBody.insertRow();
		cell(
			row,
			pacientes.find((paciente) => paciente.id === cita.paciente_id)?.nombre ?? cita.paciente_id,
		);
		cell(
			row,
			new Intl.DateTimeFormat('es-MX', { timeStyle: 'short', timeZone: CLINIC_TIME_ZONE }).format(
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
			actions.append(actionButton('Cancelar', 'cancelar', cita.id, true));
		}
	}
}

function setOptions(
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
	setOptions(
		citaPaciente,
		pacientes.map((paciente) => ({ id: paciente.id, label: paciente.nombre })),
		'Selecciona un paciente',
	);
	setOptions(
		calendarioMedico,
		medicos.map((medico) => ({
			id: medico.id,
			label: `${medico.nombre} · ${medico.especialidad}`,
		})),
		'Selecciona un médico',
	);
}

function formatDay(iso: string, options: Intl.DateTimeFormatOptions): string {
	return new Intl.DateTimeFormat('es-MX', { timeZone: 'UTC', ...options }).format(dateFromIso(iso));
}

function updateCalendarTitle(dates: string[]): void {
	if (vistaCalendario === 'dia')
		calendarPeriod.textContent = formatDay(dates[0], {
			weekday: 'long',
			day: 'numeric',
			month: 'long',
			year: 'numeric',
		});
	else if (vistaCalendario === 'semana')
		calendarPeriod.textContent = `${formatDay(dates[0], { day: 'numeric', month: 'short' })} - ${formatDay(dates.at(-1)!, { day: 'numeric', month: 'short', year: 'numeric' })}`;
	else
		calendarPeriod.textContent = formatDay(fechaSeleccionada, { month: 'long', year: 'numeric' });
	const semanaActual = startOfWeek(siguienteDiaLaborable(clinicDate(new Date())));
	regresarSemana.hidden =
		vistaCalendario !== 'semana' || startOfWeek(fechaSeleccionada) === semanaActual;
}

function slotKey(date: string, inicio: string): string {
	return `${date}T${inicio}`;
}

function createSlot(date: string, slot: DisponibilidadAgenda['slots'][number]): HTMLButtonElement {
	const target = document.createElement('button');
	target.type = 'button';
	target.className = `calendar-slot ${slot.estado}`;
	target.dataset.time = `${slot.inicio} - ${slot.fin}`;
	target.dataset.start = slot.inicio;
	target.setAttribute('aria-label', `${slot.estado}, ${date}, de ${slot.inicio} a ${slot.fin}`);
	const cita = citasPorSlot.get(slotKey(date, slot.inicio));
	if (cita && slot.estado === 'ocupado') {
		const paciente = pacientes.find((item) => item.id === cita.paciente_id);
		target.textContent = paciente?.nombre ?? 'Paciente';
		target.title = paciente?.nombre ?? 'Paciente';
	}
	if (slot.estado === 'libre') {
		target.dataset.action = 'select-slot';
		target.dataset.date = date;
	} else {
		target.disabled = true;
	}
	return target;
}

function renderWeek(dates: string[]): void {
	const grid = document.createElement('div');
	grid.className = 'week-grid';
	const corner = document.createElement('div');
	corner.className = 'week-corner';
	grid.append(corner);
	for (const date of dates) {
		const header = document.createElement('div');
		header.className = `calendar-day-header${date === fechaSeleccionada ? ' is-selected' : ''}`;
		header.textContent = formatDay(date, { day: 'numeric' });
		const day = document.createElement('time');
		const weekday = formatDay(date, { weekday: 'long' });
		day.textContent = `${weekday[0].toUpperCase()}${weekday.slice(1)}`;
		header.append(day);
		grid.append(header);
	}
	const slots = dates.flatMap((date) => agendaPorFecha.get(date)?.slots ?? []);
	const times = [...new Set(slots.map((slot) => slot.inicio))];
	for (const time of times) {
		const label = document.createElement('div');
		label.className = 'time-label';
		label.textContent = time;
		grid.append(label);
		for (const date of dates) {
			const slot = agendaPorFecha.get(date)?.slots.find((item) => item.inicio === time);
			grid.append(
				slot
					? createSlot(date, slot)
					: Object.assign(document.createElement('div'), {
							className: 'calendar-slot no_disponible',
						}),
			);
		}
	}
	calendarRegion.replaceChildren(grid);
}

function renderDay(date: string): void {
	const grid = document.createElement('div');
	grid.className = 'day-grid';
	grid.append(document.createElement('div'));
	const header = document.createElement('div');
	header.className = 'calendar-day-header is-selected';
	header.textContent = formatDay(date, { weekday: 'long' });
	const day = document.createElement('time');
	day.textContent = formatDay(date, { day: 'numeric', month: 'long' });
	header.append(day);
	grid.append(header);
	for (const slot of agendaPorFecha.get(date)?.slots ?? []) {
		const label = document.createElement('div');
		label.className = 'time-label';
		label.textContent = slot.inicio;
		grid.append(label, createSlot(date, slot));
	}
	calendarRegion.replaceChildren(grid);
}

function renderMonth(dates: string[]): void {
	const grid = document.createElement('div');
	grid.className = 'month-grid';
	for (const day of ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']) {
		const header = document.createElement('div');
		header.className = 'month-weekday';
		header.textContent = day;
		grid.append(header);
	}
	const first = dateFromIso(dates[0]);
	for (let padding = 0; padding < (first.getUTCDay() + 6) % 7; padding += 1)
		grid.append(document.createElement('div'));
	for (const date of dates) {
		const agenda = agendaPorFecha.get(date);
		const target = document.createElement('button');
		target.type = 'button';
		target.dataset.action = 'open-day';
		target.dataset.date = date;
		target.className = `month-day${date === fechaSeleccionada ? ' is-selected' : ''}${dateFromIso(date).getUTCDay() % 6 === 0 ? ' is-weekend' : ''}`;
		target.textContent = String(dateFromIso(date).getUTCDate());
		if (agenda?.slots.length) {
			const libre = agenda.slots.filter((slot) => slot.estado === 'libre').length;
			const ocupado = agenda.slots.filter((slot) => slot.estado === 'ocupado').length;
			const count = document.createElement('span');
			count.className = 'month-count';
			count.innerHTML = `<strong>${libre}</strong> libres · ${ocupado} ocupadas`;
			target.append(count);
		}
		grid.append(target);
	}
	calendarRegion.replaceChildren(grid);
}

function renderCalendar(): void {
	const dates = visibleDates();
	updateCalendarTitle(dates);
	agendaList.hidden = vistaCalendario === 'semana';
	if (!calendarioMedico.value) {
		calendarRegion.textContent = 'Registra y selecciona un médico para consultar su agenda.';
		return;
	}
	if (vistaCalendario === 'dia') renderDay(dates[0]);
	else if (vistaCalendario === 'semana') renderWeek(dates);
	else renderMonth(dates);
}

async function cargarAgenda(): Promise<void> {
	const dates = visibleDates();
	if (!calendarioMedico.value) {
		agendaPorFecha = new Map();
		citasPorSlot = new Map();
		citasDelDia = [];
		renderCalendar();
		renderCitasDelDia();
		return;
	}
	calendarRegion.textContent = 'Cargando disponibilidad…';
	try {
		const [rango, citas] = await Promise.all([
			api.citas.consultarDisponibilidadEnRango(calendarioMedico.value, dates[0], dates.at(-1)!),
			api.citas.listarPorMedicoEnRango(calendarioMedico.value, dates[0], dates.at(-1)!),
		]);
		agendaPorFecha = new Map(rango.dias.map((dia) => [dia.fecha, dia]));
		citasPorSlot = new Map(
			citas
				.filter((cita) => cita.estado !== 'cancelada')
				.map((cita) => [
					slotKey(clinicDate(new Date(cita.fecha_hora)), clinicTime(cita.fecha_hora)),
					cita,
				]),
		);
		citasDelDia = citas.filter(
			(cita) => clinicDate(new Date(cita.fecha_hora)) === fechaSeleccionada,
		);
		renderCalendar();
		renderCitasDelDia();
	} catch (error) {
		agendaPorFecha = new Map();
		citasPorSlot = new Map();
		citasDelDia = [];
		renderCalendar();
		renderCitasDelDia();
		showError(error);
	}
}

function openAppointment(date: string, time: string): void {
	if (!calendarioMedico.value) return showNotice('Selecciona un médico antes de agendar.', true);
	citaFecha.value = date;
	citaHora.value = time;
	citaMedico.value = calendarioMedico.value;
	const medico = medicos.find((item) => item.id === calendarioMedico.value);
	citaResumen.textContent = `${formatDay(date, { weekday: 'long', day: 'numeric', month: 'long' })} · ${time} · ${medico?.nombre ?? 'Médico'}`;
	citaDialog.showModal();
}

function movePeriod(direction: -1 | 1): void {
	if (vistaCalendario === 'dia') fechaSeleccionada = addDays(fechaSeleccionada, direction);
	else if (vistaCalendario === 'semana')
		fechaSeleccionada = addDays(fechaSeleccionada, direction * 7);
	else {
		const date = dateFromIso(fechaSeleccionada);
		fechaSeleccionada = isoDate(
			new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth() + direction, 1)),
		);
	}
	void cargarAgenda();
}

function showView(view: string): void {
	for (const section of document.querySelectorAll<HTMLElement>('.app-view'))
		section.hidden = section.id !== `${view}-view`;
	for (const button of document.querySelectorAll<HTMLButtonElement>('[data-view-target]'))
		button.classList.toggle('is-active', button.dataset.viewTarget === view);
}

async function refresh(): Promise<void> {
	try {
		[pacientes, medicos] = await Promise.all([api.pacientes.listar(), api.medicos.listar()]);
		renderPacientes();
		renderMedicos();
		renderSelects();
		await cargarAgenda();
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
		pacienteDialog.close();
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
		medicoDialog.close();
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
			fecha_hora: `${value(data, 'fecha')}T${value(data, 'hora')}:00`,
		});
		citaDialog.close();
		showNotice('Cita agendada.');
		await cargarAgenda();
	} catch (error) {
		showError(error);
	}
});

pacientesBody.addEventListener('click', async (event) => {
	const target = (event.target as Element).closest<HTMLButtonElement>('button[data-action]');
	const paciente = pacientes.find((item) => item.id === target?.dataset.id);
	if (!target || !paciente) return;
	if (target.dataset.action === 'editar') {
		pacienteForm.elements.namedItem('id')!.value = paciente.id;
		pacienteForm.elements.namedItem('nombre')!.value = paciente.nombre;
		pacienteForm.elements.namedItem('fecha_nacimiento')!.value = paciente.fecha_nacimiento;
		pacienteForm.elements.namedItem('contacto')!.value = paciente.contacto;
		showNotice('Editando paciente.');
		pacienteDialog.showModal();
		return;
	}
	if (confirm(`¿Eliminar a ${paciente.nombre}?`))
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
	const medico = medicos.find((item) => item.id === target?.dataset.id);
	if (!target || !medico) return;
	if (target.dataset.action === 'editar') {
		medicoForm.elements.namedItem('id')!.value = medico.id;
		medicoForm.elements.namedItem('nombre')!.value = medico.nombre;
		medicoForm.elements.namedItem('especialidad')!.value = medico.especialidad;
		showNotice('Editando médico.');
		medicoDialog.showModal();
		return;
	}
	if (confirm(`¿Eliminar a ${medico.nombre}?`))
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
		await cargarAgenda();
	} catch (error) {
		showError(error);
	}
});
calendarRegion.addEventListener('click', (event) => {
	const target = (event.target as Element).closest<HTMLElement>('[data-action]');
	if (!target) return;
	if (target.dataset.action === 'select-slot')
		openAppointment(target.dataset.date!, target.dataset.start!);
	if (target.dataset.action === 'open-day') {
		fechaSeleccionada = target.dataset.date!;
		vistaCalendario = 'dia';
		document
			.querySelectorAll<HTMLButtonElement>('[data-calendar-view]')
			.forEach((button) =>
				button.classList.toggle('is-active', button.dataset.calendarView === 'dia'),
			);
		void cargarAgenda();
	}
});
calendarioMedico.addEventListener('change', () => void cargarAgenda());
document
	.querySelectorAll<HTMLButtonElement>('[data-view-target]')
	.forEach((button) =>
		button.addEventListener('click', () => showView(button.dataset.viewTarget!)),
	);
document.querySelectorAll<HTMLButtonElement>('[data-calendar-view]').forEach((button) =>
	button.addEventListener('click', () => {
		vistaCalendario = button.dataset.calendarView as typeof vistaCalendario;
		document
			.querySelectorAll<HTMLButtonElement>('[data-calendar-view]')
			.forEach((item) => item.classList.toggle('is-active', item === button));
		void cargarAgenda();
	}),
);
byId<HTMLButtonElement>('fecha-anterior').addEventListener('click', () => movePeriod(-1));
byId<HTMLButtonElement>('fecha-siguiente').addEventListener('click', () => movePeriod(1));
regresarSemana.addEventListener('click', () => {
	fechaSeleccionada = siguienteDiaLaborable(clinicDate(new Date()));
	void cargarAgenda();
});
noticeClose.addEventListener('click', () => {
	if (noticeTimeout) window.clearTimeout(noticeTimeout);
	notice.hidden = true;
});
byId<HTMLButtonElement>('nuevo-paciente').addEventListener('click', () => {
	pacienteForm.reset();
	pacienteDialog.showModal();
});
byId<HTMLButtonElement>('nuevo-medico').addEventListener('click', () => {
	medicoForm.reset();
	medicoDialog.showModal();
});
byId<HTMLButtonElement>('cerrar-paciente').addEventListener('click', () => pacienteDialog.close());
byId<HTMLButtonElement>('cancelar-paciente-dialog').addEventListener('click', () =>
	pacienteDialog.close(),
);
byId<HTMLButtonElement>('cerrar-medico').addEventListener('click', () => medicoDialog.close());
byId<HTMLButtonElement>('cancelar-medico-dialog').addEventListener('click', () =>
	medicoDialog.close(),
);
byId<HTMLButtonElement>('cerrar-cita').addEventListener('click', () => citaDialog.close());
byId<HTMLButtonElement>('cancelar-cita-dialog').addEventListener('click', () => citaDialog.close());

void refresh();
