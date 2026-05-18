"""
pages/2_📈_Technical_Analysis.py
Detailed technical charts — RSI, MACD, returns distribution.
"""

import streamlit as st
from components import rsi_chart, macd_chart, returns_histogram

st.set_page_config(page_title="Technical Analysis", page_icon="📈", layout="wide")
st.title("📈 Technical Analysis")

if "df" not in st.session_state or "summary" not in st.session_state:
    st.info("👈 Run analysis from the **Home** page first.")
    st.stop()

df = st.session_state["df"]
s = st.session_state["summary"]

ticker = s["ticker"]

# RSI chart
st.subheader("Relative Strength Index (RSI-14)")
st.caption(
    "RSI above **70** = overbought (potential reversal down) · "
    "RSI below **30** = oversold (potential reversal up)"
)
st.plotly_chart(rsi_chart(df, ticker), use_container_width=True)

# RSI gauge
rsi_val = s["rsi_14"] or 50
rsi_color = "#D85A30" if rsi_val > 70 else "#1D9E75" if rsi_val < 30 else "#185FA5"
st.markdown(
    f"""
    <div style="text-align:center;padding:12px;background:#fff;
        border:1px solid #E8E6E0;border-radius:12px;margin-bottom:16px">
        <span style="font-size:28px;font-weight:700;color:{rsi_color}">{rsi_val}</span>
        <span style="margin-left:10px;font-size:14px;color:#888">
            {s['rsi_interpretation']}
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

# MACD chart
st.subheader("MACD (12, 26, 9)")
st.caption(
    "MACD line **crossing above** signal = bullish · "
    "crossing **below** = bearish"
)
st.plotly_chart(macd_chart(df, ticker), use_container_width=True)

col1, col2, col3 = st.columns(3)
col1.metric("MACD", s["macd"])
col2.metric("Signal Line", s["macd_signal"])
col3.metric("Histogram", s["macd_hist"], delta=s["macd_status"])

st.divider()

# Returns distribution
st.subheader("Daily Return Distribution")
st.caption("Distribution of single-day price changes over the full period.")
st.plotly_chart(returns_histogram(df, ticker), use_container_width=True)

# Bollinger Bands summary
st.divider()
st.subheader("Bollinger Bands (20, 2σ)")
bb_pct = (s["bb_pct_b"] or 0) * 100
c1, c2, c3, c4 = st.columns(4)
c1.metric("Upper Band", f"${s['bb_upper']}")
c2.metric("Middle (SMA-20)", f"${s['bb_mid']}")
c3.metric("Lower Band", f"${s['bb_lower']}")
c4.metric("%B Position", f"{bb_pct:.1f}%",
           help="0% = at lower band · 100% = at upper band · >100% = above upper band")

# %B progress bar
st.markdown(
    f"""
    <div style="margin-top:8px">
        <div style="font-size:12px;color:#888;margin-bottom:4px">%B Band Position</div>
        <div style="background:#E8E6E0;border-radius:5px;height:10px;overflow:hidden">
            <div style="width:{min(max(bb_pct,0),100):.1f}%;
                height:100%;background:#185FA5;border-radius:5px"></div>
        </div>
        <div style="display:flex;justify-content:space-between;
            font-size:10px;color:#888;margin-top:3px">
            <span>Lower Band</span><span>Mid</span><span>Upper Band</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
