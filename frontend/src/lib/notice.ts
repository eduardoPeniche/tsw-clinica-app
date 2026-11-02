import { ApiError } from './api/client';

let noticeTimeout: number | undefined;

function elements() {
	return {
		notice: document.getElementById('notice') as HTMLDivElement,
		message: document.getElementById('notice-message') as HTMLSpanElement,
	};
}

export function showNotice(message: string, isError = false): void {
	const { notice, message: messageEl } = elements();
	if (noticeTimeout) window.clearTimeout(noticeTimeout);
	messageEl.textContent = message;
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

export function showError(error: unknown): void {
	showNotice(
		error instanceof ApiError ? error.message : 'No fue posible completar la operación.',
		true,
	);
}

export function dismissNotice(): void {
	if (noticeTimeout) window.clearTimeout(noticeTimeout);
	elements().notice.hidden = true;
}
