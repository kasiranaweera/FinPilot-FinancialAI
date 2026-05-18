"""
pages/5_📓_Notebook.py
Embedded Jupyter notebook viewer — browse the source notebook inline.
"""

import json
import pathlib
import streamlit as st

st.set_page_config(page_title="Source Notebook", page_icon="📓", layout="wide")
st.title("📓 Source Notebook")
st.caption("Browse the original FinPilot-FinancialAI notebook that powers this dashboard.")

NOTEBOOK_PATH = pathlib.Path(__file__).parent.parent / "notebooks" / "FinPilot-FinancialAI.ipynb"

if not NOTEBOOK_PATH.exists():
    st.error(f"Notebook not found at `{NOTEBOOK_PATH}`")
    st.stop()

# Parse the notebook
with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
    nb = json.load(f)

cells = nb.get("cells", [])
lang = nb.get("metadata", {}).get("kernelspec", {}).get("language", "python")

st.markdown(
    f"**Kernel:** `{lang}` · **Cells:** {len(cells)} · "
    f"**Format:** nbformat {nb.get('nbformat', '?')}.{nb.get('nbformat_minor', '?')}"
)
st.divider()

# Filter options
cell_types = sorted({c["cell_type"] for c in cells})
selected_types = st.multiselect(
    "Show cell types", cell_types, default=cell_types,
    help="Filter which cell types to display"
)

show_outputs = st.checkbox("Show cell outputs", value=False,
                           help="Toggle display of saved cell outputs")

st.divider()

# Render cells
for idx, cell in enumerate(cells):
    cell_type = cell["cell_type"]
    if cell_type not in selected_types:
        continue

    source = "".join(cell.get("source", []))
    outputs = cell.get("outputs", [])

    if cell_type == "markdown":
        with st.expander(f"📝 Markdown cell {idx + 1}", expanded=True):
            st.markdown(source)

    elif cell_type == "code":
        with st.expander(f"💻 Code cell {idx + 1}", expanded=True):
            st.code(source, language=lang)

            if show_outputs and outputs:
                for out in outputs:
                    out_type = out.get("output_type", "")
                    if out_type in ("stream", "display_data", "execute_result"):
                        text = out.get("text") or out.get("data", {}).get("text/plain", [])
                        if isinstance(text, list):
                            text = "".join(text)
                        if text:
                            st.text(text[:2000] + ("..." if len(text) > 2000 else ""))
                    elif out_type == "error":
                        st.error(f"{out.get('ename')}: {out.get('evalue')}")

    elif cell_type == "raw":
        with st.expander(f"📄 Raw cell {idx + 1}", expanded=False):
            st.text(source)

# Download button
with open(NOTEBOOK_PATH, "rb") as f:
    nb_bytes = f.read()

st.divider()
st.download_button(
    label="⬇️ Download Notebook (.ipynb)",
    data=nb_bytes,
    file_name=NOTEBOOK_PATH.name,
    mime="application/x-ipynb+json",
)
