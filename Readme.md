# PetMind Analítica

Aplicación de análisis de datos para **PetMind**, desarrollada en Python. El programa obtiene información de usuarios y favoritos desde una API, la carga en DataFrames de Pandas, realiza la limpieza de los datos e imprime los resultados limpios en consola.

## Funcionalidades

- Extracción de datos desde una API.
- Generación de los archivos `user.json` y `favorite.json`.
- Carga de archivos JSON en DataFrames con Pandas.
- Manejo de valores nulos y filas vacías.
- Estandarización de texto: conversión a minúsculas y eliminación de espacios adicionales.
- Eliminación de registros duplicados.
- Validación de campos obligatorios para usuarios y favoritos.
- Impresión de los DataFrames limpios, valores nulos y cantidad de registros.

## Estructura del proyecto

```text
petmind-analitica/
├── Data/
│   ├── raw/
│   │   ├── user.json
│   │   └── favorite.json
│   └── processed/
├── src/
│   ├── extract/
│   │   └── fetch_api.py
│   └── transform/
│       ├── cargar_datos.py
│       └── limpiar_datos.py
├── main.py
├── requirements.txt
├── .gitignore
└── Readme.md
```

## Requisitos

- Python 3.
- Git.
- Conexión a internet para descargar los datos desde la API.

## Instalación

Clona el repositorio:

```bash
git clone <https://github.com/ciroescuderobrayan-SDJ/petmind-analitica>
cd petmind-analitica
```

Crea el entorno virtual:

```bash
python3 -m venv .venv
```

Activa el entorno virtual:

**macOS/Linux:**

```bash
source .venv/bin/activate
```

**Windows:**

```bash
.venv\Scripts\activate
```

Instala las dependencias:

```bash
python -m pip install -r requirements.txt
```

## Ejecución

Con el entorno virtual activo, ejecuta:

```bash
python main.py
```

El programa mostrará el siguiente menú:

```text
1. Traer datos desde la API
2. Cargar datos
3. Limpiar datos
4. Imprimir datos limpios
5. Mergear datos
6. Consultas de datos
0. Salir
```

Para ejecutar correctamente las funciones disponibles, se recomienda utilizar las opciones en este orden:

```text
1 → 2 → 3 → 4
```

1. **Traer datos desde la API:** descarga y guarda los archivos `user.json` y `favorite.json` en `Data/raw/`.
2. **Cargar datos:** convierte los archivos JSON en DataFrames.
3. **Limpiar datos:** elimina filas vacías, duplicados, valores inválidos y estandariza los textos.
4. **Imprimir datos limpios:** muestra en consola cada DataFrame limpio, los valores nulos por columna y la cantidad de registros.

## Fuentes de datos

Los datos se obtienen desde los siguientes endpoints:

- Usuarios: `https://6ac0faa8309c92da039c3567.mockapi.io/api/v1/user`
- Favoritos: `https://6ac0faa8309c92da039c3567.mockapi.io/api/v1/favorite`

## Control de versiones

El proyecto utiliza Git Flow:

- `main`: rama estable del proyecto.
- `dev`: rama de integración del equipo.
- `feature/*`: ramas para implementar funcionalidades específicas.
- `release/analisis-v1`: rama destinada a preparar la versión de entrega.

Cada funcionalidad se desarrolla en una rama `feature/`, se integra mediante Pull Request hacia `dev` y, al finalizar el proyecto, se prepara la rama de entrega.

## Integrantes

- Santiago Varela
- Emmanuel Gomez 
- Brayan ciro