"""
components/sidebar.py
Shared sidebar that renders on EVERY page.

Includes: API keys, ticker config, and the Run Analysis button.
Because this runs on every page, st.session_state data is always
available after a successful analysis regardless of which page
the user navigates to.
"""

import os
import sys
import pathlib

import streamlit as st

ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from config.settings import (
    APP_TITLE, APP_ICON, APP_VERSION,
    DEFAULT_TICKER, DEFAULT_NEWS_COUNT,
    DEFAULT_GROQ_MODEL, GROQ_MODELS, PERIODS,
)


def render_sidebar() -> bool:
    """
    Renders the sidebar on any page and returns True if a new analysis
    was just triggered (so the caller can re-render if needed).
    """
    with st.sidebar:
        st.markdown(f"## {APP_ICON} {APP_TITLE}\n*v{APP_VERSION}*")
        st.divider()

        st.subheader("🔑 API Keys")
        groq_key = st.text_input(
            "Groq API Key",
            value=st.session_state.get("groq_key", os.environ.get("GROQ_API_KEY", "")),
            type="password",
            key="sidebar_groq_key",
            help="Get a free key at console.groq.com",
        )
        av_key = st.text_input(
            "Alpha Vantage Key (optional)",
            value=st.session_state.get("av_key", os.environ.get("AV_API_KEY", "")),
            type="password",
            key="sidebar_av_key",
            help="Free fallback data source — alphavantage.co",
        )

        # Persist keys to session_state so they survive navigation
        st.session_state["groq_key"] = groq_key
        st.session_state["av_key"] = av_key

        st.divider()
        st.subheader("⚙️ Configuration")

        ticker_sb = st.text_input(
            "Ticker Symbol",
            value=st.session_state.get("cfg_ticker", DEFAULT_TICKER),
            key="sidebar_ticker",
        ).upper().strip()

        period_label_sb = st.selectbox(
            "Data Period",
            list(PERIODS.keys()),
            index=list(PERIODS.keys()).index(
                st.session_state.get("cfg_period_label", "1 Year")
            ),
            key="sidebar_period",
        )

        news_count_sb = st.slider(
            "News Headlines",
            min_value=5,
            max_value=25,
            value=st.session_state.get("cfg_news_count", DEFAULT_NEWS_COUNT),
            key="sidebar_news",
        )

        model_sb = st.selectbox(
            "Groq Model",
            GROQ_MODELS,
            index=GROQ_MODELS.index(
                st.session_state.get("cfg_model", DEFAULT_GROQ_MODEL)
            ) if st.session_state.get("cfg_model", DEFAULT_GROQ_MODEL) in GROQ_MODELS else 0,
            key="sidebar_model",
        )

        # Persist config to session_state
        st.session_state["cfg_ticker"] = ticker_sb
        st.session_state["cfg_period_label"] = period_label_sb
        st.session_state["cfg_news_count"] = news_count_sb
        st.session_state["cfg_model"] = model_sb

        st.divider()
        run_clicked = st.button(
            "🚀 Run Analysis",
            use_container_width=True,
            key="sidebar_run_btn",
            type="primary",
        )

        # Show cached ticker if analysis already exists
        if "summary" in st.session_state:
            st.success(
                f"✅ Data loaded: **{st.session_state['summary']['ticker']}**\n\n"
                f"_{st.session_state['summary']['as_of_date']}_"
            )

    if run_clicked:
        _run_analysis(groq_key, av_key, ticker_sb, period_label_sb, news_count_sb, model_sb)
        return True
    return False


def _run_analysis(groq_key, av_key, ticker, period_label, news_count, model):
    """Fetch data, compute indicators, run LLM analysis and store to session_state."""
    from utils.data_fetcher import fetch_ohlcv, fetch_stock_info, fetch_news
    from utils.indicators import compute_indicators, build_summary
    from utils.llm_analyst import analyse_sentiment, generate_trade_signal
    from utils.models import SentimentBatch
    from groq import Groq

    period = PERIODS[period_label]

    if not groq_key:
        st.error("❌ Groq API key is required. Enter it in the sidebar.")
        return
    if not ticker:
        st.error("❌ Please enter a ticker symbol.")
        return

    groq_client = Groq(api_key=groq_key)

    with st.status(f"🔄 Running analysis for **{ticker}**...", expanded=True) as status:

        st.write("📡 Fetching OHLCV data...")
        try:
            df_raw = fetch_ohlcv(ticker, period, av_key=av_key)
        except Exception as e:
            st.error(f"❌ Data fetch failed: {e}")
            return

        st.write("⚙️ Computing technical indicators...")
        df = compute_indicators(df_raw)

        st.write("🏢 Fetching company info...")
        stock_info = fetch_stock_info(ticker)

        summary = build_summary(df, ticker, pe_ratio=stock_info.get("pe_ratio"))

        st.write("📰 Fetching news headlines...")
        news = fetch_news(ticker, count=news_count)
        headlines = [n["title"] for n in news if n.get("title")]

        if headlines:
            st.write(f"🤖 Analysing {len(headlines)} headlines with Groq...")
            try:
                sentiment_batch = analyse_sentiment(headlines, ticker, groq_client, model)
            except Exception as e:
                st.warning(f"⚠️ Sentiment analysis failed: {e}")
                sentiment_batch = SentimentBatch(
                    results=[], overall_score=0.0,
                    total_headlines=0, positive_count=0,
                    negative_count=0, neutral_count=0,
                )
        else:
            st.warning("No headlines found — skipping sentiment.")
            sentiment_batch = SentimentBatch(
                results=[], overall_score=0.0,
                total_headlines=0, positive_count=0,
                negative_count=0, neutral_count=0,
            )

        st.write("📊 Generating trade signal...")
        try:
            trade_signal = generate_trade_signal(summary, sentiment_batch, groq_client, model)
        except Exception as e:
            st.error(f"❌ Trade signal failed: {e}")
            return

        # ── Persist everything to session_state ──
        st.session_state["df"] = df
        st.session_state["summary"] = summary
        st.session_state["stock_info"] = stock_info
        st.session_state["news"] = news
        st.session_state["sentiment_batch"] = sentiment_batch
        st.session_state["trade_signal"] = trade_signal

        status.update(
            label=f"✅ Analysis complete for **{ticker}**!",
            state="complete",
        )
