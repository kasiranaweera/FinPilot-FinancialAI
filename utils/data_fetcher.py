"""
utils/data_fetcher.py
OHLCV data retrieval with 4-level fallback chain.
Mirrors Step 5 of CDAZZDEV_Task1_Financial_AI.ipynb.
"""

from __future__ import annotations
import io
import logging
import time
from datetime import datetime, timedelta
from typing import Optional

import numpy as np
import pandas as pd
import requests
import yfinance as yf

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _period_to_days(period: str) -> int:
    return {"6mo": 183, "1y": 365, "2y": 730, "3y": 1095, "5y": 1825}.get(period, 730)


def _normalise(df: pd.DataFrame, min_rows: int = 50) -> pd.DataFrame:
    df = df.copy()
    df.index = pd.to_datetime(df.index)
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)
    df.sort_index(inplace=True)

    for col in ["Open", "High", "Low", "Close", "Volume"]:
        if col not in df.columns:
            raise ValueError(f"Missing column '{col}'")
    df = df[["Open", "High", "Low", "Close", "Volume"]]
    df.dropna(how="all", inplace=True)

    if len(df) < min_rows:
        raise ValueError(f"Only {len(df)} rows — suspiciously low")
    return df


# ---------------------------------------------------------------------------
# Source A: yfinance (uses curl_cffi to bypass bot-detection)
# ---------------------------------------------------------------------------

def _fetch_yf(ticker: str, period: str) -> pd.DataFrame:
    logger.info("[yfinance] Attempting history()...")
    stock = yf.Ticker(ticker)
    df = stock.history(period=period, auto_adjust=True)
    if df is None or df.empty:
        raise ValueError("yfinance returned no data")
    return df


# ---------------------------------------------------------------------------
# Source B: Stooq direct HTTP
# ---------------------------------------------------------------------------

def _fetch_stooq_direct(ticker: str, period: str) -> pd.DataFrame:
    days = _period_to_days(period)
    end = datetime.today()
    start = end - timedelta(days=days + 45)
    stooq_sym = f"{ticker.lower()}.us"
    url = (
        f"https://stooq.com/q/d/l/?s={stooq_sym}"
        f"&d1={start.strftime('%Y%m%d')}&d2={end.strftime('%Y%m%d')}&i=d"
    )
    logger.info(f"[Stooq] GET {url}")
    resp = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    if not resp.text.strip():
        raise ValueError("Stooq returned empty response")
    df = pd.read_csv(
        io.StringIO(resp.text),
        on_bad_lines="skip",
        parse_dates=["Date"],
        index_col="Date",
    )
    if df.empty:
        raise ValueError("Stooq parsed to empty DataFrame")
    df.sort_index(inplace=True)
    return df


# ---------------------------------------------------------------------------
# Source C: Alpha Vantage compact (100 days)
# ---------------------------------------------------------------------------

def _fetch_alpha_vantage(ticker: str, av_key: str) -> pd.DataFrame:
    url = (
        f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY"
        f"&symbol={ticker}&outputsize=compact&apikey={av_key}"
    )
    logger.info("[AlphaVantage] Fetching compact daily...")
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    ts = data.get("Time Series (Daily)", {})
    if not ts:
        raise ValueError(f"Alpha Vantage returned no data: {data.get('Note', data.get('Information', ''))}")
    records = [
        {
            "Date": k,
            "Open": float(v["1. open"]),
            "High": float(v["2. high"]),
            "Low": float(v["3. low"]),
            "Close": float(v["4. close"]),
            "Volume": float(v["5. volume"]),
        }
        for k, v in ts.items()
    ]
    df = pd.DataFrame(records)
    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)
    df.sort_index(inplace=True)
    return df


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def fetch_ohlcv(
    ticker: str,
    period: str = "2y",
    av_key: str = "",
) -> pd.DataFrame:
    """
    Fetch OHLCV data with 4-level fallback chain.
    Returns a clean DataFrame with columns [Open, High, Low, Close, Volume].
    """
    errors: list[str] = []

    # --- A: yfinance ---
    try:
        df = _fetch_yf(ticker, period)
        return _normalise(df)
    except Exception as e:
        errors.append(f"yfinance: {e}")
        logger.warning(f"yfinance failed: {e}")

    # --- B: Stooq direct ---
    try:
        df = _fetch_stooq_direct(ticker, period)
        return _normalise(df)
    except Exception as e:
        errors.append(f"Stooq: {e}")
        logger.warning(f"Stooq failed: {e}")

    # --- C: Alpha Vantage ---
    if av_key:
        try:
            df = _fetch_alpha_vantage(ticker, av_key)
            return _normalise(df, min_rows=20)
        except Exception as e:
            errors.append(f"AlphaVantage: {e}")
            logger.warning(f"AlphaVantage failed: {e}")

    raise RuntimeError(
        f"All data sources failed for '{ticker}':\n" + "\n".join(errors)
    )


def fetch_stock_info(ticker: str) -> dict:
    """Fetch company metadata using yfinance."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "name": info.get("longName", ticker),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "description": info.get("longBusinessSummary", ""),
        }
    except Exception as e:
        logger.warning(f"Could not fetch stock info: {e}")
        return {"name": ticker, "sector": "N/A", "industry": "N/A",
                "market_cap": None, "pe_ratio": None, "description": ""}


def fetch_news(ticker: str, count: int = 15) -> list[dict]:
    """Fetch recent news headlines via yfinance."""
    try:
        stock = yf.Ticker(ticker)
        news = stock.news or []
        results = []
        for item in news[:count]:
            content = item.get("content", {})
            title = (
                content.get("title")
                or item.get("title", "")
            )
            results.append({
                "title": title,
                "publisher": content.get("provider", {}).get("displayName", item.get("publisher", "")),
                "link": content.get("canonicalUrl", {}).get("url", item.get("link", "")),
                "published": content.get("pubDate", item.get("providerPublishTime", "")),
            })
        return results
    except Exception as e:
        logger.warning(f"News fetch failed: {e}")
        return []
