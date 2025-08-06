# FILE: strat_OM/hedging_strategy.py
# Este sistema de cobertura abre cortos por el cruce de una media rápida respecto a una corta
# VERSIÓN SIMPLIFICADA: solo salida por STOP FIJO de 2 ATR

import pandas as pd
import numpy as np

def strat_hedging_cross(df: pd.DataFrame, fast_ma_col: str, slow_ma_col: str) -> pd.DataFrame:
    """
    Estrategia de cobertura con:
    - ENTRADA: Cruce de medias (señal -2).
    - SALIDA: Cuando el precio sube y rompe un STOP FIJO de 2 ATR desde el cierre de entrada.
    """
    print("\n" + "="*60)
    print(f"📈 Estrategia de cobertura con STOP FIJO (2 ATR)...")
    print("="*60)

    required_cols = ['nasdaq', 'high_nasdaq', 'nasdaq_atr', fast_ma_col, slow_ma_col]
    if not all(col in df.columns for col in required_cols):
        raise ValueError(f"El DataFrame debe contener las columnas: {required_cols}")

    df_hedge = df.dropna(subset=required_cols).copy()
    df_hedge['position'] = np.where(df_hedge[fast_ma_col] > df_hedge[slow_ma_col], 1, -1)
    df_hedge['signal'] = df_hedge['position'].diff()

    records = []
    in_short = False
    entry_date, entry_price, stop_loss = None, None, None

    for date, row in df_hedge.iterrows():
        # Entrada en corto
        if not in_short and row['signal'] == -2:
            in_short = True
            entry_date = date
            entry_price = row['nasdaq']
            stop_loss = entry_price + (2 * row['nasdaq_atr'])

            print(f"  -> HEDGE: SHORT {entry_date.date()} @ {entry_price:.2f} | STOP: {stop_loss:.2f}")

        # Salida por STOP
        elif in_short:
            if row['high_nasdaq'] > stop_loss:
                exit_date = date
                exit_price = stop_loss
                profit_points = entry_price - exit_price
                profit_usd = profit_points * 50
                return_pct = profit_points / entry_price if entry_price else 0

                records.append({
                    'hedge_entry_date': entry_date,
                    'hedge_entry_price': round(entry_price, 2),
                    'hedge_exit_date': exit_date,
                    'hedge_exit_price': round(exit_price, 2),
                    'hedge_profit_usd': round(profit_usd, 2),
                    'hedge_return_pct': return_pct
                })

                print(f"  -> HEDGE: EXIT {exit_date.date()} @ {exit_price:.2f} | Profit: {profit_usd:,.2f}")
                in_short = False

    if not records:
        print("No se generaron operaciones de cobertura.")
        return pd.DataFrame()

    hedge_trades_df = pd.DataFrame(records)
    total_profit = hedge_trades_df['hedge_profit_usd'].sum()
    print("="*60)
    print(f"✅ Total Profit Hedge: ${total_profit:,.2f}")
    print("="*60)

    return hedge_trades_df
