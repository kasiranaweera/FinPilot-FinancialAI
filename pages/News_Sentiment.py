"""
pages/3_📰_News_Sentiment.py — FinPilot News & Sentiment
"""
import streamlit as st
from components.sidebar import render_sidebar
from utils.share import resolve_shared
from config.settings import APP_TITLE, APP_ICON

st.set_page_config(page_title=f"Sentiment | {APP_TITLE}", page_icon="📰", layout="wide", initial_sidebar_state="expanded")
resolve_shared()
render_sidebar("Sentiment")

st.markdown("""
<style>
  h2,h3{color:#185FA5}
  .fp-section-hd{display:flex;align-items:center;gap:10px;margin:28px 0 14px}
  .fp-section-hd-line{flex:1;height:1px;background:#E8E6E0}
  .fp-section-hd-text{font-size:11px;font-weight:700;color:#888;text-transform:uppercase;letter-spacing:.8px;white-space:nowrap}
  .fp-card{background:#fff;border:1px solid #E8E6E0;border-radius:14px;padding:20px 22px;margin-bottom:12px;transition:box-shadow .2s,transform .15s}
  .fp-card:hover{box-shadow:0 4px 16px rgba(0,0,0,.06);transform:translateY(-1px)}
  /* Score banner */
  .fp-score-banner{border-radius:18px;padding:28px 32px;margin-bottom:24px;position:relative;overflow:hidden}
  .fp-score-val{font-size:56px;font-weight:800;line-height:1;letter-spacing:-2px}
  .fp-score-label{font-size:18px;font-weight:700;margin-top:4px}
  .fp-score-sub{font-size:13px;opacity:.75;margin-top:4px}
  /* Distribution bar */
  .fp-dist-bar{display:flex;height:8px;border-radius:8px;overflow:hidden;margin:10px 0 6px}
  .fp-dist-labels{display:flex;gap:16px;font-size:12px;color:#555}
  .fp-dist-dot{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:4px;vertical-align:middle}
  /* Headline card */
  .hl-card{background:#fff;border:1px solid #E8E6E0;border-radius:12px;padding:14px 16px;margin-bottom:10px;transition:box-shadow .15s,border-color .15s}
  .hl-card:hover{box-shadow:0 3px 12px rgba(0,0,0,.07);border-color:#D0CEC8}
  .hl-sentiment-bar{width:3px;border-radius:3px;min-height:48px;flex-shrink:0}
  .hl-header{display:flex;align-items:center;gap:10px;margin-bottom:8px}
  .hl-badge{padding:2px 10px;border-radius:20px;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.5px}
  .hl-conf{font-size:11px;color:#888;font-weight:500}
  .hl-text{font-size:13.5px;color:#2C2C2A;font-weight:500;line-height:1.5;margin-bottom:6px}
  .hl-reason{font-size:12px;color:#888;font-style:italic;line-height:1.5}
  /* Conf bar */
  .conf-bar-wrap{height:3px;background:#F0EEE8;border-radius:3px;margin-top:8px;overflow:hidden}
  .conf-bar-fill{height:100%;border-radius:3px}
  /* News feed */
  .nf-item{display:flex;gap:12px;padding:12px 0;border-bottom:1px solid #F0EEE8}
  .nf-item:last-child{border:none}
  .nf-dot{width:6px;height:6px;border-radius:50%;background:#185FA5;flex-shrink:0;margin-top:6px}
  .nf-title{font-size:13.5px;color:#185FA5;font-weight:500;text-decoration:none;line-height:1.5}
  .nf-title:hover{text-decoration:underline}
  .nf-pub{font-size:11px;color:#888;margin-top:3px}
  /* Empty */
  .fp-empty{text-align:center;padding:80px 20px}
  .fp-empty-icon{font-size:52px;margin-bottom:16px}
  .fp-empty-title{font-size:20px;font-weight:700;color:#2C2C2A;margin-bottom:8px}
  .fp-empty-sub{font-size:14px;color:#888}
</style>
""", unsafe_allow_html=True)

st.markdown("# 📰 News Sentiment")

if "sentiment_batch" not in st.session_state:
    st.markdown("""
<div class="fp-empty">
  <div class="fp-empty-icon">📰</div>
  <div class="fp-empty-title">No sentiment data</div>
  <div class="fp-empty-sub">Run an analysis from the Home page to see AI-powered headline sentiment.</div>
</div>""", unsafe_allow_html=True)
    st.stop()

batch = st.session_state["sentiment_batch"]
news  = st.session_state.get("news", [])
s     = st.session_state["summary"]

score = batch.overall_score
total = batch.total_headlines or 1
pos_p = batch.positive_count / total * 100
neg_p = batch.negative_count / total * 100
neu_p = batch.neutral_count  / total * 100

