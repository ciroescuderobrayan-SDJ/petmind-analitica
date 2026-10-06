import json
from pathlib import Path
from typing import Any

import requests


ENDPOINTS_API = {
    "user": "https://6ac0faa8309c92da039c3567.mockapi.io/api/v1/user",
    "favorite": "https://6ac0faa8309c92da039c3567.mockapi.io/api/v1/favorite",
}
TIEMPO_ESPERA_SOLICITUD = 30
CARPETA_DATOS_ORIGINALES = Path(__file__).resolve().parents[2] / "Data" / "raw"


def obtener_datos_endpoint(direccion: str) -> Any:
    """Obtiene datos JSON desde un endpoint de la API."""
    respuesta = requests.get(direccion, timeout=TIEMPO_ESPERA_SOLICITUD)
    respuesta.raise_for_status()
    return respuesta.json()


def guardar_json(datos: Any, ruta_salida: Path) -> None:
    """Guarda los datos de la API como JSON UTF-8 y crea la carpeta si es necesario."""
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    ruta_salida.write_text(
        json.dumps(datos, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def fetch() -> None:
    for nombre_recurso, direccion_api in ENDPOINTS_API.items():
        datos = obtener_datos_endpoint(direccion_api)
        guardar_json(datos, CARPETA_DATOS_ORIGINALES / f"{nombre_recurso}.json")
        print(f"Datos de {nombre_recurso} guardados correctamente.")


if __name__ == "__main__":
    fetch()
