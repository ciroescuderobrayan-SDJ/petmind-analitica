import pandas as pd


COLUMNAS_USUARIO = ["id_user", "name", "last_name", "email", "city"]


def combinar_datos(datos: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Une cada favorito con los datos del usuario que lo marcó."""
    # Se renombran los "id" para que no choquen: en user es el id del usuario
    # y en favorite es el id del favorito.
    usuarios = datos["user"].rename(columns={"id": "id_user"})
    favoritos = datos["favorite"].rename(columns={"id": "id_favorite"})

    # La contraseña y las fechas no se necesitan para el análisis.
    usuarios = usuarios[COLUMNAS_USUARIO]

    # how="inner" deja solo los favoritos cuyo usuario existe en user.
    # validate="many_to_one": un usuario puede tener muchos favoritos,
    # pero cada favorito pertenece a un solo usuario.
    datos_combinados = pd.merge(
        favoritos,
        usuarios,
        on="id_user",
        how="inner",
        validate="many_to_one",
    )

    print(
        "Datos combinados correctamente. "
        f"Favoritos con usuario válido: {len(datos_combinados)} "
        f"de {len(favoritos)}."
    )

    return datos_combinados
