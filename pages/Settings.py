"""
pages/7_⚙️_Settings.py — FinPilot Settings
API configuration, model selection, data preferences, app info.
"""
import os
import streamlit as st
from components.sidebar import render_sidebar
from config.settings import APP_TITLE, APP_ICON, APP_VERSION, GROQ_MODELS, PERIODS, DEFAULT_NEWS_COUNT

st.set_page_config(page_title=f"Settings | {APP_TITLE}", page_icon="⚙️", layout="wide", initial_sidebar_state="expanded")
render_sidebar("Settings")

st.markdown("""
<style>
  h2,h3{color:#185FA5}
  .fp-section-hd{display:flex;align-items:center;gap:10px;margin:28px 0 14px}
  .fp-section-hd-line{flex:1;height:1px;background:#E8E6E0}
  .fp-section-hd-text{font-size:11px;font-weight:700;color:#888;text-transform:uppercase;letter-spacing:.8px;white-space:nowrap}
  .settings-card{background:#fff;border:1px solid #E8E6E0;border-radius:16px;padding:24px 28px;margin-bottom:18px;transition:box-shadow .2s}
  .settings-card:hover{box-shadow:0 4px 16px rgba(24,95,165,.07)}
  .settings-card-title{font-size:14px;font-weight:700;color:#2C2C2A;margin-bottom:4px;display:flex;align-items:center;gap:8px}
  .settings-card-desc{font-size:12px;color:#888;margin-bottom:18px}
  .info-row{display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid #F0EEE8}
  .info-row:last-child{border:none}
  .info-label{font-size:13px;color:#666}
  .info-val{font-size:13px;font-weight:600;color:#2C2C2A}
  /* Status pill */
  .status-ok{background:#E1F5EE;color:#0d5c3a;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700}
  .status-missing{background:#FCEBEB;color:#7a1c0a;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700}
  /* Save btn */
  div[data-testid="stButton"] > button[kind="primary"]{
    background:linear-gradient(135deg,#185FA5,#1D4F8A)!important;
    color:#fff!important;border:none!important;border-radius:10px!important;
    font-weight:700!important;padding:10px 28px!important;
    box-shadow:0 4px 14px rgba(24,95,165,.25)!important;
  }
  div[data-testid="stButton"] > button[kind="primary"]:hover{
    box-shadow:0 6px 20px rgba(24,95,165,.4)!important;transform:translateY(-1px)!important;
  }
  /* Clear btn */
  div[data-testid="stButton"] > button:not([kind="primary"]){
    border:1px solid #E8E6E0!important;border-radius:8px!important;
    color:#555!important;font-weight:500!important;
  }
  /* About card */
  .about-card{background:linear-gradient(135deg,#0d2b4e,#185FA5);border-radius:16px;padding:28px 32px;color:#fff;margin-bottom:18px}
  .about-logo{font-size:36px;margin-bottom:10px}
  .about-name{font-size:22px;font-weight:800;letter-spacing:-.3px}
  .about-name em{color:#1D9E75;font-style:normal}
  .about-ver{font-size:12px;opacity:.6;margin-top:4px;margin-bottom:16px}
  .about-row{display:flex;gap:12px;flex-wrap:wrap;margin-top:12px}
  .about-pill{background:rgba(255,255,255,.12);border-radius:20px;padding:4px 14px;font-size:12px}
</style>
""", unsafe_allow_html=True)

st.markdown("# ⚙️ Settings")
st.caption("Configure API keys, model preferences, and data settings.")

# ── API Keys ─────────────────────────────────────────────────────────────────
st.markdown('<div class="fp-section-hd"><div class="fp-section-hd-line"></div><div class="fp-section-hd-text">API Keys</div><div class="fp-section-hd-line"></div></div>', unsafe_allow_html=True)

groq_key = st.session_state.get("groq_key", os.environ.get("GROQ_API_KEY",""))
av_key   = st.session_state.get("av_key",   os.environ.get("AV_API_KEY",""))
groq_ok  = bool(groq_key)
av_ok    = bool(av_key)

st.markdown(f"""
<div class="settings-card">
  <div class="settings-card-title">🔑 API Key Status</div>
  <div class="settings-card-desc">Keys are stored in session memory only — never persisted to disk.</div>
  <div class="info-row">
    <span class="info-label">Groq API Key</span>
    <span class="{'status-ok' if groq_ok else 'status-missing'}">{'✓ Configured' if groq_ok else '✗ Not set'}</span>
  </div>
  <div class="info-row">
    <span class="info-label">Alpha Vantage Key</span>
    <span class="{'status-ok' if av_ok else 'status-missing'}">{'✓ Configured' if av_ok else '✗ Not set (optional)'}</span>
  </div>
</div>""", unsafe_allow_html=True)

with st.form("api_keys_form"):
    st.markdown('<div class="settings-card"><div class="settings-card-title">🔐 Update API Keys</div><div class="settings-card-desc">Enter or update your API keys. These persist for the current session only.</div>', unsafe_allow_html=True)
    new_groq = st.text_input("Groq API Key", value=groq_key, type="password",
                              placeholder="gsk_…", help="Required. Free at console.groq.com")
    new_av   = st.text_input("Alpha Vantage Key", value=av_key, type="password",
                              placeholder="Optional — alphavantage.co")
    st.markdown('</div>', unsafe_allow_html=True)
    if st.form_submit_button("💾 Save API Keys", type="primary"):
        st.session_state["groq_key"] = new_groq
        st.session_state["av_key"]   = new_av
        st.success("✅ API keys saved for this session.")

