# Este código simplemente es una herramienta auxiliar para unir los dos dataframes, el de la estrategia principal y el del hedging
# FILE: strat_OM/strats_outputs_join.py
# COMBINA TODAS LAS ESTRATEGIAS (LONG + HEDGING CROSS + HEDGING EMA)
# en realidad no es una estratagia de cobertura, sino que hace un join o unión de todas las que están activaas
import pandas as pd

def strats_outputs_join(df_long: pd.DataFrame, df_cross: pd.DataFrame, df_ema: pd.DataFrame) -> pd.DataFrame:
    """
    Combina los DataFrames de resultados de todas las estrategias:
    - Estrategia principal (VIX Long)
    - Estrategia de cobertura por cruce de medias (Hedge_Short_Cross)
    - Estrategia de cobertura por cruce de close vs slow EMA (Hedge_Short_EMA)

    Returns:
        pd.DataFrame: Un DataFrame unificado con todas las operaciones.
    """
    final_cols = ['strategy_type', 'entry_date', 'exit_date', 'entry_price', 'exit_price', 'profit_usd']

    # --- Largos ---
    df_long_final = pd.DataFrame(columns=final_cols)
    if df_long is not None and not df_long.empty:
        df_long_clean = df_long.copy()
        df_long_clean['strategy_type'] = 'VIX_Long'
        df_long_final = df_long_clean.rename(columns={
            'entry_date': 'entry_date',
            'exit_date': 'exit_date',
            'entry_price': 'entry_price',
            'exit_price': 'exit_price',
            'profit_usd': 'profit_usd'
        })[final_cols]

    # --- Cortos CROSS ---
    df_cross_final = pd.DataFrame(columns=final_cols)
    if df_cross is not None and not df_cross.empty:
        df_cross_clean = df_cross.copy()
        df_cross_clean['strategy_type'] = 'Hedge_Short_Cross'
        df_cross_final = df_cross_clean.rename(columns={
            'hedge_entry_date': 'entry_date',
            'hedge_exit_date': 'exit_date',
            'hedge_entry_price': 'entry_price',
            'hedge_exit_price': 'exit_price',
            'hedge_profit_usd': 'profit_usd'
        })[final_cols]

    # --- Cortos EMA ---
    df_ema_final = pd.DataFrame(columns=final_cols)
    if df_ema is not None and not df_ema.empty:
        df_ema_clean = df_ema.copy()
        df_ema_clean['strategy_type'] = 'Hedge_Short_EMA'
        df_ema_final = df_ema_clean.rename(columns={
            'hedge_entry_date': 'entry_date',
            'hedge_exit_date': 'exit_date',
            'hedge_entry_price': 'entry_price',
            'hedge_exit_price': 'exit_price',
            'hedge_profit_usd': 'profit_usd'
        })[final_cols]

    # --- Combinar todo ---
    combined = pd.concat([df_long_final, df_cross_final, df_ema_final], ignore_index=True)

    if combined.empty:
        print("\nNo hay operaciones en ninguna de las estrategias para combinar.")
        return pd.DataFrame()

    return combined.sort_values(by='entry_date').reset_index(drop=True)
