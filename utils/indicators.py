"""
utils/indicators.py
Compute technical indicators from OHLCV DataFrame.
Mirrors Step 6 of CDAZZDEV_Task1_Financial_AI.ipynb.
"""

from __future__ import annotations
import numpy as np
import pandas as pd


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add SMA-50, SMA-200, RSI-14, MACD (12,26,9), Bollinger Bands (20,2)
    to the OHLCV DataFrame. Returns a new DataFrame.
    """
    df = df.copy()
    close = df["Close"]

    # --- Moving averages ---
    df["SMA_50"] = close.rolling(50).mean().round(2)
    df["SMA_200"] = close.rolling(200).mean().round(2)

    # --- RSI (14) ---
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=13, adjust=False).mean()
    avg_loss = loss.ewm(com=13, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    df["RSI_14"] = (100 - 100 / (1 + rs)).round(2)

    # --- MACD (12, 26, 9) ---
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    df["MACD"] = (ema12 - ema26).round(4)
    df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean().round(4)
    df["MACD_Hist"] = (df["MACD"] - df["MACD_Signal"]).round(4)

    # --- Bollinger Bands (20, 2σ) ---
    sma20 = close.rolling(20).mean()
    std20 = close.rolling(20).std()
    df["BB_Upper"] = (sma20 + 2 * std20).round(2)
    df["BB_Lower"] = (sma20 - 2 * std20).round(2)
    df["BB_Mid"] = sma20.round(2)
    band_width = df["BB_Upper"] - df["BB_Lower"]
    df["BB_Pct_B"] = ((close - df["BB_Lower"]) / band_width.replace(0, np.nan)).round(4)

    return df


def build_summary(df: pd.DataFrame, ticker: str, pe_ratio: float | None = None) -> dict:
    """Extract the latest snapshot values from an indicator-enriched DataFrame."""
    latest = df.iloc[-1]
    current_price = round(float(latest["Close"]), 2)

    # YTD return
    year_start = df[df.index.year == df.index[-1].year].iloc[0]["Close"]
    ytd_return = round((current_price / float(year_start) - 1) * 100, 2)

    # 52-week window
    one_year_ago = df.index[-1] - pd.DateOffset(years=1)
    year_df = df[df.index >= one_year_ago]
    w52_high = round(float(year_df["High"].max()), 2)
    w52_low = round(float(year_df["Low"].min()), 2)

    # SMA cross / momentum
    sma50 = latest.get("SMA_50")
    sma200 = latest.get("SMA_200")
    if pd.notna(sma50) and pd.notna(sma200):
        sma_cross = "Golden Cross ✅" if sma50 > sma200 else "Death Cross ⚠️"
    else:
        sma_cross = "N/A"

    rsi = latest.get("RSI_14")
    if pd.notna(rsi):
        if rsi > 70:
            rsi_interp = "Overbought"
            momentum = "bearish"
        elif rsi < 30:
            rsi_interp = "Oversold"
            momentum = "bullish"
        else:
            rsi_interp = "Neutral"
            momentum = "neutral"
    else:
        rsi_interp = "N/A"
        momentum = "neutral"

    macd = latest.get("MACD")
    macd_signal = latest.get("MACD_Signal")
    macd_hist = latest.get("MACD_Hist")
    if pd.notna(macd) and pd.notna(macd_signal):
        macd_status = "Bullish crossover" if macd > macd_signal else "Bearish crossover"
    else:
        macd_status = "N/A"

    def _f(v, decimals=2):
        return round(float(v), decimals) if pd.notna(v) else None

    return {
        "ticker": ticker,
        "as_of_date": df.index[-1].strftime("%Y-%m-%d"),
        "data_points": len(df),
        "current_price": current_price,
        "52w_high": w52_high,
        "52w_low": w52_low,
        "ytd_return_pct": ytd_return,
        "pe_ratio": round(pe_ratio, 2) if pe_ratio else None,
        "sma_50": _f(sma50),
        "sma_200": _f(sma200),
        "sma_cross": sma_cross,
        "price_vs_sma50": "above" if pd.notna(sma50) and current_price > sma50 else "below",
        "price_vs_sma200": "above" if pd.notna(sma200) and current_price > sma200 else "below",
        "rsi_14": _f(rsi),
        "rsi_interpretation": rsi_interp,
        "macd": _f(macd, 4),
        "macd_signal": _f(macd_signal, 4),
        "macd_hist": _f(macd_hist, 4),
        "macd_status": macd_status,
        "bb_upper": _f(latest.get("BB_Upper")),
        "bb_lower": _f(latest.get("BB_Lower")),
        "bb_mid": _f(latest.get("BB_Mid")),
        "bb_pct_b": _f(latest.get("BB_Pct_B"), 4),
        "momentum_signal": momentum,
    }
