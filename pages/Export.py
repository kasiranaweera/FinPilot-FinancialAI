"""
pages/6_📤_Export.py — FinPilot Export & Share
Download MD/PDF, Save & Share with UUID links. No copy buttons.
"""
import io, datetime, pathlib
import streamlit as st
from components.sidebar import render_sidebar
from utils.share import build_payload, save_report, load_report, get_share_url, resolve_shared, list_reports
from config.settings import APP_TITLE, APP_ICON, RISK_DISCLAIMER

st.set_page_config(page_title=f"Export | {APP_TITLE}", page_icon="📤", layout="wide", initial_sidebar_state="expanded")
resolve_shared()
render_sidebar("Export")

st.markdown("""
<style>
  h2,h3{color:#185FA5}
  .fp-section-hd{display:flex;align-items:center;gap:10px;margin:28px 0 14px}
  .fp-section-hd-line{flex:1;height:1px;background:#E8E6E0}
  .fp-section-hd-text{font-size:11px;font-weight:700;color:#888;text-transform:uppercase;letter-spacing:.8px;white-space:nowrap}
  /* Export section card */
  .ex-card{background:#fff;border:1px solid #E8E6E0;border-radius:16px;padding:24px 26px;margin-bottom:20px;transition:box-shadow .2s,transform .15s}
  .ex-card:hover{box-shadow:0 6px 24px rgba(24,95,165,.09);transform:translateY(-1px)}
  .ex-card-icon{font-size:28px;margin-bottom:8px}
  .ex-card-title{font-size:16px;font-weight:700;color:#2C2C2A;margin-bottom:4px}
  .ex-card-desc{font-size:12px;color:#888;margin-bottom:18px;line-height:1.5}
  /* Btn grid */
  .ex-btn-row{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
  /* Preview */
  .ex-preview{background:#F8F7F4;border:1px solid #E8E6E0;border-radius:10px;padding:14px 16px;font-family:monospace;font-size:11.5px;color:#444;line-height:1.7;max-height:300px;overflow-y:auto;margin:14px 0;white-space:pre-wrap}
  /* Share box */
  .share-box{background:linear-gradient(135deg,#EAF4FF,#E5F8F2);border:1.5px solid #b8d4ef;border-radius:14px;padding:20px 24px;margin-top:14px}
  .share-uuid{font-family:monospace;font-size:11px;background:#fff;border:1px solid #DDD;border-radius:6px;padding:6px 10px;color:#444;word-break:break-all;margin:8px 0}
  .share-url{font-size:12px;color:#185FA5;word-break:break-all;margin-top:4px}
  /* History */
  .hist-row{display:flex;align-items:center;gap:12px;padding:12px 16px;border-radius:10px;background:#fff;border:1px solid #E8E6E0;margin-bottom:8px;transition:box-shadow .15s}
  .hist-row:hover{box-shadow:0 3px 10px rgba(0,0,0,.05)}
  .hist-sig{display:inline-block;padding:3px 12px;border-radius:20px;font-size:11px;font-weight:700;color:#fff}
  /* Download buttons styled */
  div[data-testid="stDownloadButton"] > button{
    border-radius:8px!important;font-weight:600!important;
    font-size:13px!important;transition:all .15s!important;
  }
  div[data-testid="stDownloadButton"] > button:hover{
    transform:translateY(-1px)!important;box-shadow:0 4px 12px rgba(0,0,0,.12)!important;
  }
  /* Share button */
  div[data-testid="stButton"] > button[kind="primary"]{
    background:linear-gradient(135deg,#1D9E75,#15825F)!important;
    color:#fff!important;border:none!important;border-radius:8px!important;
    font-weight:700!important;box-shadow:0 3px 10px rgba(29,158,117,.25)!important;
  }
  /* Empty */
  .fp-empty{text-align:center;padding:80px 20px}
  .fp-empty-icon{font-size:52px;margin-bottom:16px}
  .fp-empty-title{font-size:20px;font-weight:700;color:#2C2C2A;margin-bottom:8px}
  .fp-empty-sub{font-size:14px;color:#888}
</style>
""", unsafe_allow_html=True)

