"""
components/sidebar.py
FinPilot sidebar — full navigation + branding + developer card.

Layout (top → bottom):
  ┌─────────────────────────┐
  │  📈 FinPilot  [close ×] │  ← same level as Streamlit's collapse btn
  ├─────────────────────────┤
  │  MAIN NAVIGATION        │
  │   🏠 Home               │
  │   📈 Technical          │
  │   📰 Sentiment          │
  │   🤖 AI Signal          │
  │   📤 Export             │
  ├─────────────────────────┤
  │  RESOURCES              │
  │   📓 Notebook           │
  │   ⚙️  Settings          │
  ├─────────────────────────┤
  │  [developer card]       │
  └─────────────────────────┘
"""

import streamlit as st


# ── CSS injected once ────────────────────────────────────────────────────────
_SIDEBAR_CSS = """
<style>
  /* ── General sidebar reset ── */
  [data-testid="stSidebar"] {
    background: #F1EFE8 !important;
  }
  [data-testid="stSidebarNav"] { display: none !important; }
  [data-testid="stSidebarContent"] { padding: 0 !important; }

  /* ── Remove top-nav bar entirely (we use sidebar only) ── */
  [data-fpnav="true"] { display: none !important; }
  .block-container { padding-top: 1.8rem !important; }

  /* ── Sidebar inner wrapper ── */
  .fp-sidebar {
    display: flex;
    flex-direction: column;
    height: 100vh;
    padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  }

  /* ── Brand header ── */
  .fp-sb-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 14px 16px 12px 16px;
    border-bottom: 1px solid rgba(15,25,35,0.08);
  }
  .fp-sb-brand-icon {
    width: 34px; height: 34px;
    background: linear-gradient(135deg, #185FA5 0%, #1D9E75 100%);
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; flex-shrink: 0;
  }
  .fp-sb-brand-text { line-height: 1.2; }
  .fp-sb-brand-name {
    font-size: 20px; font-weight: 800; color: #0F1923;
    letter-spacing: -0.3px;
  }
  .fp-sb-brand-name em { color: #1D9E75; font-style: normal; }
  .fp-sb-brand-sub {
    font-size: 12px; color: rgba(15,25,35,0.45);
    letter-spacing: 0.5px; text-transform: uppercase;
  }

  /* ── Nav section label ── */
  .fp-sb-section {
    font-size: 10px; font-weight: 700; color: rgba(15,25,35,0.4);
    text-transform: uppercase; letter-spacing: 1px;
    padding: 16px 16px 6px 16px !important;
    margin-bottom: 15px !important;
  }

  /* ── Nav links ── */
  .fp-sb-nav { padding: 0 8px; flex: 1; overflow-y: auto; }
  .fp-sb-nav a, .fp-sb-nav-btn {
    display: flex; align-items: center; gap: 12px;
    padding: 10px 12px;
    border-radius: 0px;
    font-size: 14px; font-weight: 500;
    color: rgba(15,25,35,0.65);
    text-decoration: none;
    transition: background 0.15s, color 0.15s;
    cursor: pointer;
    border: none; background: transparent; width: 100%;
    text-align: left; margin-bottom: 0px;
  }
  .fp-sb-nav a:hover, .fp-sb-nav-btn:hover {
    background: rgba(15,25,35,0.06);
    color: #0F1923;
  }
  .fp-sb-nav a.active {
    background: rgba(24,95,165,0.12);
    color: #185FA5;
    font-weight: 600;
  }
  .fp-sb-nav-icon {
    width: 28px; height: 28px;
    border-radius: 0px;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; flex-shrink: 0;
    background: rgba(15,25,35,0.06);
  }
  .active .fp-sb-nav-icon {
    background: rgba(24,95,165,0.15);
  }

  /* ── Divider ── */
  .fp-sb-div {
    height: 1px;
    background: rgba(15,25,35,0.08);
    margin: 8px 8px !important;
  }

  /* ── Bottom area ── */
  .fp-sb-bottom { padding: 8px 8px 0 8px; }

  /* ── Developer card ── */
  .fp-dev-card {
    margin: 8px 8px 12px 8px !important;
    background: rgba(24,95,165,0.08);
    border: 1px solid rgba(24,95,165,0.15);
    border-radius: 12px;
    padding: 12px 20px;
    cursor: pointer;
    transition: background 0.15s;
    text-decoration: none;
    display: block;
  }
  .fp-dev-card:hover { background: rgba(24,95,165,0.12); }
  .fp-dev-card-label {
    font-size: 9.5px; font-weight: 700;
    color: rgba(15,25,35,0.4);
    text-transform: uppercase; letter-spacing: 0.8px;
    margin-bottom: 6px;
  }
  .fp-dev-card-inner {
    display: flex; align-items: center; gap: 12px;
  }
  .fp-dev-avatar {
    width: 30px; height: 30px; border-radius: 50%;
    background: linear-gradient(135deg, #185FA5, #1D9E75);
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; color: #fff; font-weight: 700; flex-shrink: 0;
  }
  .fp-dev-name {
    font-size: 12.5px; font-weight: 600; color: #0F1923; line-height: 1.2;
  }
  .fp-dev-link {
    font-size: 10px; color: #1D9E75;
  }
  .fp-dev-arrow {
    margin-left: auto; color: rgba(15,25,35,0.25); font-size: 12px;
  }

  /* ── Loaded ticker badge ── */
  .fp-loaded-badge {
    margin: 4px 8px 6px 8px;
    background: rgba(29,158,117,0.12);
    border: 1px solid rgba(29,158,117,0.2);
    border-radius: 8px;
    padding: 8px 20px;
    font-size: 12px;
    color: #1D9E75;
    display: flex; align-items: center; gap: 8px;
  }
  .fp-loaded-ticker {
    font-weight: 700; font-size: 14px; color: #0F1923;
  }

  /* ── Remove Streamlit element gaps to make buttons a tight list ── */
  [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 4px !important;
  }
  [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {
    gap: 4px !important;
  }
  [data-testid="stSidebar"] .element-container {
    margin-bottom: 0px !important;
  }
</style>
"""


