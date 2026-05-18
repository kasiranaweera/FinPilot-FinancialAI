"""
utils/models.py
Pydantic v1 models for structured LLM output.
Mirrors Step 3 of CDAZZDEV_Task1_Financial_AI.ipynb.
"""

from __future__ import annotations
from typing import List, Literal
from pydantic import BaseModel, Field, validator


class HeadlineSentiment(BaseModel):
    headline: str
    sentiment: Literal["positive", "negative", "neutral"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    brief_reason: str

    @validator("brief_reason")
    def reason_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("brief_reason cannot be empty")
        return v.strip()

    @validator("confidence")
    def confidence_range(cls, v: float) -> float:
        return round(float(v), 4)


class SentimentBatch(BaseModel):
    results: List[HeadlineSentiment]
    overall_score: float = Field(..., ge=-1.0, le=1.0)
    total_headlines: int
    positive_count: int
    negative_count: int
    neutral_count: int


class TradeSignal(BaseModel):
    signal: Literal["Buy", "Hold", "Sell"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    justification: str = Field(..., min_length=80)
    key_factors: List[str] = Field(..., min_items=2)
    risk_level: Literal["Low", "Medium", "High"]

    @validator("justification")
    def must_reason_not_restate(cls, v: str) -> str:
        reasoning_words = [
            "suggests", "implies", "combined", "confluence", "divergence",
            "therefore", "however", "while", "despite", "indicating",
            "consistent with", "aligns", "momentum", "pressure",
            "caution", "strength",
        ]
        if not any(w in v.lower() for w in reasoning_words):
            raise ValueError("Justification must reason over indicators, not just restate values.")
        return v
