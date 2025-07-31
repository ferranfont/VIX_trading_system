import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import webbrowser

def strat_vix_entry_from_tops(df, tops_df, atr_window=14, atr_multiplier_stop=3):
    df = df.copy()
    forward_days = 30

    if not isinstance(df.index, pd.DatetimeIndex):
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
        else:
            raise ValueError("El DataFrame debe tener una columna 'date' o índice datetime.")

    if not all(col in df.columns for col in ['sp500', 'parabolic_sar']):
        raise ValueError("Faltan columnas necesarias: 'sp500' y/o 'parabolic_sar'")

    if 'atr_sp500' not in df.columns:
        df['close_diff'] = df['sp500'].diff().abs()
        df['atr_sp500'] = df['close_diff'].rolling(window=atr_window).mean()

    records = []

    for _, row in tops_df.iterrows():
        date_entry = pd.to_datetime(row['top_confirm'])
        if date_entry not in df.index:
            continue

        entry_price = df.loc[date_entry, 'sp500']
        atr_val = df.loc[date_entry, 'atr_sp500']
        if np.isnan(entry_price) or np.isnan(atr_val):
            continue

        stop_loss = entry_price - atr_multiplier_stop * atr_val

        future_window = df.loc[date_entry:].iloc[1:forward_days+1]
        sar_below_started = False
        outcome, exit_price, exit_date = None, None, None

        for future_date, row_future in future_window.iterrows():
            price = row_future['sp500']
            sar = row_future['parabolic_sar']

            if price <= stop_loss:
                outcome = 'stop'
                exit_price = stop_loss
                exit_date = future_date
                break

            if sar < price:
                sar_below_started = True
            elif sar_below_started and price < sar:
                outcome = 'target'
                exit_price = price
                exit_date = future_date
                break

        if outcome is None:
            continue

        profit_points = exit_price - entry_price
        profit_usd = profit_points * 50

        records.append({
            'entry_date': date_entry,
            'entry_price': round(entry_price, 2),
            'stop_loss': round(stop_loss, 2),
            'exit_date': exit_date,
            'exit_price': round(exit_price, 2),
            'outcome': outcome,
            'profit_points': round(profit_points, 2),
            'profit_usd': round(profit_usd, 2),
            'VIX_top_value': row['VIX_top'],
            'VIX_top_date': pd.to_datetime(row['index_top_pos']),
        })

    result_df = pd.DataFrame(records)
    result_df['equity_usd'] = result_df['profit_usd'].cumsum()

    print("\n📊 Tracking Record Summary:")
    print(result_df[['entry_date', 'entry_price', 'exit_date', 'exit_price', 'outcome', 'profit_points', 'profit_usd']])

    total = len(result_df)
    wins = (result_df['outcome'] == 'target').sum()
    losses = (result_df['outcome'] == 'stop').sum()
    winrate = (wins / total) * 100 if total > 0 else 0
    avg_win = result_df[result_df['outcome'] == 'target']['profit_usd'].mean()
    avg_loss = result_df[result_df['outcome'] == 'stop']['profit_usd'].mean()
    profit_ratio = abs(avg_win / avg_loss) if avg_loss else np.nan
    total_usd = result_df['profit_usd'].sum()

    print(f"\n✅ Total trades: {total}")
    print(f"🎯 Targets hit (SAR exit): {wins}")
    print(f"🛑 Stops hit: {losses}")
    print(f"📈 Winrate: {winrate:.2f}%")
    print(f"📊 Avg Win: {avg_win:.2f} USD")
    print(f"📉 Avg Loss: {avg_loss:.2f} USD")
    print(f"📊 Profit Ratio: {profit_ratio:.2f}")
    print(f"💰 Total Profit: {total_usd:.2f} USD")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=result_df['exit_date'],
        y=result_df['equity_usd'],
        fill='tozeroy',
        mode='lines',
        line=dict(color='green'),
        name='Equity Curve',
        hovertemplate='Date: %{x}<br>Equity: %{y:.2f} USD<extra></extra>'
    ))
    fig.update_layout(
        title='💵 Cumulative Profit Curve (PSAR Confirmed Exit)',
        xaxis_title='Exit Date',
        yaxis_title='Equity in USD',
        template='plotly_white',
        height=500,
        width=900
    )

    output_path = 'charts/equity_curve_psar_confirmed.html'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.write_html(output_path)
    webbrowser.open('file://' + os.path.realpath(output_path))

    return result_df
