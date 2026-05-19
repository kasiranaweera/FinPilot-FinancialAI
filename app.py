"""
app.py — FinPilot Home Page
Merged Home + Overview: analysis config, run pipeline, results dashboard.
"""
import os, sys, pathlib
ROOT = pathlib.Path(__file__).parent
sys.path.insert(0, str(ROOT))

import streamlit as st
from dotenv import load_dotenv
from config.settings import APP_TITLE, APP_ICON, APP_VERSION, DEFAULT_TICKER, DEFAULT_NEWS_COUNT, DEFAULT_GROQ_MODEL, GROQ_MODELS, PERIODS, RISK_DISCLAIMER, COLORS
from components.sidebar import render_sidebar
from components.ui_elements import disclaimer_box
from components.charts import price_chart
from utils.share import resolve_shared

load_dotenv()


# ═══════════════════════════════════════════════════════════════
# Pipeline runner (shared between first-run and re-run)
# ═══════════════════════════════════════════════════════════════
def _run_analysis_home(groq_key, av_key, ticker, period_label, news_count, model):
    from utils.data_fetcher import fetch_ohlcv, fetch_stock_info, fetch_news
    from utils.indicators import compute_indicators, build_summary
    from utils.llm_analyst import analyse_sentiment, generate_trade_signal
    from utils.models import SentimentBatch
    from groq import Groq

    if not groq_key:
        st.error("❌ Groq API key is required.")
        return
    if not ticker:
        st.error("❌ Please enter a ticker symbol.")
        return

    st.session_state["groq_key"] = groq_key
    st.session_state["av_key"]   = av_key
    st.session_state["cfg_model"] = model

    groq_client = Groq(api_key=groq_key)
    period = PERIODS[period_label]

    with st.status(f"🔄 Running analysis for **{ticker}**…", expanded=True) as status:
        st.write("📡 Fetching OHLCV data…")
        try:
            df_raw = fetch_ohlcv(ticker, period, av_key=av_key)
        except Exception as e:
            st.error(f"❌ Data fetch failed: {e}")
            return

        st.write("⚙️ Computing technical indicators…")
        df = compute_indicators(df_raw)

        st.write("🏢 Fetching company info…")
        stock_info = fetch_stock_info(ticker)
        summary = build_summary(df, ticker, pe_ratio=stock_info.get("pe_ratio"))

        st.write("📰 Fetching news headlines…")
        news = fetch_news(ticker, count=news_count)
        headlines = [n["title"] for n in news if n.get("title")]

        if headlines:
            st.write(f"🤖 Analysing {len(headlines)} headlines with Groq…")
            try:
                sentiment_batch = analyse_sentiment(headlines, ticker, groq_client, model)
            except Exception as e:
                st.warning(f"⚠️ Sentiment analysis failed: {e}")
                sentiment_batch = SentimentBatch(results=[], overall_score=0.0,
                    total_headlines=0, positive_count=0, negative_count=0, neutral_count=0)
        else:
            sentiment_batch = SentimentBatch(results=[], overall_score=0.0,
                total_headlines=0, positive_count=0, negative_count=0, neutral_count=0)

        st.write("📊 Generating trade signal…")
        try:
            trade_signal = generate_trade_signal(summary, sentiment_batch, groq_client, model)
        except Exception as e:
            st.error(f"❌ Trade signal failed: {e}")
            return

        st.session_state.update({
            "df": df, "summary": summary, "stock_info": stock_info,
            "news": news, "sentiment_batch": sentiment_batch,
            "trade_signal": trade_signal,
        })
        status.update(label=f"✅ Analysis complete for **{ticker}**!", state="complete")



st.set_page_config(page_title=f"Home | {APP_TITLE}", page_icon=APP_ICON, layout="wide", initial_sidebar_state="expanded")

resolve_shared()
render_sidebar("Home")

