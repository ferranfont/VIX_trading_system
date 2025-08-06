import pandas as pd
import numpy as np

def generate_ema_short_hedging_signals(df):
    """
    Estrategia de cobertura basada en cruce estricto de medias (Close cruza la EMA lenta hacia abajo).
    Cierre de la posición cuando la EMA rápida cruza hacia arriba la EMA lenta o el precio toca el stop loss.

    Returns:
        pd.DataFrame: Registro de operaciones con entradas/salidas y beneficios.
    """
    atr_multiplier = 0.5

    required_cols = ['nasdaq', 'sma_fast', 'sma_slow', 'nasdaq_atr']
    if not all(col in df.columns for col in required_cols):
        raise ValueError(f"El DataFrame debe contener las columnas: {required_cols}")

    records = []
    in_trade = False
    entry_price = entry_date = stop_loss = None

    for i in range(1, len(df)):
        row_prev = df.iloc[i - 1]
        row = df.iloc[i]

        # Entrada: close cruza la slow EMA
        if not in_trade:
            if row_prev['nasdaq'] > row_prev['sma_slow'] and row['nasdaq'] < row['sma_slow']:
                in_trade = True
                entry_date = row.name
                entry_price = row['nasdaq']
                stop_loss = entry_price + (atr_multiplier * row['nasdaq_atr'])

        else:
            stop_hit = 'high_nasdaq' in df.columns and row['high_nasdaq'] > stop_loss
            cross_exit = row_prev['sma_fast'] < row_prev['sma_slow'] and row['sma_fast'] > row['sma_slow']

            if stop_hit or cross_exit:
                exit_price = stop_loss if stop_hit else row['nasdaq']
                exit_date = row.name

                profit_points = entry_price - exit_price
                profit_usd = profit_points * 50
                return_pct = profit_points / entry_price if entry_price != 0 else 0

                records.append({
                    'hedge_entry_date': entry_date,
                    'hedge_entry_price': round(entry_price, 2),
                    'hedge_exit_date': exit_date,
                    'hedge_exit_price': round(exit_price, 2),
                    'hedge_profit_usd': round(profit_usd, 2),
                    'hedge_return_pct': round(return_pct, 4)
                })

                in_trade = False
                entry_price = entry_date = stop_loss = None

    df_signals = pd.DataFrame(records)

    if not df_signals.empty:
        print(f"\n\u2705 Total Profit Hedge (Slow EMA): ${df_signals['hedge_profit_usd'].sum():,.2f}")
    else:
        print("\nNo hedge trades were generated with EMA slow strategy.")

    return df_signals
