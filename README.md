# Sistema de gestión de citas médicas

## Ejecutar con Docker

La aplicación se ejecuta desde un contenedor; no es necesario instalar las
dependencias de Python en el equipo local.

```bash
docker compose up --build
```

Por ahora, el contenedor imprime `Hello from clinica-app!` y termina. Más
adelante, al incorporar los endpoints, se configurará el servidor de FastAPI
para que permanezca disponible en el puerto `8000`.
