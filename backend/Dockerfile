FROM python:3.14-slim AS base

COPY --from=ghcr.io/astral-sh/uv:0.12.16 /uv /uvx /bin/

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

COPY pyproject.toml uv.lock ./
COPY src ./src

EXPOSE 8000

FROM base AS development

COPY tests ./tests

RUN uv sync --frozen --group mcp

CMD ["fastapi", "dev", "src/clinica_app/main.py", "--host", "0.0.0.0", "--port", "8000"]

FROM base AS mcp

RUN uv sync --frozen --no-default-groups --group mcp

CMD ["python", "-m", "clinica_app.adapters.mcp.server"]

FROM base AS production

RUN uv sync --frozen --no-dev

CMD ["fastapi", "run", "src/clinica_app/main.py", "--host", "0.0.0.0", "--port", "8000"]
