# PetMind Analytics

Microservicio de analítica para PetMind. Consulta la información del backend
Java, la convierte en `DataFrame`, la limpia y devuelve los datos agrupados
que necesita el frontend para pintar seis gráficas.

El servicio es **stateless**:

- No tiene una base de datos propia.
- No guarda los JSON procesados.
- Consulta los datos durante cada solicitud.
- Devuelve el resultado directamente al consumidor.

## En producción

| Qué | URL |
|---|---|
| Esta API | https://petmind-analitica.onrender.com |
| Documentación interactiva | https://petmind-analitica.onrender.com/docs |
| Endpoint para el frontend (Spring Boot) | https://backend-pet-mind.onrender.com/api/analitica |

El frontend no consume esta API directamente: llama a Spring Boot, que hace
de intermediario. Ver [Despliegue en Render](#despliegue-en-render) e
[Integración con Spring Boot](#integración-con-spring-boot).

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

El proyecto también conserva `src/` y `tests/`, con el código y las pruebas
de la etapa inicial de exploración. La API no los usa: todo su flujo está
dentro de `app/`.

## Requisitos

- Python 3.12 o superior (lo exige `numpy` 2.5). En producción se usa 3.14.6.
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

1. Consulta mascotas, favoritos, solicitudes, donaciones, campañas y fundaciones.
2. Convierte las respuestas JSON en `DataFrame`.
3. Limpia valores vacíos, textos, duplicados y campos técnicos de Hibernate.
4. Calcula las agrupaciones.
5. Devuelve una colección JSON para el frontend.

La limpieza conserva los registros que tienen algunos campos nulos. Solo se
eliminan filas completamente vacías y duplicados exactos. Algunos campos
numéricos secundarios, como `edadMeses`, `contadorVisitas`, `monto` y
`porcentajeAfinidad`, pueden completarse usando el promedio de los valores
disponibles. Las especies faltantes se clasifican como `OTRO`, que es la
categoría definida por el proyecto. No se inventan identificadores, estados,
nombres ni relaciones faltantes.

La respuesta contiene actualmente:

- `mascotasPorEspecie`
- `mascotasPorEstadoAdopcion`: cuántas mascotas están disponibles, en proceso, adoptadas o en tratamiento.
- `mascotasPorSemana`: mascotas publicadas cada semana (de lunes a domingo, por `fechaPublicacion` o, si falta,
  `fechaCreacion`). Las semanas sin publicaciones van en cero: `[{ "semana": "2026-10-26", "cantidad": 7 }]`.
- `favoritosPorEspecie`
- `solicitudesPorEspecie`
- `solicitudesPorEstado`
- `mascotasPorFundacion`
- `donacionesPorCampana`
- `metadata`

El backend devuelve las relaciones solo como ids (`fundacionId`, `mascotaId`). Para nombrar la fundación de
cada mascota se cruza `fundacionId` con `/api/fundaciones`, y para la especie de cada solicitud o favorito se
cruza `mascotaId` con `/api/mascotas`. Si algún día el backend envía los objetos anidados (`fundacion.nombre`,
`mascota.especie`), también se aceptan.

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

La API está desplegada como **Web Service** en el mismo proyecto de Render que
el backend (`My project` → `Production`, región Oregon), con esta
configuración:

| Campo | Valor |
|---|---|
| Language | Python 3 |
| Branch | `main` |
| Root Directory | *(vacío)* |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Health Check Path | `/health` |
| Instance Type | Free |

Variables de entorno:

| Variable | Valor |
|---|---|
| `PYTHON_VERSION` | `3.14.6`, la misma versión usada en local |
| `BACKEND_URL` | `https://backend-pet-mind.onrender.com` |

Cada push a `main` se despliega automáticamente.

El plan Free apaga el servicio después de 15 minutos sin solicitudes, y la
siguiente solicitud puede tardar 50 segundos o más mientras arranca. El
backend también usa el plan Free, así que la primera carga del dashboard
puede tardar más si ambos servicios estaban apagados. Si se llama a esta API
directamente mientras el backend está apagado, puede responder `502` porque
el cliente espera como máximo 60 segundos; basta con repetir la solicitud.

## Documentación funcional

### ¿Qué problema resuelve?

Esta mini API prepara los datos que necesita el dashboard de PetMind. No
administra usuarios, mascotas ni donaciones, y tampoco reemplaza al backend
Spring Boot. Su única responsabilidad es consultar datos, limpiarlos,
agruparlos y devolverlos listos para las gráficas.

### Flujo general

```text
Spring Boot
    ↓ solicita información
API Python
    ↓ consulta endpoints del backend
JSON original
    ↓ convierte y limpia
DataFrames de pandas
    ↓ calcula agrupaciones
JSON para el dashboard
    ↓ devuelve la respuesta
Spring Boot / frontend
```

La API es stateless. Cada solicitud ejecuta el proceso completo en memoria:
no crea tablas, no guarda archivos y no conserva los resultados después de
responder.

### Módulos

#### `app/main.py`

Es la entrada de la aplicación FastAPI. Define los endpoints y coordina el
proceso:

1. Solicita los datos al cliente HTTP.
2. Convierte las respuestas en `DataFrame`.
3. Ejecuta la limpieza.
4. Construye la respuesta del dashboard.
5. Devuelve el JSON o un error HTTP.

#### `app/client.py`

Se comunica con el backend Spring Boot usando `httpx`. Actualmente consulta:

```text
/api/mascotas
/api/favoritos
/api/solicitudes-adopcion
/api/donaciones
/api/campanas-donacion
```

La URL base se obtiene de `BACKEND_URL`. Si no se configura, usa:

```text
https://backend-pet-mind.onrender.com
```

#### `app/data_cleaning.py`

Transforma cada colección JSON en un `DataFrame` usando
`pandas.json_normalize`. Esto aplana objetos anidados; por ejemplo,
`mascota.especie` se convierte en `mascota_especie`.

Después realiza estas tareas:

- Convierte textos vacíos en valores nulos.
- Elimina únicamente filas completamente vacías.
- Normaliza espacios y mayúsculas/minúsculas.
- Elimina campos técnicos de Hibernate.
- Elimina duplicados exactos.
- Completa algunos valores numéricos secundarios con el promedio disponible.
- Clasifica especies faltantes como `OTRO`.

No inventa identificadores, estados, nombres ni relaciones entre entidades.

#### `app/analytics.py`

Trabaja únicamente con los `DataFrame` ya limpios. Calcula las colecciones
que consumirá el frontend:

- Mascotas por especie.
- Favoritos por especie.
- Solicitudes por especie.
- Solicitudes por estado.
- Mascotas por fundación.
- Donaciones por campaña.

### Endpoints disponibles

#### `GET /health`

Comprueba que la aplicación esté funcionando:

```json
{
  "status": "ok"
}
```

#### `GET /api/analytics/dashboard`

Ejecuta todo el flujo de consulta, limpieza y análisis. Devuelve una respuesta
con esta estructura:

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
  "solicitudesPorEspecie": [],
  "solicitudesPorEstado": [
    {
      "categoria": "PENDIENTE",
      "cantidad": 4
    }
  ],
  "mascotasPorFundacion": [
    {
      "fundacion": "Huellas de Esperanza",
      "cantidad": 6
    }
  ],
  "donacionesPorCampana": [
    {
      "campana": "Ayuda Luna",
      "total": 150.0
    }
  ],
  "metadata": {
    "mascotasProcesados": 10
  }
}
```

Las listas pueden estar vacías si el backend todavía no tiene registros para
una relación. Eso no significa que la API haya fallado.

### Integración con Spring Boot

El frontend no consulta directamente esta API. Spring Boot funciona como
intermediario:

```text
Frontend
    ↓ GET /api/analitica
Spring Boot (backend-pet-mind)
    ↓ GET /api/analytics/dashboard
API Python (petmind-analitica)
    ↓ consulta /api/mascotas, /api/favoritos, etc. en Spring Boot
    ↓ devuelve el JSON del dashboard
Spring Boot reenvía el JSON sin modificarlo
    ↓
Frontend pinta las gráficas
```

En el repositorio `backend-pet-mind`, el puente está formado por:

- `AnaliticaController`: expone `GET /api/analitica`.
- `AnaliticaService` y `AnaliticaServiceImpl`: llaman a esta API con
  `RestClient` y devuelven el JSON tal como llega, sin DTOs.
- `AnaliticaException`: si esta API falla o devuelve una respuesta vacía,
  `GlobalExceptionHandler` responde `502 Bad Gateway` con
  `{"mensaje": "..."}`.

No usa entidades ni repositorios, porque el resultado no se guarda en la base
de datos.

La URL de esta API se lee en `application.properties`:

```properties
analitica.api.url=${ANALITICA_API_URL}
```

`ANALITICA_API_URL` debe ser la URL **completa** del endpoint, porque el
servicio Java la llama tal cual:

| Entorno | Dónde se define | Valor |
|---|---|---|
| Local | `.env` en la raíz del backend | `http://127.0.0.1:8000/api/analytics/dashboard` |
| Render | Environment del servicio `backend-pet-mind` | `https://petmind-analitica.onrender.com/api/analytics/dashboard` |

La propiedad no tiene valor por defecto: si la variable no existe, el backend
no arranca.

Para probar todo en local, esta API debe ejecutarse con `BACKEND_URL`
apuntando al backend local (por ejemplo, `http://localhost:8080`). Si no, la
API leerá los datos del backend de Render.

### Estado actual

Actualizado el 7 de noviembre de 2026:

- La API Python, la limpieza, las agrupaciones y el endpoint del dashboard
  están implementados y desplegados en Render.
- El puente de Spring Boot (`GET /api/analitica`) está en la rama `main` del
  backend y desplegado.
- La cadena completa se probó en producción:
  `GET https://backend-pet-mind.onrender.com/api/analitica` responde `200`
  con el JSON del dashboard.
- Para pintar las gráficas, el frontend debe consumir
  `GET https://backend-pet-mind.onrender.com/api/analitica`.
