from collections import Counter
from typing import Any

import pandas as pd


def build_dashboard(
    cleaned_dataframes: dict[str, pd.DataFrame],
) -> dict[str, Any]:
    """Construye las seis colecciones que consumira el frontend."""
    pets_dataframe = cleaned_dataframes["mascotas"]
    favorites_dataframe = cleaned_dataframes["favoritos"]
    adoption_requests_dataframe = cleaned_dataframes["solicitudes"]
    donations_dataframe = cleaned_dataframes["donaciones"]

    favorites_by_species = count_nested_column(
        favorites_dataframe,
        "mascota_especie",
        "especie",
    )
    adoption_requests_by_species = count_nested_column(
        adoption_requests_dataframe,
        "mascota_especie",
        "especie",
    )
    pets_by_foundation = count_nested_column(
        pets_dataframe,
        "fundacion_nombre",
        "fundacion",
    )
    donations_by_campaign = sum_donations_by_campaign(donations_dataframe)

    return {
        "mascotasPorEspecie": count_column(pets_dataframe, "especie"),
        "favoritosPorEspecie": favorites_by_species,
        "solicitudesPorEspecie": adoption_requests_by_species,
        "solicitudesPorEstado": count_column(
            adoption_requests_dataframe,
            "estado",
        ),
        "mascotasPorFundacion": pets_by_foundation,
        "donacionesPorCampana": donations_by_campaign,
        "metadata": build_metadata(cleaned_dataframes),
    }


def count_column(
    dataframe: pd.DataFrame,
    column_name: str,
) -> list[dict[str, Any]]:
    """Cuenta cuantas veces aparece cada valor de una columna."""
    if column_name not in dataframe.columns:
        return []

    values = dataframe[column_name].dropna().astype(str).str.upper()
    value_counts = values.value_counts()

    results = []
    for category, quantity in value_counts.items():
        results.append(
            {
                "categoria": category,
                "cantidad": int(quantity),
            }
        )

    return results


def count_nested_column(
    dataframe: pd.DataFrame,
    column_name: str,
    result_field_name: str,
) -> list[dict[str, Any]]:
    """Cuenta valores de una columna que venia dentro de un objeto anidado."""
    if column_name not in dataframe.columns:
        return []

    values = dataframe[column_name].dropna().astype(str).str.upper()
    value_counts = Counter(values)

    results = []
    for category, quantity in sorted(
        value_counts.items(),
        key=lambda item: (-item[1], item[0]),
    ):
        results.append(
            {
                result_field_name: category,
                "cantidad": quantity,
            }
        )

    return results


def sum_donations_by_campaign(
    donations_dataframe: pd.DataFrame,
) -> list[dict[str, Any]]:
    """Suma el valor de las donaciones agrupandolas por campana."""
    required_columns = {"campana_titulo", "montoTotal"}
    if not required_columns.issubset(donations_dataframe.columns):
        return []

    valid_donations = donations_dataframe[
        ["campana_titulo", "montoTotal"]
    ].copy()
    valid_donations["montoTotal"] = pd.to_numeric(
        valid_donations["montoTotal"],
        errors="coerce",
    )
    valid_donations = valid_donations.dropna(
        subset=["campana_titulo", "montoTotal"],
    )

    grouped_donations = valid_donations.groupby(
        "campana_titulo",
        as_index=False,
    )["montoTotal"].sum()
    grouped_donations = grouped_donations.sort_values(
        by="montoTotal",
        ascending=False,
    )

    results = []
    for _, donation in grouped_donations.iterrows():
        results.append(
            {
                "campana": donation["campana_titulo"],
                "total": round(float(donation["montoTotal"]), 2),
            }
        )

    return results


def build_metadata(
    dataframes: dict[str, pd.DataFrame],
) -> dict[str, int]:
    """Informa cuantos registros quedaron despues de la limpieza."""
    metadata = {}

    for resource_name, dataframe in dataframes.items():
        metadata[f"{resource_name}Procesados"] = len(dataframe)

    return metadata
