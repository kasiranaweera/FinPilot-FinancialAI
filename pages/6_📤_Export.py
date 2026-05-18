"""
pages/6_📤_Export.py
Export & Share — download, copy and share FinPilot analysis reports.

Sections (one-by-one):
  • Overview
  • Technical Analysis
  • News Sentiment
  • AI Trade Signal

Plus an "All-in-One" combined report.
Each section has: ⬇ Download  |  📋 Copy  |  🔗 Share link
"""

import datetime
import streamlit as st
from components.nav import render_nav
from components.sidebar import render_sidebar
from config.settings import RISK_DISCLAIMER

st.set_page_config(
    page_title="Export Report | FinPilot",
    page_icon="📤",
    layout="wide",
    initial_sidebar_state="collapsed",
)

render_nav("Export")
render_sidebar()

# ── Styles ──────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
        .export-card {
            background: #fff;
            border: 1px solid #E8E6E0;
            border-radius: 14px;
            padding: 22px 26px;
            margin-bottom: 18px;
        }
        .export-card h3 { margin: 0 0 4px 0; color: #185FA5; font-size: 17px; }
        .export-card p  { margin: 0 0 14px 0; color: #666; font-size: 13px; }
        .copy-btn-wrap button {
            background: #F5F4F0!important;
            color: #333!important;
            border: 1px solid #ddd!important;
            border-radius: 8px!important;
            font-weight:600!important;
        }
        .copy-btn-wrap button:hover {
            background: #e8e6e0!important;
        }
        .share-btn-wrap button {
            background: #EAF2FB!important;
            color: #185FA5!important;
            border: 1px solid #b8d4ef!important;
            border-radius: 8px!important;
            font-weight:600!important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Guard ────────────────────────────────────────────────────────────────────
if "summary" not in st.session_state:
    st.info("👈 Run analysis from the **Home** page first — then come back here to export your report.")
    st.stop()

# ── Gather data ──────────────────────────────────────────────────────────────
s      = st.session_state["summary"]
sig    = st.session_state["trade_signal"]
batch  = st.session_state.get("sentiment_batch")
news   = st.session_state.get("news", [])
info   = st.session_state.get("stock_info", {})
now    = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
ticker = s["ticker"]

# ── Build individual report strings ─────────────────────────────────────────

def _overview_report() -> str:
    lines = [
        f"# FinPilot — Overview Report: {ticker}",
        f"Generated: {now}",
        "",
        f"Company  : {info.get('name', ticker)}",
        f"Sector   : {info.get('sector', 'N/A')}",
        f"Industry : {info.get('industry', 'N/A')}",
        "",
        "## Key Metrics",
        f"Current Price  : ${s['current_price']}",
        f"52-Week High   : ${s['52w_high']}",
        f"52-Week Low    : ${s['52w_low']}",
        f"YTD Return     : {s['ytd_return_pct']:+.1f}%",
        f"P/E Ratio      : {s['pe_ratio'] or 'N/A'}",
        f"RSI-14         : {s['rsi_14']}",
        "",
        "## Technical Snapshot",
        f"SMA-50         : ${s['sma_50']} (price {s['price_vs_sma50']})",
        f"SMA-200        : ${s['sma_200']} (price {s['price_vs_sma200']})",
        f"SMA Cross      : {s['sma_cross']}",
        f"MACD           : {s['macd']} — {s['macd_status']}",
        f"BB Upper/Lower : ${s['bb_upper']} / ${s['bb_lower']} (mid ${s['bb_mid']})",
        "",
        "---",
        RISK_DISCLAIMER,
    ]
    if info.get("description"):
        lines.insert(8, f"\n## Description\n{info['description']}\n")
    return "\n".join(lines)


def _technical_report() -> str:
    lines = [
        f"# FinPilot — Technical Analysis: {ticker}",
        f"Generated: {now}",
        "",
        "## RSI (14)",
        f"Value          : {s['rsi_14']}",
        f"Interpretation : {s['rsi_interpretation']}",
        "",
        "## MACD (12, 26, 9)",
        f"MACD Line      : {s['macd']}",
        f"Signal Line    : {s['macd_signal']}",
        f"Histogram      : {s['macd_hist']}",
        f"Status         : {s['macd_status']}",
        "",
        "## Bollinger Bands (20, 2σ)",
        f"Upper          : ${s['bb_upper']}",
        f"Mid (SMA-20)   : ${s['bb_mid']}",
        f"Lower          : ${s['bb_lower']}",
        f"%B Position    : {(s.get('bb_pct_b') or 0)*100:.1f}%",
        "",
        "## Moving Averages",
        f"SMA-50         : ${s['sma_50']} — price {s['price_vs_sma50']}",
        f"SMA-200        : ${s['sma_200']} — price {s['price_vs_sma200']}",
        f"Cross Signal   : {s['sma_cross']}",
        f"Momentum       : {s.get('momentum_signal','N/A').upper()}",
        "",
        "---",
        RISK_DISCLAIMER,
    ]
    return "\n".join(lines)


def _sentiment_report() -> str:
    lines = [
        f"# FinPilot — News Sentiment: {ticker}",
        f"Generated: {now}",
        "",
    ]
    if batch:
        score_label = (
            "Bullish" if batch.overall_score > 0.1
            else "Bearish" if batch.overall_score < -0.1
            else "Neutral"
        )
        lines += [
            "## Overall Sentiment",
            f"Score          : {batch.overall_score:+.3f} ({score_label})",
            f"Total Headlines: {batch.total_headlines}",
            f"Positive       : {batch.positive_count}",
            f"Negative       : {batch.negative_count}",
            f"Neutral        : {batch.neutral_count}",
            "",
            "## Headline Analysis",
        ]
        for item in batch.results:
            lines.append(
                f"[{item.sentiment.upper():8s}] ({int(item.confidence*100)}%) {item.headline}"
            )
            lines.append(f"  → {item.brief_reason}")
            lines.append("")
    else:
        lines.append("No sentiment data available.")

    lines += ["---", RISK_DISCLAIMER]
    return "\n".join(lines)


def _signal_report() -> str:
    lines = [
        f"# FinPilot — AI Trade Signal: {ticker}",
        f"Generated: {now}",
        "",
        "## Signal",
        f"Decision       : {sig.signal}",
        f"Confidence     : {sig.confidence:.0%}",
        f"Risk Level     : {sig.risk_level}",
        "",
        "## Justification",
        sig.justification,
        "",
        "## Key Factors",
    ]
    for i, f in enumerate(sig.key_factors, 1):
        lines.append(f"  {i}. {f}")
    lines += ["", "---", RISK_DISCLAIMER]
    return "\n".join(lines)


def _all_report() -> str:
    return "\n\n".join([
        _overview_report(),
        "=" * 60,
        _technical_report(),
        "=" * 60,
        _sentiment_report(),
        "=" * 60,
        _signal_report(),
    ])


# ── JS helper: copy text to clipboard ───────────────────────────────────────
def _copy_button(text: str, key: str, label: str = "📋 Copy to Clipboard"):
    escaped = text.replace("`", "\\`").replace("\\", "\\\\")
    st.markdown(
        f"""
        <button onclick="navigator.clipboard.writeText(`{escaped}`).then(
            () => {{this.innerText='✅ Copied!'; setTimeout(()=>{{this.innerText='{label}';}},2000);}},
            () => {{this.innerText='❌ Failed';}}
        );" style="cursor:pointer;background:#F5F4F0;border:1px solid #ddd;
            border-radius:8px;padding:6px 14px;font-size:13px;font-weight:600;
            color:#333;margin-right:4px;">{label}</button>
        """,
        unsafe_allow_html=True,
    )


def _share_button(label: str = "🔗 Copy Share Link"):
    st.markdown(
        f"""
        <button onclick="navigator.clipboard.writeText(window.location.href).then(
            () => {{this.innerText='✅ Link Copied!'; setTimeout(()=>{{this.innerText='{label}';}},2000);}},
            () => {{this.innerText='❌ Failed';}}
        );" style="cursor:pointer;background:#EAF2FB;border:1px solid #b8d4ef;
            border-radius:8px;padding:6px 14px;font-size:13px;font-weight:600;
            color:#185FA5;margin-right:4px;">{label}</button>
        """,
        unsafe_allow_html=True,
    )


# ── Page header ──────────────────────────────────────────────────────────────
st.markdown(f"# 📤 Export Reports — {ticker}")
st.caption(f"Last analysis: {s['as_of_date']} · Generated at {now}")
st.divider()

# ── Tabs: one-by-one vs all-in-one ──────────────────────────────────────────
tab_single, tab_all = st.tabs(["📄 Section by Section", "📦 All-in-One"])

with tab_single:
    sections = [
        {
            "icon": "📊",
            "title": "Overview Report",
            "desc": "Price, metrics, technical snapshot and company info.",
            "fn":   _overview_report,
            "fname": f"finpilot_overview_{ticker}_{s['as_of_date']}.txt",
        },
        {
            "icon": "📈",
            "title": "Technical Analysis Report",
            "desc": "RSI, MACD, Bollinger Bands, moving averages.",
            "fn":   _technical_report,
            "fname": f"finpilot_technical_{ticker}_{s['as_of_date']}.txt",
        },
        {
            "icon": "📰",
            "title": "News Sentiment Report",
            "desc": f"Sentiment analysis of {batch.total_headlines if batch else 0} headlines.",
            "fn":   _sentiment_report,
            "fname": f"finpilot_sentiment_{ticker}_{s['as_of_date']}.txt",
        },
        {
            "icon": "🤖",
            "title": "AI Trade Signal Report",
            "desc": f"Signal: {sig.signal} · Confidence: {sig.confidence:.0%} · Risk: {sig.risk_level}",
            "fn":   _signal_report,
            "fname": f"finpilot_signal_{ticker}_{s['as_of_date']}.txt",
        },
    ]

    for sec in sections:
        report_text = sec["fn"]()
        with st.container():
            st.markdown(
                f"""
                <div class="export-card">
                    <h3>{sec['icon']} {sec['title']}</h3>
                    <p>{sec['desc']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Preview
            with st.expander("👁 Preview report", expanded=False):
                st.code(report_text, language="markdown")

            # Action buttons
            col_dl, col_cp, col_sh, _ = st.columns([1.4, 1.4, 1.4, 3])
            with col_dl:
                st.download_button(
                    label="⬇️ Download",
                    data=report_text,
                    file_name=sec["fname"],
                    mime="text/plain",
                    use_container_width=True,
                    key=f"dl_{sec['title']}",
                )
            with col_cp:
                _copy_button(report_text, key=f"cp_{sec['title']}")
            with col_sh:
                _share_button()

        st.markdown("<div style='margin-bottom:6px'></div>", unsafe_allow_html=True)

with tab_all:
    all_text = _all_report()
    all_fname = f"finpilot_full_report_{ticker}_{s['as_of_date']}.txt"

    st.markdown(
        f"""
        <div class="export-card" style="border-color:#185FA5;border-width:2px;">
            <h3>📦 Complete Analysis Report — {ticker}</h3>
            <p>All four sections combined: Overview · Technical · Sentiment · AI Signal</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("👁 Preview full report", expanded=False):
        st.code(all_text, language="markdown")

    col_dl, col_cp, col_sh, _ = st.columns([1.4, 1.4, 1.4, 3])
    with col_dl:
        st.download_button(
            label="⬇️ Download Full Report",
            data=all_text,
            file_name=all_fname,
            mime="text/plain",
            use_container_width=True,
            key="dl_all",
        )
    with col_cp:
        _copy_button(all_text, key="cp_all", label="📋 Copy Full Report")
    with col_sh:
        _share_button(label="🔗 Copy Share Link")

    st.divider()
    st.info(
        "💡 **Tip:** You can share this page's URL directly — anyone opening it "
        "will land on FinPilot. To share the actual data, use **Download** or **Copy**."
    )
