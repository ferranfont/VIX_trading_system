# FILE: strat_OM/strat_ATR_stop_lost.py
# Usa el ATR para calcular un trailing stop, pero no al inicio que es fijo.
# en realidad no es una estrategia sino un auxiliar para caluclar el atr trailing stop

import pandas as pd
import numpy as np

def calculate_dynamic_atr_trailing_stop(df):
    """
    Calcula el ATR Trailing Stop para posiciones LARGAS.
    Esta función se mantiene sin cambios, ya que es nuestra referencia.
    """
    atr_period=14
    smoothing_period=10
    atr_multiplier=3.5
    method="close"

    high = df['high_nasdaq']
    low = df['low_nasdaq']
    close = df['nasdaq']
    
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low, (high - prev_close).abs(), (low - prev_close).abs()
    ], axis=1).max(axis=1)

    atr = tr.rolling(window=atr_period).mean()
    smoothed_atr = atr.rolling(window=smoothing_period).mean()
    stop_offset = smoothed_atr * atr_multiplier
    
    trailing_stop = [np.nan] * len(df)

    for i in range(1, len(df)):
        price = close.iloc[i]
        prev_price = close.iloc[i-1]
        prev_stop = trailing_stop[i-1]
        
        if pd.isna(stop_offset.iloc[i]):
            trailing_stop[i] = prev_stop
            continue

        if pd.isna(prev_stop):
            new_stop = price - stop_offset.iloc[i]
        else:
            if price > prev_stop and prev_price > prev_stop:
                new_stop = max(prev_stop, price - stop_offset.iloc[i])
            elif price < prev_stop and prev_price < prev_stop:
                new_stop = min(prev_stop, price + stop_offset.iloc[i])
            elif price > prev_stop:
                new_stop = price - stop_offset.iloc[i]
            else:
                new_stop = price + stop_offset.iloc[i]

        trailing_stop[i] = new_stop

    return pd.Series(trailing_stop, index=df.index, name="atr_trailing_stop")


def calculate_short_atr_trailing_stop(df):
    """
    Calcula un ATR Trailing Stop para posiciones CORTAS con una lógica
    simétrica y robusta, reflejando perfectamente la función para largos.
    """
    atr_period=14
    smoothing_period=10
    atr_multiplier=3.5
    
    high = df['high_nasdaq']
    low = df['low_nasdaq']
    close = df['nasdaq']
    
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low, (high - prev_close).abs(), (low - prev_close).abs()
    ], axis=1).max(axis=1)

    atr = tr.rolling(window=atr_period).mean()
    smoothed_atr = atr.rolling(window=smoothing_period).mean()
    stop_offset = smoothed_atr * atr_multiplier
    
    trailing_stop = [np.nan] * len(df)
    
    for i in range(1, len(df)):
        price = close.iloc[i]
        prev_price = close.iloc[i-1]
        prev_stop = trailing_stop[i-1]
        
        if pd.isna(stop_offset.iloc[i]):
            trailing_stop[i] = prev_stop
            continue

        # --- LÓGICA DE TRAILING STOP PARA CORTOS (SIMÉTRICA A LA DE LARGOS) ---
        
        # 1. Inicialización: El stop empieza por encima del precio.
        if pd.isna(prev_stop):
            new_stop = price + stop_offset.iloc[i]
        
        # 2. Lógica de seguimiento y "flipping"
        else:
            # Condición para una tendencia bajista (el precio está por debajo del stop)
            if price < prev_stop and prev_price < prev_stop:
                # El stop se mueve hacia abajo (ratchet). Es el MÍNIMO del stop anterior y el nuevo candidato.
                new_stop = min(prev_stop, price + stop_offset.iloc[i])
            
            # Condición para una tendencia alcista (el precio está por encima del stop)
            elif price > prev_stop and prev_price > prev_stop:
                # El stop ahora actúa como un stop para largos (se mueve hacia arriba)
                new_stop = max(prev_stop, price - stop_offset.iloc[i])
            
            # Condición para un cruce a la baja (inicia una tendencia bajista)
            elif price < prev_stop:
                new_stop = price + stop_offset.iloc[i]
            
            # Condición para un cruce al alza (inicia una tendencia alcista)
            else: # (price > prev_stop)
                new_stop = price - stop_offset.iloc[i]
        
        trailing_stop[i] = new_stop

    return pd.Series(trailing_stop, index=df.index, name="atr_trailing_stop_short")