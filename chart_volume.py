import os
import webbrowser
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

def plot_sp500_and_vix(symbol, timeframe, df, tops_df=None, trades_df=None):
    html_path = f'charts/sp500_vix_chart_{symbol}_{timeframe}.html'
    os.makedirs(os.path.dirname(html_path), exist_ok=True)

    df = df.rename(columns=str.lower)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.80, 0.20],
        vertical_spacing=0.03,
        specs=[[{"secondary_y": True}], [{}]]
    )

    # === Línea del SP500 (línea principal azul)
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['sp500'],
        mode='lines',
        name='SP500',
        line=dict(color='blue', width=1.5)
    ), row=1, col=1, secondary_y=False)

    # === Línea del EMA del SP500
    fig.add_trace(go.Scatter(
        x=df['date'],
        y= df['ema'],
        mode='lines',
        name='SP500',
        line=dict(color='green', width=0.5)
    ), row=1, col=1, secondary_y=False)

    # === Parabolic SAR (como puntos pequeños)
    if 'parabolic_sar' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['parabolic_sar'],
            mode='markers',
            name='Parabolic SAR',
            marker=dict(
                symbol='circle',
                size=2,
                color='grey',
                line=dict(width=0)
            ),
            hovertemplate='Date: %{x}<br>SAR: %{y}<extra></extra>'
        ), row=1, col=1, secondary_y=False)
   

    # 🔺 Flechas verdes en puntos de entrada (entry_date, entry_price)
    if trades_df is not None and not trades_df.empty:
        fig.add_trace(go.Scatter(
            x=trades_df['entry_date'],
            y=trades_df['entry_price'],
            mode='markers',
            name='Entry Signal',
            marker=dict(
                symbol='triangle-up',
                size=12,
                color='green',
                line=dict(width=1, color='darkgreen')
            ),
            hovertemplate='Entry Date: %{x}<br>Entry Price: %{y}<extra></extra>'
        ), row=1, col=1, secondary_y=False)


    # === Línea del VIX (eje derecho)
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['vix'],
        mode='lines',
        name='VIX',
        line=dict(color='red', width=1.2)
    ), row=1, col=1, secondary_y=True)
    
    '''
    # === Línea del ATR del VIX
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['atr'],
        mode='lines',
        name='vix_trigger_high',
        line=dict(color='green', width=1, dash='dot')
    ), row=1, col=1, secondary_y=True)
    '''

    # === Volumen SP500
    if 'sp500_volume_m' in df.columns:
        fig.add_trace(go.Bar(
            x=df['date'],
            y=df['sp500_volume_m'],
            marker_color='rgba(0, 0, 255, 0.4)',
            marker_line_color='blue',
            marker_line_width=0.4,
            opacity=0.8,
            name='Volumen SP500 (M)'
        ), row=2, col=1)

    # === Marcas de entrada/salida del sistema
    if trades_df is not None and not trades_df.empty:
        for _, trade in trades_df.iterrows():
            color = 'green' if trade['outcome'] == 'target' else 'red'
            fig.add_trace(go.Scatter(
                x=[trade['exit_date']],
                y=[trade['exit_price']],
                mode='markers',
                marker=dict(symbol='square', size=6, color=color, line=dict(width=2, color=color)),
                showlegend=False
            ), row=1, col=1, secondary_y=False)

            fig.add_trace(go.Scatter(
                x=[trade['entry_date'], trade['exit_date']],
                y=[trade['entry_price'], trade['exit_price']],
                mode='lines',
                line=dict(color='gray', width=1),
                showlegend=False
            ), row=1, col=1, secondary_y=False)

    # === Picos confirmados del VIX
    if tops_df is not None and not tops_df.empty:
        fig.add_trace(go.Scatter(
            x=tops_df['index_top_pos'],
            y=tops_df['VIX_top'],
            mode='markers',
            name='VIX Tops',
            marker=dict(symbol='circle', size=6, color='red', line=dict(width=1, color='darkred')),
        ), row=1, col=1, secondary_y=True)

    # === Ejes X y Y
    fig.update_xaxes(
        type='date',
        tickformat="%b %d<br>%Y",
        tickangle=0,
        showgrid=False,
        linecolor='gray',
        linewidth=1,
        range=[df['date'].min(), df['date'].max()],
        row=1, col=1
    )
    fig.update_xaxes(
        tickformat="%b %d<br>%Y",
        tickangle=45,
        showgrid=False,
        linecolor='gray',
        linewidth=1,
        row=2, col=1
    )
    fig.update_yaxes(
        title_text="SP500",
        row=1, col=1, secondary_y=False,
        showgrid=True,  # Muestra la cuadrícula en eje izquierdo
        linecolor='gray',
        linewidth=1
    )
    fig.update_yaxes(
        title_text="VIX",
        row=1, col=1, secondary_y=True,
        showgrid=False,  # ❌ Oculta cuadrícula horizontal del eje derecho
        linecolor='gray',
        linewidth=1
    )

    fig.update_yaxes(title_text="Volumen", row=2, col=1)

    # === Layout Final
    fig.update_layout(
        title=f'SP500 + VIX & Volume — {symbol} {timeframe}',
        width=1700,
        height=800,
        margin=dict(l=20, r=20, t=60, b=20),
        font=dict(size=12),
        plot_bgcolor='rgba(255,255,255,0.05)',
        paper_bgcolor='rgba(240,240,240,0.1)',
        template='plotly_white',
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5,
            bgcolor='rgba(255,255,255,0.7)',
            bordercolor='gray',
            borderwidth=1
        )
    )

    fig.write_html(html_path, config={"scrollZoom": True})
    print(f"✅ Gráfico Plotly guardado como HTML: '{html_path}'")
    webbrowser.open('file://' + os.path.realpath(html_path))
