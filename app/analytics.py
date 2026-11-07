from collections import Counter
from typing import Any

import pandas as pd


def build_dashboard(
    cleaned_dataframes: dict[str, pd.DataFrame],
) -> dict[str, Any]:
    """Construye las colecciones que consumira el frontend."""
    pets_dataframe = cleaned_dataframes["mascotas"]
    favorites_dataframe = cleaned_dataframes["favoritos"]
    adoption_requests_dataframe = cleaned_dataframes["solicitudes"]
    donations_dataframe = cleaned_dataframes["donaciones"]
    foundations_dataframe = cleaned_dataframes.get("fundaciones", pd.DataFrame())

    favorites_by_species = count_values(
        pet_species(favorites_dataframe, pets_dataframe),
        "especie",
    )
    adoption_requests_by_species = count_values(
        pet_species(adoption_requests_dataframe, pets_dataframe),
        "especie",
    )
    pets_by_foundation = count_values(
        foundation_names(pets_dataframe, foundations_dataframe),
        "fundacion",
    )
    donations_by_campaign = sum_donations_by_campaign(donations_dataframe)

    return {
        "mascotasPorEspecie": count_column(pets_dataframe, "especie"),
        "mascotasPorEstadoAdopcion": count_column(
            pets_dataframe,
            "estadoAdopcion",
        ),
        "mascotasPorSemana": count_pets_by_week(pets_dataframe),
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


def as_ids(values: pd.Series) -> pd.Series:
    """Convierte una columna de ids en enteros comparables (1, "1" y 1.0 son el mismo id)."""
    return pd.to_numeric(values, errors="coerce").astype("Int64")


def pet_species(
    dataframe: pd.DataFrame,
    pets_dataframe: pd.DataFrame,
) -> pd.Series:
    """
    Especie de la mascota de cada registro (solicitud o favorito).

    Si el backend manda la mascota anidada se usa mascota.especie; si solo manda
    mascotaId, se cruza con la lista de mascotas.
    """
    if "mascota_especie" in dataframe.columns:
        return dataframe["mascota_especie"]

    if "mascotaId" not in dataframe.columns or not {"id", "especie"}.issubset(
        pets_dataframe.columns,
    ):
        return pd.Series(dtype="object")

    species_by_id = dict(
        zip(as_ids(pets_dataframe["id"]), pets_dataframe["especie"]),
    )
    return as_ids(dataframe["mascotaId"]).map(species_by_id)


def foundation_names(
    pets_dataframe: pd.DataFrame,
    foundations_dataframe: pd.DataFrame,
) -> pd.Series:
    """Nombre de la fundacion de cada mascota: anidado o cruzando fundacionId con /api/fundaciones."""
    if "fundacion_nombre" in pets_dataframe.columns:
        return pets_dataframe["fundacion_nombre"]

    if "fundacionId" not in pets_dataframe.columns or not {"id", "nombre"}.issubset(
        foundations_dataframe.columns,
    ):
        return pd.Series(dtype="object")

    names_by_id = dict(
        zip(as_ids(foundations_dataframe["id"]), foundations_dataframe["nombre"]),
    )
    return as_ids(pets_dataframe["fundacionId"]).map(names_by_id)


def count_pets_by_week(pets_dataframe: pd.DataFrame) -> list[dict[str, Any]]:
    """
    Cuenta las mascotas publicadas cada semana (de lunes a domingo).

    Usa la fecha de publicacion y, si no existe, la de creacion. Las semanas sin
    publicaciones quedan en cero para que la serie no salte semanas.
    """
    dates = pd.Series(pd.NaT, index=pets_dataframe.index, dtype="datetime64[ns]")
    for column_name in ("fechaPublicacion", "fechaCreacion"):
        if column_name not in pets_dataframe.columns:
            continue
        # La limpieza pasa los textos a minusculas ("2026-10-30t10:00:00"): basta la parte AAAA-MM-DD.
        parsed = pd.to_datetime(
            pets_dataframe[column_name].astype("string").str[:10],
            format="%Y-%m-%d",
            errors="coerce",
        )
        dates = dates.fillna(parsed)

    dates = dates.dropna()
    if dates.empty:
        return []

    week_starts = dates.dt.to_period("W-SUN").dt.start_time
    counts = week_starts.value_counts().sort_index()
    all_weeks = pd.date_range(counts.index.min(), counts.index.max(), freq="7D")
    counts = counts.reindex(all_weeks, fill_value=0)

    return [
        {"semana": week.strftime("%Y-%m-%d"), "cantidad": int(quantity)}
        for week, quantity in counts.items()
    ]


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


def count_values(
    values: pd.Series,
    result_field_name: str,
) -> list[dict[str, Any]]:
    """Cuenta los valores de una serie (de mayor a menor) y los nombra con result_field_name."""
    clean_values = values.dropna().astype(str).str.upper()
    value_counts = Counter(clean_values)

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


def count_nested_column(
    dataframe: pd.DataFrame,
    column_name: str,
    result_field_name: str,
) -> list[dict[str, Any]]:
    """Cuenta valores de una columna que venia dentro de un objeto anidado."""
    if column_name not in dataframe.columns:
        return []

    return count_values(dataframe[column_name], result_field_name)


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
