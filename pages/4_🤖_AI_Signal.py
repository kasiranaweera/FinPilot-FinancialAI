"""
pages/4_🤖_AI_Signal.py
LLM-generated trade signal display.
"""

import streamlit as st
from components import signal_badge, disclaimer_box
from config.settings import COLORS, RISK_DISCLAIMER

st.set_page_config(page_title="AI Trade Signal", page_icon="🤖", layout="wide")
st.title("🤖 AI Trade Signal")

if "trade_signal" not in st.session_state:
    st.info("👈 Run analysis from the **Home** page first.")
    st.stop()

signal = st.session_state["trade_signal"]
s = st.session_state["summary"]
batch = st.session_state.get("sentiment_batch")

# Big signal display
sig_color = COLORS.get(signal.signal.lower(), "#888")
sig_bg = {"Buy": "#E1F5EE", "Hold": "#FAEEDA", "Sell": "#FCEBEB"}.get(signal.signal, "#F5F5F5")

st.markdown(
    f"""
    <div style="background:{sig_bg};border:2px solid {sig_color};border-radius:16px;
        padding:28px 32px;margin-bottom:24px">
        <div style="display:flex;align-items:center;gap:20px;margin-bottom:12px">
            <div style="font-size:52px;font-weight:800;color:{sig_color}">
                {signal.signal}
            </div>
            <div>
                <div style="font-size:13px;color:#888">Confidence</div>
                <div style="font-size:24px;font-weight:700;color:{sig_color}">
                    {signal.confidence:.0%}
                </div>
            </div>
            <div style="margin-left:20px">
                <div style="font-size:13px;color:#888">Risk Level</div>
                <div style="font-size:20px;font-weight:700;color:#2C2C2A">
                    {signal.risk_level}
                </div>
            </div>
        </div>
        <div style="font-size:15px;color:#2C2C2A;line-height:1.8;border-top:1px solid {sig_color}33;
            padding-top:14px">
            {signal.justification}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Confidence bar
st.markdown("**Confidence Level**")
st.progress(signal.confidence)

st.divider()

# Key factors
st.subheader("🔑 Key Factors")
for i, factor in enumerate(signal.key_factors, 1):
    st.markdown(
        f"""
        <div style="background:#fff;border:1px solid #E8E6E0;border-radius:8px;
            padding:12px 16px;margin-bottom:8px;display:flex;align-items:center;gap:12px">
            <span style="background:{sig_color};color:#fff;border-radius:50%;
                width:26px;height:26px;display:flex;align-items:center;
                justify-content:center;font-weight:700;font-size:13px;flex-shrink:0">
                {i}
            </span>
            <span style="font-size:14px;color:#2C2C2A">{factor}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

# Supporting data summary
st.subheader("📊 Input Summary")
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Technical Indicators**")
    st.markdown(
        f"""
| Metric | Value |
|--------|-------|
| Current Price | ${s['current_price']} |
| SMA-50 | ${s['sma_50']} ({s['price_vs_sma50']}) |
| SMA-200 | ${s['sma_200']} ({s['price_vs_sma200']}) |
| SMA Cross | {s['sma_cross']} |
| RSI-14 | {s['rsi_14']} — {s['rsi_interpretation']} |
| MACD | {s['macd']} — {s['macd_status']} |
| Momentum | {s['momentum_signal'].upper()} |
| YTD Return | {s['ytd_return_pct']:+.1f}% |
        """
    )

with col2:
    if batch:
        st.markdown("**News Sentiment**")
        score_label = (
            "Bullish" if batch.overall_score > 0.1
            else "Bearish" if batch.overall_score < -0.1
            else "Neutral"
        )
        st.markdown(
            f"""
| Metric | Value |
|--------|-------|
| Overall Score | {batch.overall_score:+.3f} ({score_label}) |
| Positive Headlines | {batch.positive_count} |
| Negative Headlines | {batch.negative_count} |
| Neutral Headlines | {batch.neutral_count} |
| Total Analysed | {batch.total_headlines} |
            """
        )

disclaimer_box(RISK_DISCLAIMER)
