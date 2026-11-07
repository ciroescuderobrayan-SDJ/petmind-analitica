import asyncio
import os
from typing import Any

import httpx


BACKEND_URL = os.getenv(
    "BACKEND_URL", "https://backend-pet-mind.onrender.com"
)
REQUEST_TIMEOUT_SECONDS = 60.0

ENDPOINTS = {
    "mascotas": "/api/mascotas",
    "favoritos": "/api/favoritos",
    "solicitudes": "/api/solicitudes-adopcion",
    "donaciones": "/api/donaciones",
    "campanas": "/api/campanas-donacion",
    # Las mascotas solo traen fundacionId: el nombre se cruza con esta lista.
    "fundaciones": "/api/fundaciones",
}


def _records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]

    if isinstance(payload, dict):
        for key in ("content", "data", "items", "results"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]

    raise ValueError("El backend no devolvio una coleccion JSON valida.")


async def fetch_resources() -> dict[str, list[dict[str, Any]]]:
    async with httpx.AsyncClient(
        base_url=BACKEND_URL,
        timeout=REQUEST_TIMEOUT_SECONDS,
    ) as client:
        names = list(ENDPOINTS)
        response_list = await asyncio.gather(
            *(client.get(ENDPOINTS[name]) for name in names)
        )
        responses = dict(zip(names, response_list))

    resources = {}
    for name, response in responses.items():
        response.raise_for_status()
        resources[name] = _records(response.json())
    return resources
