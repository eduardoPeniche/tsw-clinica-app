import { useEffect, useState, type FormEvent } from 'react';
import { api, type Paciente, type PacienteInput } from '@/lib/api/client';
import { showNotice, showError } from '@/lib/notice';
import { Button } from '@/components/ui/button';
import {
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableHeader,
	TableRow,
} from '@/components/ui/table';
import {
	Dialog,
	DialogContent,
	DialogFooter,
	DialogHeader,
	DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { SectionHeading } from '@/components/section-heading';

type FormState = { id: string; nombre: string; fecha_nacimiento: string; contacto: string };

const EMPTY_FORM: FormState = { id: '', nombre: '', fecha_nacimiento: '', contacto: '' };

function notifyPacientesChanged(): void {
	window.dispatchEvent(new Event('pacientes:changed'));
}

export function PacientesView() {
	const [pacientes, setPacientes] = useState<Paciente[]>([]);
	const [loading, setLoading] = useState(true);
	const [dialogOpen, setDialogOpen] = useState(false);
	const [form, setForm] = useState<FormState>(EMPTY_FORM);
	const [saving, setSaving] = useState(false);

	async function cargar(): Promise<void> {
		setLoading(true);
		try {
			setPacientes(await api.pacientes.listar());
		} catch (error) {
			showError(error);
		} finally {
			setLoading(false);
		}
	}

	useEffect(() => {
		void cargar();
	}, []);

	function abrirNuevo(): void {
		setForm(EMPTY_FORM);
		setDialogOpen(true);
	}

	function abrirEditar(paciente: Paciente): void {
		setForm({
			id: paciente.id,
			nombre: paciente.nombre,
			fecha_nacimiento: paciente.fecha_nacimiento,
			contacto: paciente.contacto,
		});
		setDialogOpen(true);
	}

	async function eliminar(paciente: Paciente): Promise<void> {
		if (!confirm(`¿Eliminar a ${paciente.nombre}?`)) return;
		try {
			await api.pacientes.eliminar(paciente.id);
			showNotice('Paciente eliminado.');
			await cargar();
			notifyPacientesChanged();
		} catch (error) {
			showError(error);
		}
	}

	async function guardar(event: FormEvent<HTMLFormElement>): Promise<void> {
		event.preventDefault();
		const input: PacienteInput = {
			nombre: form.nombre.trim(),
			fecha_nacimiento: form.fecha_nacimiento,
			contacto: form.contacto.trim(),
		};
		setSaving(true);
		try {
			await (form.id ? api.pacientes.actualizar(form.id, input) : api.pacientes.crear(input));
			setDialogOpen(false);
			showNotice(form.id ? 'Paciente actualizado.' : 'Paciente creado.');
			await cargar();
			notifyPacientesChanged();
		} catch (error) {
			showError(error);
		} finally {
			setSaving(false);
		}
	}

	return (
		<>
			<div className="px-[var(--content-inline)] pt-[var(--content-block)]">
				<SectionHeading
					title="Pacientes"
					description="Consulta, registra y actualiza los datos de tus pacientes."
					action={
						<Button type="button" onClick={abrirNuevo}>
							Agregar
						</Button>
					}
				/>
			</div>
			<div className="table-wrap resource-table-wrap">
				<Table>
					<TableHeader>
						<TableRow>
							<TableHead>Paciente</TableHead>
							<TableHead>Nacimiento</TableHead>
							<TableHead>Contacto</TableHead>
							<TableHead>
								<span className="sr-only">Acciones</span>
							</TableHead>
						</TableRow>
					</TableHeader>
					<TableBody>
						{loading ? (
							<TableRow>
								<TableCell colSpan={4} className="empty">
									Cargando pacientes…
								</TableCell>
							</TableRow>
						) : pacientes.length === 0 ? (
							<TableRow>
								<TableCell colSpan={4} className="empty">
									Aún no hay pacientes registrados.
								</TableCell>
							</TableRow>
						) : (
							pacientes.map((paciente) => (
								<TableRow key={paciente.id}>
									<TableCell>{paciente.nombre}</TableCell>
									<TableCell>{paciente.fecha_nacimiento}</TableCell>
									<TableCell>{paciente.contacto}</TableCell>
									<TableCell>
										<div className="row-actions">
											<Button
												type="button"
												variant="secondary"
												size="sm"
												onClick={() => abrirEditar(paciente)}
											>
												Editar
											</Button>
											<Button
												type="button"
												variant="destructive"
												size="sm"
												onClick={() => void eliminar(paciente)}
											>
												Eliminar
											</Button>
										</div>
									</TableCell>
								</TableRow>
							))
						)}
					</TableBody>
				</Table>
			</div>

			<Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
				<DialogContent>
					<DialogHeader>
						<DialogTitle>{form.id ? 'Editar paciente' : 'Nuevo paciente'}</DialogTitle>
					</DialogHeader>
					<form className="entity-dialog-form" onSubmit={(event) => void guardar(event)}>
						<Label htmlFor="paciente-nombre">
							Nombre completo
							<Input
								id="paciente-nombre"
								required
								value={form.nombre}
								onChange={(event) => setForm({ ...form, nombre: event.target.value })}
							/>
						</Label>
						<Label htmlFor="paciente-nacimiento">
							Fecha de nacimiento
							<Input
								id="paciente-nacimiento"
								type="date"
								required
								value={form.fecha_nacimiento}
								onChange={(event) => setForm({ ...form, fecha_nacimiento: event.target.value })}
							/>
						</Label>
						<Label htmlFor="paciente-contacto">
							Contacto
							<Input
								id="paciente-contacto"
								required
								value={form.contacto}
								onChange={(event) => setForm({ ...form, contacto: event.target.value })}
							/>
						</Label>
						<DialogFooter>
							<Button type="button" variant="secondary" onClick={() => setDialogOpen(false)}>
								Cancelar
							</Button>
							<Button type="submit" disabled={saving}>
								{saving ? 'Guardando…' : 'Guardar'}
							</Button>
						</DialogFooter>
					</form>
				</DialogContent>
			</Dialog>
		</>
	);
}