st.markdown("# 📤 Export & Share")

if "summary" not in st.session_state:
    st.markdown("""
<div class="fp-empty">
  <div class="fp-empty-icon">📤</div>
  <div class="fp-empty-title">Nothing to export yet</div>
  <div class="fp-empty-sub">Run an analysis from the Home page, then come back here to download or share your report.</div>
</div>""", unsafe_allow_html=True)
    st.stop()

s     = st.session_state["summary"]
sig   = st.session_state["trade_signal"]
batch = st.session_state.get("sentiment_batch")
info  = st.session_state.get("stock_info", {})
news  = st.session_state.get("news", [])
now   = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
ticker = s["ticker"]

st.caption(f"**{info.get('name',ticker)}** · {s['as_of_date']} · Generated {now}")
st.divider()

# ── Report builders ───────────────────────────────────────────────────────────
def _overview_md():
    lines = [
        f"# FinPilot — Overview: {ticker}",
        f"**Generated:** {now}  |  **Ticker:** {ticker}  |  **Date:** {s['as_of_date']}",
        "",
        f"**Company:** {info.get('name', ticker)}",
        f"**Sector:** {info.get('sector','N/A')}  |  **Industry:** {info.get('industry','N/A')}",
        "",
        "## Key Metrics",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Current Price | ${s['current_price']} |",
        f"| 52-Week High | ${s['52w_high']} |",
        f"| 52-Week Low | ${s['52w_low']} |",
        f"| YTD Return | {s['ytd_return_pct']:+.1f}% |",
        f"| P/E Ratio | {s['pe_ratio'] or 'N/A'} |",
        f"| RSI-14 | {s['rsi_14']} ({s['rsi_interpretation']}) |",
        f"| SMA Cross | {s['sma_cross']} |",
        "",
        "## Technical Snapshot",
        "| Indicator | Value | Note |",
        "|-----------|-------|------|",
        f"| SMA-50 | ${s['sma_50']} | Price {s['price_vs_sma50']} |",
        f"| SMA-200 | ${s['sma_200']} | {s['sma_cross']} |",
        f"| MACD | {s['macd']} | {s['macd_status']} |",
        f"| BB Upper/Lower | ${s['bb_upper']} / ${s['bb_lower']} | Mid: ${s['bb_mid']} |",
        "",
        "---",
        f"> {RISK_DISCLAIMER}",
    ]
    if info.get("description"):
        lines.insert(6, f"\n## About\n{info['description']}\n")
    return "\n".join(lines)

def _technical_md():
    bb_pct = (s.get("bb_pct_b") or 0)*100
    return "\n".join([
        f"# FinPilot — Technical Analysis: {ticker}",
        f"**Generated:** {now}  |  **Ticker:** {ticker}  |  **Date:** {s['as_of_date']}",
        "",
        "## RSI (14)",
        f"| Value | Status |",
        f"|-------|--------|",
        f"| {s['rsi_14']} | {s['rsi_interpretation']} |",
        "",
        "## MACD (12, 26, 9)",
        "| MACD | Signal | Histogram | Status |",
        "|------|--------|-----------|--------|",
        f"| {s['macd']} | {s['macd_signal']} | {s['macd_hist']} | {s['macd_status']} |",
        "",
        "## Moving Averages",
        "| MA | Value | Price vs MA | Cross |",
        "|----|-------|-------------|-------|",
        f"| SMA-50 | ${s['sma_50']} | {s['price_vs_sma50']} | {s['sma_cross']} |",
        f"| SMA-200 | ${s['sma_200']} | {s['price_vs_sma200']} | — |",
        "",
        "## Bollinger Bands (20, 2σ)",
        "| Upper | Mid | Lower | %B |",
        "|-------|-----|-------|----|",
        f"| ${s['bb_upper']} | ${s['bb_mid']} | ${s['bb_lower']} | {bb_pct:.1f}% |",
        "",
        f"**Momentum Signal:** {s.get('momentum_signal','N/A').upper()}",
        "",
        "---",
        f"> {RISK_DISCLAIMER}",
    ])

