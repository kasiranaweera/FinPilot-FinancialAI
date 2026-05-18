"""
components/nav.py
Top navigation bar for FinPilot.

Uses st.page_link (Streamlit's own router) so session_state is NEVER lost.
Links are LEFT-aligned and packed tightly — no space-between stretching.
The Export link sits at the far RIGHT via a CSS gap trick.

Layout:  [🏠 Home] [📊 Overview] … [📓 Notebook]  ·· spacer ··  [📤 Export]
"""

import streamlit as st

_SENTINEL_ID = "fpnav-sentinel"


def render_nav(active_page: str = "Home"):
    """
    Renders a fixed top navigation bar using st.page_link.
    All left-rail links are left-aligned; Export sits on the right.
    session_state is preserved across all pages.
    """

    # ── Page definitions (left group + right group) ────────────────────────
    left_pages = [
        {"label": "🏠 Home",      "page": "app.py",                           "name": "Home"},
        {"label": "📊 Overview",  "page": "pages/1_📊_Overview.py",           "name": "Overview"},
        {"label": "📈 Technical", "page": "pages/2_📈_Technical_Analysis.py", "name": "Technical"},
        {"label": "📰 Sentiment", "page": "pages/3_📰_News_Sentiment.py",     "name": "Sentiment"},
        {"label": "🤖 AI Signal", "page": "pages/4_🤖_AI_Signal.py",          "name": "AI Signal"},
        {"label": "📓 Notebook",  "page": "pages/5_📓_Notebook.py",           "name": "Notebook"},
    ]
    right_pages = [
        {"label": "📤 Export",    "page": "pages/6_📤_Export.py",             "name": "Export"},
    ]
    all_pages = left_pages + right_pages

    # Active path map used by JS to highlight the current link
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

    # ── CSS + JS ─────────────────────────────────────────────────────────────
    st.markdown(
        f"""
        <style>
            /* ── Hide Streamlit's auto-generated sidebar nav ── */
            [data-testid="stSidebarNav"] {{ display: none; }}

            /* ── Sidebar collapse icon ── */
            [data-testid="stSidebarCollapse"] svg,
            [data-testid="stSidebarCollapseButton"] svg {{ display: none; }}
            [data-testid="stSidebarCollapse"]::after,
            [data-testid="stSidebarCollapseButton"]::after {{
                content: "";
                font-size: 1.2rem;
                display: flex;
                align-items: center;
                justify-content: center;
            }}

            /* Sidebar padding */
            [data-testid="stSidebarContent"] {{ padding-top: 0rem !important; }}
            [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{ gap: 0rem !important; }}

            /* Push main content below the nav bar */
            .block-container {{ padding-top: 3.8rem !important; }}

            /* ══ PUSH SIDEBAR ════════════════════════════════════════════ */
            [data-testid="stAppViewContainer"] {{
                display: flex !important;
                flex-direction: row !important;
            }}
            [data-testid="stSidebar"] {{
                position: relative !important;
                height: auto !important;
                min-height: 100vh !important;
                flex-shrink: 0 !important;
                z-index: 10 !important;
            }}
            [data-testid="stSidebar"][aria-expanded="true"] {{
                min-width: 220px !important;
                max-width: 280px !important;
            }}
            [data-testid="stMain"] {{
                flex: 1 1 0% !important;
                min-width: 0 !important;
            }}

            /* ══ Fixed nav bar ══════════════════════════════════════════ */
            /* The sentinel <div> is placed inline; JS stamps the NEXT
               stVerticalBlock sibling with data-fpnav="true".           */
            [data-fpnav="true"] {{
                position: fixed !important;
                top: 0 !important;
                left: 3.5rem !important;
                right: 7rem !important;       /* leave room for Streamlit toolbar */
                height: 3.5rem !important;
                z-index: 999990 !important;
                display: flex !important;
                align-items: center !important;
                /* LEFT-aligned — no justify-content stretching */
                justify-content: flex-start !important;
                gap: 2px !important;
                padding: 0 0.5rem !important;
                background: transparent !important;
                transition: left 0.3s ease !important;
                margin-bottom: -3.5rem !important; /* collapse normal-flow height */
            }}

            /* Shift nav right when sidebar is expanded */
            [data-testid="stSidebar"][aria-expanded="true"] ~ * [data-fpnav="true"],
            body:has([data-testid="stSidebar"][aria-expanded="true"]) [data-fpnav="true"] {{
                left: calc(280px + 0.5rem) !important;
            }}

            /* ── Inner column containers ── */
            [data-fpnav="true"] [data-testid="stHorizontalBlock"] {{
                gap: 2px !important;
                align-items: center !important;
                flex-wrap: nowrap !important;
                /* Make column row itself left-aligned */
                justify-content: flex-start !important;
                width: 100% !important;
            }}
            [data-fpnav="true"] [data-testid="column"] {{
                padding: 0 !important;
                /* Auto-size to content; do NOT stretch */
                min-width: unset !important;
                max-width: fit-content !important;
                flex: 0 0 auto !important;
            }}
            /* Last column (Export) pushed to the right */
            [data-fpnav="true"] [data-testid="column"]:last-child {{
                margin-left: auto !important;
            }}

            /* ── page_link styles ── */
            [data-fpnav="true"] [data-testid="stPageLink"] {{
                padding: 0 !important;
            }}
            [data-fpnav="true"] [data-testid="stPageLink"] a {{
                text-decoration: none !important;
                color: #555 !important;
                font-size: 13px !important;
                font-weight: 600 !important;
                padding: 5px 11px !important;
                border-radius: 6px !important;
                transition: background 0.15s, color 0.15s !important;
                white-space: nowrap !important;
                display: inline-flex !important;
                align-items: center !important;
            }}
            [data-fpnav="true"] [data-testid="stPageLink"] a:hover {{
                background: rgba(24, 95, 165, 0.08) !important;
                color: #185FA5 !important;
            }}
            [data-fpnav="true"] [data-testid="stPageLink"] a[data-active="true"] {{
                background: linear-gradient(135deg, #185FA5 0%, #1D4F8A 100%) !important;
                color: #fff !important;
                box-shadow: 0 2px 6px rgba(24, 95, 165, 0.25) !important;
            }}
            /* Export button — slightly different pill style */
            [data-fpnav="true"] [data-testid="column"]:last-child [data-testid="stPageLink"] a {{
                background: linear-gradient(135deg, #1D9E75 0%, #15825F 100%) !important;
                color: #fff !important;
                box-shadow: 0 2px 6px rgba(29, 158, 117, 0.25) !important;
                border-radius: 20px !important;
                padding: 5px 14px !important;
            }}
            [data-fpnav="true"] [data-testid="column"]:last-child [data-testid="stPageLink"] a:hover {{
                background: linear-gradient(135deg, #15825F 0%, #0F6347 100%) !important;
                color: #fff !important;
            }}
            [data-fpnav="true"] [data-testid="column"]:last-child [data-testid="stPageLink"] a[data-active="true"] {{
                background: linear-gradient(135deg, #0F6347 0%, #0a4a35 100%) !important;
            }}

            /* Hide default page_link svg arrows */
            [data-fpnav="true"] [data-testid="stPageLink"] svg {{ display: none !important; }}
            [data-fpnav="true"] [data-testid="stPageLink"] p {{
                margin: 0 !important;
                font-size: 13px !important;
                font-weight: 600 !important;
            }}

            @media (max-width: 860px) {{
                [data-fpnav="true"] {{ display: none !important; }}
            }}
        </style>

        <script>
        (function() {{
            var SENTINEL_ID = "{_SENTINEL_ID}";
            var ACTIVE_HREF  = "{active_href}";

            function applyNav() {{
                var sentinel = document.getElementById(SENTINEL_ID);
                if (!sentinel) return;

                /* Walk up to the nearest stVerticalBlock, then look for the
                   NEXT sibling stVerticalBlock — that's our columns row.    */
                var parent = sentinel.closest('[data-testid="stVerticalBlock"]');
                if (!parent) parent = sentinel.parentElement;
                if (!parent) return;

                /* Find first stHorizontalBlock inside the same vertical block */
                var hblock = parent.querySelector('[data-testid="stHorizontalBlock"]');
                if (!hblock) return;

                /* Stamp the outer wrapper (parent of hblock) */
                var wrapper = hblock.parentElement || hblock;
                wrapper.setAttribute("data-fpnav", "true");

                /* Highlight active link */
                var links = wrapper.querySelectorAll('[data-testid="stPageLink"] a');
                var normActive = ACTIVE_HREF.replace(/\\/+$/, "") || "/";
                links.forEach(function(a) {{
                    var href = (a.getAttribute("href") || "").replace(/\\/+$/, "") || "/";
                    if (href === normActive || (normActive === "/" && (href === "" || href === "/"))) {{
                        a.setAttribute("data-active", "true");
                    }} else {{
                        a.removeAttribute("data-active");
                    }}
                }});
            }}

            applyNav();
            [100, 400, 900, 1800].forEach(function(ms) {{ setTimeout(applyNav, ms); }});

            /* Re-apply on SPA route changes */
            var lastHref = location.href;
            setInterval(function() {{
                if (location.href !== lastHref) {{
                    lastHref = location.href;
                    setTimeout(applyNav, 200);
                }}
            }}, 300);
        }})();
        </script>

        <!-- Sentinel: JS uses this to locate the nav columns row -->
        <div id="{_SENTINEL_ID}" style="display:none"></div>
        """,
        unsafe_allow_html=True,
    )

    # ── Native Streamlit page links (session_state-safe) ──────────────────
    # Render left pages + Export all in one columns row.
    # The Export column's CSS 'margin-left: auto' pushes it to the right.
    all_pages = left_pages + right_pages
    cols = st.columns(len(all_pages), gap="small")
    for col, p in zip(cols, all_pages):
        with col:
            st.page_link(p["page"], label=p["label"], use_container_width=False)
