"""
pages/4_🤖_AI_Signal.py — FinPilot AI Trade Signal
"""
import streamlit as st
from components.sidebar import render_sidebar
from components.ui_elements import disclaimer_box
from utils.share import resolve_shared
from config.settings import APP_TITLE, APP_ICON, RISK_DISCLAIMER

st.set_page_config(page_title=f"AI Signal | {APP_TITLE}", page_icon="💡", layout="wide", initial_sidebar_state="expanded")
resolve_shared()
render_sidebar("AI Signal")

st.markdown("""
<style>
  h2,h3{color:#185FA5}
  .fp-section-hd{display:flex;align-items:center;gap:10px;margin:28px 0 14px}
  .fp-section-hd-line{flex:1;height:1px;background:#E8E6E0}
  .fp-section-hd-text{font-size:11px;font-weight:700;color:#888;text-transform:uppercase;letter-spacing:.8px;white-space:nowrap}
  .fp-card{background:#fff;border:1px solid #E8E6E0;border-radius:14px;padding:20px 22px;transition:box-shadow .2s}
  .fp-card:hover{box-shadow:0 4px 16px rgba(24,95,165,.08)}
  /* Signal hero */
  .sig-hero{border-radius:18px;padding:36px 40px;margin-bottom:24px;position:relative;overflow:hidden}
  .sig-hero::before{content:"";position:absolute;right:-30px;top:-30px;width:200px;height:200px;background:rgba(255,255,255,.06);border-radius:50%}
  .sig-word{font-size:72px;font-weight:900;letter-spacing:-2px;line-height:1}
  .sig-row{display:flex;gap:32px;margin-top:18px;flex-wrap:wrap}
  .sig-stat-label{font-size:10px;opacity:.6;text-transform:uppercase;letter-spacing:.8px;margin-bottom:3px}
  .sig-stat-val{font-size:22px;font-weight:700}
  .sig-justification{font-size:14px;line-height:1.8;margin-top:18px;padding-top:18px;border-top:1px solid rgba(255,255,255,.15);opacity:.9;max-width:720px}
  /* Confidence arc */
  .conf-track{height:10px;background:rgba(255,255,255,.15);border-radius:10px;margin-top:8px;overflow:hidden}
  .conf-fill{height:100%;border-radius:10px;background:rgba(255,255,255,.7)}
  /* Factor cards */
  .factor-card{background:#fff;border:1px solid #E8E6E0;border-radius:10px;padding:14px 16px;margin-bottom:8px;display:flex;align-items:center;gap:14px;transition:box-shadow .15s,border-color .15s}
  .factor-card:hover{box-shadow:0 3px 12px rgba(0,0,0,.06);border-color:#D0CEC8}
  .factor-num{width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px;flex-shrink:0;color:#fff}
  .factor-text{font-size:13.5px;color:#2C2C2A;line-height:1.5}
  /* Data table */
  .dt-row{display:flex;justify-content:space-between;padding:9px 0;border-bottom:1px solid #F0EEE8}
  .dt-row:last-child{border:none}
  .dt-label{font-size:13px;color:#666}
  .dt-val{font-size:13px;font-weight:600;color:#2C2C2A}
  /* Risk badge */
  .risk-badge{display:inline-block;padding:5px 18px;border-radius:30px;font-size:13px;font-weight:700;letter-spacing:.3px}
  /* Empty */
  .fp-empty{text-align:center;padding:80px 20px}
  .fp-empty-icon{font-size:52px;margin-bottom:16px}
  .fp-empty-title{font-size:20px;font-weight:700;color:#2C2C2A;margin-bottom:8px}
  .fp-empty-sub{font-size:14px;color:#888}
</style>
""", unsafe_allow_html=True)

st.markdown("# 💡 AI Trade Signal")

if "trade_signal" not in st.session_state:
    st.markdown("""
<div class="fp-empty">
  <div class="fp-empty-icon">💡</div>
  <div class="fp-empty-title">No signal generated yet</div>
  <div class="fp-empty-sub">Run an analysis from the Home page to generate an AI-powered trade signal.</div>
</div>""", unsafe_allow_html=True)
    st.stop()

