"""
app.py  — Main entry point for the Financial AI Streamlit Dashboard.

Run:  streamlit run app.py
"""

import os
import sys
import pathlib

ROOT = pathlib.Path(__file__).parent
sys.path.insert(0, str(ROOT))

import streamlit as st
from dotenv import load_dotenv

from config.settings import (
    APP_TITLE, APP_ICON, APP_VERSION,
    DEFAULT_TICKER, PERIODS, RISK_DISCLAIMER,
    COLORS,
)
from components.ui_elements import disclaimer_box
from components.nav import render_nav
from components.sidebar import render_sidebar

load_dotenv()

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Global CSS
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
        /* Sidebar background */
        [data-testid="stSidebar"] { background: #F5F4F0; }

        /* Style buttons ONLY inside the main content area */
        [data-testid="stMain"] .stButton > button {
            background: #185FA5;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            width: 100%;
            padding: 10px;
        }
        [data-testid="stMain"] .stButton > button:hover { background: #1D4F8A; }

        h1 { color: #2C2C2A; }
        h2, h3 { color: #185FA5; }

        /* ── Landing page hero ── */
        .fp-hero {
            background: linear-gradient(135deg, #0d2b4e 0%, #185FA5 60%, #1D9E75 100%);
            border-radius: 20px;
            padding: 40px 48px;
            margin-bottom: 28px;
            color: #fff;
            position: relative;
            overflow: hidden;
        }
        .fp-hero::before {
            content: "";
            position: absolute;
            right: -60px; top: -60px;
            width: 280px; height: 280px;
            background: rgba(255,255,255,0.05);
            border-radius: 50%;
        }
        .fp-hero::after {
            content: "";
            position: absolute;
            right: 80px; bottom: -80px;
            width: 200px; height: 200px;
            background: rgba(255,255,255,0.04);
            border-radius: 50%;
        }
        .fp-hero-ticker  { font-size: 14px; opacity: .7; letter-spacing: 1px; text-transform:uppercase; margin-bottom:4px; }
        .fp-hero-company { font-size: 30px; font-weight: 800; line-height: 1.15; margin-bottom: 6px; }
        .fp-hero-sub     { font-size: 14px; opacity: .75; margin-bottom: 22px; }
        .fp-signal-pill  {
            display: inline-block;
            padding: 6px 22px;
            border-radius: 30px;
            font-size: 20px;
            font-weight: 800;
            letter-spacing: .5px;
            margin-right: 12px;
        }
        .fp-conf-text { font-size: 14px; opacity: .85; display: inline-block; vertical-align: middle; }

        /* ── KPI cards ── */
        .fp-kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 14px;
            margin-bottom: 28px;
        }
        .fp-kpi {
            background: #fff;
            border: 1px solid #E8E6E0;
            border-radius: 14px;
            padding: 18px 20px;
            text-align: center;
            transition: box-shadow .2s;
        }
        .fp-kpi:hover { box-shadow: 0 4px 16px rgba(24,95,165,.10); }
        .fp-kpi-label { font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: .5px; margin-bottom: 6px; }
        .fp-kpi-value { font-size: 24px; font-weight: 700; color: #2C2C2A; }
        .fp-kpi-sub   { font-size: 11px; color: #888; margin-top: 2px; }

        /* ── Section nav cards ── */
        .fp-nav-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
            gap: 14px;
            margin-bottom: 28px;
        }
        .fp-nav-card {
            background: #fff;
            border: 1.5px solid #E8E6E0;
            border-radius: 14px;
            padding: 20px;
            text-align: center;
            cursor: pointer;
            transition: border-color .2s, box-shadow .2s, transform .15s;
        }
        .fp-nav-card:hover {
            border-color: #185FA5;
            box-shadow: 0 4px 16px rgba(24,95,165,.12);
            transform: translateY(-3px);
        }
        .fp-nav-icon  { font-size: 28px; margin-bottom: 8px; }
        .fp-nav-title { font-size: 14px; font-weight: 700; color: #2C2C2A; margin-bottom: 3px; }
        .fp-nav-desc  { font-size: 11px; color: #888; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Top nav + Sidebar
# ---------------------------------------------------------------------------
render_nav("Home")
render_sidebar()

# ---------------------------------------------------------------------------
# Home content
# ---------------------------------------------------------------------------
if "summary" not in st.session_state:
    # ── Initial / Empty State ──────────────────────────────────────────────
    st.markdown(f"# {APP_ICON} Welcome to FinPilot")
    st.markdown(
        "Configure your market research parameters in the **sidebar** (⚙️ icon, top-left) "
        "and click **🚀 Run Analysis** to generate an AI-powered equity report."
    )

    st.divider()
    st.markdown("### What you'll get")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            "<div style='text-align:center;padding:20px;background:#fff;"
            "border:1px solid #E8E6E0;border-radius:12px'>"
            "<div style='font-size:32px'>📊</div>"
            "<div style='font-weight:700;margin-top:8px'>Overview</div>"
            "<div style='font-size:12px;color:#888;margin-top:4px'>Price, metrics, charts</div>"
            "</div>",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            "<div style='text-align:center;padding:20px;background:#fff;"
            "border:1px solid #E8E6E0;border-radius:12px'>"
            "<div style='font-size:32px'>📈</div>"
            "<div style='font-weight:700;margin-top:8px'>Technical</div>"
            "<div style='font-size:12px;color:#888;margin-top:4px'>Indicators & Trends</div>"
            "</div>",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            "<div style='text-align:center;padding:20px;background:#fff;"
            "border:1px solid #E8E6E0;border-radius:12px'>"
            "<div style='font-size:32px'>📰</div>"
            "<div style='font-weight:700;margin-top:8px'>Sentiment</div>"
            "<div style='font-size:12px;color:#888;margin-top:4px'>Headlines analysis</div>"
            "</div>",
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            "<div style='text-align:center;padding:20px;background:#fff;"
            "border:1px solid #E8E6E0;border-radius:12px'>"
            "<div style='font-size:32px'>🤖</div>"
            "<div style='font-weight:700;margin-top:8px'>AI Signal</div>"
            "<div style='font-size:12px;color:#888;margin-top:4px'>Smart recommendations</div>"
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-top:24px'></div>", unsafe_allow_html=True)
    st.info("💡 Open the ⚙️ sidebar (top-left), enter your Groq API key, pick a ticker and click **🚀 Run Analysis**.")

else:
    # ── Premium Landing (post-analysis) ──────────────────────────────────
    s   = st.session_state["summary"]
    sig = st.session_state["trade_signal"]
    info = st.session_state.get("stock_info", {})
    batch = st.session_state.get("sentiment_batch")

    # Signal colour
    sig_colors = {"Buy": "#1D9E75", "Hold": "#BA7517", "Sell": "#D85A30"}
    sig_bg_colors = {"Buy": "rgba(29,158,117,.25)", "Hold": "rgba(186,117,23,.25)", "Sell": "rgba(216,90,48,.25)"}
    sig_col = sig_colors.get(sig.signal, "#888")
    sig_bg  = sig_bg_colors.get(sig.signal, "rgba(136,136,136,.2)")

    company = info.get("name", s["ticker"])
    sector  = info.get("sector", "")
    sub     = f"{sector}  ·  As of {s['as_of_date']}" if sector else f"As of {s['as_of_date']}"

    # ── Hero banner ────────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div class="fp-hero">
            <div class="fp-hero-ticker">{s['ticker']}</div>
            <div class="fp-hero-company">{company}</div>
            <div class="fp-hero-sub">{sub}</div>
            <div>
                <span class="fp-signal-pill" style="background:{sig_bg}; color:{sig_col};">
                    {sig.signal}
                </span>
                <span class="fp-conf-text">
                    {sig.confidence:.0%} confidence &nbsp;·&nbsp; {sig.risk_level} risk
                </span>
            </div>
            <div style="margin-top:14px;font-size:13px;opacity:.8;max-width:700px;line-height:1.6;">
                {sig.justification[:280]}{"…" if len(sig.justification) > 280 else ""}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── KPI cards ─────────────────────────────────────────────────────────
    ytd_color = "#1D9E75" if s["ytd_return_pct"] >= 0 else "#D85A30"
    ytd_arrow = "▲" if s["ytd_return_pct"] >= 0 else "▼"

    rsi_val = s["rsi_14"] or 0
    rsi_color = "#D85A30" if rsi_val > 70 else "#1D9E75" if rsi_val < 30 else "#185FA5"

    sentiment_score = batch.overall_score if batch else 0
    sent_label = "Bullish" if sentiment_score > 0.1 else "Bearish" if sentiment_score < -0.1 else "Neutral"
    sent_color = "#1D9E75" if sentiment_score > 0.1 else "#D85A30" if sentiment_score < -0.1 else "#888"

    st.markdown(
        f"""
        <div class="fp-kpi-grid">
            <div class="fp-kpi">
                <div class="fp-kpi-label">Current Price</div>
                <div class="fp-kpi-value">${s['current_price']}</div>
                <div class="fp-kpi-sub" style="color:{ytd_color}">{ytd_arrow} {s['ytd_return_pct']:+.1f}% YTD</div>
            </div>
            <div class="fp-kpi">
                <div class="fp-kpi-label">52-Week Range</div>
                <div class="fp-kpi-value" style="font-size:16px">${s['52w_low']} – ${s['52w_high']}</div>
                <div class="fp-kpi-sub">Low / High</div>
            </div>
            <div class="fp-kpi">
                <div class="fp-kpi-label">P/E Ratio</div>
                <div class="fp-kpi-value">{s['pe_ratio'] or 'N/A'}</div>
                <div class="fp-kpi-sub">Price / Earnings</div>
            </div>
            <div class="fp-kpi">
                <div class="fp-kpi-label">RSI-14</div>
                <div class="fp-kpi-value" style="color:{rsi_color}">{rsi_val}</div>
                <div class="fp-kpi-sub">{s['rsi_interpretation']}</div>
            </div>
            <div class="fp-kpi">
                <div class="fp-kpi-label">News Sentiment</div>
                <div class="fp-kpi-value" style="color:{sent_color};font-size:18px">{sent_label}</div>
                <div class="fp-kpi-sub">{f'{batch.overall_score:+.3f}' if batch else 'N/A'} score</div>
            </div>
            <div class="fp-kpi">
                <div class="fp-kpi-label">SMA Signal</div>
                <div class="fp-kpi-value" style="font-size:15px">{s['sma_cross']}</div>
                <div class="fp-kpi-sub">{s['momentum_signal'].capitalize()} momentum</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Explore sections ───────────────────────────────────────────────────
    st.markdown("### Explore Analysis")

    nav_sections = [
        ("📊", "Overview",          "Price · metrics · candlestick chart",   "pages/1_📊_Overview.py"),
        ("📈", "Technical Analysis", "RSI · MACD · Bollinger Bands",          "pages/2_📈_Technical_Analysis.py"),
        ("📰", "News Sentiment",     "Headlines · AI sentiment breakdown",    "pages/3_📰_News_Sentiment.py"),
        ("🤖", "AI Trade Signal",    "LLM-generated signal & justification",  "pages/4_🤖_AI_Signal.py"),
        ("📓", "Notebook",           "Browse the source notebook inline",     "pages/5_📓_Notebook.py"),
        ("📤", "Export",             "Download · copy · share reports",       "pages/6_📤_Export.py"),
    ]

    cols = st.columns(len(nav_sections))
    for col, (icon, title, desc, page) in zip(cols, nav_sections):
        with col:
            st.page_link(
                page,
                label=f"{icon} **{title}**\n\n_{desc}_",
                use_container_width=True,
            )

    st.divider()
    st.caption(
        "To analyse a different stock, update the ticker in the ⚙️ sidebar and click **🚀 Run Analysis**."
    )

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