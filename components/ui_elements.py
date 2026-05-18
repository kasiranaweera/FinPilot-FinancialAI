"""
components/ui_elements.py
Reusable Streamlit UI building blocks.
"""

from __future__ import annotations
import streamlit as st
from config.settings import COLORS


def signal_badge(signal: str) -> str:
    """Return HTML badge for a trade signal."""
    color = COLORS.get(signal.lower(), "#888")
    return (
        f'<span style="background:{color};color:#fff;'
        f'padding:4px 14px;border-radius:20px;font-weight:700;'
        f'font-size:15px">{signal}</span>'
    )


def sentiment_badge(sentiment: str) -> str:
    color = COLORS.get(sentiment, "#888")
    return (
        f'<span style="background:{color};color:#fff;'
        f'padding:2px 10px;border-radius:12px;font-size:11px;'
        f'font-weight:600;text-transform:uppercase">{sentiment}</span>'
    )


def metric_card(label: str, value: str, delta: str | None = None,
                delta_positive: bool | None = None) -> None:
    """Render a styled metric card."""
    delta_html = ""
    if delta is not None:
        if delta_positive is True:
            color = COLORS["positive"]
            arrow = "▲"
        elif delta_positive is False:
            color = COLORS["negative"]
            arrow = "▼"
        else:
            color = COLORS["neutral"]
            arrow = ""
        delta_html = (
            f'<div style="font-size:12px;color:{color};margin-top:2px">'
            f'{arrow} {delta}</div>'
        )

    st.markdown(
        f"""
        <div style="
            background:#fff;
            border:1px solid {COLORS['border']};
            border-radius:12px;
            padding:16px 18px;
            text-align:center;
            height:90px;
            display:flex;
            flex-direction:column;
            justify-content:center;
        ">
            <div style="font-size:22px;font-weight:700;color:{COLORS['text']}">{value}</div>
            <div style="font-size:11px;color:{COLORS['muted']};text-transform:uppercase;
                        letter-spacing:0.5px;margin-top:4px">{label}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def sentiment_bar(pos: int, neg: int, neu: int) -> None:
    """Render a coloured sentiment distribution bar."""
    total = pos + neg + neu or 1
    pos_pct = pos / total * 100
    neg_pct = neg / total * 100
    neu_pct = neu / total * 100
    st.markdown(
        f"""
        <div style="display:flex;height:10px;border-radius:5px;overflow:hidden;margin:8px 0">
            <div style="flex:{pos_pct};background:{COLORS['positive']}"></div>
            <div style="flex:{neu_pct};background:{COLORS['neutral']}"></div>
            <div style="flex:{neg_pct};background:{COLORS['negative']}"></div>
        </div>
        <div style="display:flex;gap:16px;font-size:11px;color:{COLORS['muted']}">
            <span>🟢 Positive: {pos}</span>
            <span>⚫ Neutral: {neu}</span>
            <span>🔴 Negative: {neg}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def disclaimer_box(text: str) -> None:
    st.markdown(
        f"""
        <div style="
            background:#F1EFE8;
            border-left:5px solid {COLORS['neutral']};
            border-radius:0 8px 8px 0;
            padding:14px 18px;
            margin-top:24px;
            font-size:11px;
            color:#5F5E5A;
            line-height:1.6;
        ">
            <strong>⚠️ Risk Disclaimer</strong><br>{text}
        </div>
        """,
        unsafe_allow_html=True,
    )
