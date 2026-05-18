# 📈 FinPilot-FinancialAI — Equity Research Dashboard

An LLM-powered equity research Streamlit app built from the **CDAZZDEV Task 1** notebook.

## ✨ Features

| Page | Description |
|------|-------------|
| 🏠 Home | Ticker configuration & pipeline runner |
| 📊 Overview | Candlestick chart, key metrics, company info |
| 📈 Technical | RSI, MACD, Bollinger Bands, return distribution |
| 📰 Sentiment | Groq Llama-3 news headline sentiment analysis |
| 🤖 AI Signal | Buy / Hold / Sell recommendation with justification |
| 📓 Notebook | Browse & download the source `.ipynb` inline |

---

## 📁 Folder Structure

```
FinPilot-FinancialAI_app/
├── app.py                          # 🚀 Main Streamlit entry point
├── requirements.txt
├── .env.example                    # API key template
├── .streamlit/
│   └── config.toml                 # Theme & server config
│
├── notebooks/
│   └── FinPilot-FinancialAI.ipynb   # 📓 Source notebook
│
├── pages/                          # Streamlit multi-page app
│   ├── 1_📊_Overview.py
│   ├── 2_📈_Technical_Analysis.py
│   ├── 3_📰_News_Sentiment.py
│   ├── 4_🤖_AI_Signal.py
│   └── 5_📓_Notebook.py
│
├── components/                     # Reusable UI building blocks
│   ├── __init__.py
│   ├── charts.py                   # Plotly chart functions
│   └── ui_elements.py              # Metric cards, badges, bars
│
├── utils/                          # Core business logic
│   ├── __init__.py
│   ├── data_fetcher.py             # OHLCV + news (4-level fallback)
│   ├── indicators.py               # SMA, RSI, MACD, Bollinger Bands
│   ├── llm_analyst.py              # Groq sentiment + trade signal
│   └── models.py                   # Pydantic schemas
│
└── config/                         # App-wide settings
    ├── __init__.py
    └── settings.py
```

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
cd financial_ai_app
pip install -r requirements.txt
```

### 2. Set up API keys

```bash
cp .env.example .env
# Edit .env and add your keys:
#   GROQ_API_KEY=your_groq_key       (required — free at console.groq.com)
#   AV_API_KEY=your_av_key           (optional — alphavantage.co)
```

Or enter them directly in the sidebar when the app runs.

### 3. Run the app

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501)

---

## 🔑 API Keys

| Key | Required | Where to get |
|-----|----------|--------------|
| `GROQ_API_KEY` | ✅ Yes | [console.groq.com](https://console.groq.com) — free tier |
| `AV_API_KEY` | ❌ Optional | [alphavantage.co](https://www.alphavantage.co) — free (25 req/day) |

---

## 🔄 Data Pipeline

The app mirrors the notebook's 4-level OHLCV fallback chain:

```
yfinance (curl_cffi) → Stooq direct HTTP → Alpha Vantage → Error
```

---

## 🧠 LLM Models (Groq)

- `llama-3.3-70b-versatile` (default — best quality)
- `llama-3.1-8b-instant` (faster, lighter)
- `mixtral-8x7b-32768` (alternative)

---

## 📓 Source Notebook

The original notebook is stored at:
```
notebooks/CDAZZDEV_Task1_Financial_AI.ipynb
```

Browse it interactively via the **📓 Notebook** page in the app,
or download it directly from there.
