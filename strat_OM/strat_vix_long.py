# FILE: strat_OM/strat_vix_long.py
# FINAL VERSION: Includes a "synced" benchmark starting from the strategy's level in Jan 2022.

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import webbrowser

def strat_vix_entry_from_tops(df, tops_df):
    """
    Executes the trading strategy and generates TWO performance charts:
    1. Absolute cumulative profit in USD.
    2. Percentage-based cumulative return vs. TWO NASDAQ benchmarks, with one
       benchmark synced to the strategy's performance level at a fixed date.
    """

    atr_factor = 3
    df = df.copy()

    # --- Input Validation and Trade Simulation (This logic is correct and final) ---
    required_cols = ['nasdaq', 'high_nasdaq', 'low_nasdaq', 'atr_trailing_stop', 'nasdaq_atr']
    if not all(col in df.columns for col in required_cols):
        raise ValueError(f"DataFrame is missing required columns. Ensure it has: {required_cols}")
    records = []
    for _, top_row in tops_df.iterrows():
        date_entry = pd.to_datetime(top_row['top_confirm'])
        if date_entry not in df.index or pd.isna(df.loc[date_entry, 'nasdaq_atr']):
            continue
        entry_price = df.loc[date_entry, 'nasdaq']
        initial_nasdaq_atr = df.loc[date_entry, 'nasdaq_atr']
        fixed_stop = entry_price - (atr_factor * initial_nasdaq_atr)
        use_trailing_stop = False
        outcome, exit_price, exit_date = 'open', None, None
        trade_window = df.loc[date_entry:].iloc[1:]
        for future_date, future_row in trade_window.iterrows():
            current_low, current_close = future_row['low_nasdaq'], future_row['nasdaq']
            dynamic_stop_level = future_row['atr_trailing_stop']
            if use_trailing_stop:
                if current_low < dynamic_stop_level:
                    outcome, exit_price, exit_date = 'stop_trail', dynamic_stop_level, future_date
                    break
            else:
                if current_low < fixed_stop:
                    outcome, exit_price, exit_date = 'stop_fixed', fixed_stop, future_date
                    break
            if not use_trailing_stop and pd.notna(dynamic_stop_level) and current_close > dynamic_stop_level:
                use_trailing_stop = True
        if outcome == 'open':
            exit_date = trade_window.index[-1] if not trade_window.empty else date_entry
            exit_price = trade_window['nasdaq'][-1] if not trade_window.empty else entry_price
        profit_points = exit_price - entry_price
        profit_usd = profit_points * 50
        return_pct = (exit_price - entry_price) / entry_price if entry_price != 0 else 0
        records.append({
            'entry_date': date_entry, 'entry_price': round(entry_price, 2),
            'exit_date': exit_date, 'exit_price': round(exit_price, 2),
            'outcome': outcome, 'profit_points': round(profit_points, 2), 
            'profit_usd': round(profit_usd, 2), 'return_pct': return_pct
        })
    result_df = pd.DataFrame(records)
    if result_df.empty:
        print("No trades were generated. No performance charts to display.")
        return result_df

    # --- Performance Calculations ---
    result_df['equity_usd'] = result_df['profit_usd'].cumsum()
    result_df['equity_pct'] = (1 + result_df['return_pct']).cumprod() - 1
    
    # Benchmark 1: Starts on the same day as the first trade
    start_date = result_df['entry_date'].min()
    benchmark_df = df[df.index >= start_date].copy()
    initial_nasdaq_price = benchmark_df['nasdaq'].iloc[0]
    benchmark_df['benchmark_return_pct'] = (benchmark_df['nasdaq'] - initial_nasdaq_price) / initial_nasdaq_price

    # =========================================================================
    # === NEW: Calculate Benchmark 2, synced to the strategy's level in 2022 ===
    # =========================================================================
    fixed_start_date = pd.to_datetime('2022-01-01')
    benchmark_2022_df = df[df.index >= fixed_start_date].copy()
    if not benchmark_2022_df.empty:
        # Step 1: Find the strategy's return level on the benchmark start date
        strategy_at_benchmark_start_df = result_df[result_df['exit_date'] <= fixed_start_date]
        if not strategy_at_benchmark_start_df.empty:
            # This is the starting offset for our new benchmark line
            strategy_return_offset = strategy_at_benchmark_start_df.iloc[-1]['equity_pct']
        else:
            # If the strategy hasn't started yet, the offset is 0
            strategy_return_offset = 0

        # Step 2: Calculate the benchmark's own return from its start date
        initial_price_2022 = benchmark_2022_df['nasdaq'].iloc[0]
        benchmark_2022_df['benchmark_own_return'] = (benchmark_2022_df['nasdaq'] - initial_price_2022) / initial_price_2022
        
        # Step 3: Add the strategy's historical return to the benchmark's own return
        # This shifts the entire benchmark curve up to the correct starting level.
        benchmark_2022_df['benchmark_synced_return'] = strategy_return_offset + benchmark_2022_df['benchmark_own_return']

    # --- Reporting (No changes needed) ---
    print("\n📊 Tracking Record Summary:")
    result_df_display = result_df.copy()
    result_df_display['return_pct'] = result_df_display['return_pct'].apply(lambda x: f"{x:.2%}")
    print(result_df_display[['entry_date', 'exit_date', 'outcome', 'profit_usd', 'return_pct']])
    closed_trades = result_df[result_df['outcome'] != 'open']
    total = len(closed_trades)
    wins = (closed_trades['profit_usd'] > 0).sum()
    losses = (closed_trades['profit_usd'] <= 0).sum()
    winrate = (wins / total) * 100 if total > 0 else 0
    avg_win = closed_trades[closed_trades['profit_usd'] > 0]['profit_usd'].mean()
    avg_loss = closed_trades[closed_trades['profit_usd'] <= 0]['profit_usd'].mean()
    profit_ratio = abs(avg_win / avg_loss) if not pd.isna(avg_loss) and avg_loss != 0 else np.nan
    total_usd = closed_trades['profit_usd'].sum()
    print(f"\n--- Performance on Closed Trades Only ---")
    print(f"✅ Total trades closed: {total}\n📈 Wins: {wins}\n📉 Losses: {losses}")
    print(f"🎯 Winrate: {winrate:.2f}%\n💰 Avg Win: {avg_win:.2f} USD\n💸 Avg Loss: {avg_loss:.2f} USD")
    print(f"⚖️ Profit Ratio: {profit_ratio:.2f}\n🏦 Net Profit/Loss: {total_usd:.2f} USD")

    # --- Plotting Section ---

    # Chart 1: Absolute Profit in USD
    fig_usd = go.Figure()
    fig_usd.add_trace(go.Scatter(x=result_df['exit_date'], y=result_df['equity_usd'], fill='tozeroy', mode='lines', line=dict(color='green'), name='Equity Curve (USD)'))
    fig_usd.update_layout(title='💵 Cumulative Profit (Absolute USD)', xaxis_title='Date', yaxis_title='Cumulative Profit (USD)', template='plotly_white', height=800, width=1400)
    path_usd = 'charts/equity_curve_absolute_usd.html'
    fig_usd.write_html(path_usd)
    webbrowser.open('file://' + os.path.realpath(path_usd))
    print(f"✅ Generated Absolute USD equity chart: '{path_usd}'")

    # Chart 2: Percentage Return vs. Both Benchmarks
    fig_pct = go.Figure()
    fig_pct.add_trace(go.Scatter(x=result_df['exit_date'], y=result_df['equity_pct'] * 100, mode='lines', line=dict(color='darkgreen', width=2), name='Strategy Return (%)'))
    fig_pct.add_trace(go.Scatter(x=benchmark_df.index, y=benchmark_df['benchmark_return_pct'] * 100, mode='lines', line=dict(color='grey', width=1.5, dash='solid'), name='NASDAQ (from 1st trade)'))
    if not benchmark_2022_df.empty:
        fig_pct.add_trace(go.Scatter(
            x=benchmark_2022_df.index, 
            y=benchmark_2022_df['benchmark_synced_return'] * 100, # Use the new 'synced' column
            mode='lines', line=dict(color='dodgerblue', width=1.5, dash='solid'), name='NASDAQ (synced to Jan 2022)'
        ))
    fig_pct.update_layout(
        title='📈 Strategy vs. NASDAQ — Cumulative Return (%)', xaxis_title='Date', yaxis_title='Cumulative Return (%)',
        template='plotly_white', height=700, width=1500,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5)
    )
    path_pct = 'charts/equity_curve_percentage.html'
    fig_pct.write_html(path_pct)
    webbrowser.open('file://' + os.path.realpath(path_pct))
    print(f"✅ Generated Percentage Return comparison chart: '{path_pct}'")

    # =========================================================================
    # === NEW: Save the results DataFrame to a CSV file in the 'outputs' folder ===
    # =========================================================================
    output_dir = 'outputs'
    os.makedirs(output_dir, exist_ok=True)  # Create the folder if it doesn't exist
    output_path = os.path.join(output_dir, 'tracking_record_VIX_ONLY_long.csv')
    
    # Save the DataFrame to CSV. `index=False` is good practice unless the index is meaningful.
    result_df.to_csv(output_path, index=False)
    
    print(f"💾 Strategy returns DataFrame saved to: '{output_path}'")
        
    return result_df