import os
import webbrowser
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

def plot_nasdaq_and_vix(symbol, timeframe, df, tops_df=None):
    html_path = f'charts/nasdaq_vix_chart_{symbol}_{timeframe}.html'
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

    # Línea del Nasdaq (eje izquierdo)
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['nasdaq'],
        mode='lines',
        name='Nasdaq',
        line=dict(color='blue', width=1.5)
    ), row=1, col=1, secondary_y=False)

    # Flechas de tops confirmados en VIX (sobre Nasdaq, 2 pts por debajo)
    if tops_df is not None and not tops_df.empty:
        top_dates = tops_df['top_confirm']
        top_vix_values = tops_df['top_confirm'].map(df.set_index('date')['nasdaq'])


        fig.add_trace(go.Scatter(
            x=top_dates,
            y=top_vix_values - 2,  # 2 puntos por debajo del Nasdaq en esa fecha
            mode='markers',
            name='Top VIX Marker',
            marker=dict(
                symbol='triangle-up',
                size=12,
                color='green',
                line=dict(width=1, color='darkgreen')
            ),
            hoverinfo='x+y+name'
        ), row=1, col=1, secondary_y=False)

    # Línea del VIX (eje derecho)
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['vix'],
        mode='lines',
        name='VIX',
        line=dict(color='red', width=1.2, dash='solid')
    ), row=1, col=1, secondary_y=True)

    # Línea del VIX (eje derecho)
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['atr'],
        mode='lines',
        name='vix_trigger_high',
        line=dict(color='green', width=1.2, dash='dot')
    ), row=1, col=1, secondary_y=True)

    # Barras de volumen Nasdaq
    fig.add_trace(go.Bar(
        x=df['date'],
        y=df['nasdaq_volume_m'],
        marker_color='rgba(0, 0, 255, 0.4)',
        marker_line_color='blue',
        marker_line_width=0.4,
        opacity=0.8,
        name='Volumen Nasdaq (M)'
    ), row=2, col=1)

    fig.update_layout(
        title=f'NASDAQ + VIX & Volume — {symbol} {timeframe}',
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

    # Línea del VIX (eje derecho)
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['vix'],
        mode='lines',
        name='VIX',
        line=dict(color='red', width=1.2, dash='solid')
    ), row=1, col=1, secondary_y=True)

    # 🔴 Punto rojo sobre la línea del VIX en el máximo pendiente (index_top_pos)
    if tops_df is not None and not tops_df.empty:
        fig.add_trace(go.Scatter(
            x=tops_df['index_top_pos'],
            y=tops_df['VIX_top'],
            mode='markers',
            name='Pending Max VIX',
            marker=dict(
                symbol='circle',
                size=6,
                color='red',
                line=dict(width=1, color='darkred')
            ),
            hoverinfo='x+y+name'
        ), row=1, col=1, secondary_y=True)




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
        title_text="Nasdaq", linecolor='gray', linewidth=1, row=1, col=1, secondary_y=False
    )
    fig.update_yaxes(
        title_text="VIX", linecolor='gray', linewidth=1, row=1, col=1, secondary_y=True
    )
    fig.update_yaxes(
        title_text="Volumen", linecolor='grey', linewidth=1, row=2, col=1
    )

    fig.write_html(html_path, config={"scrollZoom": True})
    print(f"✅ Gráfico Plotly guardado como HTML: '{html_path}'")

    webbrowser.open('file://' + os.path.realpath(html_path))