if score > 0.1:
    label="Bullish"; sc="#1D9E75"; bg="linear-gradient(135deg,#0d3b2e,#1D9E75)"
elif score < -0.1:
    label="Bearish"; sc="#D85A30"; bg="linear-gradient(135deg,#3b1a0d,#D85A30)"
else:
    label="Neutral"; sc="#888780"; bg="linear-gradient(135deg,#2a2a28,#888780)"

# ── Score banner ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="fp-score-banner" style="background:{bg};color:#fff">
  <div style="display:flex;align-items:flex-end;gap:32px;flex-wrap:wrap">
    <div>
      <div style="font-size:11px;opacity:.6;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">Overall Sentiment Score</div>
      <div class="fp-score-val">{score:+.3f}</div>
      <div class="fp-score-label">{label}</div>
      <div class="fp-score-sub">{batch.total_headlines} headlines analysed · {s['ticker']}</div>
    </div>
    <div style="flex:1;min-width:200px">
      <div style="font-size:11px;opacity:.6;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px">Breakdown</div>
      <div class="fp-dist-bar">
        <div style="flex:{pos_p};background:#1D9E75"></div>
        <div style="flex:{neu_p};background:rgba(255,255,255,.25)"></div>
        <div style="flex:{neg_p};background:#D85A30"></div>
      </div>
      <div class="fp-dist-labels">
        <span><span class="fp-dist-dot" style="background:#1D9E75"></span>Positive {batch.positive_count}</span>
        <span><span class="fp-dist-dot" style="background:rgba(255,255,255,.4)"></span>Neutral {batch.neutral_count}</span>
        <span><span class="fp-dist-dot" style="background:#D85A30"></span>Negative {batch.negative_count}</span>
      </div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_ai, tab_raw = st.tabs(["🤖 AI Sentiment Analysis", "📡 Raw News Feed"])

with tab_ai:
    if not batch.results:
        st.info("No headline results available.")
    else:
        # Filter bar
        fc1, fc2 = st.columns([2, 1])
        with fc1:
            filter_sent = st.multiselect(
                "Filter by sentiment", ["positive", "neutral", "negative"],
                default=["positive", "neutral", "negative"],
                label_visibility="collapsed"
            )
        with fc2:
            sort_conf = st.toggle("Sort by confidence", value=False)

        items = [r for r in batch.results if r.sentiment in filter_sent]
        if sort_conf:
            items = sorted(items, key=lambda x: x.confidence, reverse=True)

        st.markdown(f"<div style='font-size:12px;color:#888;margin-bottom:12px'>Showing {len(items)} of {batch.total_headlines} headlines</div>", unsafe_allow_html=True)

        sent_cfg = {
            "positive": {"bg":"#E1F5EE","bar":"#1D9E75","badge_bg":"#1D9E75","text_c":"#0d5c3a"},
            "neutral":  {"bg":"#F5F4F0","bar":"#888780","badge_bg":"#888780","text_c":"#444"},
            "negative": {"bg":"#FCEBEB","bar":"#D85A30","badge_bg":"#D85A30","text_c":"#7a1c0a"},
        }
        for item in items:
            cfg  = sent_cfg.get(item.sentiment, sent_cfg["neutral"])
            conf = int(item.confidence * 100)
            conf_c = "#1D9E75" if conf>=70 else "#BA7517" if conf>=50 else "#D85A30"
            st.markdown(f"""
<div class="hl-card" style="border-left:3px solid {cfg['bar']}">
  <div class="hl-header">
    <span class="hl-badge" style="background:{cfg['badge_bg']};color:#fff">{item.sentiment}</span>
    <span class="hl-conf" style="color:{conf_c}">⬤ {conf}% confidence</span>
  </div>
  <div class="hl-text">{item.headline}</div>
  <div class="hl-reason">💬 {item.brief_reason}</div>
  <div class="conf-bar-wrap">
    <div class="conf-bar-fill" style="width:{conf}%;background:{conf_c}"></div>
  </div>
</div>""", unsafe_allow_html=True)

with tab_raw:
    if not news:
        st.info("No raw news data available.")
    else:
        st.markdown(f"<div style='font-size:12px;color:#888;margin-bottom:16px'>{len(news)} recent headlines for {s['ticker']}</div>", unsafe_allow_html=True)
        for item in news:
            pub   = item.get("publisher","")
            link  = item.get("link","#")
            title = item.get("title","")
            st.markdown(f"""
<div class="nf-item">
  <div class="nf-dot"></div>
  <div>
    <a class="nf-title" href="{link}" target="_blank">{title}</a>
    <div class="nf-pub">{pub}</div>
  </div>
</div>""", unsafe_allow_html=True)
