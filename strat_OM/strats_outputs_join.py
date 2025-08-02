import pandas as pd

def strats_outputs_join(result, hedge_trades_df, capital_inicial=100_000, output_path='outputs/VIX_strat_hedged.csv'):
    """
    Combina dos estrategias: VIX Long y Hedge Short en un solo DataFrame,
    calcula equity acumulada y guarda el resultado como CSV.

    Parameters:
    - result: DataFrame con operaciones de la estrategia VIX Long.
    - hedge_trades_df: DataFrame con operaciones de cobertura.
    - capital_inicial: capital inicial para calcular equity_pct.
    - output_path: ruta donde guardar el CSV final combinado.

    Returns:
    - combined_trades_sorted: DataFrame combinado y enriquecido.
    """

    if result is not None and not result.empty and hedge_trades_df is not None and not hedge_trades_df.empty:
        # Estrategia principal
        df_long = result.copy()
        df_long['strategy_type'] = 'VIX_Long'
        df_long = df_long[['strategy_type', 'entry_date', 'exit_date', 'entry_price', 'exit_price', 'profit_usd']]

        # Estrategia de cobertura
        df_short = hedge_trades_df.copy()
        df_short['strategy_type'] = 'Hedge_Short'
        df_short = df_short[['strategy_type', 'entry_date', 'exit_date', 'entry_price', 'exit_price', 'profit_usd']]

        # Combinar
        combined_trades = pd.concat([df_long, df_short])
        combined_trades_sorted = combined_trades.sort_values(by='entry_date').reset_index(drop=True)

        # Equity acumulada
        combined_trades_sorted['equity_usd'] = combined_trades_sorted['profit_usd'].cumsum()
        combined_trades_sorted['equity_pct'] = combined_trades_sorted['equity_usd'] / capital_inicial

        # Output
        print("\n" + "="*80)
        print("📜 REGISTRO DE OPERACIONES COMBINADO (Estrategia Principal + Cobertura) 📜")
        print("="*80)
        print(combined_trades_sorted)
        print("="*80 + "\n")

        combined_trades_sorted.to_csv(output_path, index=False)
        print(f"💾 Registro combinado de operaciones guardado en: '{output_path}'")

        return combined_trades_sorted

    else:
        print("\n⚠️ No se pudieron combinar los registros de operaciones porque uno o ambos están vacíos.")
        return None
