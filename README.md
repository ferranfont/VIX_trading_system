pip install -r requirements.txt

📈 Sistema de Backtesting de Estrategias VIX-NASDAQ
Este proyecto es un sistema de backtesting avanzado en Python que implementa y combina dos estrategias complementarias para operar en el NASDAQ (ETF QQQ):
Estrategia Principal (Long): Un sistema de reversión a la media que utiliza el VIX, un indicador clave de la psicología del mercado, para identificar puntos de compra en momentos de pánico extremo.
Estrategia de Cobertura (Short): Un sistema de seguimiento de tendencia que abre posiciones cortas durante mercados bajistas definidos para proteger el capital y reducir el drawdown del portafolio.
El objetivo es crear un sistema robusto que no solo capture las ganancias en mercados alcistas, sino que también se defienda activamente durante las caídas prolongadas.
🚀 Características Principales
✅ Adquisición de Datos Automatizada
Descarga precios históricos de QQQ y del índice VIX directamente desde Yahoo Finance.
📊 Indicadores Calculados
Medias Móviles Simples (SMA) para definir el régimen del mercado.
Average True Range (ATR) del NASDAQ para una gestión de riesgo adaptativa.
ATR Trailing Stop dinámico para posiciones largas y cortas.
📥 Entradas Basadas en Psicología de Mercado
La estrategia principal detecta techos en el VIX para comprar el NASDAQ cuando el miedo inversor es máximo.
🛡️ Cobertura Defensiva (Hedging) Opcional
Activa una estrategia de seguimiento de tendencia en corto, basada en el "cruce de la muerte" de las medias móviles, para proteger la cartera durante mercados bajistas prolongados.
🧬 Gestión de Salida Avanzada en Dos Fases (para ambas estrategias)
Tanto las operaciones largas como las cortas utilizan un sofisticado sistema de stop-loss:
Fase 1: Un stop fijo inicial y amplio para dar espacio a la operación.
Fase 2: Una transición a un trailing stop dinámico y más ajustado una vez que la operación se mueve a favor.
💹 Análisis de Rendimiento Avanzado
Un script dedicado (performance_analyzer.py) calcula métricas de nivel institucional utilizando la librería empyrical:
Ratios de Sharpe, Sortino y Calmar.
CAGR (Retorno Anual Compuesto) y Volatilidad Anual.
Máximo Drawdown y Tasa de Acierto.
📉 Visualización Interactiva Completa
Genera automáticamente múltiples gráficos interactivos para un análisis profundo:
Gráfico Principal de Operaciones: Muestra todas las entradas/salidas (largas y cortas), stops dinámicos, medias móviles y el VIX.
Curva de Capital (USD): Gráfico de área que muestra el crecimiento del capital en dólares.
Curva de Capital (%): Compara el rendimiento porcentual de la estrategia contra dos benchmarks del NASDAQ.
Curva de Drawdown: Un gráfico dedicado que muestra las caídas desde los picos de capital.
💾 Exportación de Resultados
Todos los registros de operaciones (principal, cobertura y combinado) se guardan en archivos CSV en la carpeta /outputs/ para su análisis en otras herramientas.
📁 Estructura del Proyecto
Generated code
/VIX_trading_system/
├── charts/                   # Gráficos HTML generados
├── outputs/                  # CSVs de resultados exportados
├── quant_stat/
│   └── find_vix_tops.py
├── strat_OM/
│   ├── strat_ATR_stop_lost.py
│   ├── strat_hedging_cross.py
│   ├── strat_vix_long.py
│   └── strats_outputs_join.py
├── chart_volume.py
├── main.py
├── performance_analyzer.py
├── requirements.txt
└── README.md

🔬 Análisis Detallado de Componentes
Cada script tiene una responsabilidad específica dentro del sistema.

