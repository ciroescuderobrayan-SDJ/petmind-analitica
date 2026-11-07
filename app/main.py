import httpx
from fastapi import FastAPI, HTTPException

from app.analytics import build_dashboard
from app.client import fetch_resources
from app.data_cleaning import (
    clean_dataframes,
    convert_resources_to_dataframes,
)


app = FastAPI(
    title="PetMind Analytics",
    description="Genera datos agregados para las graficas del dashboard.",
    version="1.0.0",
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/analytics/dashboard")
async def dashboard() -> dict:
    try:
        resources_from_backend = await fetch_resources()
        dataframes = convert_resources_to_dataframes(resources_from_backend)
        cleaned_dataframes = clean_dataframes(dataframes)

        return build_dashboard(cleaned_dataframes)
    except (httpx.HTTPError, ValueError) as error:
        raise HTTPException(
            status_code=502,
            detail=(
                "No fue posible obtener los datos del backend: "
                f"{type(error).__name__}: {error!s}"
            ),
        ) from error
