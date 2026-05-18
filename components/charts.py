"""
components/charts.py
Interactive Plotly charts for the Streamlit dashboard.
Replaces the matplotlib static charts from notebook Step 11.
"""

from __future__ import annotations
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


COLORS = {
    "candle_up": "#1D9E75",
    "candle_down": "#D85A30",
    "sma50": "#185FA5",
    "sma200": "#BA7517",
    "volume": "#D3D1C7",
    "rsi": "#185FA5",
    "rsi_ob": "#D85A30",
    "rsi_os": "#1D9E75",
    "macd": "#185FA5",
    "macd_signal": "#D85A30",
    "macd_hist_pos": "#1D9E75",
    "macd_hist_neg": "#D85A30",
    "bb_fill": "rgba(24,95,165,0.08)",
    "bb_line": "rgba(24,95,165,0.4)",
    "bg": "#FAFAF8",
    "grid": "rgba(0,0,0,0.06)",
}


def price_chart(df: pd.DataFrame, ticker: str, show_sma: bool = True) -> go.Figure:
    """Candlestick price chart with optional SMA overlays and volume."""
    tail = df.tail(252)

    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.75, 0.25],
        shared_xaxes=True,
        vertical_spacing=0.03,
    )

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=tail.index,
        open=tail["Open"], high=tail["High"],
        low=tail["Low"], close=tail["Close"],
        name="OHLC",
        increasing_line_color=COLORS["candle_up"],
        decreasing_line_color=COLORS["candle_down"],
        increasing_fillcolor=COLORS["candle_up"],
        decreasing_fillcolor=COLORS["candle_down"],
    ), row=1, col=1)

    if show_sma and "SMA_50" in tail.columns:
        fig.add_trace(go.Scatter(
            x=tail.index, y=tail["SMA_50"],
            name="SMA-50", line=dict(color=COLORS["sma50"], width=1.5),
        ), row=1, col=1)

    if show_sma and "SMA_200" in tail.columns:
        fig.add_trace(go.Scatter(
            x=tail.index, y=tail["SMA_200"],
            name="SMA-200", line=dict(color=COLORS["sma200"], width=1.5, dash="dash"),
        ), row=1, col=1)

    # Bollinger Bands
    if "BB_Upper" in tail.columns:
        fig.add_trace(go.Scatter(
            x=tail.index, y=tail["BB_Upper"],
            name="BB Upper", line=dict(color=COLORS["bb_line"], width=1),
            showlegend=False,
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=tail.index, y=tail["BB_Lower"],
            name="BB Lower", line=dict(color=COLORS["bb_line"], width=1),
            fill="tonexty", fillcolor=COLORS["bb_fill"],
            showlegend=False,
        ), row=1, col=1)

    # Volume bars
    colors = [
        COLORS["candle_up"] if c >= o else COLORS["candle_down"]
        for c, o in zip(tail["Close"], tail["Open"])
    ]
    fig.add_trace(go.Bar(
        x=tail.index, y=tail["Volume"],
        name="Volume", marker_color=colors, opacity=0.6,
    ), row=2, col=1)

    fig.update_layout(
        title=f"{ticker} — Price & Volume (1Y)",
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["bg"],
        legend=dict(orientation="h", y=1.02, x=0),
        xaxis_rangeslider_visible=False,
        hovermode="x unified",
        margin=dict(l=10, r=10, t=50, b=10),
        height=520,
    )
    fig.update_yaxes(gridcolor=COLORS["grid"])
    fig.update_xaxes(gridcolor=COLORS["grid"], showgrid=False)
    return fig


def rsi_chart(df: pd.DataFrame, ticker: str) -> go.Figure:
    """RSI-14 chart with overbought/oversold bands."""
    tail = df.tail(252)

    fig = go.Figure()
    fig.add_hrect(y0=70, y1=100, fillcolor=COLORS["rsi_ob"],
                  opacity=0.08, line_width=0)
    fig.add_hrect(y0=0, y1=30, fillcolor=COLORS["rsi_os"],
                  opacity=0.08, line_width=0)
    fig.add_hline(y=70, line_dash="dash", line_color=COLORS["rsi_ob"],
                  line_width=1, annotation_text="Overbought (70)")
    fig.add_hline(y=30, line_dash="dash", line_color=COLORS["rsi_os"],
                  line_width=1, annotation_text="Oversold (30)")

    fig.add_trace(go.Scatter(
        x=tail.index, y=tail["RSI_14"],
        name="RSI-14", line=dict(color=COLORS["rsi"], width=1.5),
        fill="tozeroy", fillcolor="rgba(24,95,165,0.07)",
    ))

    fig.update_layout(
        title=f"{ticker} — RSI (14)",
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["bg"],
        yaxis=dict(range=[0, 100], gridcolor=COLORS["grid"]),
        xaxis=dict(gridcolor=COLORS["grid"], showgrid=False),
        hovermode="x unified",
        margin=dict(l=10, r=10, t=50, b=10),
        height=300,
    )
    return fig


def macd_chart(df: pd.DataFrame, ticker: str) -> go.Figure:
    """MACD (12,26,9) chart."""
    tail = df.tail(252)

    fig = go.Figure()

    # Histogram bars
    hist_colors = [
        COLORS["macd_hist_pos"] if v >= 0 else COLORS["macd_hist_neg"]
        for v in tail["MACD_Hist"]
    ]
    fig.add_trace(go.Bar(
        x=tail.index, y=tail["MACD_Hist"],
        name="Histogram", marker_color=hist_colors, opacity=0.65,
    ))
    fig.add_trace(go.Scatter(
        x=tail.index, y=tail["MACD"],
        name="MACD", line=dict(color=COLORS["macd"], width=1.5),
    ))
    fig.add_trace(go.Scatter(
        x=tail.index, y=tail["MACD_Signal"],
        name="Signal", line=dict(color=COLORS["macd_signal"], width=1.2, dash="dash"),
    ))

    fig.update_layout(
        title=f"{ticker} — MACD (12, 26, 9)",
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["bg"],
        yaxis=dict(gridcolor=COLORS["grid"]),
        xaxis=dict(gridcolor=COLORS["grid"], showgrid=False),
        hovermode="x unified",
        barmode="overlay",
        margin=dict(l=10, r=10, t=50, b=10),
        height=300,
    )
    return fig


def returns_histogram(df: pd.DataFrame, ticker: str) -> go.Figure:
    """Distribution of daily returns."""
    returns = df["Close"].pct_change().dropna() * 100

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=returns,
        nbinsx=60,
        name="Daily Returns",
        marker_color=COLORS["sma50"],
        opacity=0.75,
    ))
    fig.add_vline(x=0, line_dash="solid", line_color=COLORS["candle_down"], line_width=1.5)

    fig.update_layout(
        title=f"{ticker} — Daily Return Distribution",
        xaxis_title="Daily Return (%)",
        yaxis_title="Frequency",
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["bg"],
        yaxis=dict(gridcolor=COLORS["grid"]),
        xaxis=dict(gridcolor=COLORS["grid"]),
        margin=dict(l=10, r=10, t=50, b=10),
        height=300,
    )
    return fig
