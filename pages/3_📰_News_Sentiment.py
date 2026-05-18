"""
pages/3_📰_News_Sentiment.py
LLM-powered headline sentiment analysis.
"""

import streamlit as st
from components import sentiment_badge, sentiment_bar

st.set_page_config(page_title="News & Sentiment", page_icon="📰", layout="wide")
st.title("📰 News Sentiment Analysis")

if "sentiment_batch" not in st.session_state:
    st.info("👈 Run analysis from the **Home** page first.")
    st.stop()

batch = st.session_state["sentiment_batch"]
news = st.session_state.get("news", [])
s = st.session_state["summary"]

# Overall score banner
score = batch.overall_score
if score > 0.1:
    label = "📈 Bullish"
    score_color = "#1D9E75"
elif score < -0.1:
    label = "📉 Bearish"
    score_color = "#D85A30"
else:
    label = "⚖️ Neutral"
    score_color = "#888780"

st.markdown(
    f"""
    <div style="background:#fff;border:1px solid #E8E6E0;border-radius:14px;
        padding:20px 24px;margin-bottom:20px;display:flex;align-items:center;gap:24px">
        <div>
            <div style="font-size:13px;color:#888;text-transform:uppercase;
                letter-spacing:0.5px">Overall Sentiment Score</div>
            <div style="font-size:42px;font-weight:700;color:{score_color}">{score:+.3f}</div>
            <div style="font-size:16px;font-weight:600;color:{score_color}">{label}</div>
        </div>
        <div style="flex:1">
            <div style="font-size:12px;color:#888;margin-bottom:8px">
                {batch.total_headlines} headlines analysed
            </div>
    """,
    unsafe_allow_html=True,
)
sentiment_bar(batch.positive_count, batch.negative_count, batch.neutral_count)
st.markdown("</div></div>", unsafe_allow_html=True)

st.divider()

# Per-headline results
st.subheader(f"Headline Breakdown — {s['ticker']}")

tab1, tab2 = st.tabs(["🤖 AI Sentiment Analysis", "📡 Raw News Feed"])

with tab1:
    for item in batch.results:
        badge = sentiment_badge(item.sentiment)
        conf_pct = int(item.confidence * 100)
        conf_color = "#1D9E75" if conf_pct >= 70 else "#BA7517" if conf_pct >= 50 else "#D85A30"
        st.markdown(
            f"""
            <div style="border:1px solid #E8E6E0;border-radius:10px;
                padding:14px 16px;margin-bottom:10px;background:#fff">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
                    {badge}
                    <span style="font-size:12px;color:{conf_color};font-weight:600">
                        {conf_pct}% confidence
                    </span>
                </div>
                <div style="font-size:14px;color:#2C2C2A;font-weight:500;margin-bottom:4px">
                    {item.headline}
                </div>
                <div style="font-size:12px;color:#888;font-style:italic">
                    💬 {item.brief_reason}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

with tab2:
    if news:
        for item in news:
            pub = item.get("publisher", "")
            link = item.get("link", "#")
            title = item.get("title", "")
            st.markdown(
                f"""
                <div style="border-bottom:1px solid #E8E6E0;padding:10px 0">
                    <a href="{link}" target="_blank"
                        style="font-size:14px;color:#185FA5;text-decoration:none;font-weight:500">
                        {title}
                    </a>
                    <div style="font-size:11px;color:#888;margin-top:3px">{pub}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("No raw news data available.")
