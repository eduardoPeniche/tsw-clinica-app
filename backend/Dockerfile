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

# Este objetivo lo utiliza Docker Compose durante el desarrollo.
RUN uv sync --frozen

CMD ["fastapi", "dev", "src/clinica_app/main.py", "--host", "0.0.0.0", "--port", "8000"]

FROM base AS production

# El objetivo predeterminado para `docker build` omite las dependencias de desarrollo.
RUN uv sync --frozen --no-dev

CMD ["fastapi", "run", "src/clinica_app/main.py", "--host", "0.0.0.0", "--port", "8000"]
