"""
app.py  — Main entry point for the Financial AI Streamlit Dashboard.

Run:  streamlit run app.py
"""

import os
import sys
import pathlib

# Ensure project root is on the path so pages can import utils/components/config
ROOT = pathlib.Path(__file__).parent
sys.path.insert(0, str(ROOT))

import streamlit as st
from dotenv import load_dotenv

from config.settings import (
    APP_TITLE, APP_ICON, APP_VERSION,
    DEFAULT_TICKER, DEFAULT_PERIOD, DEFAULT_NEWS_COUNT,
    DEFAULT_GROQ_MODEL, GROQ_MODELS, PERIODS, COLORS, RISK_DISCLAIMER,
)
from utils.data_fetcher import fetch_ohlcv, fetch_stock_info, fetch_news
from utils.indicators import compute_indicators, build_summary
from utils.llm_analyst import analyse_sentiment, generate_trade_signal
from components.ui_elements import disclaimer_box

load_dotenv()

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Global CSS — top nav + hide sidebar page links
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
        /* Sidebar styling */
        [data-testid="stSidebar"] { background: #F5F4F0; }

        /* Hide the auto-generated page links from sidebar */
        [data-testid="stSidebarNav"] { display: none; }

        /* Run button */
        .stButton > button {
            background: #185FA5;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            width: 100%;
            padding: 10px;
        }
        .stButton > button:hover { background: #1D4F8A; }

        /* Give space below the fixed top nav */
        .block-container { padding-top: 4.5rem; }

        h1 { color: #2C2C2A; }
        h2, h3 { color: #185FA5; }

        /* ── Top navigation bar ── */
        .finpilot-topnav {
            position: fixed;
            top: 0; left: 0; right: 0;
            z-index: 999;
            background: #FFFFFF;
            border-bottom: 2px solid #E8E6E0;
            display: flex;
            align-items: center;
            padding: 0 24px;
            height: 52px;
            gap: 6px;
            box-shadow: 0 1px 6px rgba(0,0,0,0.07);
        }
        .finpilot-topnav .brand {
            font-size: 16px;
            font-weight: 800;
            color: #185FA5;
            margin-right: 24px;
            white-space: nowrap;
            letter-spacing: -0.3px;
        }
        .finpilot-topnav .brand span { color: #1D9E75; }
        .finpilot-topnav a {
            text-decoration: none;
            color: #5F5E5A;
            font-size: 13px;
            font-weight: 500;
            padding: 6px 14px;
            border-radius: 6px;
            transition: background 0.15s, color 0.15s;
            white-space: nowrap;
        }
        .finpilot-topnav a:hover {
            background: #EEF3FA;
            color: #185FA5;
        }
        .finpilot-topnav a.active {
            background: #185FA5;
            color: #fff !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Inject top nav (Streamlit page links use ?page= routing in multi-page apps)
st.markdown(
    f"""
    <div class="finpilot-topnav">
        <div class="brand">Fin<span>Pilot</span>-FinancialAI</div>
        <a href="/" target="_self">🏠 Home</a>
        <a href="/Overview" target="_self">📊 Overview</a>
        <a href="/Technical_Analysis" target="_self">📈 Technical</a>
        <a href="/News_Sentiment" target="_self">📰 Sentiment</a>
        <a href="/AI_Signal" target="_self">🤖 AI Signal</a>
        <a href="/Notebook" target="_self">📓 Notebook</a>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar — configuration
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        f"## {APP_ICON} {APP_TITLE}\n*v{APP_VERSION}*"
    )
    st.divider()

    st.subheader("🔑 API Keys")
    groq_key = st.text_input(
        "Groq API Key",
        value=os.environ.get("GROQ_API_KEY", ""),
        type="password",
        help="Get a free key at console.groq.com",
    )
    av_key = st.text_input(
        "Alpha Vantage Key (optional)",
        value=os.environ.get("AV_API_KEY", ""),
        type="password",
        help="Free fallback data source — alphavantage.co",
    )

    st.divider()
    st.subheader("⚙️ Configuration")
    ticker = st.text_input("Ticker Symbol", value=DEFAULT_TICKER).upper().strip()
    period_label = st.selectbox("Data Period", list(PERIODS.keys()), index=2)
    period = PERIODS[period_label]
    news_count = st.slider("News Headlines", min_value=5, max_value=25, value=DEFAULT_NEWS_COUNT)
    model = st.selectbox("Groq Model", GROQ_MODELS)

    st.divider()
    run = st.button("🚀 Run Analysis", use_container_width=True)

# ---------------------------------------------------------------------------
# Home content (before analysis runs)
# ---------------------------------------------------------------------------
st.markdown(f"# {APP_ICON} FinPilot-FinancialAI — Equity Research Dashboard")
st.markdown(
    "An **LLM-powered equity research pipeline** built on the "
    "[FinPilot-FinancialAI notebook](/Notebook). "
    "Configure your ticker in the sidebar and click **Run Analysis**."
)

col1, col2, col3, col4 = st.columns(4)
col1.markdown("**📊 Overview**\nPrice, metrics, candlestick chart")
col2.markdown("**📈 Technical**\nRSI, MACD, Bollinger Bands")
col3.markdown("**📰 Sentiment**\nLLM headline analysis")
col4.markdown("**🤖 AI Signal**\nBuy / Hold / Sell recommendation")

st.divider()

# ---------------------------------------------------------------------------
# Run analysis pipeline
# ---------------------------------------------------------------------------
if run:
    if not groq_key:
        st.error("❌ Groq API key is required. Enter it in the sidebar.")
        st.stop()
    if not ticker:
        st.error("❌ Please enter a ticker symbol.")
        st.stop()

    from groq import Groq
    groq_client = Groq(api_key=groq_key)

    with st.status(f"🔄 Running analysis for **{ticker}**...", expanded=True) as status:

        # 1. OHLCV data
        st.write("📡 Fetching OHLCV data...")
        try:
            df_raw = fetch_ohlcv(ticker, period, av_key=av_key)
        except Exception as e:
            st.error(f"❌ Data fetch failed: {e}")
            st.stop()

        # 2. Indicators
        st.write("⚙️ Computing technical indicators...")
        df = compute_indicators(df_raw)

        # 3. Stock info
        st.write("🏢 Fetching company info...")
        stock_info = fetch_stock_info(ticker)

        # 4. Summary dict
        summary = build_summary(df, ticker, pe_ratio=stock_info.get("pe_ratio"))

        # 5. News
        st.write("📰 Fetching news headlines...")
        news = fetch_news(ticker, count=news_count)
        headlines = [n["title"] for n in news if n.get("title")]

        # 6. Sentiment
        if headlines:
            st.write(f"🤖 Analysing {len(headlines)} headlines with Groq...")
            try:
                sentiment_batch = analyse_sentiment(headlines, ticker, groq_client, model)
            except Exception as e:
                st.warning(f"⚠️ Sentiment analysis failed: {e}")
                from utils.models import SentimentBatch
                sentiment_batch = SentimentBatch(
                    results=[], overall_score=0.0,
                    total_headlines=0, positive_count=0,
                    negative_count=0, neutral_count=0,
                )
        else:
            st.warning("No headlines found — skipping sentiment.")
            from utils.models import SentimentBatch
            sentiment_batch = SentimentBatch(
                results=[], overall_score=0.0,
                total_headlines=0, positive_count=0,
                negative_count=0, neutral_count=0,
            )

        # 7. Trade signal
        st.write("📊 Generating trade signal...")
        try:
            trade_signal = generate_trade_signal(summary, sentiment_batch, groq_client, model)
        except Exception as e:
            st.error(f"❌ Trade signal failed: {e}")
            st.stop()

        # Save to session state
        st.session_state["df"] = df
        st.session_state["summary"] = summary
        st.session_state["stock_info"] = stock_info
        st.session_state["news"] = news
        st.session_state["sentiment_batch"] = sentiment_batch
        st.session_state["trade_signal"] = trade_signal

        status.update(label=f"✅ Analysis complete for **{ticker}**!", state="complete")

    # Quick result preview on home page
    st.success(
        f"**{ticker}** · {summary['as_of_date']} · "
        f"Price: **${summary['current_price']}** · "
        f"Signal: **{trade_signal.signal}** ({trade_signal.confidence:.0%} confidence)"
    )
    st.info("👈 Navigate the pages in the sidebar to explore the full analysis.")

# Show previous results if available
elif "summary" in st.session_state:
    s = st.session_state["summary"]
    sig = st.session_state["trade_signal"]
    st.success(
        f"Showing cached results for **{s['ticker']}** · {s['as_of_date']} · "
        f"Price: **${s['current_price']}** · Signal: **{sig.signal}**"
    )
    st.info("👈 Use the sidebar to run a new analysis or navigate pages.")

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
disclaimer_box(RISK_DISCLAIMER)

st.markdown(
    f"""
    <div style="text-align:center;font-size:11px;color:#888;margin-top:32px">
        FinPilot · Financial AI Dashboard v{APP_VERSION} ·
        Built with Streamlit + Groq Llama-3 + yfinance
    </div>
    """,
    unsafe_allow_html=True,
)