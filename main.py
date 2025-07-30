import yfinance as yf
import pandas as pd
from chart_volume import plot_nasdaq_and_vix



# ====================================================
# 📥 CARGA DE DATOS
# ====================================================
directorio = '../DATA'

vix = yf.download('^VIX', start='2020-01-01', end='2025-07-30')
vix = pd.DataFrame(vix)

# Eliminar niveles de columnas si es MultiIndex
if isinstance(vix.columns, pd.MultiIndex):
    vix.columns = vix.columns.droplevel(1)  # Quita 'Price'
    vix.columns.name = None  # Quita el nombre del índice si lo tiene

# Asegurar que sea solo columnas útiles (quita 'Ticker' si estuviera como fila o columna)
vix = vix.drop(columns=['Ticker'], errors='ignore')

# Renombrar columnas a minúsculas
vix.columns = [col.lower() for col in vix.columns]

# Dejar solo la columna 'close' si quieres solo esa
vix = vix[['close']]
vix.rename(columns={'close': 'VIX'}, inplace=True)
# Si 'Date' está como índice
vix.reset_index(inplace=True)
vix.rename(columns={'Date': 'date'}, inplace=True)

# Descarga de datos del SP600 y del NasdaQ
tickers = ['SPY', 'QQQ']
data = yf.download(tickers, start='2020-01-01', end='2025-07-30')

close = data['Close'].rename(columns={'SPY': 'sp500', 'QQQ': 'nasdaq'})
volume = data['Volume'].rename(columns={'SPY': 'sp500_volume_M', 'QQQ': 'nasdaq_volume_M'}) / 1_000_000
close = close.round(2)*10
volume = volume.round(2)

df = pd.concat([close, volume], axis=1)

# Eliminar nombre del eje de columnas
df.columns.name = None

df.reset_index(inplace=True)
df.rename(columns={'Date': 'date'}, inplace=True)

# Unir por la columna 'date'
df = pd.merge(df, vix, on='date', how='left')
df.set_index('date', inplace=True)

# Mostrar resultado
print(df)

df.reset_index(inplace=True)  # esto crea la columna 'date' y elimina del índice
plot_nasdaq_and_vix(symbol='NASDAQ', timeframe='daily', df=df)
