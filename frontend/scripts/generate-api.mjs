import { spawnSync } from 'node:child_process';

const openapiUrl = process.env.OPENAPI_URL;

if (!openapiUrl) {
	console.error('OPENAPI_URL debe apuntar al documento OpenAPI.');
	process.exit(1);
}

const npx = process.platform === 'win32' ? 'npx.cmd' : 'npx';
const result = spawnSync(
	npx,
	['openapi-typescript', openapiUrl, '-o', 'src/lib/api/generated/schema.d.ts'],
	{ stdio: 'inherit' },
);

process.exit(result.status ?? 1);
