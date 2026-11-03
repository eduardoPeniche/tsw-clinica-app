#!/bin/sh
# Prepara n8n antes de iniciarlo: registra la credencial de Discord e importa y
# publica el flujo versionado. Se ejecuta en cada arranque, así que el flujo del
# repositorio reemplaza los cambios hechos en el editor que no se exportaron.
set -e

credenciales=/tmp/credenciales.json
printf '[{"id":"DiscordClinica01","name":"Discord Clínica","type":"discordWebhookApi","data":{"webhookUri":"%s"}}]' \
  "$DISCORD_WEBHOOK_URL" > "$credenciales"
n8n import:credentials --input="$credenciales"
rm -f "$credenciales"

n8n import:workflow --input=/n8n/workflows/clinica-eventos.json
n8n publish:workflow --id=ClinicaEventos01

exec n8n start
