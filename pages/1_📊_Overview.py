"""
pages/1_📊_Overview.py
Stock snapshot — price, indicators, performance summary.
"""

import streamlit as st
from components import price_chart, metric_card

st.set_page_config(page_title="Overview", page_icon="📊", layout="wide")
st.title("📊 Stock Overview")

if "df" not in st.session_state or "summary" not in st.session_state:
    st.info("👈 Configure your ticker in the **Home** page and click **Run Analysis**.")
    st.stop()

df = st.session_state["df"]
s = st.session_state["summary"]
info = st.session_state.get("stock_info", {})

# Company header
st.markdown(
    f"### {info.get('name', s['ticker'])}  `{s['ticker']}`  "
    f"·  {info.get('sector', '')}  ·  {info.get('industry', '')}"
)
st.caption(f"Data as of **{s['as_of_date']}** · {s['data_points']:,} trading days")

st.divider()

# Key metrics row
c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1:
    metric_card("Current Price", f"${s['current_price']}")
with c2:
    metric_card("52-Week High", f"${s['52w_high']}")
with c3:
    metric_card("52-Week Low", f"${s['52w_low']}")
with c4:
    positive = s["ytd_return_pct"] >= 0
    metric_card("YTD Return", f"{s['ytd_return_pct']:+.1f}%", delta_positive=positive)
with c5:
    metric_card("P/E Ratio", str(s["pe_ratio"]) if s["pe_ratio"] else "N/A")
with c6:
    metric_card("RSI (14)", str(s["rsi_14"]))

st.write("")

# Candlestick chart
show_sma = st.checkbox("Show SMA overlays", value=True)
st.plotly_chart(price_chart(df, s["ticker"], show_sma=show_sma), use_container_width=True)

# Indicator snapshot
st.subheader("Technical Snapshot")
col1, col2 = st.columns(2)

with col1:
    sma50_dir = "🟢 Above" if s["price_vs_sma50"] == "above" else "🔴 Below"
    sma200_dir = "🟢 Above" if s["price_vs_sma200"] == "above" else "🔴 Below"
    st.markdown(
        f"""
| Indicator | Value | Note |
|-----------|-------|------|
| SMA-50 | ${s['sma_50']} | Price {sma50_dir} |
| SMA-200 | ${s['sma_200']} | {s['sma_cross']} |
| RSI-14 | {s['rsi_14']} | {s['rsi_interpretation']} |
        """
    )

with col2:
    st.markdown(
        f"""
| Indicator | Value | Note |
|-----------|-------|------|
| MACD | {s['macd']} | {s['macd_status']} |
| MACD Signal | {s['macd_signal']} | Histogram: {s['macd_hist']} |
| BB Upper / Lower | ${s['bb_upper']} / ${s['bb_lower']} | Mid: ${s['bb_mid']} |
        """
    )

# Company description
if info.get("description"):
    with st.expander("📋 Company Description"):
        st.write(info["description"])