# ── Global CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
  h2,h3{color:#185FA5}
  /* Config form cards */
  .cfg-card{background:#fff;border:1px solid #E8E6E0;border-radius:14px;padding:24px 26px;margin-bottom:16px}
  .cfg-card-title{font-size:13px;font-weight:700;color:#185FA5;text-transform:uppercase;letter-spacing:.5px;margin-bottom:14px;display:flex;align-items:center;gap:8px}
  /* KPI grid */
  .fp-kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:24px}
  .fp-kpi{background:#fff;border:1px solid #E8E6E0;border-radius:14px;padding:18px 16px;text-align:center;transition:box-shadow .2s,transform .15s}
  .fp-kpi:hover{box-shadow:0 6px 20px rgba(24,95,165,.1);transform:translateY(-2px)}
  .fp-kpi-label{font-size:10px;color:#888;text-transform:uppercase;letter-spacing:.6px;margin-bottom:6px}
  .fp-kpi-value{font-size:22px;font-weight:700;color:#2C2C2A;line-height:1.1}
  .fp-kpi-sub{font-size:11px;color:#888;margin-top:3px}
  /* Hero */
  .fp-hero{background:linear-gradient(135deg,#0d2b4e 0%,#185FA5 55%,#1D9E75 100%);border-radius:18px;padding:36px 40px;margin-bottom:24px;color:#fff;position:relative;overflow:hidden}
  .fp-hero::before{content:"";position:absolute;right:-40px;top:-40px;width:240px;height:240px;background:rgba(255,255,255,.05);border-radius:50%}
  .fp-hero::after{content:"";position:absolute;right:60px;bottom:-60px;width:160px;height:160px;background:rgba(255,255,255,.04);border-radius:50%}
  .fp-hero-ticker{font-size:12px;opacity:.6;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:2px}
  .fp-hero-company{font-size:28px;font-weight:800;line-height:1.15;margin-bottom:4px}
  .fp-hero-sub{font-size:13px;opacity:.7;margin-bottom:20px}
  .fp-signal-pill{display:inline-block;padding:5px 20px;border-radius:30px;font-size:18px;font-weight:800;margin-right:10px}
  /* Section header */
  .fp-section-hd{display:flex;align-items:center;gap:10px;margin:28px 0 14px}
  .fp-section-hd-line{flex:1;height:1px;background:#E8E6E0}
  .fp-section-hd-text{font-size:11px;font-weight:700;color:#888;text-transform:uppercase;letter-spacing:.8px;white-space:nowrap}
  /* Indicator row */
  .ind-row{display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid #F0EEE8}
  .ind-label{font-size:13px;color:#555;font-weight:500}
  .ind-val{font-size:13px;font-weight:700;color:#2C2C2A}
  .ind-note{font-size:11px;color:#888;text-align:right}
  /* Empty state */
  .fp-empty{text-align:center;padding:60px 20px;color:#888}
  .fp-empty-icon{font-size:52px;margin-bottom:16px}
  .fp-empty-title{font-size:20px;font-weight:700;color:#2C2C2A;margin-bottom:8px}
  .fp-empty-sub{font-size:14px;color:#888;max-width:380px;margin:0 auto}
  /* Run button */
  div[data-testid="stButton"] > button[kind="primary"]{
    background:linear-gradient(135deg,#185FA5,#1D4F8A)!important;
    color:#fff!important;border:none!important;border-radius:10px!important;
    font-weight:700!important;font-size:15px!important;
    padding:12px 0!important;letter-spacing:.3px!important;
    box-shadow:0 4px 14px rgba(24,95,165,.3)!important;
    transition:all .2s!important;
  }
  div[data-testid="stButton"] > button[kind="primary"]:hover{
    box-shadow:0 6px 20px rgba(24,95,165,.45)!important;
    transform:translateY(-1px)!important;
  }
</style>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# SECTION A — Pre-analysis: Configuration form
# ═══════════════════════════════════════════════════════════════
if "summary" not in st.session_state:

    st.markdown("""
<div class="fp-empty">
  <div class="fp-empty-icon">📈</div>
  <div class="fp-empty-title">Welcome to FinPilot</div>
  <div class="fp-empty-sub">Configure your research parameters below and run the AI-powered analysis to get started.</div>
</div>""", unsafe_allow_html=True)

    st.markdown('<div class="fp-section-hd"><div class="fp-section-hd-line"></div><div class="fp-section-hd-text">Analysis Configuration</div><div class="fp-section-hd-line"></div></div>', unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        # # API Keys card
        # st.markdown('<div class="cfg-card"><div class="cfg-card-title">🔑 API Keys</div>', unsafe_allow_html=True)
        # groq_key = st.text_input("Groq API Key", value=os.environ.get("GROQ_API_KEY",""), type="password",
        #                           help="Free at console.groq.com", placeholder="gsk_...")
        # av_key   = st.text_input("Alpha Vantage Key (optional)", value=os.environ.get("AV_API_KEY",""),
        #                           type="password", help="Fallback data source — alphavantage.co",
        #                           placeholder="Optional")
        # st.markdown('</div>', unsafe_allow_html=True)

        # Model card
        st.markdown('<div class="cfg-card"><div class="cfg-card-title">🤖 AI Model</div>', unsafe_allow_html=True)
        model = st.selectbox("Groq Model", GROQ_MODELS, index=0,
                              help="llama-3.3-70b is recommended for best quality")
        news_count   = st.slider("News Headlines to Analyse", 5, 25, DEFAULT_NEWS_COUNT)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        # Ticker card
        st.markdown('<div class="cfg-card"><div class="cfg-card-title">📊 Stock Configuration</div>', unsafe_allow_html=True)
        ticker = st.text_input("Ticker Symbol", value=DEFAULT_TICKER,
                                placeholder="AAPL, TSLA, MSFT…").upper().strip()
        period_label = st.selectbox("Data Period", list(PERIODS.keys()), index=2)
        st.markdown('</div>', unsafe_allow_html=True)

    # Run button
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    run = st.button("🚀  Run Analysis", type="primary", use_container_width=True)

    if run:
        # Get API keys from session state (set in Settings page)
        groq_key = st.session_state.get("groq_key", os.environ.get("GROQ_API_KEY", ""))
        av_key = st.session_state.get("av_key", os.environ.get("AV_API_KEY", ""))
        _run_analysis_home(groq_key, av_key, ticker, period_label, news_count, model)
        st.rerun()

    st.stop()


# ═══════════════════════════════════════════════════════════════
# SECTION B — Post-analysis: Full dashboard
# ═══════════════════════════════════════════════════════════════
s     = st.session_state["summary"]
sig   = st.session_state["trade_signal"]
info  = st.session_state.get("stock_info", {})
batch = st.session_state.get("sentiment_batch")
df    = st.session_state.get("df")

sig_colors   = {"Buy":"#1D9E75","Hold":"#BA7517","Sell":"#D85A30"}
sig_bg_map   = {"Buy":"rgba(29,158,117,.22)","Hold":"rgba(186,117,23,.22)","Sell":"rgba(216,90,48,.22)"}
sig_col      = sig_colors.get(sig.signal,"#888")
sig_bg       = sig_bg_map.get(sig.signal,"rgba(136,136,136,.2)")

company = info.get("name", s["ticker"])
sector  = info.get("sector","")
sub     = f"{sector}  ·  {info.get('industry','')}  ·  As of {s['as_of_date']}" if sector else f"As of {s['as_of_date']}"

# ── Hero ────────────────────────────────────────────────────────
st.markdown(f"""
<div class="fp-hero">
  <div class="fp-hero-ticker">{s['ticker']} &nbsp;·&nbsp; {s['data_points']:,} trading days</div>
  <div class="fp-hero-company">{company}</div>
  <div class="fp-hero-sub">{sub}</div>
  <div>
    <span class="fp-signal-pill" style="background:{sig_bg};color:{sig_col}">{sig.signal}</span>
    <span style="font-size:13px;opacity:.85">{sig.confidence:.0%} confidence &nbsp;·&nbsp; {sig.risk_level} risk</span>
  </div>
  <div style="margin-top:12px;font-size:13px;opacity:.75;max-width:680px;line-height:1.7">
    {sig.justification[:260]}{"…" if len(sig.justification)>260 else ""}
  </div>
</div>""", unsafe_allow_html=True)

# ── KPI row ─────────────────────────────────────────────────────
ytd_c   = "#1D9E75" if s["ytd_return_pct"]>=0 else "#D85A30"
ytd_arr = "▲" if s["ytd_return_pct"]>=0 else "▼"
rsi_v   = s["rsi_14"] or 0
rsi_c   = "#D85A30" if rsi_v>70 else "#1D9E75" if rsi_v<30 else "#185FA5"
sent_s  = batch.overall_score if batch else 0
sent_l  = "Bullish" if sent_s>0.1 else "Bearish" if sent_s<-0.1 else "Neutral"
sent_c  = "#1D9E75" if sent_s>0.1 else "#D85A30" if sent_s<-0.1 else "#888"

st.markdown(f"""
<div class="fp-kpi-grid">
  <div class="fp-kpi">
    <div class="fp-kpi-label">Current Price</div>
    <div class="fp-kpi-value">${s['current_price']}</div>
    <div class="fp-kpi-sub" style="color:{ytd_c}">{ytd_arr} {s['ytd_return_pct']:+.1f}% YTD</div>
  </div>
  <div class="fp-kpi">
    <div class="fp-kpi-label">52-Week Range</div>
    <div class="fp-kpi-value" style="font-size:16px">${s['52w_low']} – ${s['52w_high']}</div>
    <div class="fp-kpi-sub">Low / High</div>
  </div>
  <div class="fp-kpi">
    <div class="fp-kpi-label">P/E Ratio</div>
    <div class="fp-kpi-value">{s['pe_ratio'] or 'N/A'}</div>
    <div class="fp-kpi-sub">Trailing P/E</div>
  </div>
  <div class="fp-kpi">
    <div class="fp-kpi-label">RSI-14</div>
    <div class="fp-kpi-value" style="color:{rsi_c}">{rsi_v}</div>
    <div class="fp-kpi-sub">{s['rsi_interpretation']}</div>
  </div>
  <div class="fp-kpi">
    <div class="fp-kpi-label">Sentiment</div>
    <div class="fp-kpi-value" style="color:{sent_c};font-size:16px">{sent_l}</div>
    <div class="fp-kpi-sub">{f'{sent_s:+.3f} score' if batch else 'N/A'}</div>
  </div>
  <div class="fp-kpi">
    <div class="fp-kpi-label">SMA Signal</div>
    <div class="fp-kpi-value" style="font-size:14px">{s['sma_cross']}</div>
    <div class="fp-kpi-sub">{s['momentum_signal'].capitalize()} momentum</div>
  </div>
</div>""", unsafe_allow_html=True)

# ── Price chart ──────────────────────────────────────────────────
st.markdown('<div class="fp-section-hd"><div class="fp-section-hd-line"></div><div class="fp-section-hd-text">Price Chart</div><div class="fp-section-hd-line"></div></div>', unsafe_allow_html=True)
if df is not None:
    show_sma = st.toggle("SMA Overlays", value=True)
    st.plotly_chart(price_chart(df, s["ticker"], show_sma=show_sma), use_container_width=True)

# ── Technical snapshot ───────────────────────────────────────────
st.markdown('<div class="fp-section-hd"><div class="fp-section-hd-line"></div><div class="fp-section-hd-text">Technical Snapshot</div><div class="fp-section-hd-line"></div></div>', unsafe_allow_html=True)
sma50_dir  = "🟢 Above" if s["price_vs_sma50"]=="above" else "🔴 Below"
sma200_dir = "🟢 Above" if s["price_vs_sma200"]=="above" else "🔴 Below"

tc1, tc2 = st.columns(2, gap="large")
with tc1:
    st.markdown(f"""
<div style="background:#fff;border:1px solid #E8E6E0;border-radius:14px;padding:20px 22px">
  <div style="font-size:12px;font-weight:700;color:#185FA5;text-transform:uppercase;letter-spacing:.5px;margin-bottom:12px">Moving Averages</div>
  <div class="ind-row"><span class="ind-label">SMA-50</span><span class="ind-val">${s['sma_50']}</span><span class="ind-note">{sma50_dir}</span></div>
  <div class="ind-row"><span class="ind-label">SMA-200</span><span class="ind-val">${s['sma_200']}</span><span class="ind-note">{sma200_dir}</span></div>
  <div class="ind-row" style="border:none"><span class="ind-label">Cross Signal</span><span class="ind-val" style="font-size:12px">{s['sma_cross']}</span><span></span></div>
</div>""", unsafe_allow_html=True)
with tc2:
    bb_pct = (s.get("bb_pct_b") or 0)*100
    macd_c = "#1D9E75" if s.get("macd",0) and s.get("macd_signal",0) and s["macd"]>s["macd_signal"] else "#D85A30"
    st.markdown(f"""
<div style="background:#fff;border:1px solid #E8E6E0;border-radius:14px;padding:20px 22px">
  <div style="font-size:12px;font-weight:700;color:#185FA5;text-transform:uppercase;letter-spacing:.5px;margin-bottom:12px">Oscillators & Bands</div>
  <div class="ind-row"><span class="ind-label">RSI (14)</span><span class="ind-val" style="color:{rsi_c}">{rsi_v}</span><span class="ind-note">{s['rsi_interpretation']}</span></div>
  <div class="ind-row"><span class="ind-label">MACD</span><span class="ind-val" style="color:{macd_c}">{s['macd']}</span><span class="ind-note">{s['macd_status']}</span></div>
  <div class="ind-row" style="border:none"><span class="ind-label">BB %B</span><span class="ind-val">{bb_pct:.1f}%</span><span class="ind-note">${s['bb_lower']} – ${s['bb_upper']}</span></div>
</div>""", unsafe_allow_html=True)

# ── Company description ──────────────────────────────────────────
if info.get("description"):
    st.markdown('<div class="fp-section-hd"><div class="fp-section-hd-line"></div><div class="fp-section-hd-text">About</div><div class="fp-section-hd-line"></div></div>', unsafe_allow_html=True)
    with st.expander(f"About {company}", expanded=False):
        st.write(info["description"])

# ── Re-run controls ──────────────────────────────────────────────
st.markdown('<div class="fp-section-hd"><div class="fp-section-hd-line"></div><div class="fp-section-hd-text">Run New Analysis</div><div class="fp-section-hd-line"></div></div>', unsafe_allow_html=True)

rc1, rc2, rc3 = st.columns([2,2,1], gap="small")
with rc1:
    new_ticker = st.text_input("Ticker", value=s["ticker"], label_visibility="collapsed",
                                placeholder="Ticker…").upper().strip()
with rc2:
    new_period = st.selectbox("Period", list(PERIODS.keys()),
                               index=list(PERIODS.keys()).index("1 Year"),
                               label_visibility="collapsed")

with rc3:
    rerun = st.button("▶ Run", type="primary", use_container_width=True)

if rerun:
    _run_analysis_home(
        groq_key,
        st.session_state.get("av_key",""),
        new_ticker, new_period,
        DEFAULT_NEWS_COUNT,
        st.session_state.get("cfg_model", DEFAULT_GROQ_MODEL),
    )
    st.rerun()

disclaimer_box(RISK_DISCLAIMER)
