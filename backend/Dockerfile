FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:0.12.16 /uv /uvx /bin/

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml uv.lock ./
COPY src ./src
COPY tests ./tests

# La instalación ocurre dentro de la imagen y usa las versiones fijadas en uv.lock.
RUN uv sync --frozen --no-dev

EXPOSE 8000

CMD ["fastapi", "run", "src/clinica_app/main.py", "--host", "0.0.0.0", "--port", "8000"]