⚙️ main.py
Función Principal: Actúa como el orquestador central del backtest.
Responsabilidades:
Carga de Datos: Ejecuta yfinance para descargar y preprocesar los datos de QQQ y VIX.
Cálculo de Indicadores: Calcula y añade al DataFrame principal todas las métricas necesarias: SMAs, ATR del NASDAQ y ambos ATR Trailing Stops (largo y corto).
Ejecución de Estrategias: Llama secuencialmente a las funciones de la estrategia principal (strat_vix_entry_from_tops) y la de cobertura (strat_hedging_cross).
Combinación de Resultados: Utiliza strats_outputs_join para unificar los registros de operaciones.
Visualización Principal: Llama a plot_nasdaq_and_vix para generar el gráfico detallado de operaciones.

🧠 quant_stat/find_vix_tops.py
Función Clave: find_vix_tops()
Propósito: Es el generador de señales para la estrategia principal. Su única misión es analizar la serie de tiempo del VIX y detectar momentos de pánico extremo que cumplan con los criterios definidos (picos por encima de su media). Devuelve una lista de fechas que actúan como disparadores para las compras.

📈 strat_OM/strat_vix_long.py
Función Clave: strat_vix_entry_from_tops()
Propósito: Es el motor de backtesting para la estrategia principal (Long).
Recibe las señales de find_vix_tops.
Simula la apertura de operaciones largas en las fechas de señal.
Gestiona cada operación abierta aplicando la lógica de stop-loss de dos fases (fijo inicial y transición a trailing stop dinámico).
Registra cada operación cerrada en un DataFrame de resultados.
Genera y abre los gráficos de rendimiento de Curva de Capital (USD y %).

🛡️ strat_OM/strat_hedging_cross.py
Función Clave: strat_hedging_cross()
Propósito: Es el motor de backtesting para la estrategia de cobertura (Short).
Analiza las medias móviles para detectar un "cruce de la muerte" (SMA rápida por debajo de SMA lenta) como señal de entrada en corto.
Gestiona la posición corta con su propia lógica de stop-loss de dos fases para darle holgura inicial y proteger ganancias después.
Registra cada operación de cobertura cerrada en su propio DataFrame.

📏 strat_OM/strat_ATR_stop_lost.py
Funciones Clave: calculate_dynamic_atr_trailing_stop() y calculate_short_atr_trailing_stop()
Propósito: Es una librería de utilidad para la gestión de riesgo. Contiene la lógica matemática para calcular los niveles del ATR Trailing Stop. Es fundamental porque centraliza el cálculo del stop, permitiendo que ambas estrategias (larga y corta) lo utilicen.

🔗 strat_OM/strats_outputs_join.py
Función Clave: strats_outputs_join()
Propósito: Es una herramienta de post-procesamiento. Su única función es tomar los dos DataFrames de resultados (de los largos y los cortos), estandarizar sus columnas y unirlos en un único registro cronológico, facilitando el análisis del sistema combinado.

🎨 chart_volume.py
Función Clave: plot_nasdaq_and_vix()
Propósito: Es el motor de visualización principal. Crea el gráfico más complejo y detallado del proyecto, superponiendo en un mismo lienzo: el precio, los indicadores (SMAs, ATR stops), el VIX, el volumen y todas las señales de entrada y salida de ambas estrategias. Es crucial para depurar y entender visualmente cómo interactúan las estrategias.

🧮 performance_analyzer.py
Función Clave: analyze_performance()
Propósito: Es el módulo de análisis de rendimiento final. Se ejecuta después del main.py.
Lee el archivo CSV de resultados guardado.
Utiliza la librería empyrical para calcular métricas avanzadas (Sharpe, Sortino, Drawdown, etc.).
Genera dos gráficos de alto nivel y muy informativos: la curva de capital y la curva de drawdown, guardándolos como archivos HTML separados.


🔧 Personalización
main.py:
hedging_enabled: Activa (True) o desactiva (False) la estrategia de cobertura.
f y s: Períodos para las medias móviles rápida y lenta.
strat_OM/strat_ATR_stop_lost.py:
atr_multiplier: Ajusta la sensibilidad de los trailing stops.
strat_OM/strat_hedging_cross.py:
fixed_stop_multiplier: Ajusta la holgura del stop fijo inicial solo para los cortos.


Desarrollado por Ferran Font
ferran@orderbooktrading.com