def render_sidebar(active_page: str = "Home") -> None:
    """Render the full dark sidebar with nav, resources, and developer card."""

    # ── Page definitions ─────────────────────────────────────────────────────
    main_nav = [
        {"icon": "🏠", "label": "Home",       "page": "app.py"},
        {"icon": "📈", "label": "Technical",  "page": "pages/Technical_Analysis.py"},
        {"icon": "📰", "label": "Sentiment",  "page": "pages/News_Sentiment.py"},
        {"icon": "💡", "label": "AI Signal",  "page": "pages/AI_Signal.py"},
        {"icon": "📤", "label": "Export",     "page": "pages/Export.py"},
    ]
    resource_nav = [
        {"icon": "📓", "label": "Notebook",  "page": "pages/Notebook.py"},
        {"icon": "⚙️",  "label": "Settings",  "page": "pages/Settings.py"},
    ]

    # ── Generate consolidated navigation CSS ─────────────────────────────────
    nav_item_css = ""
    for item in main_nav + resource_nav:
        is_active = item["label"] == active_page
        label_id = item['label'].replace(' ', '')
        fs = "14px" if item in main_nav else "13.5px"
        nav_item_css += f"""
  .nav-item-{label_id} a, .nav-item-{label_id} button {{
    display: flex !important; align-items: center !important; gap: 10px !important;
    padding: 9px 20px !important; border-radius: 0px !important;
    font-size: {fs} !important; font-weight: {"600" if is_active else "500"} !important;
    color: {"#185FA5" if is_active else "rgba(15,25,35,0.65)"} !important;
    text-decoration: none !important;
    background: {"rgba(24,95,165,0.12)" if is_active else "transparent"} !important;
    transition: background 0.15s, color 0.15s !important;
    margin-bottom: 0px !important;
  }}
  .nav-item-{label_id} a:hover, .nav-item-{label_id} button:hover {{
    background: rgba(15,25,35,0.06) !important; color: #0F1923 !important;
  }}
  .nav-item-{label_id} a svg, .nav-item-{label_id} button svg, 
  .nav-item-{label_id} a p, .nav-item-{label_id} button p {{
    color: {"#185FA5" if is_active else "rgba(15,25,35,0.65)"} !important;
    font-size: {fs} !important; margin: 0 !important;
  }}
  .nav-item-{label_id} [data-testid="stPageLink"] {{ padding: 0 !important; }}
  .nav-item-{label_id} [data-testid="stPageLink"] svg {{ display: none !important; }}
"""

    st.markdown(_SIDEBAR_CSS + f"<style>{nav_item_css}</style>", unsafe_allow_html=True)

    with st.sidebar:
        # ── Brand ────────────────────────────────────────────────────────────
        st.markdown("""
<div class="fp-sb-brand">
  <div class="fp-sb-brand-icon">📈</div>
  <div class="fp-sb-brand-text">
    <div class="fp-sb-brand-name">Fin<em>Pilot</em></div>
    <div class="fp-sb-brand-sub">Financial AI</div>
  </div>
</div>""", unsafe_allow_html=True)



        # ── Main navigation ───────────────────────────────────────────────────
        st.markdown('<div class="fp-sb-section">Main</div>', unsafe_allow_html=True)
        for item in main_nav:
            is_active = item["label"] == active_page
            active_cls = " active" if is_active else ""
            # Use st.page_link for native routing
            with st.container():
                st.markdown(f'<div class="nav-item-{item["label"].replace(" ","")}">', unsafe_allow_html=True)
                st.page_link(item["page"], label=f"{'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'}{item['icon']}{'&nbsp;'}  {item['label']}", use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

        # ── Divider ───────────────────────────────────────────────────────────
        st.markdown('<div class="fp-sb-div"></div>', unsafe_allow_html=True)
        st.markdown('<div class="fp-sb-section">Resources</div>', unsafe_allow_html=True)

        for item in resource_nav:
            is_active = item["label"] == active_page
            with st.container():
                st.markdown(f'<div class="nav-item-{item["label"].replace(" ","")}">', unsafe_allow_html=True)
                st.page_link(item["page"], label=f"{'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'}{item['icon']}{'&nbsp;'}  {item['label']}", use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

        # ── Spacer pushes dev card to bottom ─────────────────────────────────
        st.markdown('<div class="fp-sb-div"></div>', unsafe_allow_html=True)
        st.markdown("<div style='flex:1;min-height:24px'></div>", unsafe_allow_html=True)


        # ── Developer card ────────────────────────────────────────────────────
        st.markdown("""
<a class="fp-dev-card" href="https://kasiranaweera.vercel.app" target="_blank">
  <div class="fp-dev-card-label">Developed by</div>
  <div class="fp-dev-card-inner">
    <div class="fp-dev-avatar">K</div>
    <div>
      <div class="fp-dev-name">Kasi Ranaweera</div>
      <div class="fp-dev-link">kasiranaweera.vercel.app</div>
    </div>
  </div>
</a>""", unsafe_allow_html=True)