def _sentiment_md():
    lines = [
        f"# FinPilot — News Sentiment: {ticker}",
        f"**Generated:** {now}  |  **Ticker:** {ticker}",
        "",
    ]
    if batch:
        lbl = "Bullish" if batch.overall_score>0.1 else "Bearish" if batch.overall_score<-0.1 else "Neutral"
        lines += [
            "## Overall Sentiment",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Score | {batch.overall_score:+.3f} ({lbl}) |",
            f"| Total | {batch.total_headlines} |",
            f"| Positive | {batch.positive_count} |",
            f"| Negative | {batch.negative_count} |",
            f"| Neutral | {batch.neutral_count} |",
            "",
            "## Headline Analysis",
            "",
        ]
        for item in batch.results:
            lines.append(f"**[{item.sentiment.upper()}]** ({int(item.confidence*100)}%)  {item.headline}")
            lines.append(f"*{item.brief_reason}*")
            lines.append("")
    else:
        lines.append("No sentiment data available.")
    lines += ["---", f"> {RISK_DISCLAIMER}"]
    return "\n".join(lines)

def _signal_md():
    lines = [
        f"# FinPilot — AI Trade Signal: {ticker}",
        f"**Generated:** {now}  |  **Ticker:** {ticker}",
        "",
        "## Signal",
        "| Decision | Confidence | Risk |",
        "|----------|-----------|------|",
        f"| {sig.signal} | {sig.confidence:.0%} | {sig.risk_level} |",
        "",
        "## Justification",
        "",
        sig.justification,
        "",
        "## Key Factors",
        "",
    ]
    for i, f in enumerate(sig.key_factors, 1):
        lines.append(f"{i}. {f}")
    lines += ["", "---", f"> {RISK_DISCLAIMER}"]
    return "\n".join(lines)

def _all_md():
    sep = "\n\n" + "="*60 + "\n\n"
    return sep.join([_overview_md(), _technical_md(), _sentiment_md(), _signal_md()])

def _md_to_pdf(md_text):
    try:
        import re as _re
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable

        def _safe(t):
            t = t.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
            t = _re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
            t = _re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', t)
            t = t.replace("*","")
            t = _re.sub(r'`([^`]*)`', r'\1', t)
            return t

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        story  = []
        primary = colors.HexColor("#185FA5")
        muted   = colors.HexColor("#888780")
        h1s = ParagraphStyle("H1", parent=styles["Heading1"], textColor=primary, fontSize=18, spaceAfter=6)
        h2s = ParagraphStyle("H2", parent=styles["Heading2"], textColor=primary, fontSize=13, spaceAfter=4)
        bdy = ParagraphStyle("Body", parent=styles["Normal"], fontSize=9.5, leading=14, spaceAfter=4)
        note= ParagraphStyle("Note", parent=styles["Normal"], fontSize=8, textColor=muted, leading=11)
        cod = ParagraphStyle("Code", parent=styles["Normal"], fontSize=8.5, leading=13, fontName="Courier", textColor=colors.HexColor("#444"))

        for line in md_text.split("\n"):
            stripped = line.strip()
            if stripped.startswith("# "):
                story.append(Paragraph(_safe(stripped[2:]), h1s))
                story.append(HRFlowable(width="100%", thickness=1, color=primary, spaceAfter=8))
            elif stripped.startswith("## "):
                story.append(Spacer(1,6))
                story.append(Paragraph(_safe(stripped[3:]), h2s))
            elif stripped.startswith("> "):
                story.append(Paragraph(_safe(stripped[2:]), note))
            elif stripped.startswith("---") and set(stripped)=={"-"}:
                story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E8E6E0"), spaceAfter=6))
            elif stripped.startswith("|"):
                if not set(stripped.replace("|","").replace("-","").replace(" ","").replace(":",""))-set():
                    continue
                cells = [_safe(c.strip()) for c in stripped.split("|") if c.strip() and not set(c.strip()).issubset({"-"," ",":"})]
                if cells:
                    story.append(Paragraph("  ·  ".join(cells), cod))
            elif stripped:
                story.append(Paragraph(_safe(stripped), bdy))
            else:
                story.append(Spacer(1,4))
        doc.build(story)
        return buf.getvalue()
    except ImportError:
        return md_text.encode("utf-8")

