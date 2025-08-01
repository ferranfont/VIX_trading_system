import pandas as pd
import numpy as np

def calculate_dynamic_atr_trailing_stop(df):
    """
    Calculates the ATR Trailing Stop with corrected initialization logic.
    
    Parameters:
    - df: DataFrame with columns 'nasdaq', 'high_nasdaq', 'low_nasdaq'
    - atr_period, smoothing_period, atr_multiplier: ATR calculation parameters.
    - method: "close", "hl", or "hlc" for stop calculation basis.
    
    Returns:
    - A pandas Series containing the correctly calculated trailing stop.
    """
    atr_period=14
    smoothing_period=10
    atr_multiplier=3.5
    method="close"

    # --- Parameter and Data Setup ---
    high = df['high_nasdaq']
    low = df['low_nasdaq']
    close = df['nasdaq']
    
    # --- ATR Calculation ---
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs()
    ], axis=1).max(axis=1)

    atr = tr.rolling(window=atr_period).mean()
    smoothed_atr = atr.rolling(window=smoothing_period).mean()
    stop_offset = smoothed_atr * atr_multiplier # The value to add/subtract
    
    trailing_stop = [np.nan] * len(df) # Initialize list for results

    # --- Main Loop for Stop Calculation ---
    for i in range(1, len(df)):
        # Get current and previous values
        price = close.iloc[i]
        prev_price = close.iloc[i-1]
        prev_stop = trailing_stop[i-1]
        
        # Ensure we have a valid stop offset value to work with
        if pd.isna(stop_offset.iloc[i]):
            trailing_stop[i] = prev_stop # Carry forward the last stop if ATR isn't ready
            continue

        # =======================================================================
        # === THE FIX: Properly initialize the first stop-loss value          ===
        # =======================================================================
        # If the previous stop is NaN, this is the first calculation.
        # For a long-biased system, we MUST start by placing the stop *below* the price.
        if pd.isna(prev_stop):
            if method == "close":
                new_stop = price - stop_offset.iloc[i]
            else: # For "hl" and "hlc", use the low for a more conservative initial stop
                new_stop = low.iloc[i] - stop_offset.iloc[i]
        # =======================================================================
        # === Original Trailing Logic (now runs only after initialization)    ===
        # =======================================================================
        else:
            if method == "close":
                # Price is trending up above the stop
                if price > prev_stop and prev_price > prev_stop:
                    new_stop = max(prev_stop, price - stop_offset.iloc[i])
                # Price is trending down below the stop (short trade direction)
                elif price < prev_stop and prev_price < prev_stop:
                    new_stop = min(prev_stop, price + stop_offset.iloc[i])
                # Price crossed up over the stop (start of a long trend)
                elif price > prev_stop:
                    new_stop = price - stop_offset.iloc[i]
                # Price crossed down over the stop (start of a short trend)
                else:
                    new_stop = price + stop_offset.iloc[i]
            
            # --- HL/HLC Method Logic ---
            else: 
                high_i = high.iloc[i]
                low_i = low.iloc[i]
                # For "hl" method, price is irrelevant, only use high/low
                price_for_hl = high_i if method == "hl" else price
                prev_price_for_hl = high.iloc[i-1] if method == "hl" else prev_price

                # Price is trending up above the stop
                if price_for_hl > prev_stop and prev_price_for_hl > prev_stop:
                    new_stop = max(prev_stop, low_i - stop_offset.iloc[i])
                # Price is trending down below the stop
                elif price_for_hl < prev_stop and prev_price_for_hl < prev_stop:
                    new_stop = min(prev_stop, high_i + stop_offset.iloc[i])
                # Price crossed up over the stop
                elif price_for_hl > prev_stop:
                    new_stop = low_i - stop_offset.iloc[i]
                # Price crossed down over the stop
                else:
                    new_stop = high_i + stop_offset.iloc[i]

        trailing_stop[i] = new_stop

    return pd.Series(trailing_stop, index=df.index, name="atr_trailing_stop")