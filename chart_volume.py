# FILE: chart_volume.py
# FINAL CORRECTED VERSION

import os
import webbrowser
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots

def plot_nasdaq_and_vix(symbol, timeframe, df, tops_df=None, trades_df=None):
    html_path = f'charts/nasdaq_vix_chart_{symbol}_{timeframe}.html'
    os.makedirs(os.path.dirname(html_path), exist_ok=True)

    df = df.rename(columns=str.lower)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    # =================================================================================
    # === FINAL FIX: Plot the stop ONLY when it is VALID (below the price)          ===
    # =================================================================================
    if trades_df is not None and not trades_df.empty and 'atr_trailing_stop' in df.columns:
        # Start with a new column full of NaNs
        df['active_atr_stop'] = np.nan
        
        # For each trade, we'll apply the new plotting rule
        for _, trade in trades_df.iterrows():
            if pd.notna(trade['exit_date']) and pd.notna(trade['entry_date']):
                # 1. Identify the time window for the current trade.
                mask = (df['date'] >= trade['entry_date']) & (df['date'] <= trade['exit_date'])
                
                # 2. Get the series for the price and the stop within this window
                prices_in_window = df.loc[mask, 'nasdaq']
                stops_in_window = df.loc[mask, 'atr_trailing_stop']

                # 3. **THE FIX**: Use .where() to keep the stop value only if it's
                #    less than or equal to the price. Otherwise, replace it with NaN.
                #    This prevents the green line from ever being drawn above the blue line.
                valid_stops = stops_in_window.where(stops_in_window <= prices_in_window, np.nan)
                
                # 4. Assign these "cleaned" stops to our plotting column
                df.loc[mask, 'active_atr_stop'] = valid_stops
    # =================================================================================

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.80, 0.20],
        vertical_spacing=0.03,
        specs=[[{"secondary_y": True}], [{}]]
    )

    # --- NASDAQ Price Line ---
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['nasdaq'], mode='lines', name='NASDAQ',
        line=dict(color='blue', width=1.5)
    ), row=1, col=1, secondary_y=False)

    '''
    # --- NASDAQ EMA Line ---
    if 'ema' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['date'], y=df['ema'], mode='lines', name='EMA',
            line=dict(color='green', width=0.5)
        ), row=1, col=1, secondary_y=False)
    '''        
    # --- ATR Trailing Stop Line (using our correctly filtered column) ---
    if 'active_atr_stop' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['date'], y=df['active_atr_stop'], mode='lines',
            name='ATR Trailing Stop',
            line=dict(color='green', width=1.5, dash='solid'),
            connectgaps=False, # Ensures NaNs create breaks in the line
            hovertemplate='Date: %{x}<br>ATR Stop: %{y:.2f}<extra></extra>'
        ), row=1, col=1, secondary_y=False)
    
    # --- Entry Signals (Triangles) ---
    if trades_df is not None and not trades_df.empty:
        fig.add_trace(go.Scatter(
            x=trades_df['entry_date'], y=trades_df['entry_price'], mode='markers', name='Entry Signal',
            marker=dict(symbol='triangle-up', size=12, color='green', line=dict(width=1, color='darkgreen')),
            hovertemplate='Entry Date: %{x}<br>Entry Price: %{y}<extra></extra>'
        ), row=1, col=1, secondary_y=False)

    # --- VIX Line ---
    if 'vix' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['date'], y=df['vix'], mode='lines', name='VIX',
            line=dict(color='red', width=1.2)
        ), row=1, col=1, secondary_y=True)

    # --- Volume Bars ---
    if 'nasdaq_volume_m' in df.columns:
        fig.add_trace(go.Bar(
            x=df['date'], y=df['nasdaq_volume_m'],
            marker_color='blue', name='NASDAQ Volume (M)'
        ), row=2, col=1)

    # --- Trade Exit Markers (Squares) with Profit/Loss Coloring ---
    if trades_df is not None and not trades_df.empty:
        for _, trade in trades_df.iterrows():
            color = 'green' if trade['profit_usd'] > 0 else 'red'
            fig.add_trace(go.Scatter(
                x=[trade['exit_date']], y=[trade['exit_price']], mode='markers',
                marker=dict(symbol='square', size=8, color=color, line=dict(width=1, color='black')),
                showlegend=False,
                hovertemplate=f"Exit: {trade['exit_price']:.2f}<br>P/L: {trade['profit_usd']:.2f} USD<extra></extra>"
            ), row=1, col=1, secondary_y=False)
            fig.add_trace(go.Scatter(
                x=[trade['entry_date'], trade['exit_date']], y=[trade['entry_price'], trade['exit_price']],
                mode='lines', line=dict(color='gray', width=1), showlegend=False
            ), row=1, col=1, secondary_y=False)

    # --- VIX Tops ---
    if tops_df is not None and not tops_df.empty:
        fig.add_trace(go.Scatter(
            x=tops_df['index_top_pos'], y=tops_df['VIX_top'], mode='markers', name='VIX Tops',
            marker=dict(symbol='circle', size=6, color='red', line=dict(width=1, color='darkred')),
        ), row=1, col=1, secondary_y=True)

    # --- Axes and Layout ---
    fig.update_xaxes(type='date', tickformat="%b %d<br>%Y", row=1, col=1)
    fig.update_xaxes(range=[df['date'].min(), df['date'].max()])
    fig.update_yaxes(title_text="NASDAQ", row=1, col=1, secondary_y=False)
    fig.update_yaxes(title_text="VIX", row=1, col=1, secondary_y=True, showgrid=False)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    fig.update_layout(
        title=f'NASDAQ + VIX & Volume — {symbol} {timeframe}', width=1700, height=800,
        template='plotly_white', showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5)
    )

    fig.write_html(html_path, config={"scrollZoom": True})
    print(f"✅ Plotly chart saved as HTML: '{html_path}'")
    webbrowser.open('file://' + os.path.realpath(html_path))