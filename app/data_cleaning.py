from typing import Any

import pandas as pd


def convert_resources_to_dataframes(
    resources: dict[str, list[dict[str, Any]]],
) -> dict[str, pd.DataFrame]:
    """Convierte cada coleccion JSON del backend en un DataFrame."""
    dataframes = {}

    for resource_name, records in resources.items():
        # json_normalize separa los objetos anidados con "_".
        # Ejemplo: mascota.especie se convierte en mascota_especie.
        dataframes[resource_name] = pd.json_normalize(
            records,
            sep="_",
        )

    return dataframes


def clean_dataframes(
    dataframes: dict[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:
    """Limpia todos los DataFrames antes de calcular las graficas."""
    cleaned_dataframes = {}

    for resource_name, dataframe in dataframes.items():
        cleaned_dataframe = clean_empty_values(dataframe)
        cleaned_dataframe = clean_text_columns(cleaned_dataframe)
        cleaned_dataframe = remove_technical_columns(cleaned_dataframe)
        cleaned_dataframe = remove_duplicate_rows(cleaned_dataframe)

        cleaned_dataframes[resource_name] = cleaned_dataframe

    return cleaned_dataframes


def clean_empty_values(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Convierte textos vacios en nulos y elimina filas totalmente vacias."""
    cleaned_dataframe = dataframe.copy()

    cleaned_dataframe = cleaned_dataframe.replace(
        r"^\s*$",
        pd.NA,
        regex=True,
    )
    cleaned_dataframe = cleaned_dataframe.dropna(how="all")

    return cleaned_dataframe


def clean_text_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Quita espacios innecesarios y normaliza los textos."""
    cleaned_dataframe = dataframe.copy()
    text_columns = cleaned_dataframe.select_dtypes(
        include=["object", "string"],
    ).columns

    for column_name in text_columns:
        cleaned_dataframe[column_name] = cleaned_dataframe[column_name].map(
            normalize_text_value,
        )

    return cleaned_dataframe


def normalize_text_value(value: Any) -> Any:
    """Normaliza un valor de texto sin modificar numeros ni nulos."""
    if isinstance(value, str):
        return " ".join(value.strip().lower().split())

    return value


def remove_technical_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Elimina campos internos de Hibernate que no sirven para las graficas."""
    technical_columns = [
        column_name
        for column_name in dataframe.columns
        if "hibernateLazyInitializer" in column_name
    ]

    return dataframe.drop(columns=technical_columns, errors="ignore")


def remove_duplicate_rows(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Elimina registros repetidos y reinicia el indice del DataFrame."""
    return dataframe.drop_duplicates().reset_index(drop=True)
