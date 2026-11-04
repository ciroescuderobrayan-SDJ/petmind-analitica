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

La limpieza conserva los registros que tienen algunos campos nulos. Solo se
eliminan filas completamente vacías y duplicados exactos. Algunos campos
numéricos secundarios, como `edadMeses`, `contadorVisitas`, `monto` y
`porcentajeAfinidad`, pueden completarse usando el promedio de los valores
disponibles. Las especies faltantes se clasifican como `OTRO`, que es la
categoría definida por el proyecto. No se inventan identificadores, estados,
nombres ni relaciones faltantes.

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

El frontend no debería consultar directamente esta API. Spring Boot debe
funcionar como intermediario:

```text
Frontend
    ↓ GET /api/analitica/dashboard
Spring Boot
    ↓ GET /api/analytics/dashboard
API Python
    ↓
Spring Boot devuelve el JSON
    ↓
Frontend pinta las gráficas
```

Para este puente no se necesita una entidad ni un repositorio, porque el
resultado no se guarda en la base de datos. Puede crearse un controlador y un
servicio en Spring Boot. Mientras la respuesta siga en desarrollo, Java puede
recibirla como JSON; cuando sea definitiva, se pueden agregar DTOs.

### Estado actual

La API Python, la limpieza, las agrupaciones y el endpoint del dashboard ya
están implementados y probados localmente. Queda pendiente crear el
controlador y el servicio intermediarios en Spring Boot, probar la
comunicación entre ambos servicios y conectar el frontend.