def _do_share(key):
    payload = build_payload()
    if not payload:
        return None, None
    payload["_section"] = key
    uid = save_report(payload)
    return uid, get_share_url(uid)

# ── Sections ──────────────────────────────────────────────────────────────────
sections = [
    {"key":"overview",  "icon":"📊", "title":"Overview Report",
     "desc":"Company info, key metrics, price snapshot and technical summary.",
     "fn":_overview_md, "fname":f"finpilot_overview_{ticker}_{s['as_of_date']}"},
    {"key":"technical", "icon":"📈", "title":"Technical Analysis Report",
     "desc":"RSI, MACD, Bollinger Bands, moving averages and momentum signals.",
     "fn":_technical_md, "fname":f"finpilot_technical_{ticker}_{s['as_of_date']}"},
    {"key":"sentiment", "icon":"📰", "title":"News Sentiment Report",
     "desc":f"LLM sentiment analysis of {batch.total_headlines if batch else 0} recent headlines.",
     "fn":_sentiment_md, "fname":f"finpilot_sentiment_{ticker}_{s['as_of_date']}"},
    {"key":"signal",    "icon":"🤖", "title":"AI Trade Signal Report",
     "desc":f"Signal: {sig.signal}  ·  Confidence: {sig.confidence:.0%}  ·  Risk: {sig.risk_level}",
     "fn":_signal_md,  "fname":f"finpilot_signal_{ticker}_{s['as_of_date']}"},
]

tab_sec, tab_all, tab_hist = st.tabs(["📄 Section Reports", "📦 Full Report", "🕓 Saved Reports"])