# ── Model & Analysis ──────────────────────────────────────────────────────────
st.markdown('<div class="fp-section-hd"><div class="fp-section-hd-line"></div><div class="fp-section-hd-text">Model & Analysis Defaults</div><div class="fp-section-hd-line"></div></div>', unsafe_allow_html=True)

with st.form("model_form"):
    st.markdown('<div class="settings-card"><div class="settings-card-title">🤖 Default Model Settings</div><div class="settings-card-desc">These defaults apply when running a new analysis from the Home page.</div>', unsafe_allow_html=True)

    mc1, mc2 = st.columns(2, gap="large")
    with mc1:
        current_model = st.session_state.get("cfg_model", GROQ_MODELS[0])
        idx = GROQ_MODELS.index(current_model) if current_model in GROQ_MODELS else 0
        new_model = st.selectbox("Default Groq Model", GROQ_MODELS, index=idx,
                                  help="llama-3.3-70b gives the best quality results")
        new_news = st.slider("Default News Headlines", 5, 25,
                              st.session_state.get("cfg_news_count", DEFAULT_NEWS_COUNT))
    with mc2:
        current_period = st.session_state.get("cfg_period_label", "1 Year")
        period_keys = list(PERIODS.keys())
        pidx = period_keys.index(current_period) if current_period in period_keys else 2
        new_period = st.selectbox("Default Data Period", period_keys, index=pidx)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.info("💡 Longer periods give better SMA-200 signals but take more time to fetch.")

    st.markdown('</div>', unsafe_allow_html=True)
    if st.form_submit_button("💾 Save Defaults", type="primary"):
        st.session_state["cfg_model"]        = new_model
        st.session_state["cfg_news_count"]   = new_news
        st.session_state["cfg_period_label"] = new_period
        st.success("✅ Defaults saved for this session.")

# ── Session Data ──────────────────────────────────────────────────────────────
st.markdown('<div class="fp-section-hd"><div class="fp-section-hd-line"></div><div class="fp-section-hd-text">Session Data</div><div class="fp-section-hd-line"></div></div>', unsafe_allow_html=True)

has_data = "summary" in st.session_state
ticker   = st.session_state.get("summary",{}).get("ticker","—")
as_of    = st.session_state.get("summary",{}).get("as_of_date","—")

st.markdown(f"""
<div class="settings-card">
  <div class="settings-card-title">🗂️ Current Session</div>
  <div class="settings-card-desc">Data loaded in the current session.</div>
  <div class="info-row"><span class="info-label">Analysis Loaded</span>
    <span class="{'status-ok' if has_data else 'status-missing'}">{'✓ Yes' if has_data else '✗ No'}</span>
  </div>
  <div class="info-row"><span class="info-label">Ticker</span><span class="info-val">{ticker}</span></div>
  <div class="info-row"><span class="info-label">As of Date</span><span class="info-val">{as_of}</span></div>
</div>""", unsafe_allow_html=True)

if has_data:
    if st.button("🗑️ Clear Current Analysis", use_container_width=False):
        for key in ["df","summary","stock_info","news","sentiment_batch","trade_signal"]:
            st.session_state.pop(key, None)
        st.success("Analysis cleared. Run a new analysis from the Home page.")
        st.rerun()

# ── About ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="fp-section-hd"><div class="fp-section-hd-line"></div><div class="fp-section-hd-text">About</div><div class="fp-section-hd-line"></div></div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="about-card">
  <div class="about-logo">📈</div>
  <div class="about-name">Fin<em>Pilot</em>-FinancialAI</div>
  <div class="about-ver">Version {APP_VERSION}</div>
  <div style="font-size:13px;opacity:.8;line-height:1.7;max-width:580px">
    An LLM-powered equity research dashboard built on the CDAZZDEV Task 1 notebook.
    Uses Groq Llama-3 for sentiment analysis and trade signal generation,
    with yfinance for market data and a 4-level fallback data chain.
  </div>
  <div class="about-row">
    <span class="about-pill">Streamlit</span>
    <span class="about-pill">Groq Llama-3</span>
    <span class="about-pill">yfinance</span>
    <span class="about-pill">Plotly</span>
    <span class="about-pill">Pydantic</span>
    <span class="about-pill">ReportLab</span>
  </div>
</div>""", unsafe_allow_html=True)

st.markdown("""
<div class="settings-card">
  <div class="settings-card-title">👨‍💻 Developer</div>
  <div class="info-row"><span class="info-label">Name</span><span class="info-val">Kasi Ranaweera</span></div>
  <div class="info-row"><span class="info-label">Website</span>
    <span class="info-val"><a href="https://kasiranaweera.vercel.app" target="_blank" style="color:#185FA5">kasiranaweera.vercel.app ↗</a></span>
  </div>
  <div class="info-row"><span class="info-label">Notebook</span><span class="info-val">FinPilot - FinancialAI</span></div>
</div>""", unsafe_allow_html=True)
