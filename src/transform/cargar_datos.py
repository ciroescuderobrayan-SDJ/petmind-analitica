from pathlib import Path

import pandas as pd


RECURSOS = ("user", "favorite")
CARPETA_DATOS_ORIGINALES = Path(__file__).resolve().parents[2] / "Data" / "raw"


def cargar_datos() -> dict[str, pd.DataFrame]:
    """Carga los archivos JSON como DataFrames de pandas."""
    datos = {}
    for nombre_recurso in RECURSOS:
        ruta_archivo = CARPETA_DATOS_ORIGINALES / f"{nombre_recurso}.json"
        datos[nombre_recurso] = pd.read_json(ruta_archivo)
        print(f"Datos de {nombre_recurso} cargados correctamente.")
    return datos
