import pandas as pd
import numpy as np

def find_vix_quiet_days(df):
    """
    Devuelve una serie booleana que marca únicamente el ÚLTIMO día
    dentro de cada bloque continuo de baja volatilidad (VIX bajo).
    """
    window = 50
    threshold = 0.8

    if 'VIX' not in df.columns:
        raise ValueError("El DataFrame debe contener una columna llamada 'VIX'.")

    vix_mean = df['VIX'].rolling(window=window).mean()
    quiet = df['VIX'] < (threshold * vix_mean)
    quiet = quiet.fillna(False)

    # Identificar los bloques de días tranquilos
    block_id = (quiet != quiet.shift()).cumsum()
    quiet_blocks = quiet.groupby(block_id)

    # Crear serie vacía de mismo índice
    quiet_filtered = pd.Series(False, index=quiet.index)

    for key, group in quiet_blocks:
        if group.iloc[-1]:  # Solo marcar el último día si el grupo es True
            quiet_filtered.loc[group.index[-1]] = True

    return quiet_filtered
