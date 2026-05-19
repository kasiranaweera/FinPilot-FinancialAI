"""
components/nav.py
FinPilot top navigation bar — three-zone layout.

LEFT   : Brand "FinPilot · FinancialAI"
CENTER : Home · Overview · Technical · Sentiment · AI Signal
RIGHT  : 📓 Notebook  📤 Export   (+ Streamlit toolbar sits here naturally)
"""

import streamlit as st

_SENTINEL_ID = "fpnav-sentinel"


def render_nav(active_page: str = "Home"):
    active_path_map = {
        "Home":      "/",
        "Overview":  "/Overview",
        "Technical": "/Technical_Analysis",
        "Sentiment": "/News_Sentiment",
        "AI Signal": "/AI_Signal",
        "Notebook":  "/Notebook",
        "Export":    "/Export",
    }
    active_href = active_path_map.get(active_page, "/")

    center_pages = [
        {"label": "🏠 Home",       "page": "app.py"},
        {"label": "📊 Overview",   "page": "pages/1_📊_Overview.py"},
        {"label": "📈 Technical",  "page": "pages/2_📈_Technical_Analysis.py"},
        {"label": "📰 Sentiment",  "page": "pages/3_📰_News_Sentiment.py"},
        {"label": "🤖 AI Signal",  "page": "pages/4_🤖_AI_Signal.py"},
    ]
    right_pages = [
        {"label": "📓 Notebook",   "page": "pages/5_📓_Notebook.py"},
        {"label": "📤 Export",     "page": "pages/6_📤_Export.py"},
    ]

    st.markdown(f"""
<style>
  [data-testid="stSidebarNav"]{{display:none}}
  .block-container{{padding-top:3.8rem!important}}
  [data-testid="stSidebarContent"]{{padding-top:0!important}}
  [data-testid="stSidebar"] [data-testid="stVerticalBlock"]{{gap:0!important}}
  [data-testid="stAppViewContainer"]{{display:flex!important;flex-direction:row!important}}
  [data-testid="stSidebar"]{{position:relative!important;height:auto!important;min-height:100vh!important;flex-shrink:0!important;z-index:10!important}}
  [data-testid="stSidebar"][aria-expanded="true"]{{min-width:220px!important;max-width:280px!important}}
  [data-testid="stMain"]{{flex:1 1 0%!important;min-width:0!important}}

  /* ── Fixed nav wrapper ── */
  [data-fpnav="true"]{{
    position:fixed!important;top:0!important;
    left:3.5rem!important;right:6rem!important;
    height:3.5rem!important;z-index:999990!important;
    display:flex!important;align-items:center!important;
    background:#FFFFFF!important;
    border-bottom:1.5px solid #E8E6E0!important;
    box-shadow:0 1px 8px rgba(0,0,0,0.07)!important;
    padding:0!important;margin-bottom:-3.5rem!important;
    transition:left 0.3s ease!important;
  }}
  body:has([data-testid="stSidebar"][aria-expanded="true"]) [data-fpnav="true"]{{
    left:calc(280px + 0.5rem)!important;
  }}

  /* Outer 3-column row */
  [data-fpnav="true"] > [data-testid="stHorizontalBlock"]{{
    width:100%!important;gap:0!important;align-items:center!important;flex-wrap:nowrap!important;
  }}

  /* Zone 1 – Brand */
  [data-fpnav="true"] > [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(1){{
    flex:0 0 auto!important;min-width:fit-content!important;
    padding:0 18px 0 14px!important;border-right:1.5px solid #E8E6E0!important;
  }}
  /* Zone 2 – Center */
  [data-fpnav="true"] > [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(2){{
    flex:1 1 auto!important;display:flex!important;justify-content:center!important;padding:0 8px!important;
  }}
  /* Zone 3 – Right */
  [data-fpnav="true"] > [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(3){{
    flex:0 0 auto!important;min-width:fit-content!important;
    padding:0 10px 0 0!important;border-left:1.5px solid #E8E6E0!important;
    display:flex!important;align-items:center!important;justify-content:flex-end!important;
  }}

  /* Inner sub-columns inside zone 2 & 3 */
  [data-fpnav="true"] [data-testid="column"]:nth-child(2) [data-testid="stHorizontalBlock"],
  [data-fpnav="true"] [data-testid="column"]:nth-child(3) [data-testid="stHorizontalBlock"]{{
    gap:2px!important;justify-content:center!important;align-items:center!important;
  }}
  [data-fpnav="true"] [data-testid="column"]:nth-child(2) [data-testid="column"],
  [data-fpnav="true"] [data-testid="column"]:nth-child(3) [data-testid="column"]{{
    flex:0 0 auto!important;min-width:unset!important;max-width:fit-content!important;padding:2px!important;
  }}

  /* page_link base */
  [data-fpnav="true"] [data-testid="stPageLink"]{{padding:0!important}}
  [data-fpnav="true"] [data-testid="stPageLink"] a{{
    text-decoration:none!important;color:#555!important;font-size:12.5px!important;
    font-weight:600!important;padding:5px 10px!important;border-radius:6px!important;
    transition:background 0.15s,color 0.15s!important;white-space:nowrap!important;
    display:inline-flex!important;align-items:center!important;
  }}
  [data-fpnav="true"] [data-testid="stPageLink"] a:hover{{
    background:rgba(24,95,165,0.08)!important;color:#185FA5!important;
  }}
  [data-fpnav="true"] [data-testid="stPageLink"] a[data-active="true"]{{
    background:linear-gradient(135deg,#185FA5 0%,#1D4F8A 100%)!important;
    color:#fff!important;box-shadow:0 2px 6px rgba(24,95,165,0.22)!important;
  }}
  [data-fpnav="true"] [data-testid="stPageLink"] svg{{display:none!important}}
  [data-fpnav="true"] [data-testid="stPageLink"] p{{margin:0!important;font-size:12.5px!important;font-weight:600!important}}

  /* Zone 3 — Notebook pill */
  [data-fpnav="true"] > [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(3) [data-testid="column"]:nth-child(1) [data-testid="stPageLink"] a{{
    background:#F5F4F0!important;color:#444!important;
    border:1px solid #DDD!important;border-radius:20px!important;padding:4px 12px!important;
  }}
  [data-fpnav="true"] > [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(3) [data-testid="column"]:nth-child(1) [data-testid="stPageLink"] a:hover{{
    background:#E8E6E0!important;color:#2C2C2A!important;
  }}
  [data-fpnav="true"] > [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(3) [data-testid="column"]:nth-child(1) [data-testid="stPageLink"] a[data-active="true"]{{
    background:#2C2C2A!important;color:#fff!important;border-color:#2C2C2A!important;box-shadow:none!important;
  }}

  /* Zone 3 — Export pill (green) */
  [data-fpnav="true"] > [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(3) [data-testid="column"]:nth-child(2) [data-testid="stPageLink"] a{{
    background:linear-gradient(135deg,#1D9E75 0%,#15825F 100%)!important;
    color:#fff!important;border-radius:20px!important;padding:4px 13px!important;
    box-shadow:0 2px 6px rgba(29,158,117,0.22)!important;
  }}
  [data-fpnav="true"] > [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(3) [data-testid="column"]:nth-child(2) [data-testid="stPageLink"] a:hover{{
    background:linear-gradient(135deg,#15825F 0%,#0F6347 100%)!important;
  }}
  [data-fpnav="true"] > [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(3) [data-testid="column"]:nth-child(2) [data-testid="stPageLink"] a[data-active="true"]{{
    background:linear-gradient(135deg,#0F6347 0%,#0a4a35 100%)!important;box-shadow:none!important;
  }}

  /* Brand typography */
  .fp-brand{{font-size:15px;font-weight:800;color:#185FA5;white-space:nowrap;letter-spacing:-0.4px;line-height:1;user-select:none}}
  .fp-brand em{{color:#1D9E75;font-style:normal}}
  .fp-brand small{{font-size:10px;font-weight:500;color:#888;display:block;letter-spacing:0.3px;margin-top:1px}}

  @media(max-width:860px){{[data-fpnav="true"]{{display:none!important}}}}
</style>

<script>
(function(){{
  var SID="{_SENTINEL_ID}", ACTIVE="{active_href}";
  function apply(){{
    var el=document.getElementById(SID); if(!el) return;
    var parent=el.closest('[data-testid="stVerticalBlock"]')||el.parentElement; if(!parent) return;
    var hb=parent.querySelector('[data-testid="stHorizontalBlock"]'); if(!hb) return;
    var wrap=hb.parentElement||hb; wrap.setAttribute("data-fpnav","true");
    var norm=ACTIVE.replace(/\/+$/,"")||"/";
    wrap.querySelectorAll('[data-testid="stPageLink"] a').forEach(function(a){{
      var h=(a.getAttribute("href")||"").replace(/\/+$/,"")||"/";
      if(h===norm||(norm==="/"&&(h===""||h==="/")))a.setAttribute("data-active","true");
      else a.removeAttribute("data-active");
    }});
  }}
  apply();
  [100,400,900,1800].forEach(function(ms){{setTimeout(apply,ms);}});
  var last=location.href;
  setInterval(function(){{if(location.href!==last){{last=location.href;setTimeout(apply,200);}}}},300);
}})();
</script>
<div id="{_SENTINEL_ID}" style="display:none"></div>
""", unsafe_allow_html=True)

    # ── Three-zone Streamlit columns ─────────────────────────────────────────
    col1, col2, col3 = st.columns([2.2, 6, 2.8], gap="small")

    with col1:
        st.markdown(
            "<div class='fp-brand'>Fin<em>Pilot</em>"
            "<small>FinancialAI · Research Dashboard</small></div>",
            unsafe_allow_html=True,
        )

    with col2:
        sub = st.columns(len(center_pages), gap="small")
        for c, p in zip(sub, center_pages):
            with c:
                st.page_link(p["page"], label=p["label"], use_container_width=False)

    with col3:
        sub = st.columns(len(right_pages), gap="small")
        for c, p in zip(sub, right_pages):
            with c:
                st.page_link(p["page"], label=p["label"], use_container_width=False)
