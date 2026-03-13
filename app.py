"""
Alpha Machine v2 — Enhanced Intelligence Platform
8 Research Modes + Live Dashboard + Alerts + Portfolio Tools
Python 3.14 | Gemini 2.5 Flash | No yfinance | Streamlit Cloud ready
"""

import streamlit as st

st.set_page_config(
    page_title="Alpha Machine v2 🎯",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

import requests
import feedparser
import json
import threading
import pandas as pd
from datetime import datetime, timedelta
import time
import re
from google import genai
from google.genai import types

# ══════════════════════════════════════════════════════════════════════════════
#  CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: #05070d; font-family: 'Inter', sans-serif;
}
[data-testid="stSidebar"] { background: #080b12; border-right: 1px solid #1a2035; }
[data-testid="stSidebar"] * { color: #c9d1e0 !important; }
.block-container { padding-top: 1rem; padding-bottom: 2rem; }
h1,h2,h3,p,li,span,div,label { color: #e2e8f0; }

.alpha-title {
    font-size: 2.2rem; font-weight: 900; letter-spacing: -1.5px;
    background: linear-gradient(90deg, #00ffa3, #00d4ff, #a78bfa, #ff6b9d);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    line-height: 1.1; margin-bottom: 2px;
}
.alpha-sub { color: #4b5e7a; font-size: 0.82rem; letter-spacing: 0.5px; }

/* Mode cards */
.mode-card {
    background: linear-gradient(135deg, #0d1321, #111827);
    border: 1px solid #1e2d45; border-radius: 12px;
    padding: 16px; text-align: center; cursor: pointer;
    transition: all 0.2s; margin-bottom: 8px;
}
.mode-card:hover { border-color: #00ffa3; transform: translateY(-2px); }
.mode-icon { font-size: 1.8rem; display: block; margin-bottom: 6px; }
.mode-name { font-size: 0.78rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; }

/* Macro ticker boxes */
.mbox {
    background: #0d1321; border: 1px solid #1e2d45;
    border-radius: 10px; padding: 12px 8px; text-align: center; min-height: 82px;
}
.mlbl { color: #4b5e7a; font-size: 0.65rem; text-transform: uppercase; letter-spacing: 1.5px; display: block; }
.mval { color: #f1f5f9; font-size: 1.2rem; font-weight: 700; display: block; margin: 3px 0; font-family: 'JetBrains Mono', monospace; }
.mup  { color: #10b981; font-size: 0.75rem; font-weight: 600; }
.mdn  { color: #ef4444; font-size: 0.75rem; font-weight: 600; }
.mna  { color: #374151; font-size: 0.75rem; }

/* Section headers */
.shdr {
    color: #94a3b8; font-size: 0.72rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 2px;
    border-bottom: 1px solid #1e2d45; padding-bottom: 6px; margin: 16px 0 10px;
}

/* Result cards */
.result-card {
    background: linear-gradient(135deg, #08111e, #0d1928);
    border: 1px solid #1e3a5f; border-left: 4px solid #00ffa3;
    border-radius: 12px; padding: 20px 24px; margin: 12px 0;
    font-family: 'JetBrains Mono', monospace; font-size: 0.84rem;
    color: #cde8ff; white-space: pre-wrap; line-height: 1.7;
}
.result-card.supply  { border-left-color: #f59e0b; }
.result-card.sector  { border-left-color: #8b5cf6; }
.result-card.stress  { border-left-color: #ef4444; }
.result-card.geo     { border-left-color: #3b82f6; }
.result-card.commodity { border-left-color: #f97316; }
.result-card.portfolio { border-left-color: #ec4899; }
.result-card.compare { border-left-color: #14b8a6; }
.result-card.rotation { border-left-color: #a78bfa; }
.result-card.catalyst { border-left-color: #fbbf24; }

/* Agent status */
.agent-box {
    background: #0d1321; border: 1px solid #1e2d45; border-radius: 8px;
    padding: 10px 14px; font-size: 0.78rem; text-align: center;
}
.agent-running { border-color: #f59e0b; color: #fbbf24; }
.agent-done    { border-color: #10b981; color: #34d399; }
.agent-error   { border-color: #ef4444; color: #f87171; }

/* News cards */
.news-item {
    border-bottom: 1px solid #1e2d45; padding: 8px 0;
    font-size: 0.82rem; color: #94a3b8;
}
.news-title { color: #cbd5e1; font-weight: 600; }

/* Tab styling */
[data-testid="stTabs"] button {
    font-size: 0.8rem !important; font-weight: 600 !important;
    letter-spacing: 0.5px;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════════════════════
col_title, col_time = st.columns([3, 1])
with col_title:
    st.markdown('<p class="alpha-title">🎯 Alpha Machine v2</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="alpha-sub">MULTI-MODE INTELLIGENCE PLATFORM &nbsp;·&nbsp; {datetime.now().strftime("%d %b %Y · %H:%M UTC")}</p>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🔑 Gemini API")
    gemini_key = st.text_input("API Key (Free)", type="password", placeholder="AIza...")
    st.caption("[Get free key →](https://aistudio.google.com/app/apikey)")

    st.markdown("### 📱 Telegram Alerts")
    tg_token = st.text_input("Bot Token", type="password")
    tg_chat  = st.text_input("Chat ID",   placeholder="-100123456789")

    st.markdown("### 📋 Default Watchlist")
    stocks_raw  = st.text_area("Stocks",      value="NVDA,TSM,ASML,PLTR,IONQ,RKLB,HIMS,CELH,NVO,MELI", height=80)
    sectors_raw = st.text_area("Sector ETFs", value="XLK,XLE,XLF,XLV,XBI,ARKK,GDX,COPX,ITB,XAR",      height=80)

    st.markdown("---")
    st.markdown("**Free tier limits:**")
    st.caption("• 15 requests / minute\n• 1,500 requests / day\n• $0/month forever")

STOCKS  = [s.strip() for s in stocks_raw.split(",")  if s.strip()]
SECTORS = [s.strip() for s in sectors_raw.split(",") if s.strip()]

# ══════════════════════════════════════════════════════════════════════════════
#  DATA HELPERS
# ══════════════════════════════════════════════════════════════════════════════

YF_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}

@st.cache_data(ttl=300, show_spinner=False)
def get_price_yf(sym):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range=5d"
        r   = requests.get(url, headers=YF_HEADERS, timeout=6)
        closes = r.json()["chart"]["result"][0]["indicators"]["quote"][0]["close"]
        closes = [c for c in closes if c is not None]
        if len(closes) >= 2:
            return round(closes[-1], 2), round((closes[-1]/closes[-2]-1)*100, 2)
    except: pass
    return None, None

@st.cache_data(ttl=300, show_spinner=False)
def get_macro_prices():
    tickers = {"10Y Yield":"%5ETNX","S&P 500":"%5EGSPC","Gold":"GC%3DF","Oil":"CL%3DF","VIX":"%5EVIX","DXY":"DX-Y.NYB"}
    results = {}
    for label, sym in tickers.items():
        results[label] = get_price_yf(sym)
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price",
            params={"ids":"bitcoin","vs_currencies":"usd","include_24hr_change":"true"},
            timeout=6, headers={"User-Agent":"AlphaMachine/2.0"})
        d = r.json()
        results["Bitcoin"] = (round(d["bitcoin"]["usd"],0), round(d["bitcoin"]["usd_24h_change"],2))
    except:
        results["Bitcoin"] = (None, None)
    return results

@st.cache_data(ttl=300, show_spinner=False)
def get_stock_table(tickers):
    rows = []
    for sym in tickers:
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range=3mo"
            r   = requests.get(url, headers=YF_HEADERS, timeout=8)
            res    = r.json()["chart"]["result"][0]
            closes = [c for c in res["indicators"]["quote"][0]["close"] if c is not None]
            if len(closes) < 15: continue
            price = round(closes[-1], 2)
            m1    = round((closes[-1]/closes[-22]-1)*100, 2) if len(closes)>=22 else 0
            diffs = [closes[i]-closes[i-1] for i in range(1,len(closes))]
            gains = [max(d,0) for d in diffs[-14:]]
            losses= [abs(min(d,0)) for d in diffs[-14:]]
            ag,al = sum(gains)/14, sum(losses)/14
            rsi   = round(100 - 100/(1+ag/(al+1e-9)), 1)
            meta  = res.get("meta", {})
            w52h  = meta.get("fiftyTwoWeekHigh", 0) or 0
            w52l  = meta.get("fiftyTwoWeekLow",  0) or 0
            sigs  = []
            if rsi < 35:                      sigs.append("🟢 Oversold")
            if rsi > 70:                      sigs.append("🔴 Overbought")
            if w52h and price >= w52h*0.97:   sigs.append("🚀 52W High")
            if w52h and price <= w52h*0.55:   sigs.append("💎 Deep Value")
            if m1 > 15:                       sigs.append("⚡ Momentum")
            rows.append({"Ticker":sym,"Price":price,"1M%":m1,"RSI":rsi,"52W Hi":w52h,"52W Lo":w52l,"Signals":" ".join(sigs) or "—"})
            time.sleep(0.12)
        except:
            rows.append({"Ticker":sym,"Price":"—","1M%":"—","RSI":"—","52W Hi":"—","52W Lo":"—","Signals":"—"})
    return pd.DataFrame(rows) if rows else pd.DataFrame()

@st.cache_data(ttl=300, show_spinner=False)
def get_sector_table(tickers):
    rows = []
    for sym in tickers:
        try:
            url  = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range=1mo"
            r    = requests.get(url, headers=YF_HEADERS, timeout=8)
            closes = [c for c in r.json()["chart"]["result"][0]["indicators"]["quote"][0]["close"] if c is not None]
            if len(closes) < 5: continue
            m1 = round((closes[-1]/closes[0]-1)*100, 2)
            w1 = round((closes[-1]/closes[-6]-1)*100, 2) if len(closes)>=6 else 0
            rows.append({"ETF":sym,"1M%":m1,"1W%":w1})
            time.sleep(0.1)
        except: pass
    return pd.DataFrame(rows).sort_values("1M%", ascending=False).reset_index(drop=True) if rows else pd.DataFrame()

@st.cache_data(ttl=600, show_spinner=False)
def get_news(query, n=10):
    try:
        url  = f"https://news.google.com/rss/search?q={requests.utils.quote(query)}&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(url)
        return [{"title":e.get("title",""),"source":e.get("source",{}).get("title",""),
                 "link":e.get("link",""),"published":e.get("published","")} for e in feed.entries[:n]]
    except: return []

# ══════════════════════════════════════════════════════════════════════════════
#  GEMINI CORE
# ══════════════════════════════════════════════════════════════════════════════

def call_gemini(system, user, key):
    """Gemini 2.5 Flash with Google Search grounding — free tier."""
    try:
        client = genai.Client(api_key=key)
        google_search_tool = types.Tool(google_search=types.GoogleSearch())
        config = types.GenerateContentConfig(
            tools=[google_search_tool],
            temperature=0.2,
            system_instruction=system,
        )
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user,
            config=config,
        )
        return response.text
    except Exception as e:
        return f"[API error: {e}]"

def send_telegram(text, token, chat_id):
    for chunk in [text[i:i+4000] for i in range(0, len(text), 4000)]:
        try:
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id":chat_id,"text":chunk}, timeout=10)
        except: pass

# ══════════════════════════════════════════════════════════════════════════════
#  INTELLIGENCE MODES — PROMPTS & RUNNERS
# ══════════════════════════════════════════════════════════════════════════════

# ── MODE 1: Asymmetric Scan (5-agent parallel) ────────────────────────────────

def _agent(fn, key, results, *args):
    results[fn.__name__] = fn(key, *args)

def _macro_agent(key, macro_data, news):
    return call_gemini(
        "You are a global macro strategist. Think Ray Dalio. Find invisible forces moving markets before the crowd.",
        f"""Date: {datetime.now().strftime('%Y-%m-%d')}
LIVE MACRO DATA: {json.dumps({k:{"price":v[0],"chg%":v[1]} for k,v in macro_data.items()}, indent=2)}
NEWS: {json.dumps(news[:10], indent=2)}

Identify TOP 3 macro tailwinds creating asymmetric opportunities RIGHT NOW.
For each: theme, beneficiary assets, timeline, crowding level, confidence 1-10, kill risk.
Use live web search for latest geopolitical/policy developments. Plain text.""", key)

def _sector_agent(key, df_sec, news):
    return call_gemini(
        "You are a sector rotation specialist. Find sectors before ETF inflows show on Bloomberg.",
        f"""Date: {datetime.now().strftime('%Y-%m-%d')}
SECTOR ETF DATA: {df_sec.to_string(index=False) if not df_sec.empty else "unavailable"}
NEWS: {json.dumps(news[:8], indent=2)}
Find TOP 2 sectors in EARLY accumulation. For each: ETF, theme, why early, macro driver, score 1-10. Plain text.""", key)

def _stocks_agent(key, df_st, news):
    return call_gemini(
        "You are a stock catalyst specialist. Find asymmetric setups where 3+ signals stack.",
        f"""Date: {datetime.now().strftime('%Y-%m-%d')}
STOCK SIGNALS: {df_st.to_string(index=False) if not df_st.empty else "unavailable"}
CATALYST NEWS: {json.dumps(news[:10], indent=2)}
Find TOP 3 stocks with 3+ stacking signals: oversold RSI, deep value, high short float, upcoming catalyst, sector tailwind.
For each: ticker, signals list, catalyst+date, entry rationale, asymmetry score 1-10, horizon. Plain text.""", key)

def _contra_agent(key, df_st, news):
    return call_gemini(
        "You are a contrarian short-seller. Stress-test every bull thesis relentlessly.",
        f"""Date: {datetime.now().strftime('%Y-%m-%d')}
STOCK DATA: {df_st.to_string(index=False) if not df_st.empty else "unavailable"}
BEAR NEWS: {json.dumps(news[:8], indent=2)}
Stress-test each stock: what's priced in, bear case, kill scenario, crowding 1-10.
Verdict per stock: BUY / WATCH / AVOID. Flag AVOID clearly. Plain text.""", key)

def _thesis_agent(key, macro_r, sector_r, stocks_r, contra_r):
    return call_gemini(
        "You are the CIO of a macro hedge fund. Only surface alpha scoring 7+/10. No fluff.",
        f"""Date: {datetime.now().strftime('%Y-%m-%d')}
MACRO SCOUT: {macro_r}
SECTOR ANALYST: {sector_r}
STOCK SNIPER: {stocks_r}
CONTRARIAN: {contra_r}

Synthesize into ASYMMETRIC BET REPORT. Skip any AVOID tickers.
FORMAT each bet:
🎯 ASYMMETRIC BET: [TICKER]
📊 THEME: [one-line driver]
🔥 CATALYSTS:
   • [signal 1]
   • [signal 2]
   • [signal 3]
⚠️ KEY RISK: [one line]
📈 SETUP: Entry ~$X | Target $X–$X | Stop $X | Horizon: X months
🏆 SCORE: Asymmetry X/10 | Catalyst X/10 | Macro X/10

End with:
📋 PORTFOLIO NOTE: [correlation/concentration]
🌍 MACRO REGIME: [one sentence backdrop]""", key)

def run_asymmetric_scan(key):
    macro   = get_macro_prices()
    df_sec  = get_sector_table(SECTORS)
    df_st   = get_stock_table(STOCKS)
    news_m  = get_news("geopolitical risk Federal Reserve rate inflation 2026", 8)
    news_s  = get_news("sector rotation ETF institutional buying 2026", 6)
    news_c  = get_news("insider buying FDA approval DoD contract earnings catalyst 2026", 8)
    news_b  = get_news("overvalued crowded trade short seller warning 2026", 6)

    results = {}
    threads = [
        threading.Thread(target=lambda: results.update({"macro":  _macro_agent(key, macro, news_m)})),
        threading.Thread(target=lambda: results.update({"sector": _sector_agent(key, df_sec, news_s)})),
        threading.Thread(target=lambda: results.update({"stocks": _stocks_agent(key, df_st, news_c)})),
        threading.Thread(target=lambda: results.update({"contra": _contra_agent(key, df_st, news_b)})),
    ]
    for t in threads: t.start()
    for t in threads: t.join(timeout=200)

    results["thesis"] = _thesis_agent(key,
        results.get("macro",""), results.get("sector",""),
        results.get("stocks",""), results.get("contra",""))
    return results

# ── MODE 2: Supply Chain Mapper ───────────────────────────────────────────────

def run_supply_chain(key, target):
    return call_gemini(
        "You are a supply chain intelligence analyst. Map complete supply ecosystems and find hidden asymmetric bets in obscure suppliers.",
        f"""Date: {datetime.now().strftime('%Y-%m-%d')}
TARGET: {target}

Use live web search to provide a COMPLETE SUPPLY CHAIN MAP for {target}.

1. 🏭 TIER 1 SUPPLIERS (direct, large-cap)
   - List top 5-7 with ticker, what they supply, market cap, dependency level

2. 🔩 TIER 2 SUPPLIERS (components, mid-cap — the hidden plays)
   - List 5-7 with ticker, specific component/material, why they matter
   - Flag anyone with >30% revenue exposure to {target}

3. ⛏️ TIER 3 RAW MATERIALS (commodities, miners, specialty chemicals)
   - Who owns the critical inputs? Any bottlenecks?
   - Any single-source materials or geographic concentration risk?

4. 🏆 PATENT & IP MOAT
   - Who holds critical patents in this supply chain?
   - Any licensing choke points?

5. 💎 TOP 3 ASYMMETRIC PLAYS (the obscure bets)
   For each: ticker, why obscure/under-followed, catalyst, price target rationale

6. ⚠️ SUPPLY CHAIN RISKS
   - Geopolitical vulnerabilities
   - Concentration risks
   - Substitution threats

STRICT: End with TICKERS: [list all mentioned tickers]""")

# ── MODE 3: Sector Deep Dive ──────────────────────────────────────────────────

def run_sector_dive(key, sector):
    df_sec = get_sector_table(SECTORS)
    return call_gemini(
        "You are a sector specialist with deep knowledge of industry dynamics, competitive moats, and cycle positioning.",
        f"""Date: {datetime.now().strftime('%Y-%m-%d')}
SECTOR: {sector}
CURRENT SECTOR ETF DATA: {df_sec.to_string(index=False) if not df_sec.empty else "N/A"}

Use live web search for current data. Provide FULL SECTOR INTELLIGENCE REPORT:

1. 📊 SECTOR SNAPSHOT
   - Current cycle position (early/mid/late/contraction)
   - Key ETF: performance, flows, RSI signal
   - Institutional positioning (over/under-weight vs history)

2. 🏆 TOP PLAYERS RANKED BY ASYMMETRY
   For each top 5: ticker, market cap, why interesting now, valuation vs peers, score 1-10

3. 💎 HIDDEN GEMS (sub-$5B market cap)
   - 3 small/mid-cap plays most analysts ignore
   - Why they have asymmetric upside in this sector

4. 🌍 MACRO TAILWINDS & HEADWINDS
   - What macro forces help this sector right now?
   - What kills this trade?

5. 📅 UPCOMING CATALYSTS
   - Key earnings, conferences, regulatory decisions in next 90 days
   - Which event has the highest asymmetric potential?

6. 🎯 BEST ASYMMETRIC BET IN THIS SECTOR RIGHT NOW
   - Single best risk/reward: entry, target, stop, horizon

STRICT: End with TICKERS: [list all mentioned tickers]""", key)

# ── MODE 4: Single Stock Stress Test ─────────────────────────────────────────

def run_stock_stress(key, ticker):
    price, chg = get_price_yf(ticker)
    return call_gemini(
        "You are a forensic equity analyst who stress-tests stocks from both bull and bear angles with brutal honesty.",
        f"""Date: {datetime.now().strftime('%Y-%m-%d')}
TICKER: {ticker.upper()}
CURRENT PRICE: ${price} ({chg:+.2f}% today) if price else "N/A"

Use live web search for latest earnings, news, filings on {ticker}. Provide FULL STRESS TEST:

1. 🐂 BULL CASE (12-month)
   - Revenue/earnings growth drivers
   - Margin expansion levers
   - Upcoming catalysts that could re-rate
   - Price target: Base $X | Bull $X | Ultra-bull $X

2. 🐻 BEAR CASE (12-month)
   - What does the short thesis say?
   - Valuation red flags (P/E, P/S, EV/EBITDA vs growth)
   - What's already priced in that could disappoint?
   - Downside scenario: Base $X | Bear $X

3. 🔍 FORENSIC FLAGS
   - Any accounting concerns? (revenue recognition, cash vs earnings)
   - Insider selling trends (last 6 months)
   - Debt structure and covenant risks
   - Customer concentration risk

4. 🏆 ASYMMETRIC PLAY VS SUPPLIERS
   - Who are the Tier 2/3 suppliers to {ticker}?
   - Is there a smaller, lesser-known supplier that's a BETTER asymmetric bet?
   - Compare risk/reward: {ticker} vs best supplier alternative

5. ⚖️ VERDICT
   - Current sentiment vs fair value
   - Crowding score 1-10 (10 = very crowded)
   - Final verdict: STRONG BUY / BUY / HOLD / SELL / STRONG SELL
   - Conviction level and key assumption to monitor

STRICT: End with TICKERS: {ticker}, [SUPPLIER_TICKER_1], [SUPPLIER_TICKER_2]""", key)

# ── MODE 5: Geopolitical Trade Finder ────────────────────────────────────────

def run_geo_trade(key, scenario):
    return call_gemini(
        "You are a geopolitical risk analyst specializing in translating macro events into specific investable trades.",
        f"""Date: {datetime.now().strftime('%Y-%m-%d')}
GEOPOLITICAL SCENARIO: {scenario}

Use live web search for latest developments on: {scenario}

1. 🌍 SCENARIO ANALYSIS
   - Current status and probability of escalation/resolution
   - Historical precedents and how markets responded
   - Timeline: near-term (0-3mo) vs medium-term (3-12mo) implications

2. 📈 DIRECT WINNERS (explicit beneficiaries)
   For each top 5: ticker, why they win, magnitude of impact, timeframe

3. 📉 DIRECT LOSERS (explicit victims)
   For each top 3: ticker, specific exposure, downside scenario

4. 💎 SECOND-ORDER PLAYS (non-obvious, asymmetric)
   - What does the market NOT see yet?
   - Supply chain disruptions creating hidden winners
   - Currency/commodity plays most ignore
   - Geographic rotation opportunities

5. 🛡️ HEDGE PLAYS
   - Best ways to hedge a portfolio against this scenario
   - Instruments: ETFs, options, commodities, currencies

6. ⚡ HIGHEST ASYMMETRY TRADE
   - Single best risk/reward if this scenario plays out
   - Entry, target, stop, catalyst to watch

STRICT: End with TICKERS: [list all mentioned tickers]""", key)

# ── MODE 6: Commodity Chain Tracer ───────────────────────────────────────────

def run_commodity_chain(key, commodity):
    return call_gemini(
        "You are a commodity markets expert who traces entire value chains from raw material to end product.",
        f"""Date: {datetime.now().strftime('%Y-%m-%d')}
COMMODITY: {commodity}

Use live web search for current prices, supply/demand data, and latest news on {commodity}.

1. 📊 CURRENT MARKET STATE
   - Spot price, 1Y trend, supply/demand balance
   - Key price drivers right now
   - Contango/backwardation and what it signals

2. ⛏️ UPSTREAM (who extracts/produces)
   - Top 5 producers by ticker: market cap, production cost, leverage to price
   - Geographic concentration risk (which countries control supply?)
   - Any near-term supply disruptions?

3. 🏭 MIDSTREAM (who refines/processes)
   - Key processors/refiners with tickers
   - Who has the cheapest processing costs? (moat)
   - Any bottlenecks in processing capacity?

4. 🏗️ DOWNSTREAM (who consumes)
   - Top end-users with tickers
   - Which companies are most exposed to price changes?
   - Winners if price rises vs falls

5. 💎 BEST ASYMMETRIC PLAYS RIGHT NOW
   - Top 3 tickers with entry rationale
   - Why these are better than just buying the commodity ETF
   - Specific catalyst for each

6. 🔄 SUBSTITUTION RISK
   - What could replace this commodity?
   - Timeline and impact on current producers

STRICT: End with TICKERS: [list all mentioned tickers]""", key)

# ── MODE 7: Portfolio Stress Tester ──────────────────────────────────────────

def run_portfolio_stress(key, holdings):
    return call_gemini(
        "You are a risk manager and portfolio strategist. You stress-test portfolios with brutal honesty.",
        f"""Date: {datetime.now().strftime('%Y-%m-%d')}
PORTFOLIO HOLDINGS: {holdings}

Use live web search for current market conditions and analysis. PORTFOLIO STRESS TEST:

1. 📊 PORTFOLIO ANALYSIS
   - Sector concentration (where are you over/under-exposed?)
   - Factor exposure: growth vs value, large vs small cap, domestic vs international
   - Correlation matrix risk (are your "diversified" holdings actually correlated?)

2. 🔥 SCENARIO STRESS TESTS
   Run each scenario and estimate portfolio impact:
   a) 2008-style crash (-40% market): estimated portfolio drawdown
   b) Rate spike (+200bps in 3 months): winners and losers in your holdings
   c) Stagflation (high inflation + recession): what survives?
   d) Geopolitical shock (Taiwan conflict): specific exposure
   e) AI bubble burst (-60% tech): your tech exposure analysis

3. 🎯 HIGHEST RISK POSITIONS
   - Which 3 positions have worst risk/reward right now?
   - What's the bear case for each?

4. 💎 GAPS & OPPORTUNITIES
   - What themes are you MISSING that should be in this portfolio?
   - Any positions that should be trimmed/sold?
   - Suggested new positions to improve risk-adjusted returns

5. 🛡️ HEDGING RECOMMENDATIONS
   - 3 specific hedges for this portfolio
   - Cost-effective options strategies or ETF hedges

6. ✅ OVERALL VERDICT
   - Portfolio health score 1-10
   - Top 3 action items this week""", key)

# ── MODE 8: Relative Value Comparator ────────────────────────────────────────

def run_relative_value(key, ticker_a, ticker_b):
    pa, ca = get_price_yf(ticker_a)
    pb, cb = get_price_yf(ticker_b)
    return call_gemini(
        "You are a fundamental analyst specializing in relative value and pair trade identification.",
        f"""Date: {datetime.now().strftime('%Y-%m-%d')}
COMPARE: {ticker_a.upper()} vs {ticker_b.upper()}
{ticker_a}: ${pa} ({ca:+.2f}%) | {ticker_b}: ${pb} ({cb:+.2f}%)

Use live web search for latest financials, news, and analyst targets. HEAD-TO-HEAD ANALYSIS:

1. 📊 VALUATION COMPARISON
   | Metric          | {ticker_a} | {ticker_b} | Winner |
   Compare: P/E, Forward P/E, P/S, EV/EBITDA, P/FCF, PEG ratio

2. 📈 GROWTH COMPARISON
   Compare: Revenue growth (1Y, 3Y CAGR), EPS growth, margin trends, guidance

3. 🏰 MOAT COMPARISON
   - Market share and trend
   - Pricing power evidence
   - Switching costs / network effects
   - R&D investment and patent portfolio

4. 💰 BALANCE SHEET COMPARISON
   - Debt/Equity, Interest Coverage, Cash position
   - Share buybacks and dividend history
   - Capital allocation quality

5. 🎯 CATALYST COMPARISON
   - Upcoming catalysts for each (next 6 months)
   - Which has more identifiable near-term upside?

6. ⚖️ PAIR TRADE ANALYSIS
   - Historical spread: is {ticker_a}/{ticker_b} at extreme?
   - Long/short recommendation with rationale
   - Entry level, target spread, stop loss

7. 🏆 FINAL VERDICT
   - Better risk/reward RIGHT NOW: {ticker_a} or {ticker_b}?
   - Conviction: HIGH / MEDIUM / LOW
   - Key assumptions that change this verdict""", key)

# ── MODE 9: Sector Rotation Timer ────────────────────────────────────────────

def run_rotation_timer(key):
    macro = get_macro_prices()
    df_sec = get_sector_table(SECTORS)
    return call_gemini(
        "You are a market cycle analyst who identifies where we are in the economic cycle and what to rotate into next.",
        f"""Date: {datetime.now().strftime('%Y-%m-%d')}
MACRO DATA: {json.dumps({k:{"price":v[0],"chg%":v[1]} for k,v in macro.items()}, indent=2)}
SECTOR ETF PERFORMANCE: {df_sec.to_string(index=False) if not df_sec.empty else "N/A"}

Use live web search for latest economic data (PMI, CPI, jobs, yield curve). ROTATION ANALYSIS:

1. 🕐 CYCLE POSITIONING
   - Where are we in the economic cycle? (Early/Mid/Late/Contraction)
   - Evidence: yield curve, PMI, employment, earnings trend
   - Confidence level and what would change this view

2. 📊 CURRENT SECTOR LEADERSHIP
   - Which sectors are leading RIGHT NOW and why
   - Which are lagging and whether it's a buying opportunity
   - Institutional flow data: where is smart money moving?

3. 🔄 NEXT ROTATION (0-6 months)
   - What rotates INTO next based on cycle logic?
   - Historical cycle pattern: what typically follows current phase?
   - Specific ETFs and stocks to position in NOW

4. ⏰ TIMING SIGNALS TO WATCH
   - 3 specific indicators that would confirm/deny the rotation
   - Current readings vs historical thresholds

5. 💎 HIGHEST CONVICTION ROTATION TRADE
   - Specific long/short pair trade for the rotation
   - ETF or stock level implementation
   - Entry, target, stop, horizon

6. 🌍 INTERNATIONAL ROTATION
   - Any country/regional markets offering better cycle positioning?
   - Best international ETF plays right now""", key)

# ── MODE 10: Catalyst Calendar ────────────────────────────────────────────────

def run_catalyst_calendar(key, watchlist):
    return call_gemini(
        "You are an event-driven trading specialist who tracks and ranks upcoming catalysts by asymmetric potential.",
        f"""Date: {datetime.now().strftime('%Y-%m-%d')}
WATCHLIST: {watchlist}

Use live web search to find ALL upcoming catalysts for these tickers. CATALYST CALENDAR:

1. 📅 90-DAY CATALYST CALENDAR
   Format each event as:
   DATE | TICKER | EVENT TYPE | EXPECTED IMPACT | ASYMMETRY SCORE

   Event types: Earnings, FDA Decision, Product Launch, Analyst Day, Conference,
   Contract Award, Regulatory, M&A, Macro (Fed, CPI, Jobs)

2. 🔥 TOP 5 HIGHEST ASYMMETRY EVENTS (next 30 days)
   For each:
   - What's the event and when exactly?
   - What does consensus expect?
   - What's the "surprise" scenario that creates asymmetry?
   - How to position: entry, size, stop, target

3. ⚡ BINARY EVENT PLAYS
   - Any FDA/regulatory decisions that are binary (big move either way)?
   - Earnings setups where implied vol is cheap vs expected move?
   - Options strategy for each binary event

4. 📊 MACRO CALENDAR
   - Key Fed meetings, CPI releases, jobs reports in next 90 days
   - How each could impact your watchlist stocks

5. 🎯 THIS WEEK'S BEST SETUP
   - Single best catalyst trade in the next 7 days
   - Exact entry, catalyst date, target, stop""", key)

# ══════════════════════════════════════════════════════════════════════════════
#  UI — MAIN TABS
# ══════════════════════════════════════════════════════════════════════════════

tab_dash, tab_scan, tab_supply, tab_sector, tab_stock, tab_geo, tab_commodity, tab_port, tab_compare, tab_rotation, tab_calendar, tab_info = st.tabs([
    "📊 Dashboard",
    "🎯 Alpha Scan",
    "🔗 Supply Chain",
    "🏭 Sector Dive",
    "🔬 Stock Stress",
    "🌍 Geo Trade",
    "⛏️ Commodity",
    "⚖️ Portfolio",
    "🆚 Compare",
    "🔄 Rotation",
    "📅 Catalyst",
    "ℹ️ Info",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB: DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
with tab_dash:
    st.markdown('<p class="shdr">🌍 Live Macro Pulse</p>', unsafe_allow_html=True)
    with st.spinner("Fetching live prices..."):
        macro = get_macro_prices()
    cols = st.columns(len(macro))
    for col, (label, (price, chg)) in zip(cols, macro.items()):
        with col:
            if price is not None:
                cls = "mup" if (chg or 0) >= 0 else "mdn"
                sgn = "+" if (chg or 0) >= 0 else ""
                fmt = f"{price:,.0f}" if price > 1000 else f"{price:,.2f}"
                st.markdown(f"""<div class="mbox">
<span class="mlbl">{label}</span>
<span class="mval">{fmt}</span>
<span class="{cls}">{sgn}{chg:.2f}%</span>
</div>""", unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="mbox"><span class="mlbl">{label}</span><span class="mval">—</span><span class="mna">loading</span></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns([1, 2])

    with left:
        st.markdown('<p class="shdr">🔄 Sector Momentum</p>', unsafe_allow_html=True)
        with st.spinner(""):
            df_sec = get_sector_table(SECTORS)
        if not df_sec.empty:
            def csec(v):
                if isinstance(v, (int,float)):
                    return "color:#10b981;font-weight:600" if v>0 else "color:#ef4444;font-weight:600"
                return ""
            st.dataframe(df_sec.style.map(csec, subset=["1M%","1W%"]),
                         width="stretch", hide_index=True, height=365)
        else:
            st.warning("Sector data temporarily unavailable")

    with right:
        st.markdown('<p class="shdr">🎯 Watchlist Signals</p>', unsafe_allow_html=True)
        with st.spinner(""):
            df_st = get_stock_table(STOCKS)
        if not df_st.empty:
            def crsi(v):
                if isinstance(v,(int,float)):
                    if v < 35: return "color:#10b981;font-weight:700"
                    if v > 70: return "color:#ef4444;font-weight:700"
                return ""
            def cm1(v):
                if isinstance(v,(int,float)):
                    return "color:#10b981" if v>0 else "color:#ef4444"
                return ""
            st.dataframe(
                df_st.style.map(crsi, subset=["RSI"]).map(cm1, subset=["1M%"]),
                width="stretch", hide_index=True, height=365)
        else:
            st.warning("Stock data temporarily unavailable")

    st.markdown('<p class="shdr">📰 Market Intelligence Feed</p>', unsafe_allow_html=True)
    col_n1, col_n2 = st.columns(2)
    with col_n1:
        st.markdown("**Markets & Macro**")
        for h in get_news("stock market asymmetric opportunity macro 2026", 5):
            st.markdown(f'<div class="news-item"><span class="news-title">{h["title"]}</span><br><span style="color:#374151;font-size:0.72rem">{h["source"]}</span></div>', unsafe_allow_html=True)
    with col_n2:
        st.markdown("**Geopolitics & Policy**")
        for h in get_news("geopolitical risk Federal Reserve tariff trade war 2026", 5):
            st.markdown(f'<div class="news-item"><span class="news-title">{h["title"]}</span><br><span style="color:#374151;font-size:0.72rem">{h["source"]}</span></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HELPER: key check
# ══════════════════════════════════════════════════════════════════════════════
def key_check():
    if not gemini_key:
        st.warning("👈 Enter your **Gemini API key** in the sidebar to use this feature.")
        st.info("Get a free key at [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)")
        return False
    return True

def show_result(text, mode_class=""):
    st.markdown(f'<div class="result-card {mode_class}">{text}</div>', unsafe_allow_html=True)

def tg_button(text, label="📱 Send to Telegram"):
    if tg_token and tg_chat:
        if st.button(label):
            send_telegram(text, tg_token, tg_chat)
            st.success("✅ Sent to Telegram!")
    dl_name = f"alpha_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    st.download_button("⬇️ Download", data=text, file_name=dl_name, mime="text/plain")

# ══════════════════════════════════════════════════════════════════════════════
# TAB: ALPHA SCAN (5-agent parallel)
# ══════════════════════════════════════════════════════════════════════════════
with tab_scan:
    st.markdown("### 🎯 Asymmetric Bet Scanner")
    st.markdown("5 AI agents run in parallel — Macro · Sector · Stock Sniper · Contrarian · CIO Synthesis")

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.markdown("**🌍 Macro**\nGeopolitics\nRates · FX · Cycles")
    c2.markdown("**🔄 Sector**\nRotation\nETF Flow · Positioning")
    c3.markdown("**🎯 Stocks**\nCatalysts\nInsiders · Signals")
    c4.markdown("**⚠️ Contra**\nBear cases\nStress tests")
    c5.markdown("**📝 CIO**\nSynthesis\nFinal scored alert")
    st.divider()

    if key_check():
        if st.button("🚀 Run Full Alpha Scan", type="primary"):
            prog = st.progress(0, text="Fetching market data...")
            with st.spinner("Loading market data..."):
                df_stocks  = get_stock_table(STOCKS)
                df_sectors = get_sector_table(SECTORS)
            st.success(f"✅ {len(df_stocks)} stocks · {len(df_sectors)} sectors loaded")

            stat_cols = st.columns(4)
            for col, lbl in zip(stat_cols, ["🌍 Macro Scout","🔄 Sector Analyst","🎯 Stock Sniper","⚠️ Contrarian"]):
                col.info(f"{lbl}\n⏳ Running...")

            prog.progress(20, text="4 agents running in parallel (~2-3 min)...")

            try:
                results = run_asymmetric_scan(gemini_key)
                prog.progress(85, text="CIO synthesizing...")

                for col, lbl, key_r in zip(stat_cols,
                    ["🌍 Macro","🔄 Sector","🎯 Stocks","⚠️ Contra"],
                    ["macro","sector","stocks","contra"]):
                    val = results.get(key_r,"")
                    if val.startswith("[API"): col.error(f"{lbl}\n❌")
                    else: col.success(f"{lbl}\n✅")

                prog.progress(100, text="✅ Complete!")

                st.markdown("## 🏆 Final Alpha Report")
                final = results.get("thesis","[No output]")
                show_result(final)
                tg_button(f"🤖 ALPHA MACHINE v2\n{datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n\n{final}")

                with st.expander("🌍 Macro Scout details"): st.write(results.get("macro",""))
                with st.expander("🔄 Sector Analyst details"): st.write(results.get("sector",""))
                with st.expander("🎯 Stock Sniper details"): st.write(results.get("stocks",""))
                with st.expander("⚠️ Contrarian details"): st.write(results.get("contra",""))

            except Exception as e:
                prog.progress(0)
                st.error(f"❌ Error: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB: SUPPLY CHAIN
# ══════════════════════════════════════════════════════════════════════════════
with tab_supply:
    st.markdown("### 🔗 Supply Chain Intelligence Mapper")
    st.markdown("Enter any company ticker or sector — AI maps the complete Tier 1/2/3 supply chain and finds hidden asymmetric plays in obscure suppliers.")

    col_in, col_btn = st.columns([3,1])
    with col_in:
        supply_target = st.text_input("Company or Sector", placeholder="e.g. NVDA · Tesla · Solid State Batteries · Quantum Computing", label_visibility="collapsed")
    with col_btn:
        supply_run = st.button("🔍 Map Chain", type="primary", key="supply_btn")

    st.caption("Examples: `NVDA` `TSLA` `Lithium batteries` `Semiconductor fab` `Defense electronics`")

    if supply_run:
        if not key_check(): pass
        elif not supply_target:
            st.warning("Enter a company or sector to map")
        else:
            with st.spinner(f"Mapping supply chain for {supply_target}..."):
                result = run_supply_chain(gemini_key, supply_target)
            show_result(result, "supply")
            tg_button(f"🔗 SUPPLY CHAIN: {supply_target}\n\n{result}", "📱 Send Chain Map to Telegram")

# ══════════════════════════════════════════════════════════════════════════════
# TAB: SECTOR DEEP DIVE
# ══════════════════════════════════════════════════════════════════════════════
with tab_sector:
    st.markdown("### 🏭 Sector Deep Dive")
    st.markdown("Full sector intelligence: cycle positioning, top plays, hidden gems, catalysts, best asymmetric bet.")

    col_in, col_btn = st.columns([3,1])
    with col_in:
        sector_target = st.text_input("Sector Name", placeholder="e.g. Defense · Biotech · Energy · Semiconductors · Financials", label_visibility="collapsed")
    with col_btn:
        sector_run = st.button("🔍 Dive Deep", type="primary", key="sector_btn")

    st.caption("Examples: `Defense` `Biotech` `Clean Energy` `Semiconductors` `Healthcare` `Fintech`")

    if sector_run:
        if not key_check(): pass
        elif not sector_target:
            st.warning("Enter a sector name")
        else:
            with st.spinner(f"Analyzing {sector_target} sector..."):
                result = run_sector_dive(gemini_key, sector_target)
            show_result(result, "sector")
            tg_button(f"🏭 SECTOR DIVE: {sector_target}\n\n{result}", "📱 Send to Telegram")

# ══════════════════════════════════════════════════════════════════════════════
# TAB: STOCK STRESS TEST
# ══════════════════════════════════════════════════════════════════════════════
with tab_stock:
    st.markdown("### 🔬 Single Stock Stress Test")
    st.markdown("Full forensic analysis: bull case, bear case, accounting flags, insider trends, and supplier alternatives.")

    col_in, col_btn = st.columns([3,1])
    with col_in:
        stress_ticker = st.text_input("Stock Ticker", placeholder="e.g. NVDA · PLTR · TSLA · RKLB", label_visibility="collapsed")
    with col_btn:
        stress_run = st.button("🔬 Stress Test", type="primary", key="stress_btn")

    if stress_run:
        if not key_check(): pass
        elif not stress_ticker:
            st.warning("Enter a ticker to stress test")
        else:
            ticker_clean = stress_ticker.strip().upper().replace("$","")
            with st.spinner(f"Stress testing {ticker_clean}..."):
                result = run_stock_stress(gemini_key, ticker_clean)
            show_result(result, "stress")
            tg_button(f"🔬 STRESS TEST: {ticker_clean}\n\n{result}", "📱 Send to Telegram")

# ══════════════════════════════════════════════════════════════════════════════
# TAB: GEO TRADE FINDER
# ══════════════════════════════════════════════════════════════════════════════
with tab_geo:
    st.markdown("### 🌍 Geopolitical Trade Finder")
    st.markdown("Translate any geopolitical scenario into specific investable trades — winners, losers, second-order plays, and hedges.")

    col_in, col_btn = st.columns([3,1])
    with col_in:
        geo_scenario = st.text_input("Geopolitical Scenario", placeholder="e.g. Taiwan conflict · US-China trade war · Middle East escalation · EU energy crisis", label_visibility="collapsed")
    with col_btn:
        geo_run = st.button("🌍 Find Trades", type="primary", key="geo_btn")

    st.caption("Examples: `Taiwan strait conflict` `Russia sanctions escalation` `OPEC+ production cut` `US election outcome`")

    if geo_run:
        if not key_check(): pass
        elif not geo_scenario:
            st.warning("Enter a geopolitical scenario")
        else:
            with st.spinner(f"Mapping trades for: {geo_scenario}..."):
                result = run_geo_trade(gemini_key, geo_scenario)
            show_result(result, "geo")
            tg_button(f"🌍 GEO TRADE: {geo_scenario}\n\n{result}", "📱 Send to Telegram")

# ══════════════════════════════════════════════════════════════════════════════
# TAB: COMMODITY CHAIN
# ══════════════════════════════════════════════════════════════════════════════
with tab_commodity:
    st.markdown("### ⛏️ Commodity Chain Tracer")
    st.markdown("Trace any commodity from mine to end-product. Find the bottleneck, the moat, and the best asymmetric play in the chain.")

    col_in, col_btn = st.columns([3,1])
    with col_in:
        commodity_target = st.text_input("Commodity", placeholder="e.g. Lithium · Uranium · Copper · Rare Earth · Natural Gas · Cocoa", label_visibility="collapsed")
    with col_btn:
        commodity_run = st.button("⛏️ Trace Chain", type="primary", key="commodity_btn")

    st.caption("Examples: `Lithium` `Uranium` `Copper` `Silicon` `Rare earth elements` `LNG`")

    if commodity_run:
        if not key_check(): pass
        elif not commodity_target:
            st.warning("Enter a commodity")
        else:
            with st.spinner(f"Tracing {commodity_target} chain..."):
                result = run_commodity_chain(gemini_key, commodity_target)
            show_result(result, "commodity")
            tg_button(f"⛏️ COMMODITY CHAIN: {commodity_target}\n\n{result}", "📱 Send to Telegram")

# ══════════════════════════════════════════════════════════════════════════════
# TAB: PORTFOLIO STRESS TEST
# ══════════════════════════════════════════════════════════════════════════════
with tab_port:
    st.markdown("### ⚖️ Portfolio Stress Tester")
    st.markdown("Paste your holdings — AI stress-tests against 5 macro scenarios, finds concentration risks, and suggests improvements.")

    holdings_input = st.text_area(
        "Your Holdings",
        placeholder="NVDA 15%, AAPL 10%, MSFT 10%, PLTR 8%, TSLA 7%, Cash 20%, BTC 5%, Gold ETF 5%...\nOr just list tickers: NVDA, AAPL, MSFT, PLTR, TSLA",
        height=120
    )
    port_run = st.button("⚖️ Stress Test Portfolio", type="primary", key="port_btn")

    if port_run:
        if not key_check(): pass
        elif not holdings_input.strip():
            st.warning("Enter your portfolio holdings")
        else:
            with st.spinner("Running 5-scenario stress test..."):
                result = run_portfolio_stress(gemini_key, holdings_input)
            show_result(result, "portfolio")
            tg_button(f"⚖️ PORTFOLIO STRESS TEST\n\n{result}", "📱 Send to Telegram")

# ══════════════════════════════════════════════════════════════════════════════
# TAB: RELATIVE VALUE COMPARE
# ══════════════════════════════════════════════════════════════════════════════
with tab_compare:
    st.markdown("### 🆚 Relative Value Comparator")
    st.markdown("Head-to-head forensic comparison: valuation, growth, moat, catalysts, and pair trade analysis.")

    col_a, col_vs, col_b = st.columns([2, 0.5, 2])
    with col_a:
        ticker_a = st.text_input("Ticker A", placeholder="NVDA", key="ta")
    with col_vs:
        st.markdown("<br><br>**vs**", unsafe_allow_html=True)
    with col_b:
        ticker_b = st.text_input("Ticker B", placeholder="AMD", key="tb")

    compare_run = st.button("🆚 Compare", type="primary", key="compare_btn")

    if compare_run:
        if not key_check(): pass
        elif not ticker_a or not ticker_b:
            st.warning("Enter both tickers")
        else:
            ta, tb = ticker_a.strip().upper(), ticker_b.strip().upper()
            with st.spinner(f"Comparing {ta} vs {tb}..."):
                result = run_relative_value(gemini_key, ta, tb)
            show_result(result, "compare")
            tg_button(f"🆚 {ta} vs {tb}\n\n{result}", "📱 Send to Telegram")

# ══════════════════════════════════════════════════════════════════════════════
# TAB: ROTATION TIMER
# ══════════════════════════════════════════════════════════════════════════════
with tab_rotation:
    st.markdown("### 🔄 Sector Rotation Timer")
    st.markdown("AI determines exactly where we are in the economic cycle, what's rotating next, and the highest-conviction rotation trade right now.")

    if key_check():
        if st.button("🔄 Analyze Current Rotation", type="primary", key="rotation_btn"):
            with st.spinner("Analyzing economic cycle and sector positioning..."):
                result = run_rotation_timer(gemini_key)
            show_result(result, "rotation")
            tg_button(f"🔄 ROTATION TIMER\n{datetime.now().strftime('%Y-%m-%d')}\n\n{result}", "📱 Send to Telegram")

# ══════════════════════════════════════════════════════════════════════════════
# TAB: CATALYST CALENDAR
# ══════════════════════════════════════════════════════════════════════════════
with tab_calendar:
    st.markdown("### 📅 Catalyst Calendar")
    st.markdown("Enter any watchlist — AI finds all upcoming catalysts, ranks by asymmetric potential, and identifies the best event-driven trade this week.")

    watchlist_input = st.text_input(
        "Watchlist (comma-separated)",
        value=",".join(STOCKS[:8]),
        placeholder="NVDA, PLTR, RKLB, IONQ, HIMS..."
    )
    calendar_run = st.button("📅 Generate Catalyst Calendar", type="primary", key="cal_btn")

    if calendar_run:
        if not key_check(): pass
        elif not watchlist_input.strip():
            st.warning("Enter at least one ticker")
        else:
            with st.spinner("Scanning for upcoming catalysts..."):
                result = run_catalyst_calendar(gemini_key, watchlist_input)
            show_result(result, "catalyst")
            tg_button(f"📅 CATALYST CALENDAR\n{datetime.now().strftime('%Y-%m-%d')}\n\n{result}", "📱 Send to Telegram")

# ══════════════════════════════════════════════════════════════════════════════
# TAB: INFO
# ══════════════════════════════════════════════════════════════════════════════
with tab_info:
    st.markdown("## 🏗️ Alpha Machine v2 — All Modes")

    modes = [
        ("🎯", "Alpha Scan",      "5 parallel agents find asymmetric bets across macro, sector, stock, and contrarian layers"),
        ("🔗", "Supply Chain",    "Maps complete Tier 1/2/3 supplier chains — finds the obscure $2B company that's the real play"),
        ("🏭", "Sector Dive",     "Full sector intelligence: cycle position, hidden gems, institutional flow, best bet"),
        ("🔬", "Stock Stress",    "Forensic bull + bear analysis, accounting flags, insider trends, supplier alternatives"),
        ("🌍", "Geo Trade",       "Translates geopolitical scenarios into specific winners, losers, and hedges"),
        ("⛏️", "Commodity Chain", "Traces any commodity upstream/downstream — finds the moat, bottleneck, and best play"),
        ("⚖️", "Portfolio",       "5-scenario stress test + concentration risk + hedging recommendations"),
        ("🆚", "Compare",         "Head-to-head forensic comparison + pair trade with entry/stop/target"),
        ("🔄", "Rotation Timer",  "Identifies cycle phase, next rotation, and highest-conviction rotation trade"),
        ("📅", "Catalyst",        "90-day event calendar ranked by asymmetric potential + this week's best setup"),
    ]

    col1, col2 = st.columns(2)
    for i, (icon, name, desc) in enumerate(modes):
        col = col1 if i % 2 == 0 else col2
        col.markdown(f"**{icon} {name}**\n\n{desc}\n")
        col.divider()

    st.markdown("## 🔑 Setup Guide")
    st.markdown("""
**1. Get Gemini API Key (free, 2 minutes):**
- Go to [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
- Click **Create API Key** → select any project
- Copy key (starts with `AIza...`) → paste in sidebar

**2. Set up Telegram alerts (optional):**
- Message [@BotFather](https://t.me/BotFather) → `/newbot` → copy token
- Add bot to your channel as admin
- Get chat ID: `https://api.telegram.org/bot<TOKEN>/getUpdates`

**3. All 10 modes use:**
- Gemini 2.5 Flash with **live Google Search grounding** (real-time web access)
- Free tier: 15 requests/min · 1,500/day · $0/month
    """)
