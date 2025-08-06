# FILE: chart_active_trades.py
import os
import webbrowser
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

def plot_vix_and_price_only(symbol, timeframe, df, tops_df=None):
    """
    Genera un único gráfico con el NASDAQ y el VIX superpuestos, con control de cuadrícula y puntos de picos en ambas curvas.
    """
    # --- 1. Preparación de Datos ---
    df = df.rename(columns=str.lower)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    html_path = f'charts/nasdaq_vix_overlay_{symbol}_{timeframe}.html'
    os.makedirs(os.path.dirname(html_path), exist_ok=True)

    # --- 2. Creación de la Figura con Eje Y Secundario ---
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # --- 3. Añadir las Líneas Principales ---
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['nasdaq'], mode='lines',
        name='NASDAQ', line=dict(color='blue', width=1.5)
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=df['date'], y=df['vix'], mode='lines',
        name='VIX', line=dict(color='red', width=1.2)
    ), secondary_y=True)

    # --- 4. Añadir los Puntos de Señal del DataFrame principal 'df' ---
    if 'vix_spike' in df.columns and df['vix_spike'].any():
        spikes = df[df['vix_spike'] == True]
        fig.add_trace(go.Scatter(
            x=spikes['date'], y=spikes['nasdaq'], mode='markers', name='VIX Low',
            marker=dict(color='orange', size=8, symbol='circle')
        ), secondary_y=False)
        fig.add_trace(go.Scatter(
            x=spikes['date'], y=spikes['vix'], mode='markers', showlegend=False,
            marker=dict(color='orange', size=8, symbol='circle')
        ), secondary_y=True)

    if 'vix_quiet' in df.columns and df['vix_quiet'].any():
        quiet = df[df['vix_quiet'] == True]
        fig.add_trace(go.Scatter(
            x=quiet['date'], y=quiet['nasdaq'], mode='markers', name='VIX Quiet',
            marker=dict(color='red', size=8, symbol='circle')
        ), secondary_y=False)
        fig.add_trace(go.Scatter(
            x=quiet['date'], y=quiet['vix'], mode='markers', showlegend=False,
            marker=dict(color='red', size=8, symbol='circle')
        ), secondary_y=True)

    # --- 5. AÑADIR LOS PUNTOS DE 'tops_df' EN AMBAS CURVAS ---
    if tops_df is not None and not tops_df.empty:
        tops_df['index_top_pos'] = pd.to_datetime(tops_df['index_top_pos'])
        merged_tops = pd.merge(tops_df, df[['date', 'nasdaq']], left_on='index_top_pos', right_on='date', how='inner')

        if not merged_tops.empty:
            # Dibujar los puntos en la curva del VIX (roja)
            fig.add_trace(go.Scatter(
                x=merged_tops['index_top_pos'], 
                y=merged_tops['VIX_top'], 
                mode='markers', 
                name='VIX Tops', 
                ### CAMBIO: Símbolo a 'circle' y tamaño reducido
                marker=dict(symbol='circle', size=7, color='red', line=dict(width=1, color='darkred'))
            ), secondary_y=True)

            # Dibujar los puntos correspondientes en la curva del NASDAQ (azul)
            fig.add_trace(go.Scatter(
                x=merged_tops['index_top_pos'], 
                y=merged_tops['nasdaq'],
                mode='markers', 
                showlegend=False,
                ### CAMBIO: Símbolo a 'circle' y tamaño reducido
                marker=dict(symbol='circle', size=7, color='red', line=dict(width=1, color='darkred'))
            ), secondary_y=False)

    # --- 6. Diseño y Títulos (Layout) ---
    fig.update_layout(
        title_text=f'NASDAQ y VIX — {symbol} {timeframe}',
        width=1700, height=800,
        template='plotly_white',
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5)
    )

    # Configuración de la cuadrícula por eje
    # DESPUÉS (sin negrita)
    fig.update_yaxes(title_text="Nasdaq", color="blue", secondary_y=False, showgrid=True)
    fig.update_yaxes(title_text="VIX", color="red", secondary_y=True, showgrid=False)
    
    ### NUEVO: Ocultar la cuadrícula vertical del eje X
    fig.update_xaxes(showgrid=False)

    # --- 7. Guardar y Mostrar el Gráfico ---
    fig.write_html(html_path, config={"scrollZoom": True})
    print(f"✅ Gráfico Plotly guardado como HTML: '{html_path}'")
    webbrowser.open('file://' + os.path.realpath(html_path))