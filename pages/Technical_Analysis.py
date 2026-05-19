"""
pages/2_📈_Technical_Analysis.py — FinPilot Technical Analysis
"""
import streamlit as st
from components.sidebar import render_sidebar
from components.charts import rsi_chart, macd_chart, returns_histogram
from utils.share import resolve_shared
from config.settings import APP_TITLE, APP_ICON

st.set_page_config(page_title=f"Technical | {APP_TITLE}", page_icon="📈", layout="wide", initial_sidebar_state="expanded")
resolve_shared()
render_sidebar("Technical")

st.markdown("""
<style>
  h2,h3{color:#185FA5}
  .fp-section-hd{display:flex;align-items:center;gap:10px;margin:28px 0 14px}
  .fp-section-hd-line{flex:1;height:1px;background:#E8E6E0}
  .fp-section-hd-text{font-size:11px;font-weight:700;color:#888;text-transform:uppercase;letter-spacing:.8px;white-space:nowrap}
  .fp-card{background:#fff;border:1px solid #E8E6E0;border-radius:14px;padding:20px 22px;margin-bottom:16px;transition:box-shadow .2s}
  .fp-card:hover{box-shadow:0 4px 16px rgba(24,95,165,.08)}
  .fp-card-title{font-size:12px;font-weight:700;color:#185FA5;text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px}
  .fp-card-desc{font-size:12px;color:#888;margin-bottom:14px}
  .ind-row{display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid #F0EEE8}
  .ind-row:last-child{border:none}
  .ind-label{font-size:13px;color:#555;font-weight:500}
  .ind-val{font-size:13px;font-weight:700;color:#2C2C2A}
  .ind-note{font-size:11px;color:#888}
  /* Gauge */
  .fp-gauge-wrap{position:relative;height:10px;background:#F0EEE8;border-radius:10px;overflow:hidden;margin:8px 0}
  .fp-gauge-fill{height:100%;border-radius:10px;transition:width .6s ease}
  /* Big stat */
  .fp-big-stat{text-align:center;padding:20px 12px}
  .fp-big-stat-val{font-size:40px;font-weight:800;line-height:1}
  .fp-big-stat-label{font-size:12px;color:#888;margin-top:6px;text-transform:uppercase;letter-spacing:.5px}
  .fp-big-stat-note{font-size:13px;font-weight:600;margin-top:4px}
  /* Badge */
  .fp-badge{display:inline-block;padding:3px 12px;border-radius:20px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.5px}
  /* Empty state */
  .fp-empty{text-align:center;padding:80px 20px}
  .fp-empty-icon{font-size:52px;margin-bottom:16px}
  .fp-empty-title{font-size:20px;font-weight:700;color:#2C2C2A;margin-bottom:8px}
  .fp-empty-sub{font-size:14px;color:#888}
</style>
""", unsafe_allow_html=True)

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("# 📈 Technical Analysis")

if "df" not in st.session_state or "summary" not in st.session_state:
    st.markdown("""
<div class="fp-empty">
  <div class="fp-empty-icon">📈</div>
  <div class="fp-empty-title">No data loaded yet</div>
  <div class="fp-empty-sub">Run an analysis from the Home page to see technical indicators.</div>
</div>""", unsafe_allow_html=True)
    st.stop()

df = st.session_state["df"]
s  = st.session_state["summary"]
ticker = s["ticker"]

rsi_v  = s["rsi_14"] or 50
rsi_c  = "#D85A30" if rsi_v > 70 else "#1D9E75" if rsi_v < 30 else "#185FA5"
rsi_bg = "#FCEBEB" if rsi_v > 70 else "#E1F5EE" if rsi_v < 30 else "#EEF3FA"
rsi_lbl = s["rsi_interpretation"]

macd_bull = s.get("macd",0) and s.get("macd_signal",0) and float(s["macd"] or 0) > float(s["macd_signal"] or 0)
macd_c = "#1D9E75" if macd_bull else "#D85A30"
macd_lbl = "Bullish" if macd_bull else "Bearish"

bb_pct = (s.get("bb_pct_b") or 0) * 100
bb_fill_pct = min(max(bb_pct, 0), 100)
bb_c = "#D85A30" if bb_pct > 80 else "#1D9E75" if bb_pct < 20 else "#185FA5"

# ══ SUMMARY STAT CARDS ════════════════════════════════════════════════════════
st.markdown('<div class="fp-section-hd"><div class="fp-section-hd-line"></div><div class="fp-section-hd-text">Indicator Snapshot</div><div class="fp-section-hd-line"></div></div>', unsafe_allow_html=True)

ks1, ks2, ks3, ks4 = st.columns(4, gap="small")
with ks1:
    st.markdown(f"""
<div class="fp-card" style="border-top:3px solid {rsi_c}">
  <div class="fp-big-stat">
    <div class="fp-big-stat-val" style="color:{rsi_c}">{rsi_v}</div>
    <div class="fp-big-stat-label">RSI (14)</div>
    <div class="fp-big-stat-note" style="color:{rsi_c}">{rsi_lbl}</div>
  </div>
  <div class="fp-gauge-wrap">
    <div class="fp-gauge-fill" style="width:{rsi_v}%;background:{rsi_c}"></div>
  </div>
  <div style="display:flex;justify-content:space-between;font-size:10px;color:#aaa;margin-top:4px">
    <span>Oversold 30</span><span>Overbought 70</span>
  </div>
</div>""", unsafe_allow_html=True)

