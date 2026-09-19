import type { MiddlewareHandler } from 'astro';

const API_PREFIX = '/api';

export const onRequest: MiddlewareHandler = async (context, next) => {
	if (context.url.pathname !== API_PREFIX && !context.url.pathname.startsWith(`${API_PREFIX}/`)) {
		return next();
	}

	const backendUrl = import.meta.env.BACKEND_URL;

	if (!backendUrl) {
		return new Response('BACKEND_URL no está configurada.', { status: 500 });
	}

	const target = new URL(context.url.pathname.slice(API_PREFIX.length) || '/', backendUrl);
	target.search = context.url.search;

	const headers = new Headers(context.request.headers);
	headers.delete('host');

	const isBodylessRequest = ['GET', 'HEAD'].includes(context.request.method);
	const response = await fetch(target, {
		method: context.request.method,
		headers,
		body: isBodylessRequest ? undefined : await context.request.arrayBuffer(),
	});

	return new Response(response.body, {
		status: response.status,
		headers: response.headers,
	});
};
