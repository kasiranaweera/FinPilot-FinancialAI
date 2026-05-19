"""
pages/5_📓_Notebook.py — FinPilot Source Notebook Viewer
"""
import json, pathlib
import streamlit as st
from components.sidebar import render_sidebar
from config.settings import APP_TITLE, APP_ICON

st.set_page_config(page_title=f"Notebook | {APP_TITLE}", page_icon="📓", layout="wide", initial_sidebar_state="expanded")
render_sidebar("Notebook")

st.markdown("""
<style>
  .fp-section-hd{display:flex;align-items:center;gap:10px;margin:28px 0 14px}
  .fp-section-hd-line{flex:1;height:1px;background:#E8E6E0}
  .fp-section-hd-text{font-size:11px;font-weight:700;color:#888;text-transform:uppercase;letter-spacing:.8px;white-space:nowrap}
  .nb-meta{background:#fff;border:1px solid #E8E6E0;border-radius:14px;padding:20px 24px;margin-bottom:20px;display:flex;gap:24px;flex-wrap:wrap;align-items:center}
  .nb-meta-item{text-align:center}
  .nb-meta-val{font-size:22px;font-weight:700;color:#185FA5}
  .nb-meta-label{font-size:11px;color:#888;text-transform:uppercase;letter-spacing:.4px;margin-top:2px}
  .nb-cell-code{border-left:3px solid #185FA5}
  .nb-cell-md{border-left:3px solid #1D9E75}
  .nb-cell-raw{border-left:3px solid #888}
  .nb-cell-type{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;margin-bottom:8px}
</style>
""", unsafe_allow_html=True)

st.markdown("# 📓 Source Notebook")
st.caption("Browse the original CDAZZDEV Task 1 notebook that powers FinPilot's analysis pipeline.")

NB_PATH = pathlib.Path(__file__).parent.parent / "notebooks" / "FinPilot-FinancialAI.ipynb"

if not NB_PATH.exists():
    st.error(f"Notebook not found at `{NB_PATH}`. Please place the `.ipynb` file in the `notebooks/` directory.")
    st.stop()

with open(NB_PATH, "r", encoding="utf-8") as f:
    nb = json.load(f)

cells   = nb.get("cells", [])
lang    = nb.get("metadata", {}).get("kernelspec", {}).get("language", "python")
n_code  = sum(1 for c in cells if c["cell_type"]=="code")
n_md    = sum(1 for c in cells if c["cell_type"]=="markdown")

# ── Notebook metadata ─────────────────────────────────────────────────────────
st.markdown(f"""
<div class="nb-meta">
  <div class="nb-meta-item"><div class="nb-meta-val">{len(cells)}</div><div class="nb-meta-label">Total Cells</div></div>
  <div class="nb-meta-item"><div class="nb-meta-val">{n_code}</div><div class="nb-meta-label">Code Cells</div></div>
  <div class="nb-meta-item"><div class="nb-meta-val">{n_md}</div><div class="nb-meta-label">Markdown Cells</div></div>
  <div class="nb-meta-item"><div class="nb-meta-val">{lang.capitalize()}</div><div class="nb-meta-label">Kernel</div></div>
  <div class="nb-meta-item"><div class="nb-meta-val">{nb.get('nbformat','?')}.{nb.get('nbformat_minor','?')}</div><div class="nb-meta-label">Format</div></div>
  <div style="margin-left:auto">
""", unsafe_allow_html=True)

with open(NB_PATH, "rb") as f:
    nb_bytes = f.read()
st.download_button("⬇️ Download Notebook", data=nb_bytes, file_name=NB_PATH.name,
                   mime="application/x-ipynb+json")
st.markdown("</div></div>", unsafe_allow_html=True)

# ── Controls ──────────────────────────────────────────────────────────────────
ctl1, ctl2, ctl3 = st.columns([2, 2, 1])
with ctl1:
    cell_types = sorted({c["cell_type"] for c in cells})
    show_types = st.multiselect("Show cell types", cell_types, default=cell_types)
with ctl2:
    search_q = st.text_input("Search cells", placeholder="Search in cell content…")
with ctl3:
    show_out = st.toggle("Show outputs", value=False)

st.divider()

# ── Render cells ──────────────────────────────────────────────────────────────
shown = 0
for idx, cell in enumerate(cells):
    ct  = cell["cell_type"]
    src = "".join(cell.get("source", []))
    if ct not in show_types:
        continue
    if search_q and search_q.lower() not in src.lower():
        continue
    shown += 1
    border_cls = {"code":"nb-cell-code","markdown":"nb-cell-md"}.get(ct,"nb-cell-raw")
    type_colors = {"code":"#185FA5","markdown":"#1D9E75","raw":"#888"}
    type_c = type_colors.get(ct,"#888")

    with st.expander(f"Cell {idx+1} · {ct.upper()}", expanded=(ct=="markdown")):
        st.markdown(f'<div class="nb-cell-type" style="color:{type_c}">{ct} cell</div>', unsafe_allow_html=True)
        if ct == "markdown":
            st.markdown(src)
        else:
            st.code(src, language=lang if ct=="code" else "text")
        if show_out:
            for out in cell.get("outputs", []):
                ot   = out.get("output_type","")
                text = out.get("text") or out.get("data",{}).get("text/plain",[])
                if isinstance(text, list):
                    text = "".join(text)
                if text:
                    st.text(text[:2000]+("…" if len(text)>2000 else ""))
                elif ot == "error":
                    st.error(f"{out.get('ename')}: {out.get('evalue')}")

st.caption(f"Showing {shown} of {len(cells)} cells.")
