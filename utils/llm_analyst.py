"""
utils/llm_analyst.py
Groq LLM calls for sentiment analysis & trade signal generation.
Mirrors Steps 4, 8, 9 of CDAZZDEV_Task1_Financial_AI.ipynb.
"""

from __future__ import annotations
import json
import logging
from typing import List

from groq import Groq

from .models import HeadlineSentiment, SentimentBatch, TradeSignal

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prompt constants (from notebook Step 4)
# ---------------------------------------------------------------------------

SENTIMENT_SYSTEM = """You are a professional financial news sentiment analyst.
Your job is to analyse stock-related news headlines and classify their sentiment.

RULES:
1. Return ONLY a valid JSON array. No markdown, no explanation, no preamble.
2. Each item must have exactly these four fields:
   - "headline": the exact headline text (string)
   - "sentiment": exactly one of "positive", "negative", or "neutral"
   - "confidence": a float between 0.0 and 1.0
   - "brief_reason": one sentence explaining the sentiment
3. Assess from a financial/investor perspective.
4. Do not add any text before or after the JSON array."""

SENTIMENT_USER = """Analyse the investor sentiment of these {ticker} news headlines.
Return a JSON array with one object per headline.

Headlines:
{headlines}

Return only the JSON array."""

SIGNAL_SYSTEM = """You are a senior equity research analyst at a tier-1 investment bank.
You specialise in technical analysis and quantitative signals.

Generate a clear Buy, Hold, or Sell recommendation.
Write a 3-5 sentence justification that REASONS over the COMBINATION of indicators.
Do NOT simply restate each indicator value — identify confluences and divergences.

Return ONLY a valid JSON object:
{
  "signal": "Buy" | "Hold" | "Sell",
  "confidence": 0.0 to 1.0,
  "justification": "3-5 sentences reasoning over indicator combinations",
  "key_factors": ["factor1", "factor2", ...],
  "risk_level": "Low" | "Medium" | "High"
}
No markdown. No preamble. Only the JSON object."""

SIGNAL_USER = """Generate a trade signal for {ticker} based on:

=== PRICE SNAPSHOT ===
Current Price:  ${current_price}
52-Week High:   ${w52_high}
52-Week Low:    ${w52_low}
YTD Return:     {ytd_return}%
P/E Ratio:      {pe_ratio}

=== TECHNICAL INDICATORS ===
SMA-50:   ${sma_50}   — Price is {price_vs_sma50} the 50-day moving average
SMA-200:  ${sma_200}  — Price is {price_vs_sma200} the 200-day moving average
SMA Cross: {sma_cross}

RSI (14):  {rsi}  — {rsi_interpretation}

MACD:      {macd}
Signal:    {macd_signal}
Histogram: {macd_hist}
Status:    {macd_status}

Bollinger Upper: ${bb_upper}
Bollinger Lower: ${bb_lower}
Bollinger Mid:   ${bb_mid}
Price Position:  {bb_pct:.1f}% of band width

Momentum Signal: {momentum}

=== NEWS SENTIMENT ===
Overall Score: {news_sentiment:.3f}  (-1.0=bearish to +1.0=bullish)
Positive: {pos_count} | Negative: {neg_count} | Neutral: {neu_count}

Return ONLY the JSON object."""


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------

def analyse_sentiment(
    headlines: List[str],
    ticker: str,
    groq_client: Groq,
    model: str = "llama-3.3-70b-versatile",
) -> SentimentBatch:
    """Run LLM sentiment analysis on a list of headlines."""
    headlines_text = "\n".join(f"{i+1}. {h}" for i, h in enumerate(headlines))

    response = groq_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SENTIMENT_SYSTEM},
            {"role": "user", "content": SENTIMENT_USER.format(
                ticker=ticker, headlines=headlines_text
            )},
        ],
        temperature=0.1,
        max_tokens=2000,
    )

    raw = response.choices[0].message.content.strip()
    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = "\n".join(raw.split("\n")[1:])
        if raw.endswith("```"):
            raw = raw[:-3]

    items = json.loads(raw)
    parsed: List[HeadlineSentiment] = []
    for item in items:
        try:
            parsed.append(HeadlineSentiment(**item))
        except Exception as e:
            logger.warning(f"Skipping malformed sentiment item: {e}")

    pos = [r for r in parsed if r.sentiment == "positive"]
    neg = [r for r in parsed if r.sentiment == "negative"]
    neu = [r for r in parsed if r.sentiment == "neutral"]

    direction = {"positive": 1, "negative": -1, "neutral": 0}
    if parsed:
        overall = sum(direction[r.sentiment] * r.confidence for r in parsed) / len(parsed)
    else:
        overall = 0.0

    return SentimentBatch(
        results=parsed,
        overall_score=round(overall, 4),
        total_headlines=len(parsed),
        positive_count=len(pos),
        negative_count=len(neg),
        neutral_count=len(neu),
    )


def generate_trade_signal(
    summary: dict,
    sentiment_batch: SentimentBatch,
    groq_client: Groq,
    model: str = "llama-3.3-70b-versatile",
    max_retries: int = 3,
) -> TradeSignal:
    """Generate a LLM trade signal from technical indicators + sentiment."""
    prompt = SIGNAL_USER.format(
        ticker=summary["ticker"],
        current_price=summary["current_price"],
        w52_high=summary["52w_high"],
        w52_low=summary["52w_low"],
        ytd_return=summary["ytd_return_pct"],
        pe_ratio=summary["pe_ratio"] or "N/A",
        sma_50=summary["sma_50"] or "N/A",
        sma_200=summary["sma_200"] or "N/A",
        price_vs_sma50=summary["price_vs_sma50"],
        price_vs_sma200=summary["price_vs_sma200"],
        sma_cross=summary["sma_cross"],
        rsi=summary["rsi_14"] or "N/A",
        rsi_interpretation=summary["rsi_interpretation"],
        macd=summary["macd"] or "N/A",
        macd_signal=summary["macd_signal"] or "N/A",
        macd_hist=summary["macd_hist"] or "N/A",
        macd_status=summary["macd_status"],
        bb_upper=summary["bb_upper"] or "N/A",
        bb_lower=summary["bb_lower"] or "N/A",
        bb_mid=summary["bb_mid"] or "N/A",
        bb_pct=(summary["bb_pct_b"] or 0) * 100,
        momentum=summary["momentum_signal"],
        news_sentiment=sentiment_batch.overall_score,
        pos_count=sentiment_batch.positive_count,
        neg_count=sentiment_batch.negative_count,
        neu_count=sentiment_batch.neutral_count,
    )

    last_err: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            resp = groq_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SIGNAL_SYSTEM},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=800,
            )
            raw = resp.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = "\n".join(raw.split("\n")[1:])
                if raw.endswith("```"):
                    raw = raw[:-3]
            data = json.loads(raw)
            return TradeSignal(**data)
        except Exception as e:
            last_err = e
            logger.warning(f"Trade signal attempt {attempt} failed: {e}")

    raise RuntimeError(f"Trade signal generation failed after {max_retries} attempts: {last_err}")
