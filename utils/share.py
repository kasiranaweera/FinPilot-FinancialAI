"""
utils/share.py
UUID-based save & share system.

Flow:
  1. save_report(payload) -> uuid_str
     Serialises the analysis payload to  reports/{uuid}.json
  2. load_report(uuid_str) -> dict | None
     Reads it back.
  3. get_share_url(uuid_str) -> str
     Builds the sharable URL  ?shared={uuid}

Streamlit has no HTTP server of its own, so we implement the "API route"
pattern using st.query_params:
  - Writer page sets  ?shared=<uuid>  in the URL
  - Any page calls    resolve_shared()  on load; if the param is present
    it reads the JSON and re-hydrates session_state automatically.
"""

from __future__ import annotations
import json
import pathlib
import uuid
import datetime
from typing import Any, Dict, Optional

# All reports are stored under  <project_root>/reports/
_REPORTS_DIR = pathlib.Path(__file__).parent.parent / "reports"
_REPORTS_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def save_report(payload: Dict[str, Any]) -> str:
    """Persist payload to reports/<uuid>.json.  Returns the UUID string."""
    uid = str(uuid.uuid4())
    path = _REPORTS_DIR / f"{uid}.json"
    payload["_saved_at"] = datetime.datetime.utcnow().isoformat()
    payload["_uuid"] = uid
    path.write_text(json.dumps(payload, indent=2, default=_json_default), encoding="utf-8")
    return uid


def load_report(uid: str) -> Optional[Dict[str, Any]]:
    """Load a previously saved report.  Returns None if not found."""
    path = _REPORTS_DIR / f"{uid}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def get_share_url(uid: str) -> str:
    """Return the sharable URL (uses Streamlit query-param convention)."""
    try:
        import streamlit as st
        # In newer Streamlit we can read the server address from session info
        base = "http://localhost:8501"
    except Exception:
        base = "http://localhost:8501"
    return f"{base}/Export?shared={uid}"


def build_payload() -> Optional[Dict[str, Any]]:
    """
    Read the current analysis from st.session_state and return a
    serialisable dict.  Returns None if no analysis is loaded.
    """
    import streamlit as st
    import pandas as pd

    if "summary" not in st.session_state:
        return None

    s = st.session_state["summary"]
    sig = st.session_state["trade_signal"]
    batch = st.session_state.get("sentiment_batch")
    info = st.session_state.get("stock_info", {})
    news = st.session_state.get("news", [])

    payload: Dict[str, Any] = {
        "summary": s,
        "stock_info": info,
        "news": news,
        "trade_signal": {
            "signal": sig.signal,
            "confidence": sig.confidence,
            "justification": sig.justification,
            "key_factors": sig.key_factors,
            "risk_level": sig.risk_level,
        },
    }

    if batch:
        payload["sentiment_batch"] = {
            "overall_score": batch.overall_score,
            "total_headlines": batch.total_headlines,
            "positive_count": batch.positive_count,
            "negative_count": batch.negative_count,
            "neutral_count": batch.neutral_count,
            "results": [
                {
                    "headline": r.headline,
                    "sentiment": r.sentiment,
                    "confidence": r.confidence,
                    "brief_reason": r.brief_reason,
                }
                for r in batch.results
            ],
        }

    return payload


def restore_payload(payload: Dict[str, Any]) -> None:
    """Re-hydrate st.session_state from a saved payload."""
    import streamlit as st
    from utils.models import TradeSignal, SentimentBatch, HeadlineSentiment

    st.session_state["summary"] = payload["summary"]
    st.session_state["stock_info"] = payload.get("stock_info", {})
    st.session_state["news"] = payload.get("news", [])

    td = payload["trade_signal"]
    st.session_state["trade_signal"] = TradeSignal(**td)

    sb = payload.get("sentiment_batch")
    if sb:
        results = [HeadlineSentiment(**r) for r in sb.get("results", [])]
        sb_copy = dict(sb)
        sb_copy["results"] = results
        st.session_state["sentiment_batch"] = SentimentBatch(**sb_copy)


def resolve_shared() -> bool:
    """
    Call at the top of every page.
    If ?shared=<uuid> is in query params, load the report and return True.
    """
    import streamlit as st
    params = st.query_params
    uid = params.get("shared", "")
    if not uid:
        return False
    if st.session_state.get("_loaded_uuid") == uid:
        return True   # already loaded this share
    payload = load_report(uid)
    if payload is None:
        st.warning(f"⚠️ Shared report `{uid}` not found or expired.")
        return False
    restore_payload(payload)
    st.session_state["_loaded_uuid"] = uid
    return True


def list_reports() -> list[Dict[str, Any]]:
    """Return metadata for all saved reports, newest first."""
    reports = []
    for f in sorted(_REPORTS_DIR.glob("*.json"), reverse=True):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            reports.append({
                "uuid": data.get("_uuid", f.stem),
                "saved_at": data.get("_saved_at", ""),
                "ticker": data.get("summary", {}).get("ticker", "?"),
                "signal": data.get("trade_signal", {}).get("signal", "?"),
                "as_of_date": data.get("summary", {}).get("as_of_date", "?"),
            })
        except Exception:
            pass
    return reports


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _json_default(obj: Any) -> Any:
    """Fallback JSON serialiser for types json module can't handle."""
    import pandas as pd
    import numpy as np
    if isinstance(obj, (pd.Timestamp, datetime.datetime, datetime.date)):
        return str(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return str(obj)