signal = st.session_state["trade_signal"]
s      = st.session_state["summary"]
batch  = st.session_state.get("sentiment_batch")

sig_colors  = {"Buy":"#1D9E75","Hold":"#BA7517","Sell":"#D85A30"}
sig_bgs     = {"Buy":"linear-gradient(135deg,#0d3b2e 0%,#1D9E75 100%)",
               "Hold":"linear-gradient(135deg,#3b2a0d 0%,#BA7517 100%)",
               "Sell":"linear-gradient(135deg,#3b0d0d 0%,#D85A30 100%)"}
risk_colors = {"Low":"#1D9E75","Medium":"#BA7517","High":"#D85A30"}

sig_c  = sig_colors.get(signal.signal, "#888")
sig_bg = sig_bgs.get(signal.signal, "linear-gradient(135deg,#222,#555)")
risk_c = risk_colors.get(signal.risk_level, "#888")
conf_p = signal.confidence * 100

# ── Signal hero ───────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="sig-hero" style="background:{sig_bg};color:#fff">
  <div class="sig-word">{signal.signal}</div>
  <div class="sig-row">
    <div>
      <div class="sig-stat-label">Confidence</div>
      <div class="sig-stat-val">{signal.confidence:.0%}</div>
      <div class="conf-track"><div class="conf-fill" style="width:{conf_p:.0f}%"></div></div>
    </div>
    <div>
      <div class="sig-stat-label">Risk Level</div>
      <div class="sig-stat-val">{signal.risk_level}</div>
    </div>
    <div>
      <div class="sig-stat-label">Ticker</div>
      <div class="sig-stat-val">{s['ticker']}</div>
    </div>
    <div>
      <div class="sig-stat-label">Price</div>
      <div class="sig-stat-val">${s['current_price']}</div>
    </div>
  </div>
  <div class="sig-justification">{signal.justification}</div>
</div>""", unsafe_allow_html=True)

# ── Key factors ───────────────────────────────────────────────────────────────
st.markdown('<div class="fp-section-hd"><div class="fp-section-hd-line"></div><div class="fp-section-hd-text">Key Factors</div><div class="fp-section-hd-line"></div></div>', unsafe_allow_html=True)

for i, factor in enumerate(signal.key_factors, 1):
    st.markdown(f"""
<div class="factor-card">
  <div class="factor-num" style="background:{sig_c}">{i}</div>
  <div class="factor-text">{factor}</div>
</div>""", unsafe_allow_html=True)

# ── Supporting data ───────────────────────────────────────────────────────────
st.markdown('<div class="fp-section-hd"><div class="fp-section-hd-line"></div><div class="fp-section-hd-text">Supporting Data</div><div class="fp-section-hd-line"></div></div>', unsafe_allow_html=True)

dc1, dc2 = st.columns(2, gap="large")
with dc1:
    rsi_c2 = "#D85A30" if (s["rsi_14"] or 50)>70 else "#1D9E75" if (s["rsi_14"] or 50)<30 else "#185FA5"
    macd_c2 = "#1D9E75" if "Bull" in s["macd_status"] else "#D85A30"
    sma50_c = "#1D9E75" if s["price_vs_sma50"]=="above" else "#D85A30"
    sma200_c= "#1D9E75" if s["price_vs_sma200"]=="above" else "#D85A30"
    ytd_c   = "#1D9E75" if s["ytd_return_pct"]>=0 else "#D85A30"
    st.markdown(f"""