with ks2:
    st.markdown(f"""
<div class="fp-card" style="border-top:3px solid {macd_c}">
  <div class="fp-big-stat">
    <div class="fp-big-stat-val" style="color:{macd_c};font-size:28px">{s['macd']}</div>
    <div class="fp-big-stat-label">MACD</div>
    <div class="fp-big-stat-note" style="color:{macd_c}">{s['macd_status']}</div>
  </div>
  <div class="ind-row" style="padding:6px 0">
    <span class="ind-label" style="font-size:12px">Signal Line</span>
    <span class="ind-val" style="font-size:12px">{s['macd_signal']}</span>
  </div>
  <div class="ind-row" style="padding:6px 0;border:none">
    <span class="ind-label" style="font-size:12px">Histogram</span>
    <span class="ind-val" style="font-size:12px;color:{macd_c}">{s['macd_hist']}</span>
  </div>
</div>""", unsafe_allow_html=True)

with ks3:
    sma50_c  = "#1D9E75" if s["price_vs_sma50"]=="above" else "#D85A30"
    sma200_c = "#1D9E75" if s["price_vs_sma200"]=="above" else "#D85A30"
    st.markdown(f"""
<div class="fp-card" style="border-top:3px solid #185FA5">
  <div class="fp-big-stat">
    <div class="fp-big-stat-val" style="font-size:22px;color:#185FA5">{s['sma_cross']}</div>
    <div class="fp-big-stat-label">SMA Cross Signal</div>
  </div>
  <div class="ind-row" style="padding:6px 0">
    <span class="ind-label" style="font-size:12px">SMA-50</span>
    <span class="ind-val" style="font-size:12px;color:{sma50_c}">${s['sma_50']} ↑</span>
  </div>
  <div class="ind-row" style="padding:6px 0;border:none">
    <span class="ind-label" style="font-size:12px">SMA-200</span>
    <span class="ind-val" style="font-size:12px;color:{sma200_c}">${s['sma_200']} ↑</span>
  </div>
</div>""", unsafe_allow_html=True)

with ks4:
    st.markdown(f"""
<div class="fp-card" style="border-top:3px solid {bb_c}">
  <div class="fp-big-stat">
    <div class="fp-big-stat-val" style="color:{bb_c}">{bb_pct:.0f}%</div>
    <div class="fp-big-stat-label">Bollinger %B</div>
    <div class="fp-big-stat-note" style="color:{bb_c}">{'Near Upper Band' if bb_pct>80 else 'Near Lower Band' if bb_pct<20 else 'Mid-Band'}</div>
  </div>
  <div class="fp-gauge-wrap">
    <div class="fp-gauge-fill" style="width:{bb_fill_pct}%;background:{bb_c}"></div>
  </div>
  <div style="display:flex;justify-content:space-between;font-size:10px;color:#aaa;margin-top:4px">
    <span>${s['bb_lower']}</span><span>${s['bb_upper']}</span>
  </div>
</div>""", unsafe_allow_html=True)

# ══ RSI CHART ════════════════════════════════════════════════════════════════
st.markdown('<div class="fp-section-hd"><div class="fp-section-hd-line"></div><div class="fp-section-hd-text">RSI (14) — Relative Strength Index</div><div class="fp-section-hd-line"></div></div>', unsafe_allow_html=True)
st.caption("Above **70** = overbought · Below **30** = oversold · Ideal range 40–60")
st.plotly_chart(rsi_chart(df, ticker), use_container_width=True)

# ══ MACD CHART ═══════════════════════════════════════════════════════════════
st.markdown('<div class="fp-section-hd"><div class="fp-section-hd-line"></div><div class="fp-section-hd-text">MACD (12, 26, 9)</div><div class="fp-section-hd-line"></div></div>', unsafe_allow_html=True)
st.caption("MACD **crossing above** signal line = bullish momentum · **crossing below** = bearish")
st.plotly_chart(macd_chart(df, ticker), use_container_width=True)

# ══ BOLLINGER DETAIL + RETURNS ═══════════════════════════════════════════════
bc1, bc2 = st.columns([1, 1], gap="large")
with bc1:
    st.markdown('<div class="fp-section-hd"><div class="fp-section-hd-line"></div><div class="fp-section-hd-text">Bollinger Bands (20, 2σ)</div><div class="fp-section-hd-line"></div></div>', unsafe_allow_html=True)
    st.markdown(f"""
<div class="fp-card">
  <div class="ind-row"><span class="ind-label">Upper Band</span><span class="ind-val">${s['bb_upper']}</span></div>
  <div class="ind-row"><span class="ind-label">Middle (SMA-20)</span><span class="ind-val">${s['bb_mid']}</span></div>
  <div class="ind-row"><span class="ind-label">Lower Band</span><span class="ind-val">${s['bb_lower']}</span></div>
  <div class="ind-row" style="border:none"><span class="ind-label">Current Price</span><span class="ind-val">${s['current_price']}</span></div>
  <div style="margin-top:12px">
    <div style="font-size:11px;color:#888;margin-bottom:6px">%B Position — {bb_pct:.1f}%</div>
    <div class="fp-gauge-wrap" style="height:12px">
      <div class="fp-gauge-fill" style="width:{bb_fill_pct}%;background:{bb_c}"></div>
    </div>
    <div style="display:flex;justify-content:space-between;font-size:10px;color:#aaa;margin-top:4px">
      <span>Lower Band (0%)</span><span>Middle (50%)</span><span>Upper Band (100%)</span>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

with bc2:
    st.markdown('<div class="fp-section-hd"><div class="fp-section-hd-line"></div><div class="fp-section-hd-text">Daily Return Distribution</div><div class="fp-section-hd-line"></div></div>', unsafe_allow_html=True)
    st.plotly_chart(returns_histogram(df, ticker), use_container_width=True)
