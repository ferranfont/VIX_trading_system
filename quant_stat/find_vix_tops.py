import pandas as pd

def find_vix_tops(df, window_top=5, factor_top=1.0):
    """
    Detecta techos relevantes del VIX.

    Criterios:
    - Se detecta un nuevo pico si el valor actual del VIX es al menos `factor_top`
      veces mayor que la media de los últimos `window_top` días.
    - Se confirma un techo cuando el VIX cae por debajo del ATR registrado en el pico.

    Requiere columnas: 'VIX' y 'atr'.
    Devuelve una lista de tuplas con: (tag, fecha_top, valor_top, fecha_confirmación)
    """
    if not all(col in df.columns for col in ['VIX', 'atr']):
        raise ValueError("El DataFrame debe contener las columnas 'VIX' y 'atr'.")

    tops = []
    pending_max = None
    pending_max_i = None

    for i in range(window_top, len(df)):
        current_vix = df['VIX'].iloc[i]
        recent_mean = df['VIX'].iloc[i - window_top:i].mean()

        if pending_max is None:
            if current_vix >= factor_top * recent_mean:
                pending_max = current_vix
                pending_max_i = i
            continue

        if current_vix > pending_max:
            pending_max = current_vix
            pending_max_i = i

        elif current_vix < df['atr'].iloc[pending_max_i]:
            date_top = df.index[pending_max_i]
            date_confirm = df.index[i]
            tops.append(('top', date_top, pending_max, date_confirm))
            pending_max = None
            pending_max_i = None

    return tops
