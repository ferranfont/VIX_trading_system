# FILE: main.py
# FINAL CORRECTED VERSION - FIXES THE MERGEERROR

import yfinance as yf
import os
import ta
import pandas as pd
from chart_volume import plot_nasdaq_and_vix
from quant_stat.find_vix_tops import find_vix_tops
from strat_OM.strat_vix_long import strat_vix_entry_from_tops
from strat_OM.strat_ATR_stop_lost import calculate_dynamic_atr_trailing_stop

# ====================================================
# 📅 CARGA DE DATOS SOLO NASDAQ (QQQ)
# ====================================================
directorio = '../DATA'

# --- VIX Data Loading (This part is correct) ---
vix = yf.download('^VIX', start='2020-01-01', end='2025-08-01')
vix = pd.DataFrame(vix)
# This block correctly handles the VIX columns if they are a MultiIndex
if isinstance(vix.columns, pd.MultiIndex):
    vix.columns = vix.columns.droplevel(1)
    vix.columns.name = None
vix = vix.drop(columns=['Ticker'], errors='ignore')
vix.columns = [col.lower() for col in vix.columns]
vix = vix[['close']]
vix.rename(columns={'close': 'VIX'}, inplace=True)
vix.reset_index(inplace=True)
vix.rename(columns={'Date': 'date'}, inplace=True)

# =========================================================================
# === QQQ Data Loading (CORRECTED SECTION TO FIX THE MERGEERROR)        ===
# =========================================================================
data = yf.download(['QQQ'], start='2020-01-01', end='2025-07-30')

# ** THE FIX IS HERE **
# If yfinance returns a MultiIndex (e.g., ('Close', 'QQQ')),
# we flatten it to a single level (e.g., 'Close').
if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.droplevel(1)

# Now that the columns are flattened, we can proceed as before.
df = data[['Close', 'High', 'Low', 'Volume']].copy()
df.rename(columns={
    'Close': 'nasdaq',
    'High': 'high_nasdaq',
    'Low': 'low_nasdaq',
    'Volume': 'nasdaq_volume_M'
}, inplace=True)

# Perform scaling and calculations on the now-correctly-structured DataFrame
df['nasdaq_volume_M'] = df['nasdaq_volume_M'] / 1_000_000
df['nasdaq'] = df['nasdaq'].round(2) * 10
df['high_nasdaq'] = df['high_nasdaq'].round(2) * 10
df['low_nasdaq'] = df['low_nasdaq'].round(2) * 10
df['nasdaq_volume_M'] = df['nasdaq_volume_M'].round(2)

# Unir con VIX
df.reset_index(inplace=True)
df.rename(columns={'Date': 'date'}, inplace=True)
# This merge will now work because both DataFrames have a single column level.
df = pd.merge(df, vix, on='date', how='left')
df.set_index('date', inplace=True)


# ====================================================
# 🧠 CÁLCULO DE INDICADORES (This logic is correct)
# ====================================================
n = 5
p = 100
df['atr'] = df['VIX'].rolling(window=n).mean()
df['EMA'] = df['nasdaq'].rolling(window=p).mean().round(2)

atr_indicator = ta.volatility.AverageTrueRange(
    high=df['high_nasdaq'],
    low=df['low_nasdaq'],
    close=df['nasdaq'],
    window=14
)
df['nasdaq_atr'] = atr_indicator.average_true_range()

psar = ta.trend.PSARIndicator(
    high=df['high_nasdaq'],
    low=df['low_nasdaq'],
    close=df['nasdaq'],
    step=0.01,
    max_step=0.1
)
df['parabolic_sar'] = psar.psar().round(2)
df['atr_trailing_stop'] = calculate_dynamic_atr_trailing_stop(df).round(2)

# ====================================================
# 🔍 FIND VIX TOPS (No changes needed)
# ====================================================
window_top_value = 10
factor_top_value = 1.2
tops_df = pd.DataFrame(find_vix_tops(df.copy(), window_top=window_top_value, factor_top=factor_top_value),
                       columns=['tag', 'index_top_pos', 'VIX_top', 'top_confirm'])

# ====================================================
# 🔍 STRATEGY ORDER MANAGEMENT (No changes needed)
# ====================================================
result = strat_vix_entry_from_tops(df, tops_df)
print(result)

# ====================================================
# 📊 GRAFICACIÓN (No changes needed)
# ====================================================
df.reset_index(inplace=True)
plot_nasdaq_and_vix(symbol='NASDAQ', timeframe='daily', df=df, tops_df=tops_df, trades_df=result)