<div class="fp-card">
  <div style="font-size:12px;font-weight:700;color:#185FA5;text-transform:uppercase;letter-spacing:.5px;margin-bottom:12px">Technical Indicators</div>
  <div class="dt-row"><span class="dt-label">Current Price</span><span class="dt-val">${s['current_price']}</span></div>
  <div class="dt-row"><span class="dt-label">YTD Return</span><span class="dt-val" style="color:{ytd_c}">{s['ytd_return_pct']:+.1f}%</span></div>
  <div class="dt-row"><span class="dt-label">RSI (14)</span><span class="dt-val" style="color:{rsi_c2}">{s['rsi_14']} — {s['rsi_interpretation']}</span></div>
  <div class="dt-row"><span class="dt-label">MACD Status</span><span class="dt-val" style="color:{macd_c2}">{s['macd_status']}</span></div>
  <div class="dt-row"><span class="dt-label">SMA-50</span><span class="dt-val" style="color:{sma50_c}">${s['sma_50']} ({s['price_vs_sma50']})</span></div>
  <div class="dt-row"><span class="dt-label">SMA-200</span><span class="dt-val" style="color:{sma200_c}">${s['sma_200']} ({s['price_vs_sma200']})</span></div>
  <div class="dt-row"><span class="dt-label">SMA Cross</span><span class="dt-val">{s['sma_cross']}</span></div>
  <div class="dt-row"><span class="dt-label">Momentum</span><span class="dt-val">{s['momentum_signal'].upper()}</span></div>
</div>""", unsafe_allow_html=True)

with dc2:
    if batch:
        sent_s = batch.overall_score
        sent_l = "Bullish" if sent_s>0.1 else "Bearish" if sent_s<-0.1 else "Neutral"
        sent_c = "#1D9E75" if sent_s>0.1 else "#D85A30" if sent_s<-0.1 else "#888"
        pos_pct= batch.positive_count/(batch.total_headlines or 1)*100
        neg_pct= batch.negative_count/(batch.total_headlines or 1)*100
        neu_pct= batch.neutral_count /(batch.total_headlines or 1)*100
        st.markdown(f"""
<div class="fp-card">
  <div style="font-size:12px;font-weight:700;color:#185FA5;text-transform:uppercase;letter-spacing:.5px;margin-bottom:12px">News Sentiment</div>
  <div class="dt-row"><span class="dt-label">Overall Score</span><span class="dt-val" style="color:{sent_c}">{sent_s:+.3f} — {sent_l}</span></div>
  <div class="dt-row"><span class="dt-label">Headlines Analysed</span><span class="dt-val">{batch.total_headlines}</span></div>
  <div class="dt-row"><span class="dt-label">Positive</span><span class="dt-val" style="color:#1D9E75">{batch.positive_count} ({pos_pct:.0f}%)</span></div>
  <div class="dt-row"><span class="dt-label">Neutral</span><span class="dt-val" style="color:#888">{batch.neutral_count} ({neu_pct:.0f}%)</span></div>
  <div class="dt-row"><span class="dt-label">Negative</span><span class="dt-val" style="color:#D85A30">{batch.negative_count} ({neg_pct:.0f}%)</span></div>
  <div style="margin-top:14px">
    <div style="display:flex;height:6px;border-radius:6px;overflow:hidden">
      <div style="flex:{pos_pct};background:#1D9E75"></div>
      <div style="flex:{neu_pct};background:#E0DDD6"></div>
      <div style="flex:{neg_pct};background:#D85A30"></div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    # Risk breakdown card
    risk_bg_map = {"Low":"#E1F5EE","Medium":"#FAEEDA","High":"#FCEBEB"}
    st.markdown(f"""
<div class="fp-card" style="margin-top:16px;border-left:3px solid {risk_c}">
  <div style="font-size:12px;font-weight:700;color:#185FA5;text-transform:uppercase;letter-spacing:.5px;margin-bottom:14px">Risk Assessment</div>
  <div style="text-align:center;padding:10px 0">
    <span class="risk-badge" style="background:{risk_bg_map.get(signal.risk_level,'#F5F4F0')};color:{risk_c}">
      {signal.risk_level} Risk
    </span>
  </div>
  <div class="dt-row" style="margin-top:10px"><span class="dt-label">52W High</span><span class="dt-val">${s['52w_high']}</span></div>
  <div class="dt-row"><span class="dt-label">52W Low</span><span class="dt-val">${s['52w_low']}</span></div>
  <div class="dt-row"><span class="dt-label">P/E Ratio</span><span class="dt-val">{s['pe_ratio'] or 'N/A'}</span></div>
</div>""", unsafe_allow_html=True)

disclaimer_box(RISK_DISCLAIMER)
