# PetMind Analytics

Microservicio de analítica para PetMind. Consulta la información del backend
Java, la convierte en `DataFrame`, la limpia y devuelve los datos agrupados
que necesita el frontend para pintar seis gráficas.

El servicio es **stateless**:

- No tiene una base de datos propia.
- No guarda los JSON procesados.
- Consulta los datos durante cada solicitud.
- Devuelve el resultado directamente al consumidor.

## Flujo de datos

```text
Backend Spring Boot
        |
        | JSON
        v
Cliente HTTP de Python
        |
        v
DataFrames de pandas
        |
        v
Limpieza de datos
        |
        v
Agrupaciones para las gráficas
        |
        v
Respuesta JSON
```

## Estructura actual

```text
app/
├── analytics.py       # Calcula las métricas del dashboard.
├── client.py          # Consulta los endpoints del backend Java.
├── data_cleaning.py   # Convierte y limpia los datos con pandas.
└── main.py            # Define la aplicación FastAPI y sus endpoints.
```

El proyecto también conserva `src/` y `Data/` con el código y los archivos
utilizados durante la etapa inicial de exploración. La API actual utiliza el
flujo ubicado dentro de `app/`.

## Requisitos

- Python 3.10 o superior.
- Dependencias instaladas desde `requirements.txt`.
- Acceso al backend de PetMind.

## Instalación local

Crear y activar un entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instalar las dependencias:

```powershell
pip install -r requirements.txt
```

## Ejecutar localmente

Desde la carpeta raíz del proyecto:

```powershell
uvicorn app.main:app --reload
```

La API estará disponible en:

```text
http://127.0.0.1:8000
```

La documentación interactiva de FastAPI está disponible en:

```text
http://127.0.0.1:8000/docs
```

## Endpoints

### Verificar el estado del servicio

```http
GET /health
```

Respuesta:

```json
{
  "status": "ok"
}
```

### Obtener los datos del dashboard

```http
GET /api/analytics/dashboard
```

Este endpoint:

1. Consulta mascotas, favoritos, solicitudes, donaciones y campañas.
2. Convierte las respuestas JSON en `DataFrame`.
3. Limpia valores vacíos, textos, duplicados y campos técnicos de Hibernate.
4. Calcula las agrupaciones.
5. Devuelve una colección JSON para el frontend.

La respuesta contiene actualmente:

- `mascotasPorEspecie`
- `favoritosPorEspecie`
- `solicitudesPorEspecie`
- `solicitudesPorEstado`
- `mascotasPorFundacion`
- `donacionesPorCampana`
- `metadata`

Ejemplo de estructura:

```json
{
  "mascotasPorEspecie": [
    {
      "categoria": "PERRO",
      "cantidad": 10
    }
  ],
  "favoritosPorEspecie": [
    {
      "especie": "PERRO",
      "cantidad": 8
    }
  ],
  "solicitudesPorEstado": [
    {
      "categoria": "PENDIENTE",
      "cantidad": 4
    }
  ],
  "metadata": {
    "mascotasProcesados": 10
  }
}
```

## Backend consultado

Por defecto, el cliente consulta:

```text
https://backend-pet-mind.onrender.com
```

La URL puede cambiarse mediante la variable de entorno `BACKEND_URL`.

En PowerShell:

```powershell
$env:BACKEND_URL = "https://otra-url.example.com"
uvicorn app.main:app --reload
```

## Despliegue en Render

Configurar el proyecto como **Web Service** con:

```text
Build command: pip install -r requirements.txt
Start command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

También se puede configurar `BACKEND_URL` como variable de entorno en Render.

## Estado del proyecto

- [x] Crear la aplicación FastAPI.
- [x] Crear un endpoint de salud.
- [x] Consultar el backend Spring Boot.
- [x] Convertir las respuestas JSON en `DataFrame`.
- [x] Limpiar los datos antes de analizarlos.
- [x] Generar seis colecciones para las gráficas.
- [x] Evitar la persistencia de resultados.
- [ ] Probar con todas las respuestas reales del backend.
- [ ] Revisar casos con datos vacíos o incompletos.
- [ ] Conectar el frontend.
- [ ] Pintar las seis gráficas.
- [ ] Configurar y validar el despliegue en Render.

## Historial de cambios

### 2026-11-02

- Se creó la API FastAPI de analítica.
- Se agregó el endpoint único `/api/analytics/dashboard`.
- Se agregó el endpoint `/health`.
- Se configuró la consulta al backend desplegado en Render.
- Se agregó la conversión de JSON a `DataFrame` usando pandas.
- Se agregó la limpieza de valores vacíos, textos, duplicados y campos
  técnicos de Hibernate.
- Se agregaron agrupaciones por especie, estado, fundación y campaña.
- Se dejó el servicio sin persistencia de datos.
- Se documentó la ejecución local y el despliegue en Render.
