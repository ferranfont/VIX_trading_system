pip install -r requirements.txt


# 📈 VIX Trading System – NASDAQ + VIX Visualizer
# 📈 Sistema de Backtesting de Estrategia VIX-NASDAQ

Este proyecto implementa un sistema de backtesting en Python para una estrategia de **reversión a la media** en el NASDAQ (ETF QQQ), utilizando los **picos de volatilidad del índice VIX** como señales de entrada.

La lógica se basa en **comprar en momentos de pánico** (VIX alto) y gestionar la salida mediante un **stop-loss dinámico de dos fases** basado en el ATR para proteger capital y asegurar beneficios.

---

## 🚀 Características Principales

✅ **Adquisición de Datos Automatizada**  
Descarga precios históricos de **QQQ** y **VIX** desde Yahoo Finance.

📊 **Indicadores Calculados**  
- EMA  
- ATR del NASDAQ  
- ATR Trailing Stop

📥 **Entradas Basadas en el VIX**  
Detecta techos locales en el VIX para comprar el NASDAQ cuando hay miedo extremo.

🛡️ **Gestión de Salida Avanzada** (Stop-Loss en 2 Fases)  
- **Fase 1:** Stop fijo inicial = entrada - (atr_factor × ATR)  
- **Fase 2:** Si el precio cierra por encima del ATR Trailing Stop, se activa el trailing stop dinámico.

📈 **Reportes de Rendimiento**  
- Tasa de acierto  
- Ganancia/pérdida media  
- Profit ratio  
- P&L total

📉 **Visualización Interactiva**  
- Gráfico de operaciones (señales, stops, volumen, VIX)  
- Curva de capital en USD  
- Curva de capital en % vs. dos benchmarks del NASDAQ

💾 **Exportación de Resultados**  
Los trades se guardan en `/outputs/trade_results.csv` para análisis externo.

---

## 📁 Estructura del Proyecto

VIX_trading_system/
├── charts/ # Gráficos HTML generados
├── outputs/ # CSVs de resultados exportados
├── quant_stat/
│ └── find_vix_tops.py # Lógica para detectar techos del VIX
├── strat_OM/
│ ├── strat_ATR_stop_lost.py # Cálculo del trailing stop
│ └── strat_vix_long.py # Estrategia principal y backtesting
├── chart_volume.py # Visualización con Plotly
├── main.py # Script principal de ejecución
├── requirements.txt # Dependencias
└── README.md

🧠 Lógica de la Estrategia
🎯 Entrada
Compra QQQ cuando el VIX marca un pico significativo por encima de su media móvil.

🔓 Fase 1: Stop Fijo Inicial
Stop inicial = precio entrada - (atr_factor × ATR)

🔒 Fase 2: Stop Dinámico
Se activa solo si el precio de cierre supera la línea verde de ATR Trailing Stop. A partir de entonces, el stop fijo se descarta y el stop dinámico gestiona la operación.

🔧 Personalización
strat_OM/strat_ATR_stop_lost.py
atr_period: Período del ATR

smoothing_period: Suavizado

atr_multiplier: Multiplicador del trailing stop

strat_OM/strat_vix_long.py
atr_factor: Multiplicador para el stop fijo inicial

quant_stat/find_vix_tops.py
window_top y factor_top: Sensibilidad para detectar picos en el VIX

desarrollado por Ferran font
ferran@orderbooktrading.com
