# FILE: summary_stat.py

import pandas as pd
import numpy as np
import plotly.graph_objs as go
import os
import webbrowser
import empyrical as emp

# -------- CONFIG --------
input_csv = "outputs/tracking_record_VIX_long.csv"
initial_capital = 10000
output_html_equity = "outputs/equity_tracking_curve.html"
output_html_drawdown = "outputs/drawdown_curve.html"

# -------- LOAD & PROCESS DATA --------
df = pd.read_csv(input_csv, parse_dates=["entry_date", "exit_date"])
df = df.sort_values("exit_date")

# Cumulative equity curve
df['equity'] = df['profit_usd'].cumsum() + initial_capital
equity_curve = pd.Series(df['equity'].values, index=df['exit_date'])

# Remove duplicates and forward fill
equity_curve_daily = equity_curve.groupby(equity_curve.index.date).last()
equity_curve_daily.index = pd.to_datetime(equity_curve_daily.index)
equity_curve_daily = equity_curve_daily.asfreq("D").ffill()

returns = equity_curve_daily.pct_change().dropna()

# -------- RATIOS --------
ratios = {
    "Total Return (%)": (equity_curve_daily.iloc[-1] / equity_curve_daily.iloc[0] - 1) * 100,
    "CAGR (%)": emp.annual_return(returns) * 100,
    "Sharpe Ratio": emp.sharpe_ratio(returns),
    "Sortino Ratio": emp.sortino_ratio(returns),
    "Calmar Ratio": emp.calmar_ratio(returns),
    "Max Drawdown (%)": emp.max_drawdown(returns) * 100,
    "Volatility (%)": emp.annual_volatility(returns) * 100,
    "Win Rate (%)": (df['profit_usd'] > 0).sum() / len(df) * 100,
    "Avg Win ($)": df[df['profit_usd'] > 0]['profit_usd'].mean(),
    "Avg Loss ($)": df[df['profit_usd'] < 0]['profit_usd'].mean(),
    "Expectancy ($)": df['profit_usd'].mean(),
    "Number of Trades": len(df)
}

# -------- PRINT RATIOS --------
print("\n📊 RATIO SUMMARY:")
print(pd.DataFrame(ratios, index=["Metrics"]).T.round(2))

# -------- EQUITY CURVE PLOT --------
df['day'] = df['exit_date'].dt.date
summary = df.groupby('day').agg(pnl_sum=('profit_usd', 'sum')).reset_index()
summary['equity'] = summary['pnl_sum'].cumsum() + initial_capital
summary['equity_pos'] = summary['equity'].where(summary['equity'] >= initial_capital, np.nan)
summary['equity_neg'] = summary['equity'].where(summary['equity'] < initial_capital, np.nan)

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=summary['day'], y=summary['equity_pos'],
    mode='lines', fill='tozeroy',
    line=dict(color='rgba(46,204,113,1)', width=2),
    fillcolor='rgba(46,204,113,0.3)', name='Equity +'
))

fig.add_trace(go.Scatter(
    x=summary['day'], y=summary['equity_neg'],
    mode='lines', fill='tozeroy',
    line=dict(color='rgba(231,76,60,1)', width=2),
    fillcolor='rgba(231,76,60,0.3)', name='Equity -'
))

fig.update_layout(
    title='✅ Cumulative Equity Curve (Green = Gain, Red = Loss)',
    xaxis_title='Date',
    yaxis_title='Equity ($)',
    width=1400, height=800,
    template='plotly_white',
    font=dict(size=14),
    margin=dict(l=30, r=30, t=60, b=30)
)

fig.write_html(output_html_equity, auto_open=False)
webbrowser.open('file://' + os.path.realpath(output_html_equity))
print(f"\n📈 Equity curve saved to: {output_html_equity}")

# -------- DRAWDOWN CHART (New) --------
rolling_max = equity_curve_daily.cummax()
drawdown_pct = (equity_curve_daily - rolling_max) / rolling_max

fig_dd = go.Figure()
fig_dd.add_trace(go.Scatter(
    x=drawdown_pct.index,
    y=drawdown_pct * 100,
    mode='lines',
    fill='tozeroy',
    line=dict(color='rgba(255,99,132,0.8)', width=2),
    fillcolor='rgba(255,99,132,0.3)',
    name='Drawdown (%)'
))
fig_dd.update_layout(
    title='📉 Drawdown Curve',
    xaxis_title='Date',
    yaxis_title='Drawdown (%)',
    width=1400,
    height=600,
    template='plotly_white',
    font=dict(size=14),
    margin=dict(l=30, r=30, t=60, b=30)
)

fig_dd.write_html(output_html_drawdown, auto_open=False)
webbrowser.open('file://' + os.path.realpath(output_html_drawdown))
print(f"\n📉 Drawdown chart saved to: {output_html_drawdown}")
