import pandas as pd
import numpy as np

def strat_hedging_cross(df, fast_ma_col: str, slow_ma_col: str):
    """
    Ejecuta una estrategia de cobertura basada en cruce de medias móviles.

    Args:
        df (pd.DataFrame): DataFrame que contiene el precio (columna 'nasdaq') y las medias.
        fast_ma_col (str): Nombre de la media móvil rápida.
        slow_ma_col (str): Nombre de la media móvil lenta.

    Returns:
        pd.DataFrame: Registro detallado de operaciones de cobertura.
    """
    print("\n" + "="*150)
    print(f"📈 Ejecutando la estrategia de cobertura (Hedging) con '{fast_ma_col}' vs '{slow_ma_col}'...")
    print("="*150)

    required_cols = ['nasdaq', fast_ma_col, slow_ma_col]
    if not all(col in df.columns for col in required_cols):
        raise ValueError(f"El DataFrame debe contener las columnas: {required_cols}")
    
    df_hedge = df.dropna(subset=required_cols).copy()
    df_hedge['position'] = np.where(df_hedge[fast_ma_col] > df_hedge[slow_ma_col], 1, -1)
    df_hedge['signal'] = df_hedge['position'].diff()

    records = []
    in_short = False
    entry_date, entry_price = None, None
    cumulative_equity = 0.0
    initial_capital = 100_000  # opcional: base para equity_pct

    for date, row in df_hedge.iterrows():
        if not in_short and row['signal'] == -2:
            in_short = True
            entry_date = date
            entry_price = row['nasdaq']
            print(f"  -> HEDGE: Entrando en corto el {entry_date.date()} a ${entry_price:.2f}")

        elif in_short and row['signal'] == 2:
            in_short = False
            exit_date = date
            exit_price = row['nasdaq']
            profit_points = entry_price - exit_price
            profit_usd = profit_points * 50
            return_pct = profit_points / entry_price if entry_price != 0 else 0
            cumulative_equity += profit_usd
            equity_pct = cumulative_equity / initial_capital

            records.append({
                'entry_date': entry_date,
                'entry_price': round(entry_price, 2),
                'exit_date': exit_date,
                'exit_price': round(exit_price, 2),
                'outcome': 'hedge',  # para identificar esta estrategia
                'profit_points': round(profit_points, 2),
                'profit_usd': round(profit_usd, 2),
                'return_pct': round(return_pct, 4),
                'equity_usd': round(cumulative_equity, 2),
                'equity_pct': round(equity_pct, 4)
            })


    return pd.DataFrame(records)