"""
Alpha Machine v5 — Quantitative Intelligence Platform
Gemini 2.5 Flash · numpy/scipy Quant Engine · 6 Data Providers
DCF Valuation · Anti-Portfolio Risk · 23 Intelligence Modes
"""
import streamlit as st
st.set_page_config(page_title="Alpha Machine", page_icon="◈", layout="wide",
                   initial_sidebar_state="expanded")

import requests, feedparser, json, threading, time, math
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from google import genai
from google.genai import types

# ══════════════════════════════════════════════════════════════════════════════
#  MINIMAL UI — clean, readable, mobile-first
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {
    background: #09090f;
    font-family: 'Inter', system-ui, sans-serif;
    color: #e1e4e8;
}
[data-testid="stSidebar"] {
    background: #0d0d14;
    border-right: 1px solid #1c1f2e;
}
[data-testid="stSidebar"] * { color: #b0b8cc !important; }
.block-container { padding: 1.5rem 2rem 3rem; max-width: 1400px; }

/* ── Typography ── */
h1,h2,h3,h4 { color: #f0f2f5; font-weight: 600; letter-spacing: -0.3px; }
p, li { color: #b0b8cc; line-height: 1.75; }

/* ── Header ── */
.am-header { padding: 8px 0 20px; border-bottom: 1px solid #1c1f2e; margin-bottom: 24px; }
.am-logo { font-size: 1.5rem; font-weight: 700; color: #f0f2f5; letter-spacing: -1px; }
.am-logo span { color: #3b82f6; }
.am-sub { font-size: 0.75rem; color: #4a5568; letter-spacing: 1.5px; text-transform: uppercase; margin-top: 2px; }

/* ── Macro ticker strip ── */
.ticker-strip { display: flex; gap: 1px; margin-bottom: 24px; }
.ticker-box {
    flex: 1; background: #0f1117; border: 1px solid #1c1f2e;
    border-radius: 8px; padding: 10px 12px; min-width: 0;
}
.ticker-label { font-size: 0.62rem; color: #4a5568; text-transform: uppercase;
                letter-spacing: 1.5px; display: block; margin-bottom: 3px; }
.ticker-price { font-size: 1.05rem; font-weight: 600; color: #f0f2f5;
                font-family: 'JetBrains Mono', monospace; display: block; }
.up  { color: #22c55e; font-size: 0.72rem; font-weight: 500; }
.dn  { color: #ef4444; font-size: 0.72rem; font-weight: 500; }
.flat{ color: #4a5568; font-size: 0.72rem; }

/* ── Section label ── */
.sec-label {
    font-size: 0.68rem; font-weight: 600; letter-spacing: 2px;
    text-transform: uppercase; color: #4a5568;
    border-bottom: 1px solid #1c1f2e; padding-bottom: 8px; margin: 20px 0 12px;
}

/* ── Report card ── */
.report {
    background: #0f1117;
    border: 1px solid #1c1f2e;
    border-radius: 10px;
    padding: 28px 32px;
    margin: 16px 0;
    line-height: 1.85;
    word-wrap: break-word;
    overflow-wrap: break-word;
    max-width: 100%;
    box-sizing: border-box;
    font-size: 0.93rem;
    color: #c9d1df;
}
.report.blue   { border-left: 3px solid #3b82f6; }
.report.green  { border-left: 3px solid #22c55e; }
.report.amber  { border-left: 3px solid #f59e0b; }
.report.red    { border-left: 3px solid #ef4444; }
.report.purple { border-left: 3px solid #a78bfa; }
.report.teal   { border-left: 3px solid #14b8a6; }
.report.pink   { border-left: 3px solid #ec4899; }
.report.orange { border-left: 3px solid #f97316; }
.report.lime   { border-left: 3px solid #84cc16; }
.report.cyan   { border-left: 3px solid #06b6d4; }
.report.rose   { border-left: 3px solid #f43f5e; }

@media (max-width: 768px) {
    .block-container { padding: 1rem 1rem 2rem; }
    .report { padding: 16px 18px; font-size: 0.88rem; }
    .ticker-price { font-size: 0.9rem; }
}

/* ── Stat cards (DCF/Quant) ── */
.stat-row { display: flex; gap: 10px; flex-wrap: wrap; margin: 12px 0; }
.stat-card {
    background: #0f1117; border: 1px solid #1c1f2e; border-radius: 8px;
    padding: 12px 16px; flex: 1; min-width: 120px;
}
.stat-label { font-size: 0.68rem; color: #4a5568; text-transform: uppercase;
              letter-spacing: 1px; display: block; margin-bottom: 4px; }
.stat-val { font-size: 1.15rem; font-weight: 700; color: #f0f2f5;
            font-family: 'JetBrains Mono', monospace; }
.stat-val.green { color: #22c55e; }
.stat-val.red   { color: #ef4444; }
.stat-val.amber { color: #f59e0b; }

/* ── Signal badge ── */
.badge {
    display: inline-block; padding: 2px 8px; border-radius: 4px;
    font-size: 0.72rem; font-weight: 600; margin: 2px;
}
.badge.buy   { background: #052e1c; color: #22c55e; }
.badge.sell  { background: #2e0505; color: #ef4444; }
.badge.watch { background: #1c1505; color: #f59e0b; }
.badge.blue  { background: #05112e; color: #3b82f6; }

/* ── Alert ── */
.alert-ok  { background:#052e1c; border:1px solid #22c55e; border-radius:7px;
             padding:10px 14px; margin:6px 0; font-size:0.85rem; color:#86efac; }
.alert-err { background:#2e0505; border:1px solid #ef4444; border-radius:7px;
             padding:10px 14px; margin:6px 0; font-size:0.85rem; color:#fca5a5; }

/* ── News ── */
.news-item { padding: 9px 0; border-bottom: 1px solid #1c1f2e; }
.news-title { color: #c9d1df; font-size: 0.85rem; font-weight: 500; display: block; }
.news-src   { color: #4a5568; font-size: 0.72rem; margin-top: 2px; display: block; }

/* ── Tab strip ── */
[data-testid="stTabs"] button {
    font-size: 0.78rem !important; font-weight: 500 !important;
    color: #4a5568 !important; padding: 6px 14px !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #f0f2f5 !important; font-weight: 600 !important;
}
[data-testid="stTabs"] [role="tablist"] {
    border-bottom: 1px solid #1c1f2e; gap: 2px;
}

/* ── Sidebar inputs ── */
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stTextArea textarea {
    background: #13131f !important;
    border: 1px solid #1c1f2e !important;
    color: #c9d1df !important;
    font-size: 0.82rem !important;
}
[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] {
    background: #13131f !important;
    border: 1px solid #1c1f2e !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border: 1px solid #1c1f2e !important;
    border-radius: 8px !important;
    overflow: hidden;
}

/* ── Progress / status ── */
[data-testid="stStatusWidget"] { border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR — API Keys + Config
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("**◈ Alpha Machine v5**")
    st.divider()

    st.markdown("**AI Engine**")
    gemini_key = st.text_input("Gemini API Key", type="password", placeholder="AIza...",
                               help="Free · aistudio.google.com/app/apikey")

    st.markdown("**Data Providers** *(optional — free tiers)*")
    with st.expander("Configure Data APIs"):
        finnhub_key = st.text_input("Finnhub",       type="password", placeholder="60 calls/min",
                                    help="finnhub.io — real-time quotes, news, sentiment")
        fmp_key     = st.text_input("FMP",            type="password", placeholder="250 calls/day",
                                    help="financialmodelingprep.com — financials, DCF")
        av_key      = st.text_input("Alpha Vantage",  type="password", placeholder="25 calls/day",
                                    help="alphavantage.co — technicals, RSI, MACD")
        polygon_key = st.text_input("Polygon.io",     type="password", placeholder="5 calls/min",
                                    help="polygon.io — US market data, normalized")
    st.caption("All providers have free tiers. App works without any data keys using Yahoo Finance fallback.")

    st.markdown("**Alerts**")
    tg_token = st.text_input("Telegram Token", type="password", placeholder="123456:ABC...")
    tg_chat  = st.text_input("Chat ID",        placeholder="-100123456789")

    st.markdown("**Watchlist**")
    stocks_raw  = st.text_area("Stocks",   value="NVDA,TSM,ASML,PLTR,IONQ,RKLB,HIMS,CELH,NVO,MELI", height=70)
    sectors_raw = st.text_area("Sectors",  value="XLK,XLE,XLF,XLV,XBI,ARKK,GDX,COPX,ITB,XAR",      height=55)

    st.divider()
    # Live status
    if gemini_key:
        st.markdown('<span style="color:#22c55e;font-size:0.8rem">● Gemini ready</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span style="color:#ef4444;font-size:0.8rem">● No API key</span>', unsafe_allow_html=True)

    data_count = sum(1 for k in [finnhub_key, fmp_key, av_key, polygon_key] if k)
    st.markdown(f'<span style="color:#3b82f6;font-size:0.8rem">● {data_count}/4 data providers</span>', unsafe_allow_html=True)

    if tg_token and tg_chat:
        st.markdown('<span style="color:#22c55e;font-size:0.8rem">● Telegram connected</span>', unsafe_allow_html=True)

    if st.button("Reset session", use_container_width=True):
        st.session_state.clear(); st.rerun()

STOCKS  = [s.strip() for s in stocks_raw.split(",") if s.strip()]
SECTORS = [s.strip() for s in sectors_raw.split(",") if s.strip()]

# ══════════════════════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="am-header">
  <div class="am-logo">◈ Alpha<span>Machine</span></div>
  <div class="am-sub">Quantitative Intelligence · {datetime.now().strftime("%d %b %Y · %H:%M UTC")} · 23 Modes</div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  DATA LAYER — Yahoo Finance (free fallback) + optional providers
# ══════════════════════════════════════════════════════════════════════════════
YF_HDR = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
          "Accept": "application/json"}

# ── Yahoo Finance (always available) ─────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def yf_price(sym):
    try:
        r = requests.get(
            f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range=5d",
            headers=YF_HDR, timeout=6)
        c = [x for x in r.json()["chart"]["result"][0]["indicators"]["quote"][0]["close"] if x]
        return (round(c[-1],2), round((c[-1]/c[-2]-1)*100,2)) if len(c)>=2 else (None,None)
    except: return None, None

@st.cache_data(ttl=300, show_spinner=False)
def yf_history(sym, range_="3mo"):
    """Return list of close prices."""
    try:
        r = requests.get(
            f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range={range_}",
            headers=YF_HDR, timeout=8)
        res = r.json()["chart"]["result"][0]
        closes = [c for c in res["indicators"]["quote"][0]["close"] if c is not None]
        meta   = res.get("meta", {})
        return closes, meta
    except: return [], {}

# ── Finnhub (60 calls/min free) ───────────────────────────────────────────────
@st.cache_data(ttl=60, show_spinner=False)
def finnhub_quote(sym, key):
    if not key: return {}
    try:
        r = requests.get(f"https://finnhub.io/api/v1/quote?symbol={sym}&token={key}", timeout=5)
        return r.json()
    except: return {}

@st.cache_data(ttl=600, show_spinner=False)
def finnhub_news_sentiment(sym, key):
    if not key: return {}
    try:
        r = requests.get(f"https://finnhub.io/api/v1/news-sentiment?symbol={sym}&token={key}", timeout=6)
        return r.json()
    except: return {}

@st.cache_data(ttl=600, show_spinner=False)
def finnhub_company_news(sym, key, days=7):
    if not key: return []
    try:
        end   = datetime.now().strftime("%Y-%m-%d")
        start = (datetime.now()-timedelta(days=days)).strftime("%Y-%m-%d")
        r = requests.get(f"https://finnhub.io/api/v1/company-news?symbol={sym}&from={start}&to={end}&token={key}", timeout=6)
        return r.json()[:8]
    except: return []

@st.cache_data(ttl=600, show_spinner=False)
def finnhub_insider(sym, key):
    if not key: return []
    try:
        r = requests.get(f"https://finnhub.io/api/v1/stock/insider-transactions?symbol={sym}&token={key}", timeout=6)
        return r.json().get("data", [])[:10]
    except: return []

# ── FMP — Financial Modeling Prep (250 calls/day free) ───────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fmp_income(sym, key, limit=4):
    if not key: return []
    try:
        r = requests.get(f"https://financialmodelingprep.com/api/v3/income-statement/{sym}?limit={limit}&apikey={key}", timeout=8)
        return r.json()
    except: return []

@st.cache_data(ttl=3600, show_spinner=False)
def fmp_cashflow(sym, key, limit=4):
    if not key: return []
    try:
        r = requests.get(f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{sym}?limit={limit}&apikey={key}", timeout=8)
        return r.json()
    except: return []

@st.cache_data(ttl=3600, show_spinner=False)
def fmp_profile(sym, key):
    if not key: return {}
    try:
        r = requests.get(f"https://financialmodelingprep.com/api/v3/profile/{sym}?apikey={key}", timeout=6)
        d = r.json()
        return d[0] if d else {}
    except: return {}

@st.cache_data(ttl=3600, show_spinner=False)
def fmp_ratios(sym, key):
    if not key: return {}
    try:
        r = requests.get(f"https://financialmodelingprep.com/api/v3/ratios/{sym}?limit=1&apikey={key}", timeout=6)
        d = r.json()
        return d[0] if d else {}
    except: return {}

# ── Alpha Vantage (25 calls/day free) — use sparingly ────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def av_rsi(sym, key, period=14):
    if not key: return None
    try:
        r = requests.get("https://www.alphavantage.co/query", params={
            "function":"RSI","symbol":sym,"interval":"daily",
            "time_period":period,"series_type":"close","apikey":key}, timeout=8)
        d = r.json().get("Technical Analysis: RSI", {})
        if d:
            latest_date = sorted(d.keys())[-1]
            return round(float(d[latest_date]["RSI"]),1)
    except: return None

@st.cache_data(ttl=3600, show_spinner=False)
def av_macd(sym, key):
    if not key: return None, None
    try:
        r = requests.get("https://www.alphavantage.co/query", params={
            "function":"MACD","symbol":sym,"interval":"daily","series_type":"close","apikey":key}, timeout=8)
        d = r.json().get("Technical Analysis: MACD", {})
        if d:
            latest = sorted(d.keys())[-1]
            return round(float(d[latest]["MACD"]),3), round(float(d[latest]["MACD_Signal"]),3)
    except: return None, None

# ── EDGAR — SEC filings (free, no key) ───────────────────────────────────────
@st.cache_data(ttl=1800, show_spinner=False)
def edgar_filings(ticker, forms="8-K,4,10-Q"):
    try:
        start = (datetime.now()-timedelta(days=90)).strftime("%Y-%m-%d")
        r = requests.get(
            f"https://efts.sec.gov/LATEST/search-index?q=%22{ticker}%22&dateRange=custom&startdt={start}&forms={forms}",
            headers={"User-Agent":"AlphaMachine research@alpha.com"}, timeout=10)
        hits = r.json().get("hits",{}).get("hits",[])[:8]
        return [{"form":h["_source"].get("form_type",""), "filed":h["_source"].get("file_date",""),
                 "company":h["_source"].get("entity_name","")} for h in hits]
    except: return []

# ── Google News RSS (free) ───────────────────────────────────────────────────
@st.cache_data(ttl=600, show_spinner=False)
def get_news(query, n=8):
    try:
        url  = f"https://news.google.com/rss/search?q={requests.utils.quote(query)}&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(url)
        return [{"title":e.get("title",""),"source":e.get("source",{}).get("title",""),
                 "link":e.get("link","")} for e in feed.entries[:n]]
    except: return []

# ── CoinGecko (crypto, free) ─────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def coingecko_btc():
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price",
            params={"ids":"bitcoin","vs_currencies":"usd","include_24hr_change":"true"},
            timeout=5, headers={"User-Agent":"AlphaMachine/5.0"})
        d = r.json()["bitcoin"]
        return round(d["usd"],0), round(d["usd_24h_change"],2)
    except: return None, None

# ══════════════════════════════════════════════════════════════════════════════
#  QUANTITATIVE ENGINE — numpy/scipy calculations (not guessing)
# ══════════════════════════════════════════════════════════════════════════════

def calc_rsi(closes: list, period: int = 14) -> float:
    """Wilder RSI from price series."""
    if len(closes) < period+1: return 50.0
    arr   = np.array(closes, dtype=float)
    diffs = np.diff(arr)
    gains  = np.where(diffs > 0, diffs, 0.0)
    losses = np.where(diffs < 0, -diffs, 0.0)
    avg_g  = np.mean(gains[-period:])
    avg_l  = np.mean(losses[-period:])
    rs     = avg_g / (avg_l + 1e-9)
    return round(float(100 - 100/(1+rs)), 1)

def calc_macd(closes: list, fast=12, slow=26, signal=9):
    """MACD line and signal line."""
    if len(closes) < slow+signal: return None, None
    arr = pd.Series(closes, dtype=float)
    ema_f = arr.ewm(span=fast, adjust=False).mean()
    ema_s = arr.ewm(span=slow, adjust=False).mean()
    macd  = ema_f - ema_s
    sig   = macd.ewm(span=signal, adjust=False).mean()
    return round(float(macd.iloc[-1]),3), round(float(sig.iloc[-1]),3)

def calc_bollinger(closes: list, period=20, std_dev=2):
    """Returns (upper, mid, lower)."""
    if len(closes) < period: return None, None, None
    arr = np.array(closes[-period:], dtype=float)
    mid = np.mean(arr)
    std = np.std(arr)
    return round(mid+std_dev*std,2), round(mid,2), round(mid-std_dev*std,2)

def calc_atr(highs, lows, closes, period=14):
    """Average True Range."""
    if len(closes) < period+1: return None
    h = np.array(highs[-period-1:], dtype=float)
    l = np.array(lows[-period-1:],  dtype=float)
    c = np.array(closes[-period-1:],dtype=float)
    tr = np.maximum(h[1:]-l[1:], np.maximum(abs(h[1:]-c[:-1]), abs(l[1:]-c[:-1])))
    return round(float(np.mean(tr)), 2)

def calc_correlation_matrix(price_dict: dict) -> pd.DataFrame:
    """Pearson correlation matrix for a dict of {ticker: [closes]}."""
    returns = {}
    for sym, closes in price_dict.items():
        if len(closes) > 5:
            arr = np.array(closes, dtype=float)
            returns[sym] = np.diff(arr) / arr[:-1]
    if not returns: return pd.DataFrame()
    min_len = min(len(v) for v in returns.values())
    df = pd.DataFrame({k: v[-min_len:] for k, v in returns.items()})
    return df.corr().round(3)

def dcf_valuation(revenue: float, revenue_growth: float, fcf_margin: float,
                  wacc: float, terminal_growth: float,
                  shares: float, net_debt: float = 0,
                  years: int = 5) -> dict:
    """
    Full numpy DCF — returns bear/base/bull fair value per share.
    revenue: most recent annual revenue ($M)
    revenue_growth: expected annual growth rate (decimal, e.g. 0.20)
    fcf_margin: FCF / Revenue margin (decimal)
    wacc: weighted avg cost of capital (decimal)
    terminal_growth: long-term FCF growth (decimal)
    shares: shares outstanding (M)
    net_debt: net debt ($M) — positive = net debt, negative = net cash
    """
    scenarios = {
        "Bear":  {"g": revenue_growth * 0.5,  "m": fcf_margin * 0.7,  "wacc": wacc * 1.2},
        "Base":  {"g": revenue_growth,         "m": fcf_margin,         "wacc": wacc},
        "Bull":  {"g": revenue_growth * 1.5,  "m": fcf_margin * 1.25, "wacc": wacc * 0.9},
    }
    results = {}
    for name, s in scenarios.items():
        g, m, w = s["g"], s["m"], s["wacc"]
        rev_proj = np.array([revenue * (1+g)**t for t in range(1, years+1)])
        fcf_proj = rev_proj * m
        discount = np.array([1/(1+w)**t for t in range(1, years+1)])
        pv_fcf   = float(np.sum(fcf_proj * discount))
        # Gordon Growth terminal value
        tv       = fcf_proj[-1] * (1 + terminal_growth) / max(w - terminal_growth, 0.001)
        pv_tv    = tv * discount[-1]
        ev       = pv_fcf + pv_tv
        equity   = ev - net_debt
        fv_share = equity / shares if shares > 0 else 0
        results[name] = {
            "FCF_PV": round(pv_fcf,1), "TV_PV": round(pv_tv,1),
            "EV": round(ev,1), "Equity": round(equity,1),
            "FV_per_share": round(fv_share,2)
        }
    return results

def portfolio_correlation_risk(holdings_dict: dict) -> dict:
    """
    holdings_dict: {ticker: weight_pct}
    Returns correlation matrix + risk flags.
    """
    price_data = {}
    for sym in holdings_dict:
        closes, _ = yf_history(sym, "6mo")
        if closes: price_data[sym] = closes
    corr = calc_correlation_matrix(price_data)
    flags = []
    if not corr.empty:
        for i in range(len(corr.columns)):
            for j in range(i+1, len(corr.columns)):
                c = corr.iloc[i,j]
                if abs(c) > 0.75:
                    flags.append({
                        "pair":  f"{corr.columns[i]} / {corr.columns[j]}",
                        "corr":  round(c,3),
                        "risk":  "HIGH" if abs(c)>0.85 else "MEDIUM"
                    })
    return {"correlation_matrix": corr, "flags": flags}

def score_signals(closes, rsi, macd_line, macd_sig, price, w52h, w52l):
    """Returns (score 0-10, signal_list, verdict)."""
    signals = []; score = 5
    if rsi < 30:  signals.append("🟢 RSI Oversold"); score += 2
    elif rsi < 40: signals.append("🟡 RSI Low"); score += 1
    elif rsi > 70: signals.append("🔴 RSI Overbought"); score -= 2
    elif rsi > 60: signals.append("🟡 RSI Elevated"); score -= 1
    if macd_line and macd_sig:
        if macd_line > macd_sig:  signals.append("🟢 MACD Bullish Cross"); score += 1
        else:                     signals.append("🔴 MACD Bearish"); score -= 1
    if w52h and w52l:
        pct_from_low = (price - w52l) / max(w52h - w52l, 0.01)
        if pct_from_low < 0.25:   signals.append("💎 Near 52W Low"); score += 2
        elif pct_from_low > 0.90: signals.append("🚀 Near 52W High"); score += 1
    if len(closes) > 50:
        ma50 = np.mean(closes[-50:])
        if price > ma50: signals.append("✅ Above 50MA"); score += 1
        else:            signals.append("⚠️ Below 50MA"); score -= 1
    boll_u, boll_m, boll_l = calc_bollinger(closes)
    if boll_l and price < boll_l: signals.append("🟢 BB Oversold"); score += 1
    if boll_u and price > boll_u: signals.append("🔴 BB Overbought"); score -= 1
    score = max(0, min(10, score))
    if score >= 7:   verdict = "STRONG BUY"
    elif score >= 6: verdict = "BUY"
    elif score >= 4: verdict = "WATCH"
    elif score >= 3: verdict = "CAUTION"
    else:            verdict = "AVOID"
    return score, signals, verdict

# ══════════════════════════════════════════════════════════════════════════════
#  COMPOSITE MARKET DATA
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=300, show_spinner=False)
def get_macro_strip():
    tickers = {"10Y":"%5ETNX","SPX":"%5EGSPC","Gold":"GC%3DF",
               "Oil":"CL%3DF","VIX":"%5EVIX","DXY":"DX-Y.NYB"}
    res = {}
    for lbl, sym in tickers.items():
        p, c = yf_price(sym)
        res[lbl] = (p, c)
    p, c = coingecko_btc()
    res["BTC"] = (p, c)
    return res

@st.cache_data(ttl=300, show_spinner=False)
def get_full_stock_table(tickers):
    rows = []
    for sym in tickers:
        closes, meta = yf_history(sym, "3mo")
        if len(closes) < 20:
            rows.append({"Ticker":sym,"Price":"—","1M%":"—","RSI":"—","MACD":"—","Signal":"—","Verdict":"—"}); continue
        price = round(closes[-1],2)
        m1    = round((closes[-1]/closes[-22]-1)*100,2) if len(closes)>=22 else 0
        rsi   = calc_rsi(closes)
        ml, ms= calc_macd(closes)
        w52h  = meta.get("fiftyTwoWeekHigh",0) or 0
        w52l  = meta.get("fiftyTwoWeekLow", 0) or 0
        score, sigs, verdict = score_signals(closes, rsi, ml, ms, price, w52h, w52l)
        macd_str = f"{ml:+.3f}" if ml else "—"
        rows.append({"Ticker":sym,"Price":price,"1M%":m1,"RSI":rsi,"MACD":macd_str,
                     "Score":score,"Verdict":verdict,"Signals":"\n".join(sigs)})
        time.sleep(0.1)
    return pd.DataFrame(rows) if rows else pd.DataFrame()

@st.cache_data(ttl=300, show_spinner=False)
def get_sector_table(tickers):
    rows = []
    for sym in tickers:
        closes, _ = yf_history(sym, "1mo")
        if len(closes) < 5: continue
        m1 = round((closes[-1]/closes[0]-1)*100,2)
        w1 = round((closes[-1]/closes[-6]-1)*100,2) if len(closes)>=6 else 0
        rows.append({"ETF":sym,"1M%":m1,"1W%":w1})
        time.sleep(0.08)
    return pd.DataFrame(rows).sort_values("1M%",ascending=False).reset_index(drop=True) if rows else pd.DataFrame()

# ══════════════════════════════════════════════════════════════════════════════
#  GEMINI AI ENGINE
# ══════════════════════════════════════════════════════════════════════════════

# ── System prompts (institutional grade) ─────────────────────────────────────
SP = {
"macro": """You are a Lead Global Macro Strategist at a tier-1 hedge fund.
Analyze Global Liquidity, Bond Yields, Currency flows, and Volatility.
Always provide: BASE CASE (60-70% prob) + BLACK SWAN (10-20% prob) + SMART MONEY DIVERGENCE.
Be specific with tickers. If X happens → Y is the asymmetric play.""",

"supply": """You are a Supply Chain Forensic Analyst.
Map the 'Nervous System' of any sector. Find the company that owns the IP or bottleneck
that the giants (AAPL, NVDA, TSLA, AMZN) cannot live without.
Bold all tickers: **$TICKER**. Identify: moat owner, capacity constraint, hidden Tier-2 play.""",

"dcf": """You are a Quantitative Valuation Specialist with CFA and CPA credentials.
You combine DCF modeling with qualitative business analysis.
Provide precise bear/base/bull fair value targets with clear assumptions.
Explain what revenue growth rate, FCF margin, and WACC you're using and why.""",

"risk": """You are an Anti-Portfolio Risk Agent at a multi-strategy hedge fund.
Your job: stress-test every bull thesis. Find hidden correlations, concentration risks, and tail risks.
Always check: (1) What's already priced in? (2) What kills this trade? (3) Portfolio overlap?
Be the devil's advocate. Recommend a specific hedge for each position.""",

"earnings": """You are a Forensic Earnings Analyst.
Detect management tone shifts vs prior quarters, sandbagging, guidance games.
Flag metrics management started/stopped reporting. Score credibility 1-10.""",

"geo": """You are a Geopolitical Risk Analyst who thinks in second and third-order effects.
Always identify: direct winners, direct losers, non-obvious plays, and a specific hedge.
Use historical precedents for probability weighting.""",

"sector": """You are a Sector Rotation Specialist at a quantitative macro fund.
Identify sectors in 'early accumulation' vs 'late distribution' using yield curve, PMI, earnings revisions.
Rank by institutional conviction. Provide specific ETF + stock plays.""",

"cio": """You are the CIO of a $10B macro hedge fund.
Synthesize multi-agent research into razor-sharp, actionable investment theses.
Only surface bets scoring 7+/10 across: Asymmetry · Catalyst Clarity · Macro Alignment.
No fluff. Only alpha.""",
}

def call_gemini(system: str, user: str, key: str) -> str:
    if not key: return "[No API key]"
    try:
        client   = genai.Client(api_key=key)
        srch     = types.Tool(google_search=types.GoogleSearch())
        config   = types.GenerateContentConfig(
            tools=[srch], temperature=0.3, system_instruction=system)
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=user, config=config)
        return response.text
    except Exception as e:
        return f"[API error: {e}]"

def stream_gemini(system: str, user: str, key: str):
    if not key: yield "⚠️ No API key."; return
    try:
        client = genai.Client(api_key=key)
        resp   = client.models.generate_content_stream(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(system_instruction=system, temperature=0.35),
            contents=user)
        for chunk in resp:
            if chunk.text: yield chunk.text
    except Exception as e:
        yield f"\n❌ {e}"

def send_telegram(text, token, chat_id):
    if not token or not chat_id: return
    for chunk in [text[i:i+4000] for i in range(0,len(text),4000)]:
        try:
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id":chat_id,"text":chunk}, timeout=10)
        except: pass

# ══════════════════════════════════════════════════════════════════════════════
#  UI HELPERS
# ══════════════════════════════════════════════════════════════════════════════
ACCENT = {"blue":"blue","green":"green","amber":"amber","red":"red","purple":"purple",
          "teal":"teal","pink":"pink","orange":"orange","lime":"lime","cyan":"cyan","rose":"rose"}

def show_result(text: str, color: str = "blue"):
    c = ACCENT.get(color, "blue")
    st.markdown(f'<div class="report {c}"></div>', unsafe_allow_html=True)
    st.markdown(text)

def stat_card(label, value, color=""):
    c = f' class="stat-val {color}"' if color else ' class="stat-val"'
    return f'<div class="stat-card"><span class="stat-label">{label}</span><span{c}>{value}</span></div>'

def show_stat_row(stats: dict):
    """stats = {label: (value, color_class)}"""
    cards = "".join([stat_card(k, v[0], v[1]) for k, v in stats.items()])
    st.markdown(f'<div class="stat-row">{cards}</div>', unsafe_allow_html=True)

def badge(text, kind="blue"):
    return f'<span class="badge {kind}">{text}</span>'

def key_check():
    if not gemini_key:
        st.warning("Enter your Gemini API key in the sidebar — it's free at [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)")
        return False
    return True

def dl_tg(text, prefix):
    c1, c2 = st.columns(2)
    fname = f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with c1: st.download_button("⬇ Download", data=text, file_name=fname, mime="text/plain", use_container_width=True)
    with c2:
        if tg_token and tg_chat:
            if st.button("→ Telegram", key=f"tg_{prefix}_{int(time.time())}", use_container_width=True):
                send_telegram(f"◈ Alpha Machine\n{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n{text}", tg_token, tg_chat)
                st.success("Sent")

# ══════════════════════════════════════════════════════════════════════════════
#  INTELLIGENCE FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

# ── 1. ASYMMETRIC SCAN (5 parallel agents) ───────────────────────────────────
def _agent_macro(key, macro, news): return call_gemini(SP["macro"],
    f"Date:{datetime.now():%Y-%m-%d}\nMACRO:{json.dumps({k:{'p':v[0],'chg':v[1]} for k,v in macro.items()},indent=2)}\nNEWS:{json.dumps(news[:8],indent=2)}\n\nTOP 3 macro tailwinds RIGHT NOW. Each scored 1-10. Use live web search.", key)

def _agent_sector(key, df_sec, news): return call_gemini(SP["sector"],
    f"Date:{datetime.now():%Y-%m-%d}\nETF DATA:{df_sec.to_string(index=False) if not df_sec.empty else 'N/A'}\nNEWS:{json.dumps(news[:6],indent=2)}\n\nTOP 2 sectors in EARLY accumulation. Each scored 1-10.", key)

def _agent_stocks(key, df_st, news): return call_gemini(SP["cio"],
    f"Date:{datetime.now():%Y-%m-%d}\nSTOCK SIGNALS:{df_st[['Ticker','Price','1M%','RSI','Score','Verdict']].to_string(index=False) if not df_st.empty else 'N/A'}\nNEWS:{json.dumps(news[:8],indent=2)}\n\nTOP 3 stocks with 3+ stacking signals. Ticker, signals, catalyst+date, asymmetry score, horizon.", key)

def _agent_contra(key, df_st, news): return call_gemini(SP["risk"],
    f"Date:{datetime.now():%Y-%m-%d}\nSTOCK DATA:{df_st[['Ticker','Price','RSI','Score','Verdict']].to_string(index=False) if not df_st.empty else 'N/A'}\nBEAR NEWS:{json.dumps(news[:6],indent=2)}\n\nStress-test each. BUY/WATCH/AVOID verdict. Flag AVOID prominently.", key)

def _agent_thesis(key, macro_r, sector_r, stocks_r, contra_r):
    return call_gemini(SP["cio"],
    f"MACRO:{macro_r}\nSECTOR:{sector_r}\nSTOCKS:{stocks_r}\nCONTRA:{contra_r}\n\nSynthesize into ASYMMETRIC BET REPORT. Skip AVOID tickers.\n\nFOR EACH BET:\n🎯 BET: [TICKER]\n📊 THEME: [one line]\n🔥 CATALYSTS:\n  • [1]\n  • [2]\n  • [3]\n⚠️ RISK: [one line]\n📈 SETUP: Entry/Target/Stop/Horizon\n🏆 SCORE: Asymmetry/Catalyst/Macro (each /10)\n\nEnd: 📋 PORTFOLIO NOTE + 🌍 MACRO REGIME", key)

def run_alpha_scan(key):
    macro   = get_macro_strip()
    df_sec  = get_sector_table(SECTORS)
    df_st   = get_full_stock_table(STOCKS)
    nm = get_news("Fed inflation geopolitical macro 2026", 6)
    ns = get_news("sector rotation ETF institutional 2026", 5)
    nc = get_news("insider FDA DoD contract earnings catalyst 2026", 7)
    nb = get_news("overvalued crowded short seller warning 2026", 5)
    results = {}
    threads = [
        threading.Thread(target=lambda: results.update({"macro":  _agent_macro(key,macro,nm)})),
        threading.Thread(target=lambda: results.update({"sector": _agent_sector(key,df_sec,ns)})),
        threading.Thread(target=lambda: results.update({"stocks": _agent_stocks(key,df_st,nc)})),
        threading.Thread(target=lambda: results.update({"contra": _agent_contra(key,df_st,nb)})),
    ]
    for t in threads: t.start()
    for t in threads: t.join(timeout=200)
    results["thesis"] = _agent_thesis(key, results.get("macro",""), results.get("sector",""),
                                      results.get("stocks",""), results.get("contra",""))
    return results, df_st

# ── 2. PRO DCF VALUATION ─────────────────────────────────────────────────────
def run_dcf_agent(key, ticker):
    """Pulls real data from FMP if key available, otherwise asks Gemini to estimate."""
    price, chg = yf_price(ticker)
    closes, meta = yf_history(ticker, "1y")
    rsi   = calc_rsi(closes) if closes else None
    ml,ms = calc_macd(closes) if closes else (None,None)
    w52h  = meta.get("fiftyTwoWeekHigh",0) or 0

    # Try to get real financials from FMP
    income  = fmp_income(ticker, fmp_key, 4)  if fmp_key else []
    cashflow= fmp_cashflow(ticker, fmp_key, 4) if fmp_key else []
    profile = fmp_profile(ticker, fmp_key)     if fmp_key else {}
    ratios  = fmp_ratios(ticker, fmp_key)      if fmp_key else {}

    # Extract DCF inputs from real data if available
    quant_context = ""
    dcf_results   = {}

    if income and cashflow:
        try:
            revenues = [abs(i.get("revenue",0))/1e6 for i in income if i.get("revenue")]
            rev_latest = revenues[0] if revenues else 0
            rev_growth = ((revenues[0]/revenues[-1])**(1/max(len(revenues)-1,1))-1) if len(revenues)>1 else 0.15
            fcfs = [abs(c.get("freeCashFlow",0))/1e6 for c in cashflow if c.get("freeCashFlow")]
            fcf_latest = fcfs[0] if fcfs else 0
            fcf_margin = fcf_latest/rev_latest if rev_latest>0 else 0.10
            shares = profile.get("mktCap",0) / (price*1e6) if price and profile.get("mktCap") else 0
            shares = shares if shares > 0 else 1000  # fallback
            net_debt = (profile.get("totalDebt",0) - profile.get("totalCash",0))/1e6 if profile else 0

            # Run DCF
            dcf_results = dcf_valuation(
                revenue=rev_latest, revenue_growth=max(rev_growth,0.05),
                fcf_margin=max(fcf_margin,0.02), wacc=0.10,
                terminal_growth=0.03, shares=shares, net_debt=net_debt)

            quant_context = f"""
REAL FINANCIAL DATA (FMP):
- Revenue (TTM): ${rev_latest:.0f}M
- Revenue CAGR: {rev_growth*100:.1f}%
- FCF (latest): ${fcf_latest:.0f}M
- FCF Margin: {fcf_margin*100:.1f}%
- P/E: {ratios.get('priceEarningsRatio','N/A')}
- EV/EBITDA: {ratios.get('enterpriseValueMultiple','N/A')}
- Debt/Equity: {ratios.get('debtEquityRatio','N/A')}

CALCULATED DCF (numpy):
- Bear FV: ${dcf_results.get('Bear',{}).get('FV_per_share','N/A')}
- Base FV: ${dcf_results.get('Base',{}).get('FV_per_share','N/A')}
- Bull FV: ${dcf_results.get('Bull',{}).get('FV_per_share','N/A')}
- Current Price: ${price}
"""
        except Exception as e:
            quant_context = f"FMP data parsing error: {e}. AI will estimate."
    else:
        quant_context = "No FMP key provided — AI will estimate financials from public data."

    # Technical context
    tech_context = f"""
CALCULATED TECHNICALS (numpy):
- RSI(14): {rsi}
- MACD: {ml}, Signal: {ms}
- 52W High: ${w52h} | Current: ${price}
- Distance from 52W High: {round((price/w52h-1)*100,1) if w52h and price else 'N/A'}%
"""
    # Insider data from Finnhub
    insider_data = ""
    if finnhub_key:
        insiders = finnhub_insider(ticker, finnhub_key)
        if insiders:
            buys  = [i for i in insiders if i.get("transactionType","").lower() in ["p","purchase","buy"]]
            sells = [i for i in insiders if i.get("transactionType","").lower() in ["s","sale","sell"]]
            insider_data = f"\nINSIDER ACTIVITY (Finnhub):\n- Buys (last 3mo): {len(buys)}\n- Sells: {len(sells)}\n"
            if len(buys) > len(sells)*2:
                insider_data += "⚡ CLUSTER BUYING DETECTED — Ultra-High Conviction Signal\n"

    prompt = f"""Date: {datetime.now():%Y-%m-%d}
TICKER: {ticker.upper()}
CURRENT PRICE: ${price} ({chg:+.2f}%) if price else N/A
{quant_context}
{tech_context}
{insider_data}

Run PRO VALUATION ANALYSIS:

## 1. Business Quality Assessment
- What does this company actually sell? Who are the customers?
- Competitive moat: is it durable or eroding?
- Revenue quality (recurring vs one-time, concentration risk)
- Management track record on capital allocation

## 2. DCF Scenarios (use the calculated values above, explain assumptions)
| Scenario | Growth | FCF Margin | WACC | Fair Value |
|----------|--------|-----------|------|-----------|
| Bear     | ...    | ...       | ...  | $...      |
| Base     | ...    | ...       | ...  | $...      |
| Bull     | ...    | ...       | ...  | $...      |

**Current Price vs Fair Value:** [undervalued/fairly valued/overvalued by X%]

## 3. Asymmetric Gap Analysis
- What does the market currently believe about this company?
- What is the market WRONG about? (the asymmetric gap)
- Catalyst that would close the gap and when?

## 4. Supply Chain Alpha
- Who are the Tier-2/3 suppliers benefiting if {ticker} succeeds?
- Any supplier that's a better risk/reward than {ticker} itself?

## 5. Anti-Portfolio Check
- If you already own NVDA/AAPL/MSFT, is this additive or correlated?
- What macro scenario destroys this thesis?

## 6. VERDICT
- **Intrinsic Value:** $X–$X (bear–bull)
- **Margin of Safety at current price:** X%
- **Conviction:** HIGH/MEDIUM/LOW
- **Action:** BUY below $X | SELL above $X | AVOID if [condition]
- **Position size:** X% of portfolio (based on conviction and correlation)"""

    ai_analysis = call_gemini(SP["dcf"], prompt, key)
    return ai_analysis, dcf_results, price

# ── 3. ANTI-PORTFOLIO RISK AGENT ─────────────────────────────────────────────
def run_anti_portfolio(key, holdings_raw: str):
    """Parse holdings, calculate correlations, run AI stress test."""
    # Parse input — flexible format
    holdings = {}
    for item in re.split(r'[,\n]', holdings_raw):
        item = item.strip()
        if not item: continue
        parts = re.split(r'[\s@%]+', item.replace('$',''))
        sym = parts[0].upper()
        wt  = float(parts[1]) if len(parts)>1 else 10.0
        holdings[sym] = wt

    if len(holdings) < 2:
        return "Need at least 2 holdings to analyze portfolio.", pd.DataFrame(), []

    # Calculate real correlations
    corr_data = portfolio_correlation_risk(holdings)
    corr_matrix = corr_data["correlation_matrix"]
    flags = corr_data["flags"]

    # Get quant summary per holding
    quant_summary = []
    for sym, wt in holdings.items():
        closes, _ = yf_history(sym, "3mo")
        rsi = calc_rsi(closes) if len(closes)>20 else None
        p, c = yf_price(sym)
        quant_summary.append({
            "Ticker":sym, "Weight%":wt,
            "Price":p or "—", "RSI":rsi or "—",
            "1D%": round(c,2) if c else "—"
        })

    portfolio_df = pd.DataFrame(quant_summary)
    flags_str = "\n".join([f"• {f['pair']}: corr={f['corr']} ({f['risk']} correlation risk)" for f in flags]) or "No extreme correlations found."

    prompt = f"""Date: {datetime.now():%Y-%m-%d}
PORTFOLIO:
{portfolio_df.to_string(index=False)}

CALCULATED CORRELATION FLAGS (numpy):
{flags_str}

Run ANTI-PORTFOLIO STRESS TEST:

## 1. Concentration Risk
- Sector/factor concentration
- Single stock > 15% of portfolio?
- Which 2 positions are most correlated? What does that mean?

## 2. Five Macro Stress Tests
| Scenario | Estimated Impact | Biggest Loser | Hedge |
|----------|-----------------|---------------|-------|
| 2008-style crash (-40%) | | | |
| Rate spike +200bps | | | |
| Stagflation | | | |
| AI bubble burst (-50% tech) | | | |
| Geopolitical shock (Taiwan) | | | |

## 3. The Double-Down Problem
- Which positions are betting on the same underlying thesis?
- Example: "NVDA + {list(holdings.keys())[1] if len(holdings)>1 else 'X'} = double down on AI chip cycle"
- Risk: if the thesis breaks, both crash simultaneously

## 4. Portfolio Gaps
- What themes are MISSING that would provide real diversification?
- Specific hedges: 3 positions to add for risk reduction

## 5. PORTFOLIO HEALTH SCORE
- Overall score: X/10
- Biggest risk: [one sentence]
- Top 3 immediate actions: (1) ... (2) ... (3) ..."""

    ai_analysis = call_gemini(SP["risk"], prompt, key)
    return ai_analysis, corr_matrix, flags

# ── 4. SUPPLY CHAIN ───────────────────────────────────────────────────────────
def run_supply_chain(key, target):
    news = get_news(f"{target} supply chain supplier 2026", 6)
    return call_gemini(SP["supply"],
        f"Date:{datetime.now():%Y-%m-%d}\nTARGET:{target}\nRELATED NEWS:{json.dumps(news,indent=2)}\n\n"
        f"MAP complete supply chain:\n1. TIER 1 SUPPLIERS — top 5 **$TICKER**, what supplied, dependency\n"
        f"2. TIER 2 HIDDEN PLAYS — 5 **$TICKER**, component, revenue exposure %, asymmetry reason\n"
        f"3. TIER 3 RAW MATERIALS — bottleneck owner, geographic concentration\n"
        f"4. THE MOAT — who owns IP/process giants cannot bypass?\n"
        f"5. TOP 3 ASYMMETRIC BETS — specific **$TICKER**, catalyst, timeline\n"
        f"6. RISKS — geopolitical, substitution, concentration\n"
        f"End with TICKERS: [all mentioned]", key)

# ── 5. SECTOR DIVE ────────────────────────────────────────────────────────────
def run_sector_dive(key, sector):
    df_sec = get_sector_table(SECTORS)
    return call_gemini(SP["sector"],
        f"Date:{datetime.now():%Y-%m-%d}\nSECTOR:{sector}\nETF DATA:{df_sec.to_string(index=False) if not df_sec.empty else 'N/A'}\n\n"
        f"1. Cycle position (early/mid/late)\n2. Top 5 players by asymmetry (score each /10)\n"
        f"3. 3 hidden gems sub-$5B\n4. Macro tailwinds + headwinds\n5. Best asymmetric bet: entry/target/stop\nTICKERS:[all]", key)

# ── 6. GEO TRADE ──────────────────────────────────────────────────────────────
def run_geo_trade(key, scenario):
    return call_gemini(SP["geo"],
        f"Date:{datetime.now():%Y-%m-%d}\nSCENARIO:{scenario}\n\n"
        f"1. Scenario probability & current status\n2. Direct winners top 5 (tickers, magnitude, timeframe)\n"
        f"3. Direct losers top 3 (tickers, specific exposure)\n4. Second-order plays (non-obvious)\n"
        f"5. Best hedge\n6. Highest asymmetry trade: entry/target/stop\nTICKERS:[all]", key)

# ── 7. COMMODITY CHAIN ────────────────────────────────────────────────────────
def run_commodity_chain(key, commodity):
    return call_gemini(SP["supply"],
        f"Date:{datetime.now():%Y-%m-%d}\nCOMMODITY:{commodity}\n\n"
        f"1. Current price & supply/demand balance\n2. Upstream producers top 5 (tickers, production cost)\n"
        f"3. Midstream processors (moat, bottlenecks)\n4. Downstream consumers (winners if price rises/falls)\n"
        f"5. Top 3 asymmetric plays vs commodity ETF\n6. Substitution risk\nTICKERS:[all]", key)

# ── 8. STOCK STRESS TEST ──────────────────────────────────────────────────────
def run_stock_stress(key, ticker):
    price, chg = yf_price(ticker)
    closes, meta = yf_history(ticker, "1y")
    rsi = calc_rsi(closes) if closes else "N/A"
    ml, ms = calc_macd(closes) if closes else (None, None)
    w52h = meta.get("fiftyTwoWeekHigh",0) or 0
    tech = f"RSI:{rsi} | MACD:{ml} vs Signal:{ms} | 52WH:${w52h} | Price:${price}"
    insider_ctx = ""
    if finnhub_key:
        ins = finnhub_insider(ticker, finnhub_key)
        buys  = len([i for i in ins if "p" in i.get("transactionType","").lower()])
        sells = len([i for i in ins if "s" in i.get("transactionType","").lower()])
        insider_ctx = f"\nINSIDER (Finnhub): {buys} buys / {sells} sells (last 90 days)"
    sentiment = finnhub_news_sentiment(ticker, finnhub_key) if finnhub_key else {}
    sent_str = f"\nNEWS SENTIMENT (Finnhub): score={sentiment.get('companyNewsScore','N/A')} | buzz={sentiment.get('buzz',{}).get('buzz','N/A')}" if sentiment else ""
    filings = edgar_filings(ticker)
    filings_str = f"\nSEC FILINGS: {json.dumps(filings[:4],indent=2)}" if filings else ""
    return call_gemini(SP["dcf"],
        f"Date:{datetime.now():%Y-%m-%d}\nTICKER:{ticker}\nPRICE:${price} ({chg:+.2f}%)\n"
        f"TECHNICALS (calculated):{tech}{insider_ctx}{sent_str}{filings_str}\n\n"
        f"1. BULL CASE 12mo — revenue drivers, catalysts, price targets (base/bull)\n"
        f"2. BEAR CASE — short thesis, valuation flags, downside targets\n"
        f"3. FORENSIC FLAGS — accounting, insider trends, debt, customer concentration\n"
        f"4. SUPPLIER PLAY — Tier-2/3 supplier that's a better asymmetric bet?\n"
        f"5. VERDICT: intrinsic value range, crowding 1-10, BUY/HOLD/SELL, key catalyst to watch", key)

# ── 9. PORTFOLIO STRESS ───────────────────────────────────────────────────────
def run_portfolio_stress(key, holdings):
    return call_gemini(SP["risk"],
        f"Date:{datetime.now():%Y-%m-%d}\nPORTFOLIO:{holdings}\n\n"
        f"1. Sector/factor concentration\n2. 5 stress scenarios (2008, rates, stagflation, AI bust, geo shock)\n"
        f"3. Highest risk positions\n4. Gaps & what to add\n5. 3 specific hedges\n6. Health score /10", key)

# ── 10. RELATIVE VALUE ────────────────────────────────────────────────────────
def run_relative_value(key, ta, tb):
    pa,ca=yf_price(ta); pb,cb=yf_price(tb)
    ca_s=ca_s=f"{ca:+.2f}%" if ca else "—"; cb_s=f"{cb:+.2f}%" if cb else "—"
    return call_gemini(SP["dcf"],
        f"Date:{datetime.now():%Y-%m-%d}\n{ta}:${pa} ({ca_s}) vs {tb}:${pb} ({cb_s})\n\n"
        f"1. Valuation table (P/E, Fwd P/E, P/S, EV/EBITDA, PEG — winner each)\n"
        f"2. Growth comparison (revenue, EPS, margin trends)\n3. Moat comparison\n"
        f"4. Balance sheet quality\n5. Pair trade: long/short, entry, target spread, stop\n"
        f"6. Verdict: better risk/reward NOW, conviction, key assumption", key)

# ── 11. ROTATION TIMER ────────────────────────────────────────────────────────
def run_rotation_timer(key):
    macro=get_macro_strip(); df_sec=get_sector_table(SECTORS)
    return call_gemini(SP["macro"],
        f"Date:{datetime.now():%Y-%m-%d}\nMACRO:{json.dumps({k:{'p':v[0],'chg':v[1]} for k,v in macro.items()},indent=2)}\n"
        f"SECTOR PERF:{df_sec.to_string(index=False) if not df_sec.empty else 'N/A'}\n\n"
        f"1. Cycle position evidence\n2. Current sector leadership + institutional flow\n"
        f"3. Next rotation (0-6mo) + historical precedent\n4. 3 timing signals to confirm\n"
        f"5. Highest conviction rotation trade: long/short pair, entry/target/stop\n6. International rotation", key)

# ── 12. CATALYST CALENDAR ─────────────────────────────────────────────────────
def run_catalyst_calendar(key, watchlist):
    return call_gemini(SP["cio"],
        f"Date:{datetime.now():%Y-%m-%d}\nWATCHLIST:{watchlist}\n\n"
        f"1. 90-day calendar: DATE | TICKER | EVENT | EXPECTED IMPACT | ASYMMETRY SCORE\n"
        f"2. Top 5 highest asymmetry events next 30 days (surprise scenario + how to position)\n"
        f"3. Binary events (FDA/regulatory/earnings where vol is cheap)\n"
        f"4. Macro calendar (Fed, CPI, jobs) and watchlist impact\n5. This week's best setup", key)

# ── 13. EARNINGS ANALYZER ─────────────────────────────────────────────────────
def run_earnings_analyzer(key, ticker):
    sentiment = finnhub_news_sentiment(ticker, finnhub_key) if finnhub_key else {}
    sent_ctx = f"\nNEWS SENTIMENT (Finnhub): {json.dumps(sentiment,indent=2)[:300]}" if sentiment else ""
    return call_gemini(SP["earnings"],
        f"Date:{datetime.now():%Y-%m-%d}\nTICKER:{ticker}{sent_ctx}\n\n"
        f"1. Headline numbers vs expectations (EPS, Rev, key metrics)\n"
        f"2. Tone vs prior quarter (more/less confident? specific language changes)\n"
        f"3. What they're hiding (stopped reporting, dodged questions, guidance width)\n"
        f"4. Analyst reaction (target changes, revision direction)\n"
        f"5. Trading implication + credibility score /10", key)

# ── 14. SEC SCANNER ───────────────────────────────────────────────────────────
def run_sec_scanner(key, ticker):
    filings = edgar_filings(ticker)
    insiders = finnhub_insider(ticker, finnhub_key) if finnhub_key else []
    return call_gemini(SP["risk"],
        f"Date:{datetime.now():%Y-%m-%d}\nTICKER:{ticker}\n"
        f"EDGAR FILINGS:{json.dumps(filings,indent=2)}\n"
        f"INSIDER TRANSACTIONS (Finnhub):{json.dumps(insiders[:8],indent=2)}\n\n"
        f"1. Form 4 insider activity — cluster buying/selling, open-market buys (strong signal)\n"
        f"2. 8-K material events — contracts, executive changes, financing\n"
        f"3. 10-Q red flags — new risk factors, revenue recognition, cash burn runway\n"
        f"4. Red flags vs bullish signals\n5. Net signal: BULLISH/NEUTRAL/BEARISH + trading implication", key)

# ── 15. OPTIONS FLOW ──────────────────────────────────────────────────────────
def run_options_flow(key, ticker):
    price, chg = yf_price(ticker)
    sentiment  = finnhub_news_sentiment(ticker, finnhub_key) if finnhub_key else {}
    return call_gemini(SP["cio"],
        f"Date:{datetime.now():%Y-%m-%d}\nTICKER:{ticker}\nPRICE:${price} ({chg:+.2f}%)\n"
        f"SENTIMENT:{json.dumps(sentiment,indent=2)[:300] if sentiment else 'N/A'}\n\n"
        f"Use live web search for unusual options activity, IV data, put/call ratios.\n"
        f"1. Put/call ratio signal\n2. Unusual activity (last 5 days)\n3. IV vs HV (cheap or expensive?)\n"
        f"4. Smart money verdict: BULLISH/BEARISH/HEDGING + conviction\n"
        f"5. Best options trade now: structure, strike, expiry, risk/reward", key)

# ── 16. 13F TRACKER ───────────────────────────────────────────────────────────
def run_13f_tracker(key, query):
    return call_gemini(SP["cio"],
        f"Date:{datetime.now():%Y-%m-%d}\nQUERY:{query}\n\n"
        f"Use live web search for latest 13F. 1. Latest filing snapshot\n"
        f"2. New positions (initiated this quarter)\n3. Largest additions\n4. Largest exits\n"
        f"5. What is this manager betting on? Best copycat trade. (Note: 13Fs are 45-day delayed)", key)

# ── 17. WATCHDOG ──────────────────────────────────────────────────────────────
def run_watchdog(key, tickers_list, triggers):
    rows = []
    for sym in tickers_list:
        closes, meta = yf_history(sym, "3mo")
        if not closes: continue
        p = round(closes[-1],2)
        rsi = calc_rsi(closes)
        m1  = round((closes[-1]/closes[-22]-1)*100,2) if len(closes)>=22 else 0
        w52h = meta.get("fiftyTwoWeekHigh",0) or 0
        fired = []
        if "RSI < 30"      in triggers and rsi < 30:    fired.append(f"RSI={rsi} OVERSOLD")
        if "RSI > 75"      in triggers and rsi > 75:    fired.append(f"RSI={rsi} OVERBOUGHT")
        if "Drop > 8% 1M"  in triggers and m1 < -8:     fired.append(f"1M={m1}% DIP")
        if "Momentum >15%" in triggers and m1 > 15:     fired.append(f"1M={m1}% MOMENTUM")
        if "Near 52W High" in triggers and w52h and p>=w52h*0.98: fired.append("NEAR 52W HIGH")
        if fired: rows.append({"ticker":sym,"price":p,"signals":fired})
    if not rows:
        return [], "✅ No alerts fired — all within normal parameters."
    alert_str = "\n".join([f"• {r['ticker']} @ ${r['price']}: {', '.join(r['signals'])}" for r in rows])
    ai = call_gemini(SP["cio"],
        f"FIRED ALERTS:\n{alert_str}\n\nFor each: is it actionable NOW or false positive? "
        f"Urgency: ACT NOW / WATCH / LOW. End with TOP PRIORITY: [ticker] — [one sentence why]", key)
    return rows, ai

# ── 18. BACKTESTER ────────────────────────────────────────────────────────────
def run_backtester(key, thesis, ticker):
    closes, _ = yf_history(ticker, "1y")
    price = round(closes[-1],2) if closes else None
    rsi   = calc_rsi(closes) if closes else None
    return call_gemini(SP["dcf"],
        f"Date:{datetime.now():%Y-%m-%d}\nTICKER:{ticker}\nCURRENT PRICE:${price}\nRSI:{rsi}\n"
        f"THESIS:{thesis}\n\n"
        f"1. Core assumptions — what must go RIGHT and WRONG\n"
        f"2. Historical regime analysis (2008 crash, 2020 COVID, 2022 rate hikes, 2024 AI bull)\n"
        f"3. Performance metrics (best case, base case, worst drawdown, Sharpe quality)\n"
        f"4. Thesis killers ranked by probability\n"
        f"5. Historical base rate of success for this type of bet\n"
        f"6. Optimal position sizing, stop loss, conviction level", key)

# ── 19. NEWSLETTER ────────────────────────────────────────────────────────────
def run_newsletter(key, scan_results, name, newsletter):
    thesis = scan_results.get("thesis","") if scan_results else ""
    return call_gemini(SP["cio"],
        f"Date:{datetime.now():%Y-%m-%d}\nNEWSLETTER:{newsletter}\nAUTHOR:{name}\n"
        f"RESEARCH:{thesis[:2500] if thesis else 'Use live web search for current market context'}\n\n"
        f"Write full weekly newsletter (600-900 words):\n"
        f"# [Title]\n## Macro Backdrop\n## The Alpha Opportunity\n## Sector Rotation Signal\n"
        f"## Portfolio Moves\n## Key Dates Next Week\n## One-Line Market Take\n"
        f"Tone: confident, data-driven, slightly contrarian. No fluff.", key)

# ══════════════════════════════════════════════════════════════════════════════
#  TABS
# ══════════════════════════════════════════════════════════════════════════════
tabs = st.tabs([
    "Dashboard", "Alpha Scan", "⚗ Quant DCF", "⚖ Anti-Portfolio",
    "Supply Chain", "Sector Dive", "Stock Stress",
    "Geo Trade", "Commodity", "Portfolio",
    "Compare", "Rotation", "Catalyst",
    "Earnings", "SEC Filings", "Options Flow", "13F Tracker",
    "Watchdog", "Backtest", "Macro Regime", "Monetize", "Newsletter", "Info",
])
(tab_dash, tab_scan, tab_dcf, tab_anti,
 tab_supply, tab_sector, tab_stock,
 tab_geo, tab_commodity, tab_port,
 tab_compare, tab_rotation, tab_calendar,
 tab_earnings, tab_sec, tab_options, tab_inst,
 tab_watchdog, tab_backtest, tab_macro, tab_monetize, tab_newsletter, tab_info) = tabs

# ══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
with tab_dash:
    with st.spinner(""):
        macro_strip = get_macro_strip()

    # Ticker strip
    ticker_items = ""
    for lbl, (p, c) in macro_strip.items():
        if p is not None:
            cls = "up" if (c or 0)>=0 else "dn"
            fmt = f"{p:,.0f}" if p>500 else f"{p:.2f}"
            sgn = "+" if (c or 0)>=0 else ""
            ticker_items += f'<div class="ticker-box"><span class="ticker-label">{lbl}</span><span class="ticker-price">{fmt}</span><span class="{cls}">{sgn}{c:.2f}%</span></div>'
        else:
            ticker_items += f'<div class="ticker-box"><span class="ticker-label">{lbl}</span><span class="ticker-price">—</span><span class="flat">—</span></div>'
    st.markdown(f'<div class="ticker-strip">{ticker_items}</div>', unsafe_allow_html=True)

    left, right = st.columns([1,2])
    with left:
        st.markdown('<div class="sec-label">Sector Momentum</div>', unsafe_allow_html=True)
        with st.spinner(""):
            df_sec = get_sector_table(SECTORS)
        if not df_sec.empty:
            def _csec(v):
                if isinstance(v,(int,float)): return "color:#22c55e;font-weight:600" if v>0 else "color:#ef4444;font-weight:600"
                return ""
            st.dataframe(df_sec.style.map(_csec,subset=["1M%","1W%"]), width="stretch", hide_index=True, height=345)
        else: st.info("Sector data unavailable")

    with right:
        st.markdown('<div class="sec-label">Watchlist · Quantitative Signals</div>', unsafe_allow_html=True)
        with st.spinner(""):
            df_watch = get_full_stock_table(STOCKS)
        if not df_watch.empty:
            def _crsi(v):
                if isinstance(v,(int,float)):
                    if v<35: return "color:#22c55e;font-weight:600"
                    if v>70: return "color:#ef4444;font-weight:600"
                return ""
            def _cv(v):
                colors = {"STRONG BUY":"color:#22c55e;font-weight:700","BUY":"color:#4ade80",
                          "WATCH":"color:#f59e0b","CAUTION":"color:#fb923c","AVOID":"color:#ef4444;font-weight:700"}
                return colors.get(v,"")
            display_cols = [c for c in ["Ticker","Price","1M%","RSI","MACD","Score","Verdict"] if c in df_watch.columns]
            st.dataframe(
                df_watch[display_cols].style.map(_crsi,subset=["RSI"]).map(_cv,subset=["Verdict"]),
                width="stretch", hide_index=True, height=345)
        else: st.info("Stock data unavailable")

    st.markdown('<div class="sec-label">Market Intelligence Feed</div>', unsafe_allow_html=True)
    nc1, nc2 = st.columns(2)
    with nc1:
        st.markdown("**Macro & Markets**")
        for h in get_news("asymmetric investment macro opportunity 2026",5):
            st.markdown(f'<div class="news-item"><span class="news-title">{h["title"]}</span><span class="news-src">{h["source"]}</span></div>', unsafe_allow_html=True)
    with nc2:
        st.markdown("**Geopolitics & Policy**")
        for h in get_news("geopolitical risk Federal Reserve trade war 2026",5):
            st.markdown(f'<div class="news-item"><span class="news-title">{h["title"]}</span><span class="news-src">{h["source"]}</span></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  ALPHA SCAN
# ══════════════════════════════════════════════════════════════════════════════
with tab_scan:
    st.markdown("### 5-Agent Asymmetric Bet Scanner")
    st.markdown("Macro Scout · Sector Analyst · Stock Sniper · Contrarian · CIO Synthesis — parallel execution")
    if key_check():
        if st.button("Run Alpha Scan →", type="primary"):
            prog = st.progress(0, "Loading market data...")
            try:
                prog.progress(20, "4 agents running in parallel (~2-3 min)...")
                stat_cols = st.columns(4)
                for col,lbl in zip(stat_cols,["Macro","Sector","Stocks","Contra"]): col.info(f"⏳ {lbl}")
                results, df_st = run_alpha_scan(gemini_key)
                for col,lbl,k in zip(stat_cols,["Macro","Sector","Stocks","Contra"],["macro","sector","stocks","contra"]):
                    v = results.get(k,"")
                    col.success(f"✓ {lbl}") if not v.startswith("[API") else col.error(f"✗ {lbl}")
                prog.progress(100, "Complete")
                st.markdown("---")
                st.markdown("#### Final Alpha Report")
                final = results.get("thesis","[No output]")
                show_result(final, "blue")
                dl_tg(f"◈ ALPHA MACHINE\n{datetime.now():%Y-%m-%d %H:%M}\n\n{final}", "alpha_scan")
                st.session_state["last_scan"] = results
                with st.expander("Macro Scout"): st.write(results.get("macro",""))
                with st.expander("Sector Analyst"): st.write(results.get("sector",""))
                with st.expander("Stock Sniper"): st.write(results.get("stocks",""))
                with st.expander("Contrarian"): st.write(results.get("contra",""))
            except Exception as e:
                prog.empty(); st.error(f"Scan failed: {e}")

# ══════════════════════════════════════════════════════════════════════════════
#  QUANT DCF VALUATION (NEW)
# ══════════════════════════════════════════════════════════════════════════════
with tab_dcf:
    st.markdown("### ⚗ Quantitative DCF Valuation")
    st.markdown("numpy-powered DCF across 3 scenarios · Real FMP financial data · Insider signals · Supply chain alpha")

    if fmp_key:
        st.markdown('<div class="alert-ok">✓ FMP connected — using real financial statements for DCF</div>', unsafe_allow_html=True)
    else:
        st.info("Add FMP API key in sidebar for real financial data. Without it, AI estimates from public data.")

    c1,c2 = st.columns([3,1])
    with c1: dcf_ticker = st.text_input("Ticker", placeholder="NVDA · PLTR · TSLA · AXTI", label_visibility="collapsed")
    with c2: dcf_run = st.button("Run DCF →", type="primary")

    if dcf_run:
        if key_check() and dcf_ticker:
            t = dcf_ticker.strip().upper().replace("$","")
            with st.spinner(f"Running quantitative DCF for {t}..."):
                analysis, dcf_results, price = run_dcf_agent(gemini_key, t)

            # Show calculated DCF stats
            if dcf_results:
                st.markdown('<div class="sec-label">Calculated DCF — numpy</div>', unsafe_allow_html=True)
                bear_fv = dcf_results.get("Bear",{}).get("FV_per_share",0)
                base_fv = dcf_results.get("Base",{}).get("FV_per_share",0)
                bull_fv = dcf_results.get("Bull",{}).get("FV_per_share",0)
                upside  = round((base_fv/price-1)*100,1) if price and price>0 else 0
                col_a, col_b, col_c, col_d = st.columns(4)
                col_a.metric("Bear FV",  f"${bear_fv:,.2f}")
                col_b.metric("Base FV",  f"${base_fv:,.2f}")
                col_c.metric("Bull FV",  f"${bull_fv:,.2f}")
                col_d.metric("Upside (Base)", f"{upside:+.1f}%",
                             delta_color="normal" if upside>0 else "inverse")

            st.markdown("---")
            show_result(analysis, "teal")
            dl_tg(analysis, f"dcf_{t}")

# ══════════════════════════════════════════════════════════════════════════════
#  ANTI-PORTFOLIO RISK AGENT (NEW)
# ══════════════════════════════════════════════════════════════════════════════
with tab_anti:
    st.markdown("### ⚖ Anti-Portfolio Risk Agent")
    st.markdown("numpy correlation matrix · 5-scenario stress test · Double-down detection · Specific hedges")

    holdings_input = st.text_area("Your Holdings",
        placeholder="NVDA 20%, AAPL 15%, MSFT 15%, PLTR 10%, TSLA 8%, Cash 15%, BTC 7%, Gold 5%\nOr just tickers: NVDA, AAPL, MSFT, PLTR",
        height=90)
    anti_run = st.button("Stress Test Portfolio →", type="primary")

    if anti_run:
        if key_check() and holdings_input.strip():
            with st.spinner("Calculating correlations and running stress test..."):
                analysis, corr_matrix, flags = run_anti_portfolio(gemini_key, holdings_input)

            if not corr_matrix.empty:
                st.markdown('<div class="sec-label">Correlation Matrix — numpy · Pearson</div>', unsafe_allow_html=True)
                def _ccorr(v):
                    if not isinstance(v,(int,float)): return ""
                    if abs(v)==1: return ""
                    if abs(v)>0.85: return "background:#2e0505;color:#fca5a5;font-weight:600"
                    if abs(v)>0.70: return "background:#2e1505;color:#fbbf24"
                    if abs(v)<0.2:  return "color:#22c55e"
                    return ""
                st.dataframe(corr_matrix.style.map(_ccorr), width="stretch")

            if flags:
                st.markdown('<div class="sec-label">High Correlation Flags</div>', unsafe_allow_html=True)
                for f in flags:
                    cls = "alert-err" if f["risk"]=="HIGH" else "alert-ok"
                    st.markdown(f'<div class="{cls}"><strong>{f["pair"]}</strong> — correlation: {f["corr"]} ({f["risk"]} risk)</div>', unsafe_allow_html=True)

            st.markdown("---")
            show_result(analysis, "red")
            dl_tg(analysis, "anti_portfolio")

# ══════════════════════════════════════════════════════════════════════════════
#  SUPPLY CHAIN
# ══════════════════════════════════════════════════════════════════════════════
with tab_supply:
    st.markdown("### Supply Chain Forensic Mapper")
    st.markdown("Map the nervous system — find the company the giants cannot live without.")
    c1,c2 = st.columns([3,1])
    with c1: supply_t = st.text_input("Company or Sector", placeholder="NVDA · EUV Lithography · Solid State Batteries", label_visibility="collapsed")
    with c2: supply_r = st.button("Map Chain →", type="primary")
    if supply_r:
        if key_check() and supply_t:
            with st.status(f"Mapping {supply_t} supply chain...", expanded=True) as s:
                st.write("Identifying Tier 1 suppliers..."); st.write("Scanning Tier 2 hidden plays...")
                out=st.empty(); full=""
                for chunk in stream_gemini(SP["supply"],
                    f"Date:{datetime.now():%Y-%m-%d}\nTARGET:{supply_t}\n\n"
                    f"MAP complete supply chain. Use live web search.\n"
                    f"1. TIER 1 — top 5 **$TICKER**, what supplied, dependency level\n"
                    f"2. TIER 2 HIDDEN PLAYS — 5 **$TICKER**, component, revenue exposure %, why asymmetric\n"
                    f"3. TIER 3 RAW MATERIALS — bottleneck, geographic concentration\n"
                    f"4. THE MOAT — who owns IP/process giants cannot bypass?\n"
                    f"5. TOP 3 ASYMMETRIC BETS — **$TICKER**, catalyst, timeline, entry/target\n"
                    f"6. RISKS — geopolitical, substitution, concentration\n"
                    f"TICKERS:[all mentioned]", gemini_key):
                    full+=chunk; out.markdown(full)
                s.update(label="✓ Chain mapped", state="complete")
            st.session_state["last_research"] = full
            dl_tg(full, "supply_chain")

# ══════════════════════════════════════════════════════════════════════════════
#  SECTOR DIVE
# ══════════════════════════════════════════════════════════════════════════════
with tab_sector:
    st.markdown("### Sector Deep Dive")
    st.markdown("Cycle position · Hidden gems · Institutional flow · Best bet")
    c1,c2 = st.columns([3,1])
    with c1: sector_t = st.text_input("Sector", placeholder="Defense · Biotech · Semiconductors · Clean Energy", label_visibility="collapsed")
    with c2: sector_r = st.button("Dive Deep →", type="primary")
    if sector_r:
        if key_check() and sector_t:
            with st.spinner(f"Analyzing {sector_t}..."):
                result = run_sector_dive(gemini_key, sector_t)
            show_result(result,"purple"); dl_tg(result,"sector_dive")

# ══════════════════════════════════════════════════════════════════════════════
#  STOCK STRESS TEST
# ══════════════════════════════════════════════════════════════════════════════
with tab_stock:
    st.markdown("### Single Stock Stress Test")
    st.markdown("Forensic bull/bear · Accounting flags · Insider signals · Supplier alternatives")
    c1,c2 = st.columns([3,1])
    with c1: stress_t = st.text_input("Ticker", placeholder="NVDA · PLTR · TSLA · RKLB", label_visibility="collapsed")
    with c2: stress_r = st.button("Stress Test →", type="primary")
    if stress_r:
        if key_check() and stress_t:
            t = stress_t.strip().upper().replace("$","")
            with st.spinner(f"Stress testing {t}..."):
                result = run_stock_stress(gemini_key, t)
            show_result(result,"red"); dl_tg(result,f"stress_{t}")

# ══════════════════════════════════════════════════════════════════════════════
#  GEO TRADE
# ══════════════════════════════════════════════════════════════════════════════
with tab_geo:
    st.markdown("### Geopolitical Trade Finder")
    st.markdown("Winners · Losers · Second-order plays · Specific hedge")
    c1,c2 = st.columns([3,1])
    with c1: geo_t = st.text_input("Scenario", placeholder="Taiwan conflict · US-China tariffs · OPEC+ cut", label_visibility="collapsed")
    with c2: geo_r = st.button("Find Trades →", type="primary")
    if geo_r:
        if key_check() and geo_t:
            with st.spinner(f"Mapping trades for: {geo_t}..."):
                result = run_geo_trade(gemini_key, geo_t)
            show_result(result,"blue"); dl_tg(result,"geo_trade")

# ══════════════════════════════════════════════════════════════════════════════
#  COMMODITY CHAIN
# ══════════════════════════════════════════════════════════════════════════════
with tab_commodity:
    st.markdown("### Commodity Chain Tracer")
    st.markdown("Full upstream/downstream · Find the moat and the best asymmetric play")
    c1,c2 = st.columns([3,1])
    with c1: comm_t = st.text_input("Commodity", placeholder="Lithium · Uranium · Copper · Rare Earth · LNG", label_visibility="collapsed")
    with c2: comm_r = st.button("Trace Chain →", type="primary")
    if comm_r:
        if key_check() and comm_t:
            with st.spinner(f"Tracing {comm_t} chain..."):
                result = run_commodity_chain(gemini_key, comm_t)
            show_result(result,"orange"); dl_tg(result,"commodity")

# ══════════════════════════════════════════════════════════════════════════════
#  PORTFOLIO STRESS
# ══════════════════════════════════════════════════════════════════════════════
with tab_port:
    st.markdown("### Portfolio Stress Tester")
    st.markdown("5-scenario stress test · Concentration risk · Hedging recommendations")
    port_input = st.text_area("Holdings", placeholder="NVDA 15%, AAPL 10%, MSFT 10%, PLTR 8%, Cash 20%", height=80)
    if st.button("Stress Test →", type="primary"):
        if key_check() and port_input.strip():
            with st.spinner("Running stress test..."):
                result = run_portfolio_stress(gemini_key, port_input)
            show_result(result,"pink"); dl_tg(result,"portfolio")

# ══════════════════════════════════════════════════════════════════════════════
#  COMPARE
# ══════════════════════════════════════════════════════════════════════════════
with tab_compare:
    st.markdown("### Relative Value Comparator")
    st.markdown("Head-to-head forensic · Pair trade setup")
    ca,cv,cb = st.columns([2,0.4,2])
    with ca: ta = st.text_input("Ticker A", placeholder="NVDA", key="ta")
    with cv: st.markdown("<br>**vs**", unsafe_allow_html=True)
    with cb: tb = st.text_input("Ticker B", placeholder="AMD", key="tb")
    if st.button("Compare →", type="primary"):
        if key_check() and ta and tb:
            with st.spinner(f"Comparing {ta.upper()} vs {tb.upper()}..."):
                result = run_relative_value(gemini_key, ta.upper(), tb.upper())
            show_result(result,"teal"); dl_tg(result,f"compare_{ta}_{tb}")

# ══════════════════════════════════════════════════════════════════════════════
#  ROTATION
# ══════════════════════════════════════════════════════════════════════════════
with tab_rotation:
    st.markdown("### Sector Rotation Timer")
    st.markdown("Cycle phase · What rotates next · Highest conviction rotation trade")
    if key_check():
        if st.button("Analyze Rotation →", type="primary"):
            with st.spinner("Analyzing economic cycle..."):
                result = run_rotation_timer(gemini_key)
            show_result(result,"purple"); dl_tg(result,"rotation")

# ══════════════════════════════════════════════════════════════════════════════
#  CATALYST CALENDAR
# ══════════════════════════════════════════════════════════════════════════════
with tab_calendar:
    st.markdown("### Catalyst Calendar")
    st.markdown("90-day event calendar ranked by asymmetric potential · This week's best setup")
    cal_input = st.text_input("Watchlist", value=",".join(STOCKS[:8]))
    if st.button("Generate Calendar →", type="primary"):
        if key_check() and cal_input.strip():
            with st.spinner("Scanning for catalysts..."):
                result = run_catalyst_calendar(gemini_key, cal_input)
            show_result(result,"amber"); dl_tg(result,"catalyst_calendar")

# ══════════════════════════════════════════════════════════════════════════════
#  EARNINGS
# ══════════════════════════════════════════════════════════════════════════════
with tab_earnings:
    st.markdown("### Earnings Call Analyzer")
    st.markdown("Tone shift detection · What CEO is hiding · Trading implication · Credibility score")
    c1,c2 = st.columns([3,1])
    with c1: earn_t = st.text_input("Ticker", placeholder="NVDA · AAPL · MSFT · AMZN", label_visibility="collapsed", key="earn_k")
    with c2: earn_r = st.button("Analyze Call →", type="primary")
    if earn_r:
        if key_check() and earn_t:
            t = earn_t.strip().upper().replace("$","")
            with st.spinner(f"Analyzing {t} earnings..."):
                result = run_earnings_analyzer(gemini_key, t)
            show_result(result,"cyan"); dl_tg(result,f"earnings_{t}")

# ══════════════════════════════════════════════════════════════════════════════
#  SEC FILINGS
# ══════════════════════════════════════════════════════════════════════════════
with tab_sec:
    st.markdown("### SEC Filing Scanner")
    st.markdown("Form 4 insider buys/sells · 8-K material events · 10-Q red flags")
    if finnhub_key:
        st.markdown('<div class="alert-ok">✓ Finnhub connected — real insider transaction data</div>', unsafe_allow_html=True)
    c1,c2 = st.columns([3,1])
    with c1: sec_t = st.text_input("Ticker", placeholder="PLTR · NVDA · TSLA", label_visibility="collapsed", key="sec_k")
    with c2: sec_r = st.button("Scan Filings →", type="primary")
    if sec_r:
        if key_check() and sec_t:
            t = sec_t.strip().upper().replace("$","")
            with st.spinner(f"Scanning SEC filings for {t}..."):
                result = run_sec_scanner(gemini_key, t)
            show_result(result,"rose"); dl_tg(result,f"sec_{t}")

# ══════════════════════════════════════════════════════════════════════════════
#  OPTIONS FLOW
# ══════════════════════════════════════════════════════════════════════════════
with tab_options:
    st.markdown("### Options Flow Watcher")
    st.markdown("Unusual activity · Smart money positioning · IV vs HV · Optimal strategy")
    c1,c2 = st.columns([3,1])
    with c1: opt_t = st.text_input("Ticker", placeholder="NVDA · SPY · TSLA", label_visibility="collapsed", key="opt_k")
    with c2: opt_r = st.button("Scan Flow →", type="primary")
    if opt_r:
        if key_check() and opt_t:
            t = opt_t.strip().upper().replace("$","")
            with st.spinner(f"Scanning options flow for {t}..."):
                result = run_options_flow(gemini_key, t)
            show_result(result,"lime"); dl_tg(result,f"options_{t}")

# ══════════════════════════════════════════════════════════════════════════════
#  13F TRACKER
# ══════════════════════════════════════════════════════════════════════════════
with tab_inst:
    st.markdown("### 13F Institutional Tracker")
    st.markdown("Ticker → who owns it, who bought/sold. Manager name → full 13F changes.")
    c1,c2 = st.columns([3,1])
    with c1: inst_t = st.text_input("Ticker or Manager", placeholder="NVDA  ·  Soros  ·  Burry  ·  Ackman", label_visibility="collapsed", key="inst_k")
    with c2: inst_r = st.button("Track →", type="primary")
    if inst_r:
        if key_check() and inst_t:
            with st.spinner(f"Fetching 13F for {inst_t}..."):
                result = run_13f_tracker(gemini_key, inst_t.strip())
            show_result(result,"orange"); dl_tg(result,f"13f_{inst_t.strip()}")

# ══════════════════════════════════════════════════════════════════════════════
#  SMART WATCHDOG
# ══════════════════════════════════════════════════════════════════════════════
with tab_watchdog:
    st.markdown("### Smart Watchdog")
    st.markdown("Custom triggers · numpy-calculated signals · Auto-fires Telegram when condition met")
    wc1,wc2 = st.columns([2,1])
    with wc1: wd_list = st.text_input("Watchlist", value=",".join(STOCKS))
    with wc2: wd_triggers = st.multiselect("Triggers",
        ["RSI < 30","RSI > 75","Drop > 8% 1M","Momentum >15%","Near 52W High"],
        default=["RSI < 30","Drop > 8% 1M"])
    if st.button("Run Watchdog →", type="primary"):
        if key_check():
            tks = [t.strip() for t in wd_list.split(",") if t.strip()]
            with st.spinner("Scanning..."):
                alerts, ai = run_watchdog(gemini_key, tks, wd_triggers)
            if alerts:
                st.markdown(f"**{len(alerts)} alert(s) fired**")
                for a in alerts:
                    st.markdown(f'<div class="alert-ok"><strong>{a["ticker"]}</strong> @ ${a["price"]} — {" · ".join(a["signals"])}</div>', unsafe_allow_html=True)
                st.markdown("---")
                show_result(ai, "purple")
                if tg_token and tg_chat:
                    msg = f"◈ WATCHDOG\n{datetime.now():%Y-%m-%d %H:%M}\n\n"
                    msg += "\n".join([f"• {a['ticker']} @ ${a['price']}: {', '.join(a['signals'])}" for a in alerts])
                    send_telegram(msg+f"\n\n{ai[:1000]}", tg_token, tg_chat)
                    st.success("Alerts sent to Telegram")
                dl_tg(ai, "watchdog")
            else:
                st.markdown('<div class="alert-ok">✓ No alerts — all watchlist stocks within normal parameters.</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  BACKTESTER
# ══════════════════════════════════════════════════════════════════════════════
with tab_backtest:
    st.markdown("### Thesis Backtester")
    st.markdown("Test thesis against 2008 · 2020 · 2022 · 2024 regimes · Proof of concept before risking capital")
    bc1,bc2 = st.columns([2,1])
    with bc1:
        bt_thesis = st.text_area("Investment Thesis",
            placeholder="PLTR is undervalued due to AI government contract tailwind and strong insider buying...",
            height=85)
    with bc2:
        bt_ticker = st.text_input("Primary Ticker", placeholder="PLTR · NVDA · CCJ", key="bt_k")
        bt_run = st.button("Backtest →", type="primary")
    if bt_run:
        if key_check() and bt_thesis and bt_ticker:
            t = bt_ticker.strip().upper().replace("$","")
            with st.spinner(f"Backtesting across 4 regimes..."):
                result = run_backtester(gemini_key, bt_thesis, t)
            show_result(result,"blue"); dl_tg(result,f"backtest_{t}")

# ══════════════════════════════════════════════════════════════════════════════
#  MACRO REGIME
# ══════════════════════════════════════════════════════════════════════════════
with tab_macro:
    st.markdown("### Macro Regime Analyzer")
    st.markdown("Streaming · Base Case + Black Swan + Smart Money Divergence")
    mc1,mc2 = st.columns([2,1])
    with mc1: macro_q = st.text_input("Focus (optional)", placeholder="DXY impact on EM · Fed pivot timing · Yield curve", key="mq")
    with mc2: macro_h = st.selectbox("Horizon", ["8-hour","1-week","1-month","1-quarter"], key="mh")
    mc_run = st.button("Stream Macro Brief →", type="primary", key="macro_run")
    if mc_run:
        if key_check():
            focus = macro_q or "current global market regime"
            macro_d = get_macro_strip()
            snap = " | ".join([f"{k}:{v[0]}" for k,v in macro_d.items() if v[0]])
            with st.status(f"Analyzing {macro_h} regime...", expanded=True) as s:
                st.write("Fetching DXY, VIX, yield curve..."); st.write("Modeling base/black swan scenarios...")
                out=st.empty(); full=""
                for chunk in stream_gemini(SP["macro"],
                    f"Date:{datetime.now():%Y-%m-%d}\nFOCUS:{focus}\nHORIZON:{macro_h}\n"
                    f"LIVE:{snap}\n\n"
                    f"Analyze regime:\n## Current Regime\n## Base Case ({macro_h})\n## Black Swan\n"
                    f"## Smart Money Divergence\n## Highest Conviction Trade\n\nBe specific with tickers.", gemini_key):
                    full+=chunk; out.markdown(full)
                s.update(label="✓ Brief complete", state="complete")
            st.session_state["last_macro"] = full
            dl_tg(full, "macro_regime")

# ══════════════════════════════════════════════════════════════════════════════
#  MONETIZE
# ══════════════════════════════════════════════════════════════════════════════
with tab_monetize:
    st.markdown("### Monetization Agent")
    st.markdown("One-click: turn any scan output into viral content")

    src_options = {}
    if st.session_state.get("last_scan"):
        t = st.session_state["last_scan"].get("thesis","")
        if t: src_options["Alpha Scan Report"] = t
    if st.session_state.get("last_macro"):    src_options["Macro Brief"]    = st.session_state["last_macro"]
    if st.session_state.get("last_research"): src_options["Supply Chain Research"] = st.session_state["last_research"]

    if src_options:
        src_lbl = st.selectbox("Source", list(src_options.keys()))
        src     = src_options[src_lbl]
        with st.expander("Preview"):
            st.write(src[:600]+"..." if len(src)>600 else src)
        st.markdown("---")
        col1,col2,col3,col4 = st.columns(4)
        with col1:
            if st.button("𝕏 Thread", type="primary", use_container_width=True):
                with st.status("Writing X thread...", expanded=True) as s:
                    out=st.empty(); full=""
                    for chunk in stream_gemini("You are a viral financial X creator. Write 7-tweet threads that go viral by sharing alpha retail can't find.",
                        f"Turn into 7-tweet X thread:\n{src[:2500]}\n\nTweet 1: shocking hook (max 280 chars)\nTweets 2-6: one insight each with $TICKER\nTweet 7: CTA for RT + follow", gemini_key):
                        full+=chunk; out.markdown(full)
                    s.update(label="✓ Thread ready", state="complete")
                st.session_state["monetize_out"] = full
        with col2:
            if st.button("Substack", type="primary", use_container_width=True):
                with st.status("Writing Substack post...", expanded=True) as s:
                    out=st.empty(); full=""
                    for chunk in stream_gemini("You write like Howard Marks meets Paul Graham — deep, contrarian, beautifully structured.",
                        f"Turn into Substack research note:\n{src[:2500]}\n\n# [Title]\n## The Setup\n## The Alpha\n## The Risk\n## The Trade\n---\n*Not financial advice.*", gemini_key):
                        full+=chunk; out.markdown(full)
                    s.update(label="✓ Post ready", state="complete")
                st.session_state["monetize_out"] = full
        with col3:
            if st.button("LinkedIn", type="primary", use_container_width=True):
                with st.status("Writing LinkedIn post...", expanded=True) as s:
                    out=st.empty(); full=""
                    for chunk in stream_gemini("You write LinkedIn posts that get 50k+ impressions by being specific and contrarian.",
                        f"Turn into high-performing LinkedIn post:\n{src[:2000]}\n\nBold opening. 3-5 insight paragraphs. Actionable takeaway. Question to drive comments. 3-5 hashtags.", gemini_key):
                        full+=chunk; out.markdown(full)
                    s.update(label="✓ Post ready", state="complete")
                st.session_state["monetize_out"] = full
        with col4:
            if st.button("TikTok", type="primary", use_container_width=True):
                with st.status("Writing TikTok script...", expanded=True) as s:
                    out=st.empty(); full=""
                    for chunk in stream_gemini("You write viral 60-second TikTok finance scripts. Short sentences. No jargon.",
                        f"Turn into 60-sec TikTok script:\n{src[:1500]}\n\n[0-3s HOOK]\n[3-15s CONTEXT]\n[15-45s THE ALPHA]\n[45-55s THE TRADE]\n[55-60s CTA: follow for daily alpha]", gemini_key):
                        full+=chunk; out.markdown(full)
                    s.update(label="✓ Script ready", state="complete")
                st.session_state["monetize_out"] = full
        if st.session_state.get("monetize_out"):
            st.markdown("---"); dl_tg(st.session_state["monetize_out"], "monetize")
    else:
        st.info("Run Alpha Scan, Macro Brief, or Supply Chain first — then come back here to monetize it in one click.")

# ══════════════════════════════════════════════════════════════════════════════
#  NEWSLETTER
# ══════════════════════════════════════════════════════════════════════════════
with tab_newsletter:
    st.markdown("### Newsletter Generator")
    st.markdown("Full weekly edition from your scan results — ready for Substack or Beehiiv")
    nc1,nc2 = st.columns(2)
    with nc1: nl_name = st.text_input("Newsletter Name", value="Alpha Intelligence Weekly")
    with nc2: nl_author = st.text_input("Author", value="Alpha Machine")
    if st.button("Generate Newsletter →", type="primary"):
        if key_check():
            scan = st.session_state.get("last_scan",{})
            with st.spinner("Writing newsletter..."):
                result = run_newsletter(gemini_key, scan, nl_author, nl_name)
            st.markdown("---"); st.markdown(result); st.markdown("---")
            dl_tg(result, "newsletter")

# ══════════════════════════════════════════════════════════════════════════════
#  INFO
# ══════════════════════════════════════════════════════════════════════════════
with tab_info:
    st.markdown("## ◈ Alpha Machine v5 — Full Reference")

    st.markdown("### Data Providers")
    providers = [
        ("Yahoo Finance","Always active — no key needed","Prices, history, 52W range"),
        ("CoinGecko","Always active — no key needed","BTC/ETH prices"),
        ("EDGAR (SEC)","Always active — no key needed","Form 4, 8-K, 10-Q filings"),
        ("Google News RSS","Always active — no key needed","Market headlines"),
        ("Finnhub","Free: 60 calls/min — finnhub.io","Real-time quotes, insider transactions, news sentiment"),
        ("FMP","Free: 250 calls/day — financialmodelingprep.com","Income statements, cash flow, DCF inputs"),
        ("Alpha Vantage","Free: 25 calls/day — alphavantage.co","RSI, MACD, technical indicators"),
        ("Polygon.io","Free: 5 calls/min — polygon.io","Normalized US market data"),
    ]
    df_prov = pd.DataFrame(providers, columns=["Provider","Free Tier","Best For"])
    st.dataframe(df_prov, hide_index=True, width="stretch")

    st.markdown("### Quantitative Engine — numpy/scipy")
    st.code("""
# Everything is CALCULATED, not guessed:
calc_rsi(closes, period=14)          # Wilder RSI
calc_macd(closes, 12, 26, 9)         # EMA-based MACD
calc_bollinger(closes, 20, 2)        # Bollinger Bands
calc_atr(highs, lows, closes, 14)    # Average True Range
calc_correlation_matrix(price_dict)  # Pearson correlations
dcf_valuation(revenue, growth, ...)  # Bear/Base/Bull DCF
portfolio_correlation_risk(holdings) # Correlation flags
score_signals(closes, rsi, macd,...) # 0-10 composite score
    """, language="python")

    st.markdown("### All 23 Modes")
    modes = [
        ("Dashboard","Live macro, sector momentum, quantitative watchlist signals"),
        ("Alpha Scan","5 parallel agents — Macro/Sector/Stocks/Contra → CIO synthesis"),
        ("⚗ Quant DCF","numpy DCF bear/base/bull · FMP real financials · Insider signals"),
        ("⚖ Anti-Portfolio","Correlation matrix · 5-scenario stress · Double-down detection"),
        ("Supply Chain","Tier 1/2/3 forensic map — find what giants cannot bypass"),
        ("Sector Dive","Cycle position, hidden gems, best asymmetric bet"),
        ("Stock Stress","Forensic bull/bear, accounting flags, supplier alternatives"),
        ("Geo Trade","Scenario → winners/losers/hedges/second-order plays"),
        ("Commodity","Full upstream/downstream value chain"),
        ("Portfolio","5-scenario stress, concentration, hedging recs"),
        ("Compare","Head-to-head + pair trade setup"),
        ("Rotation","Cycle phase, next rotation, highest conviction trade"),
        ("Catalyst","90-day calendar ranked by asymmetric potential"),
        ("Earnings","Tone shift, what CEO is hiding, credibility score"),
        ("SEC Filings","Form 4 insider, 8-K events, 10-Q forensics"),
        ("Options Flow","Unusual activity, IV/HV, smart money, optimal strategy"),
        ("13F Tracker","By ticker or fund manager name"),
        ("Watchdog","Custom numpy-calculated triggers, auto Telegram"),
        ("Backtest","Thesis vs 2008/2020/2022/2024 regimes"),
        ("Macro Regime","Streaming · Base Case + Black Swan + Smart Money"),
        ("Monetize","X thread, Substack, LinkedIn, TikTok — one click"),
        ("Newsletter","Full weekly edition, Substack-ready"),
        ("Info","This page"),
    ]
    col1, col2 = st.columns(2)
    for i,(name,desc) in enumerate(modes):
        (col1 if i%2==0 else col2).markdown(f"**{name}** — {desc}")

    st.markdown("### Setup Guide")
    st.markdown("""
**Gemini API (required):**
1. [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) → Create API Key
2. Paste in sidebar

**Data providers (optional, all free):**
- [finnhub.io](https://finnhub.io) — create account → API key (real-time data)
- [financialmodelingprep.com](https://financialmodelingprep.com) — API key (financials for DCF)
- [alphavantage.co](https://www.alphavantage.co) — free key (technicals)
- [polygon.io](https://polygon.io) — free key (US markets)

**Telegram bot:**
- Message [@BotFather](https://t.me/BotFather) → `/newbot` → copy token
- Get chat ID via `https://api.telegram.org/bot<TOKEN>/getUpdates`
    """)
