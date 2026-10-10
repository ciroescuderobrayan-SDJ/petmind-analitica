import pandas as pd


def combinar_datos(datos: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Une cada favorito con los datos del usuario que lo marcó."""
    return pd.merge(
        datos["favorite"], datos["user"], left_on="id_user", right_on="id"
    )
