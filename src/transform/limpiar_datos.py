import pandas as pd


def manejar_valores_nulos(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte textos vacíos en nulos y elimina filas sin ningún dato."""
    df_limpio = df.copy()

    # "", "   " y tabulaciones se consideran valores nulos.
    df_limpio = df_limpio.replace(r"^\s*$", pd.NA, regex=True)

    # Solo elimina registros completamente vacíos.
    df_limpio = df_limpio.dropna(how="all")

    return df_limpio


def estandarizar_texto(df: pd.DataFrame) -> pd.DataFrame:
    """Pasa textos a minúsculas y elimina espacios adicionales."""
    df_limpio = df.copy()

    columnas_texto = df_limpio.select_dtypes(
        include=["object", "string"]
    ).columns

    for columna in columnas_texto:
        df_limpio[columna] = df_limpio[columna].map(
            lambda valor: " ".join(valor.strip().lower().split())
            if isinstance(valor, str)
            else valor
        )

    return df_limpio


def limpieza_especifica_petmind(
    nombre_recurso: str, df: pd.DataFrame
) -> pd.DataFrame:
    """
    Elimina registros inválidos según el recurso obtenido por PetMind.
    Solo usa columnas que realmente existan en el DataFrame.
    """
    df_limpio = df.copy()

    campos_obligatorios = {
        "user": ["id", "name", "email"],
        "favorite": ["id", "userId"],
    }

    columnas_existentes = [
        columna
        for columna in campos_obligatorios.get(nombre_recurso, [])
        if columna in df_limpio.columns
    ]

    if columnas_existentes:
        df_limpio = df_limpio.dropna(subset=columnas_existentes)

    # Un correo debe conservarse en minúsculas.
    if nombre_recurso == "user" and "email" in df_limpio.columns:
        df_limpio["email"] = df_limpio["email"].str.lower().str.strip()

    return df_limpio


def limpiar_datos(datos: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Limpia todos los DataFrames cargados desde la API."""
    datos_limpios = {}

    for nombre, df in datos.items():
        if not isinstance(df, pd.DataFrame):
            print(f'No se pudo limpiar "{nombre}": no es un DataFrame.')
            continue

        cantidad_inicial = len(df)

        df_limpio = manejar_valores_nulos(df)
        df_limpio = estandarizar_texto(df_limpio)
        df_limpio = limpieza_especifica_petmind(nombre, df_limpio)
        df_limpio = df_limpio.drop_duplicates()

        cantidad_eliminada = cantidad_inicial - len(df_limpio)

        print(
            f'Datos de "{nombre}" limpiados. '
            f"Registros eliminados: {cantidad_eliminada}."
        )

        datos_limpios[nombre] = df_limpio

    return datos_limpios