# ── Section reports ───────────────────────────────────────────────────────────
with tab_sec:
    for sec in sections:
        md = sec["fn"]()
        pdf = _md_to_pdf(md)
        pdf_ok = pdf[:4]==b"%PDF"

        st.markdown(f"""
<div class="ex-card">
  <div class="ex-card-icon">{sec['icon']}</div>
  <div class="ex-card-title">{sec['title']}</div>
  <div class="ex-card-desc">{sec['desc']}</div>
</div>""", unsafe_allow_html=True)

        with st.expander("👁️ Preview report content"):
            st.markdown(f'<div class="ex-preview">{md[:1200]}{"…" if len(md)>1200 else ""}</div>', unsafe_allow_html=True)

        btn1, btn2, btn3, _spc = st.columns([1.4, 1.4, 1.6, 3])
        with btn1:
            st.download_button(f"⬇️ Download .md", data=md.encode(), file_name=sec["fname"]+".md",
                               mime="text/markdown", use_container_width=True, key=f"md_{sec['key']}")
        with btn2:
            st.download_button(f"⬇️ Download .pdf", data=pdf,
                               file_name=sec["fname"]+(".pdf" if pdf_ok else ".txt"),
                               mime="application/pdf" if pdf_ok else "text/plain",
                               use_container_width=True, key=f"pdf_{sec['key']}")
        with btn3:
            if st.button("💾 Save & Share", key=f"share_{sec['key']}", type="primary", use_container_width=True):
                uid, url = _do_share(sec["key"])
                st.session_state[f"shared_{sec['key']}"] = {"uid":uid,"url":url}

        saved = st.session_state.get(f"shared_{sec['key']}")
        if saved:
            st.markdown(f"""
<div class="share-box">
  <div style="font-size:13px;font-weight:700;color:#185FA5;margin-bottom:6px">✅ Report saved & ready to share</div>
  <div style="font-size:11px;color:#666">File: <code>reports/{saved['uid']}.json</code></div>
  <div class="share-uuid">{saved['uid']}</div>
  <div class="share-url">🔗 {saved['url']}</div>
</div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── Full report ───────────────────────────────────────────────────────────────
with tab_all:
    all_md  = _all_md()
    all_pdf = _md_to_pdf(all_md)
    pdf_ok  = all_pdf[:4]==b"%PDF"
    fname   = f"finpilot_full_{ticker}_{s['as_of_date']}"

    st.markdown(f"""
<div class="ex-card" style="border:2px solid #185FA5">
  <div class="ex-card-icon">📦</div>
  <div class="ex-card-title">Complete Analysis — {ticker}</div>
  <div class="ex-card-desc">
    All four reports combined into one document:<br>
    Overview · Technical Analysis · News Sentiment · AI Trade Signal
  </div>
</div>""", unsafe_allow_html=True)

    with st.expander("👁️ Preview full report"):
        st.markdown(f'<div class="ex-preview">{all_md[:2000]}{"…" if len(all_md)>2000 else ""}</div>', unsafe_allow_html=True)

    b1, b2, b3, _sp = st.columns([1.4, 1.4, 1.6, 3])
    with b1:
        st.download_button("⬇️ Download .md", data=all_md.encode(), file_name=fname+".md",
                           mime="text/markdown", use_container_width=True, key="md_all")
    with b2:
        st.download_button("⬇️ Download .pdf", data=all_pdf,
                           file_name=fname+(".pdf" if pdf_ok else ".txt"),
                           mime="application/pdf" if pdf_ok else "text/plain",
                           use_container_width=True, key="pdf_all")
    with b3:
        if st.button("💾 Save & Share", key="share_all", type="primary", use_container_width=True):
            uid, url = _do_share("full")
            st.session_state["shared_all"] = {"uid":uid,"url":url}

    saved_all = st.session_state.get("shared_all")
    if saved_all:
        st.markdown(f"""
<div class="share-box">
  <div style="font-size:13px;font-weight:700;color:#185FA5;margin-bottom:6px">✅ Full report saved & ready to share</div>
  <div style="font-size:11px;color:#666">File: <code>reports/{saved_all['uid']}.json</code></div>
  <div class="share-uuid">{saved_all['uid']}</div>
  <div class="share-url">🔗 {saved_all['url']}</div>
</div>""", unsafe_allow_html=True)

    st.info("💡 **Save & Share** stores the full analysis as `reports/<uuid>.json`. Anyone with the link will have the data auto-loaded when they open FinPilot.")

# ── History ───────────────────────────────────────────────────────────────────
with tab_hist:
    st.subheader("🕓 Saved Reports")
    reports = list_reports()
    if not reports:
        st.markdown("""
<div style="text-align:center;padding:40px;color:#888">
  <div style="font-size:32px;margin-bottom:12px">📂</div>
  <div style="font-weight:600;margin-bottom:6px">No saved reports yet</div>
  <div style="font-size:13px">Use Save &amp; Share on any report to create one.</div>
</div>""", unsafe_allow_html=True)
    else:
        sig_c_map = {"Buy":"#1D9E75","Hold":"#BA7517","Sell":"#D85A30"}
        for r in reports:
            sc  = sig_c_map.get(r["signal"],"#888")
            url = get_share_url(r["uuid"])
            c_info, c_uuid, c_load = st.columns([4, 4, 1.5])
            with c_info:
                st.markdown(f"""
<div class="hist-row">
  <span class="hist-sig" style="background:{sc}">{r['signal']}</span>
  <div>
    <div style="font-weight:600;font-size:14px">{r['ticker']}</div>
    <div style="font-size:11px;color:#888">{r['as_of_date']} · Saved {r['saved_at'][:16]}</div>
  </div>
</div>""", unsafe_allow_html=True)
            with c_uuid:
                st.caption(f"`{r['uuid'][:16]}…`")
                st.caption(f"[🔗 Share Link]({url})")
            with c_load:
                if st.button("Load", key=f"load_{r['uuid']}", use_container_width=True):
                    payload = load_report(r["uuid"])
                    if payload:
                        from utils.share import restore_payload
                        restore_payload(payload)
                        st.success(f"Loaded {r['ticker']}!")
                        st.rerun()
