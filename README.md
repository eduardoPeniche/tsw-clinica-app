# Sistema de gestión de citas médicas

## Ejecutar con Docker

La aplicación se ejecuta desde un contenedor; no es necesario instalar las
dependencias de Python en el equipo local.

```bash
docker compose up --build
```

La API queda disponible en `http://localhost:8000`; la documentación
interactiva está en `http://localhost:8000/docs`.

## Ejecutar pruebas

```bash
docker compose run --rm api python -m unittest discover -s tests
```
