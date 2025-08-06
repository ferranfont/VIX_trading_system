# FILE: main.py
import yfinance as yf
import os
import ta
import pandas as pd
import warnings
warnings.filterwarnings("ignore")
from chart_volume import plot_nasdaq_and_vix
from chart_active_trades import plot_vix_and_price_only
from quant_stat.find_vix_tops import find_vix_tops
from quant_stat.vix_spike_indicator import find_vix_quiet_days
from strat_OM.strat_vix_long import strat_vix_entry_from_tops
from strat_OM.strat_ATR_stop_lost import calculate_dynamic_atr_trailing_stop, calculate_short_atr_trailing_stop
from strat_OM.strat_hedging_cross import strat_hedging_cross
from strat_OM.strats_outputs_join import strats_outputs_join
from strat_OM.strat_hedging_ema import generate_ema_short_hedging_signals


hedging_enabled = False                 # Si True se activa el Hedging por cruce de medias
hedging_slow_ema_enable = True         # Si True se actica el Hedging por cruce del Close la slow EMA

# ====================================================
# ⬇️ CÁLCULO DE INDICADORES
# ====================================================
# ... (tu código de yfinance para QQQ y VIX) ...
vix = yf.download('^VIX', start='2020-01-01', end='2025-08-01')

if isinstance(vix.columns, pd.MultiIndex):
    vix.columns = vix.columns.droplevel(1)
vix = vix.drop(columns=['Ticker'], errors='ignore')
vix.columns = [col.lower() for col in vix.columns]
vix.rename(columns={'close': 'VIX'}, inplace=True)
vix.reset_index(inplace=True)
vix.rename(columns={'Date': 'date'}, inplace=True)

data = yf.download(['QQQ'], start='2020-01-01', end='2025-07-30')
if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.droplevel(1)
df = data[['Close', 'High', 'Low', 'Volume']].copy()
df.rename(columns={'Close': 'nasdaq', 'High': 'high_nasdaq', 'Low': 'low_nasdaq', 'Volume': 'nasdaq_volume_M'}, inplace=True)
df['nasdaq_volume_M'] /= 1_000_000
df[['nasdaq', 'high_nasdaq', 'low_nasdaq']] = (df[['nasdaq', 'high_nasdaq', 'low_nasdaq']].round(2) * 10)
df['nasdaq_volume_M'] = df['nasdaq_volume_M'].round(2)
df.reset_index(inplace=True)
df.rename(columns={'Date': 'date'}, inplace=True)
df = pd.merge(df, vix[['date', 'VIX']], on='date', how='left')
df.set_index('date', inplace=True)

# ====================================================
#  ➗ CÁLCULO DE INDICADORES
# ====================================================
n = 5
f = 40
s = 200

df['atr'] = df['VIX'].rolling(window=n).mean()
df['sma_fast'] = df['nasdaq'].rolling(window=f).mean().round(2)
df['sma_slow'] = df['nasdaq'].rolling(window=s).mean().round(2)
atr_indicator = ta.volatility.AverageTrueRange(high=df['high_nasdaq'], low=df['low_nasdaq'], close=df['nasdaq'], window=14)
df['nasdaq_atr'] = atr_indicator.average_true_range()
df['atr_trailing_stop'] = calculate_dynamic_atr_trailing_stop(df).round(2)
df['atr_trailing_stop_short'] = calculate_short_atr_trailing_stop(df).round(2)
df['vix_spike'] = find_vix_quiet_days(df).values

# Opcional: mostrar días con spike
print('vix spike\n', df[df['vix_spike']])


print(df.tail()) 

# ====================================================
# 🔍 BUSQUEDA DE PICOS EN EL VIX
# ====================================================
window_top_value = 15
factor_top_value = 1.2
tops_df = pd.DataFrame(find_vix_tops(df.copy(), window_top=window_top_value, factor_top=factor_top_value),
                       columns=['tag', 'index_top_pos', 'VIX_top', 'top_confirm'])

# ====================================================
# 🧠 ESTRATEGIA DE COBERTURA_CROSS_OVER_EMA
# ====================================================
hedge_trades_df = pd.DataFrame()  
if hedging_enabled:
    hedge_trades_df = strat_hedging_cross(
        df=df.copy(), fast_ma_col='sma_fast', slow_ma_col='sma_slow'
    )

# ====================================================
# 🧠 ESTRATEGIA DE COBERTURA_close versus _SLOW_EMA
# ====================================================
hedge_trades_df_slow_ema = pd.DataFrame()  
if hedging_slow_ema_enable:
    hedge_trades_df_slow_ema = generate_ema_short_hedging_signals(df)
    print("SLOW EMA hedge:\n", hedge_trades_df_slow_ema)
        

# ====================================================
# 🧠 ESTRATEGIA PRINCIPAL
# ====================================================
result = strat_vix_entry_from_tops(df.copy(), tops_df)

# --- Combinar y Mostrar Resultados ---
combined_trades_sorted = strats_outputs_join(result, hedge_trades_df, hedge_trades_df_slow_ema)

if not combined_trades_sorted.empty:
    print("\n" + "="*80)
    print("📜 REGISTRO DE OPERACIONES COMBINADO 📜")
    print("="*80)
    print(combined_trades_sorted)
    combined_trades_sorted.to_csv('outputs/combined_trades_log.csv', index=False)
    print("\n💾 Registro combinado guardado en: 'outputs/combined_trades_log.csv'")

# ====================================================
# 📊 GRAFICACIÓN
# ====================================================
df.reset_index(inplace=True)
plot_nasdaq_and_vix(
    symbol='NASDAQ', timeframe='daily', df=df, 
    tops_df=tops_df, trades_df=result, hedge_trades_df=hedge_trades_df, hedge_trades_df_slow_ema=hedge_trades_df_slow_ema
)


# ====================================================
# 📊 GRAFICACIÓN ACTIVE TRADES
# ====================================================
df.reset_index(inplace=True)

plot_vix_and_price_only(
    symbol="QQQ", 
    timeframe="Daily", 
    df=df,          # Tu DataFrame principal
    tops_df=tops_df # Tu DataFrame con los picos del VIX
)