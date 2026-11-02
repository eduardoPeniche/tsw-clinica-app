import { useEffect, useState, type FormEvent } from 'react';
import { api, type Medico, type MedicoInput } from '@/lib/api/client';
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

type FormState = { id: string; nombre: string; especialidad: string };

const EMPTY_FORM: FormState = { id: '', nombre: '', especialidad: '' };

function notifyMedicosChanged(): void {
	window.dispatchEvent(new Event('medicos:changed'));
}

export function MedicosView() {
	const [medicos, setMedicos] = useState<Medico[]>([]);
	const [loading, setLoading] = useState(true);
	const [dialogOpen, setDialogOpen] = useState(false);
	const [form, setForm] = useState<FormState>(EMPTY_FORM);
	const [saving, setSaving] = useState(false);

	async function cargar(): Promise<void> {
		setLoading(true);
		try {
			setMedicos(await api.medicos.listar());
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

	function abrirEditar(medico: Medico): void {
		setForm({ id: medico.id, nombre: medico.nombre, especialidad: medico.especialidad });
		setDialogOpen(true);
	}

	async function eliminar(medico: Medico): Promise<void> {
		if (!confirm(`¿Eliminar a ${medico.nombre}?`)) return;
		try {
			await api.medicos.eliminar(medico.id);
			showNotice('Médico eliminado.');
			await cargar();
			notifyMedicosChanged();
		} catch (error) {
			showError(error);
		}
	}

	async function guardar(event: FormEvent<HTMLFormElement>): Promise<void> {
		event.preventDefault();
		const input: MedicoInput = {
			nombre: form.nombre.trim(),
			especialidad: form.especialidad.trim(),
		};
		setSaving(true);
		try {
			await (form.id ? api.medicos.actualizar(form.id, input) : api.medicos.crear(input));
			setDialogOpen(false);
			showNotice(form.id ? 'Médico actualizado.' : 'Médico creado.');
			await cargar();
			notifyMedicosChanged();
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
					title="Médicos"
					description="Gestiona el directorio de médicos y sus especialidades."
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
							<TableHead>Médico</TableHead>
							<TableHead>Especialidad</TableHead>
							<TableHead>
								<span className="sr-only">Acciones</span>
							</TableHead>
						</TableRow>
					</TableHeader>
					<TableBody>
						{loading ? (
							<TableRow>
								<TableCell colSpan={3} className="empty">
									Cargando médicos…
								</TableCell>
							</TableRow>
						) : medicos.length === 0 ? (
							<TableRow>
								<TableCell colSpan={3} className="empty">
									Aún no hay médicos registrados.
								</TableCell>
							</TableRow>
						) : (
							medicos.map((medico) => (
								<TableRow key={medico.id}>
									<TableCell>{medico.nombre}</TableCell>
									<TableCell>{medico.especialidad}</TableCell>
									<TableCell>
										<div className="row-actions">
											<Button
												type="button"
												variant="secondary"
												size="sm"
												onClick={() => abrirEditar(medico)}
											>
												Editar
											</Button>
											<Button
												type="button"
												variant="destructive"
												size="sm"
												onClick={() => void eliminar(medico)}
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
						<DialogTitle>{form.id ? 'Editar médico' : 'Nuevo médico'}</DialogTitle>
					</DialogHeader>
					<form className="entity-dialog-form" onSubmit={(event) => void guardar(event)}>
						<Label htmlFor="medico-nombre">
							Nombre completo
							<Input
								id="medico-nombre"
								required
								value={form.nombre}
								onChange={(event) => setForm({ ...form, nombre: event.target.value })}
							/>
						</Label>
						<Label htmlFor="medico-especialidad">
							Especialidad
							<Input
								id="medico-especialidad"
								required
								value={form.especialidad}
								onChange={(event) => setForm({ ...form, especialidad: event.target.value })}
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
