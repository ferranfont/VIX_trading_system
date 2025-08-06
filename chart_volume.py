# FILE: chart_volume.py
# VERSIÓN ACTUALIZADA: Plotea el ATR Trailing Stop para largos (verde) y para cortos (rojo).

import os
import webbrowser
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots

def plot_nasdaq_and_vix(symbol, timeframe, df, tops_df=None, trades_df=None, hedge_trades_df=None, hedge_trades_df_slow_ema= None):
    html_path = f'charts/nasdaq_vix_chart_{symbol}_{timeframe}.html'
    os.makedirs(os.path.dirname(html_path), exist_ok=True)

    df = df.rename(columns=str.lower)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    # --- Prepara el ATR dinámico para plotear (para la estrategia de LARGOS) ---
    if trades_df is not None and not trades_df.empty and 'atr_trailing_stop' in df.columns:
        df['active_atr_stop'] = np.nan
        for _, trade in trades_df.iterrows():
            if pd.notna(trade['exit_date']) and pd.notna(trade['entry_date']):
                mask = (df['date'] >= trade['entry_date']) & (df['date'] <= trade['exit_date'])
                prices_in_window = df.loc[mask, 'nasdaq']
                stops_in_window = df.loc[mask, 'atr_trailing_stop']
                valid_stops = stops_in_window.where(stops_in_window <= prices_in_window, np.nan)
                df.loc[mask, 'active_atr_stop'] = valid_stops
    
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        row_heights=[0.8, 0.2], vertical_spacing=0.03,
        specs=[[{"secondary_y": True}], [{}]]
    )

    # --- Trazo del Precio y Medias Móviles ---
    fig.add_trace(go.Scatter(x=df['date'], y=df['nasdaq'], mode='lines', name='NASDAQ', line=dict(color='blue', width=1.5)), row=1, col=1)
    if 'sma_slow' in df.columns:
        fig.add_trace(go.Scatter(x=df['date'], y=df['sma_slow'], mode='lines', name='SMA Lenta', line=dict(color='green', width=0.7)), row=1, col=1)
    if 'sma_fast' in df.columns:
        fig.add_trace(go.Scatter(x=df['date'], y=df['sma_fast'], mode='lines', name='SMA Rápida', line=dict(color='turquoise', width=0.9)), row=1, col=1)
    
    # 🔸 Añadir círculos naranjas donde hay picos de VIX (vix_spike == True)
    if 'vix_spike' in df.columns:
        spike_points = df[df['vix_spike'] == True]
        fig.add_trace(go.Scatter(
            x=spike_points['date'],
            y=spike_points['nasdaq'],
            mode='markers',
            name='VIX Spike',
            marker=dict(
                size=7,
                color='orange',
                symbol='circle'
            )
        ), row=1, col=1)

    # 🔸 Añadir círculos naranjas sobre la línea roja del VIX (eje secundario)
    if 'vix_spike' in df.columns:
        spike_points = df[df['vix_spike'] == True]
        fig.add_trace(go.Scatter(
            x=spike_points['date'],
            y=spike_points['vix'],  # Asegúrate que esta columna existe
            mode='markers',
            name='VIX Spike',
            marker=dict(
                size=8,
                color='orange',
                symbol='circle'
            )
        ), row=1, col=1, secondary_y=True)  # 👈 Esto es lo importante


    # --- ATR Trailing Stop Line (para Largos) ---
    if 'active_atr_stop' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['date'], y=df['active_atr_stop'], mode='lines',
            name='ATR Trailing Stop (Long)',
            line=dict(color='green', width=1.5, dash='solid'),
            connectgaps=False
        ), row=1, col=1)
    
    # --- Ploteo de la Estrategia Principal (Largos) ---
    if trades_df is not None and not trades_df.empty:
        fig.add_trace(go.Scatter(x=trades_df['entry_date'], y=trades_df['entry_price'], mode='markers', name='Entrada Largo', marker=dict(symbol='triangle-up', size=12, color='green', line=dict(width=1, color='darkgreen'))), row=1, col=1)
        for _, trade in trades_df.iterrows():
            color = 'green' if trade['profit_usd'] > 0 else 'red'
            fig.add_trace(go.Scatter(x=[trade['exit_date']], y=[trade['exit_price']], mode='markers', marker=dict(symbol='square', size=8, color=color, line=dict(width=1, color='black')), showlegend=False), row=1, col=1)
            fig.add_trace(go.Scatter(x=[trade['entry_date'], trade['exit_date']], y=[trade['entry_price'], trade['exit_price']], mode='lines', line=dict(color='gray', width=1), showlegend=False), row=1, col=1)

    # --- Ploteo de la Estrategia de Cobertura (Cortos) ---
    if hedge_trades_df is not None and not hedge_trades_df.empty:
        fig.add_trace(go.Scatter(x=hedge_trades_df['hedge_entry_date'], y=hedge_trades_df['hedge_entry_price'], mode='markers', name='Entrada Corto (Hedge)', marker=dict(symbol='triangle-down', size=10, color='red', line=dict(width=1, color='darkred'))), row=1, col=1)
        for _, trade in hedge_trades_df.iterrows():
            color = 'green' if trade['hedge_profit_usd'] > 0 else 'red'
            fig.add_trace(go.Scatter(x=[trade['hedge_exit_date']], y=[trade['hedge_exit_price']], mode='markers', marker=dict(symbol='square', size=8, color=color, line=dict(width=1, color='black')), showlegend=False), row=1, col=1)
            fig.add_trace(go.Scatter(x=[trade['hedge_entry_date'], trade['hedge_exit_date']], y=[trade['hedge_entry_price'], trade['hedge_exit_price']], mode='lines', line=dict(color='red', width=1, dash='solid'), showlegend=False), row=1, col=1)
    
    # --- Ploteo de Entradas de Cobertura Corto con Triángulo Invertido Rojo ---
    if hedge_trades_df_slow_ema is not None and not hedge_trades_df_slow_ema.empty:
        fig.add_trace(go.Scatter(
            x=hedge_trades_df_slow_ema['hedge_entry_date'],
            y=hedge_trades_df_slow_ema['hedge_entry_price'],
            mode='markers',
            name='Entrada Corto (Hedge)',
            marker=dict(
                symbol='triangle-down',
                size=10,
                color='red',
                line=dict(width=1, color='darkred')
            )
        ), row=1, col=1)

    # Cuadrados de salida
    for _, trade in hedge_trades_df_slow_ema.iterrows():
        color = 'green' if trade['hedge_profit_usd'] > 0 else 'red'
        fig.add_trace(go.Scatter(
            x=[trade['hedge_exit_date']],
            y=[trade['hedge_exit_price']],
            mode='markers',
            marker=dict(symbol='square', size=10, color=color, line=dict(width=1, color='black')),
            name='Salida Corto (EMA)',
            showlegend=False
        ), row=1, col=1)

        # Línea entre entrada y salida
        fig.add_trace(go.Scatter(
            x=[trade['hedge_entry_date'], trade['hedge_exit_date']],
            y=[trade['hedge_entry_price'], trade['hedge_exit_price']],
            mode='lines',
            line=dict(color='grey', width=1, dash='solid'),
            showlegend=False
        ), row=1, col=1)

    # --- Ploteo de VIX, Volumen y Ejes ---
    if 'vix' in df.columns:
        fig.add_trace(go.Scatter(x=df['date'], y=df['vix'], mode='lines', name='VIX', line=dict(color='red', width=1.2)), row=1, col=1, secondary_y=True)
    if 'nasdaq_volume_m' in df.columns:
        fig.add_trace(go.Bar(x=df['date'], y=df['nasdaq_volume_m'], marker_color='rgba(0, 0, 255, 0.6)', name='NASDAQ Volume (M)'), row=2, col=1)
    if tops_df is not None and not tops_df.empty:
        fig.add_trace(go.Scatter(x=tops_df['index_top_pos'], y=tops_df['VIX_top'], mode='markers', name='VIX Tops', marker=dict(symbol='circle', size=6, color='red', line=dict(width=1, color='darkred'))), row=1, col=1, secondary_y=True)

    fig.update_xaxes(type='date', range=[df['date'].min(), df['date'].max()], showgrid=False)
    fig.update_yaxes(title_text="NASDAQ", row=1, col=1, showgrid=True)
    fig.update_yaxes(title_text="VIX", row=1, col=1, secondary_y=True, showgrid=False)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    fig.update_layout(
        title=f'NASDAQ + VIX & Volume — {symbol} {timeframe}', width=1700, height=800,
        template='plotly_white', showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5)
    )

    fig.write_html(html_path, config={"scrollZoom": True})
    print(f"✅ Gráfico Plotly guardado como HTML: '{html_path}'")
    webbrowser.open('file://' + os.path.realpath(html_path))