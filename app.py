"""
Alpha Machine v4 — Institutional Intelligence & Agentic Research
18 Modes | Telegram Bot | Smart Watchdog | SEC Scanner | Options Flow
13F Tracker | Earnings Analyzer | Backtester | Newsletter | PDF Report
Python 3.14 | Gemini 2.5 Flash | Streamlit Cloud ready
"""

import streamlit as st

st.set_page_config(
    page_title="Alpha Machine v4 🛡️",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

import requests, feedparser, json, threading, time, re, io, base64
import pandas as pd
from datetime import datetime, timedelta
from google import genai
from google.genai import types

# ══════════════════════════════════════════════════════════════════════════════
#  CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&family=JetBrains+Mono:wght@400;600&display=swap');
html, body, [data-testid="stAppViewContainer"] { background:#05070d; font-family:'Inter',sans-serif; }
[data-testid="stSidebar"] { background:#080b12; border-right:1px solid #1a2035; }
[data-testid="stSidebar"] * { color:#c9d1e0 !important; }
.block-container { padding-top:1rem; padding-bottom:2rem; }
h1,h2,h3,p,li,span,div,label { color:#e2e8f0; }
.alpha-title {
    font-size:2.2rem; font-weight:900; letter-spacing:-1.5px;
    background:linear-gradient(90deg,#00ffa3,#00d4ff,#a78bfa,#ff6b9d);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; line-height:1.1;
}
.alpha-sub { color:#4b5e7a; font-size:0.82rem; letter-spacing:0.5px; }
.shdr { color:#94a3b8; font-size:0.72rem; font-weight:700; text-transform:uppercase;
        letter-spacing:2px; border-bottom:1px solid #1e2d45; padding-bottom:6px; margin:16px 0 10px; }
.mbox { background:#0d1321; border:1px solid #1e2d45; border-radius:10px;
        padding:12px 8px; text-align:center; min-height:82px; }
.mlbl { color:#4b5e7a; font-size:0.65rem; text-transform:uppercase; letter-spacing:1.5px; display:block; }
.mval { color:#f1f5f9; font-size:1.2rem; font-weight:700; display:block; margin:3px 0;
        font-family:'JetBrains Mono',monospace; }
.mup { color:#10b981; font-size:0.75rem; font-weight:600; }
.mdn { color:#ef4444; font-size:0.75rem; font-weight:600; }
.mna { color:#374151; font-size:0.75rem; }
.result-card {
    background:linear-gradient(135deg,#08111e,#0d1928); border:1px solid #1e3a5f;
    border-left:4px solid #00ffa3; border-radius:12px; padding:20px 24px; margin:12px 0;
    font-family:'JetBrains Mono',monospace; font-size:0.84rem;
    color:#cde8ff; white-space:pre-wrap; line-height:1.7;
}
.result-card.supply    { border-left-color:#f59e0b; }
.result-card.sector    { border-left-color:#8b5cf6; }
.result-card.stress    { border-left-color:#ef4444; }
.result-card.geo       { border-left-color:#3b82f6; }
.result-card.commodity { border-left-color:#f97316; }
.result-card.portfolio { border-left-color:#ec4899; }
.result-card.compare   { border-left-color:#14b8a6; }
.result-card.rotation  { border-left-color:#a78bfa; }
.result-card.catalyst  { border-left-color:#fbbf24; }
.result-card.earnings  { border-left-color:#06b6d4; }
.result-card.sec       { border-left-color:#f43f5e; }
.result-card.options   { border-left-color:#84cc16; }
.result-card.inst      { border-left-color:#fb923c; }
.result-card.watchdog  { border-left-color:#e879f9; }
.result-card.backtest  { border-left-color:#22d3ee; }
.result-card.newsletter { border-left-color:#4ade80; }
.result-card.macro-regime { border-left-color:#00ffa3; }
.result-card.monetize { border-left-color:#f0abfc; }
.news-item { border-bottom:1px solid #1e2d45; padding:8px 0; font-size:0.82rem; color:#94a3b8; }
.news-title { color:#cbd5e1; font-weight:600; }
.alert-box { background:#0a1f0a; border:1px solid #10b981; border-radius:8px;
             padding:12px 16px; margin:8px 0; font-size:0.82rem; color:#86efac; }
.warn-box  { background:#1f0a0a; border:1px solid #ef4444; border-radius:8px;
             padding:12px 16px; margin:8px 0; font-size:0.82rem; color:#fca5a5; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="alpha-title">🛡️ Alpha Machine v4</p>', unsafe_allow_html=True)
st.markdown(f'<p class="alpha-sub">INSTITUTIONAL INTELLIGENCE · 21 MODES · STREAMING · LIVE WEB GROUNDING · {datetime.now().strftime("%d %b %Y · %H:%M UTC")}</p>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🔑 Gemini API (Free)")
    gemini_key = st.text_input("API Key", type="password", placeholder="AIza...")
    st.caption("[Get free key →](https://aistudio.google.com/app/apikey)")

    st.markdown("### 📱 Telegram Alerts")
    tg_token = st.text_input("Bot Token",  type="password", placeholder="123456:ABC...")
    tg_chat  = st.text_input("Chat ID",    placeholder="-100123456789")

    st.markdown("### 📋 Default Watchlist")
    stocks_raw  = st.text_area("Stocks",      value="NVDA,TSM,ASML,PLTR,IONQ,RKLB,HIMS,CELH,NVO,MELI", height=75)
    sectors_raw = st.text_area("Sector ETFs", value="XLK,XLE,XLF,XLV,XBI,ARKK,GDX,COPX,ITB,XAR",      height=75)
    st.markdown("---")
    st.markdown("**Free limits:** 15 req/min · 1,500/day · $0/month")
    st.markdown("v4 · 21 modes · Gemini 2.5 Flash · Streaming")
    st.divider()
    st.markdown("**⚡ Live Status**")
    st.success("🟢 Gemini 2.5 Flash — Ready" if gemini_key else "🔴 API Key Missing")
    st.info("🔵 Streaming Engine — Active")
    if tg_token and tg_chat:
        st.success("🟢 Telegram — Connected")
    if st.button("🔄 Reset Session", use_container_width=True):
        st.session_state.clear()
        st.rerun()

STOCKS  = [s.strip() for s in stocks_raw.split(",")  if s.strip()]
SECTORS = [s.strip() for s in sectors_raw.split(",") if s.strip()]

# ══════════════════════════════════════════════════════════════════════════════
#  DATA HELPERS
# ══════════════════════════════════════════════════════════════════════════════
YF_HDR = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36","Accept":"application/json"}

@st.cache_data(ttl=300, show_spinner=False)
def get_price_yf(sym):
    try:
        r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range=5d",
                         headers=YF_HDR, timeout=6)
        closes = [c for c in r.json()["chart"]["result"][0]["indicators"]["quote"][0]["close"] if c is not None]
        if len(closes) >= 2:
            return round(closes[-1],2), round((closes[-1]/closes[-2]-1)*100,2)
    except: pass
    return None, None

@st.cache_data(ttl=300, show_spinner=False)
def get_macro_prices():
    tickers = {"10Y Yield":"%5ETNX","S&P 500":"%5EGSPC","Gold":"GC%3DF","Oil":"CL%3DF","VIX":"%5EVIX","DXY":"DX-Y.NYB"}
    res = {lbl: get_price_yf(sym) for lbl, sym in tickers.items()}
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price",
            params={"ids":"bitcoin","vs_currencies":"usd","include_24hr_change":"true"},
            timeout=6, headers={"User-Agent":"AlphaMachine/3.0"})
        d = r.json()
        res["Bitcoin"] = (round(d["bitcoin"]["usd"],0), round(d["bitcoin"]["usd_24h_change"],2))
    except:
        res["Bitcoin"] = (None, None)
    return res

@st.cache_data(ttl=300, show_spinner=False)
def get_stock_table(tickers):
    rows = []
    for sym in tickers:
        try:
            r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range=3mo",
                             headers=YF_HDR, timeout=8)
            res    = r.json()["chart"]["result"][0]
            closes = [c for c in res["indicators"]["quote"][0]["close"] if c is not None]
            if len(closes) < 15: continue
            price = round(closes[-1],2)
            m1    = round((closes[-1]/closes[-22]-1)*100,2) if len(closes)>=22 else 0
            diffs = [closes[i]-closes[i-1] for i in range(1,len(closes))]
            gains = [max(d,0) for d in diffs[-14:]]; losses=[abs(min(d,0)) for d in diffs[-14:]]
            ag,al = sum(gains)/14, sum(losses)/14
            rsi   = round(100-100/(1+ag/(al+1e-9)),1)
            meta  = res.get("meta",{}); w52h=meta.get("fiftyTwoWeekHigh",0) or 0; w52l=meta.get("fiftyTwoWeekLow",0) or 0
            sigs  = []
            if rsi<35: sigs.append("🟢 Oversold")
            if rsi>70: sigs.append("🔴 Overbought")
            if w52h and price>=w52h*0.97: sigs.append("🚀 52W High")
            if w52h and price<=w52h*0.55: sigs.append("💎 Deep Value")
            if m1>15: sigs.append("⚡ Momentum")
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
            r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range=1mo",
                             headers=YF_HDR, timeout=8)
            closes=[c for c in r.json()["chart"]["result"][0]["indicators"]["quote"][0]["close"] if c is not None]
            if len(closes)<5: continue
            rows.append({"ETF":sym,"1M%":round((closes[-1]/closes[0]-1)*100,2),
                         "1W%":round((closes[-1]/closes[-6]-1)*100,2) if len(closes)>=6 else 0})
            time.sleep(0.1)
        except: pass
    return pd.DataFrame(rows).sort_values("1M%",ascending=False).reset_index(drop=True) if rows else pd.DataFrame()

@st.cache_data(ttl=600, show_spinner=False)
def get_news(query, n=10):
    try:
        url  = f"https://news.google.com/rss/search?q={requests.utils.quote(query)}&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(url)
        return [{"title":e.get("title",""),"source":e.get("source",{}).get("title",""),
                 "link":e.get("link",""),"published":e.get("published","")} for e in feed.entries[:n]]
    except: return []

@st.cache_data(ttl=1800, show_spinner=False)
def get_sec_filings(ticker, form_types="8-K,4,10-Q"):
    """Fetch recent SEC filings via EDGAR full-text search."""
    results = []
    try:
        # Search EDGAR for company CIK
        r = requests.get(f"https://efts.sec.gov/LATEST/search-index?q=%22{ticker}%22&dateRange=custom&startdt={(datetime.now()-timedelta(days=90)).strftime('%Y-%m-%d')}&forms={form_types}",
                         headers={"User-Agent":"AlphaMachine research@alpha.com"}, timeout=10)
        data = r.json()
        hits = data.get("hits",{}).get("hits",[])[:10]
        for h in hits:
            src = h.get("_source",{})
            results.append({
                "form":    src.get("form_type",""),
                "filed":   src.get("file_date",""),
                "company": src.get("entity_name",""),
                "title":   src.get("display_names","")[:80] if src.get("display_names") else src.get("file_date",""),
                "url":     f"https://www.sec.gov/Archives/edgar/data/{src.get('entity_id','')}/{src.get('file_date','').replace('-','')}"
            })
    except: pass
    return results

@st.cache_data(ttl=600, show_spinner=False)
def get_unusual_options(ticker):
    """Get unusual options activity via free finviz-style scrape."""
    try:
        r = requests.get(f"https://finance.yahoo.com/quote/{ticker}/options",
                         headers=YF_HDR, timeout=8)
        return r.status_code == 200
    except: return False

# ══════════════════════════════════════════════════════════════════════════════
#  GEMINI CORE
# ══════════════════════════════════════════════════════════════════════════════
def call_gemini(system, user, key):
    try:
        client = genai.Client(api_key=key)
        google_search_tool = types.Tool(google_search=types.GoogleSearch())
        config  = types.GenerateContentConfig(
            tools=[google_search_tool], temperature=0.2, system_instruction=system)
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=user, config=config)
        return response.text
    except Exception as e:
        return f"[API error: {e}]"


# ── STREAMING ENGINE (v4 — Premium feel, faster UX) ──────────────────────────

# Enhanced institutional system prompts
MACRO_SYSTEM = """You are a Lead Global Macro Strategist at a tier-1 hedge fund.
Analyze the intersection of Global Liquidity, Bond Yields, Currency flows, and Volatility.
ALWAYS structure your response with:
- A 'BASE CASE' scenario (60-70% probability) with specific asset plays
- A 'BLACK SWAN' scenario (10-20% probability) with tail-risk hedges
- 'SMART MONEY DIVERGENCE' — where positioning differs from consensus
Focus on correlations: if X happens, Y is the asymmetric play. Be specific with tickers."""

SUPPLY_SYSTEM = """You are a Supply Chain Forensic Analyst with deep tech sector expertise.
Your job: map the 'Nervous System' of any sector. Find the one company that owns the IP,
the bottleneck material, or the process that giants (AAPL, NVDA, TSLA, AMZN) cannot live without.
Bold all tickers in your response as **$TICKER**.
Always identify: the moat owner, the capacity constraint, and the hidden Tier-2 play."""

SECTOR_SYSTEM = """You are a Sector Rotation Specialist at a quantitative macro fund.
Identify which sectors are in 'early accumulation' vs 'late distribution' phases.
Use bond yield curve, PMI data, and earnings revision trends as your primary signals.
Rank sectors by institutional conviction and provide specific ETF + stock plays."""

EARNINGS_SYSTEM = """You are a Forensic Earnings Analyst who specializes in detecting
management tone shifts and reading between the lines of earnings calls.
Your edge: compare language vs prior quarters, detect sandbagging, identify guidance games,
and flag metrics that management started/stopped reporting. Score credibility 1-10."""

GEO_SYSTEM = """You are a Geopolitical Risk Analyst who translates macro events into
specific investable trades. You think in second and third-order effects.
Always identify: direct winners, direct losers, non-obvious second-order plays,
and a specific hedge trade. Use historical precedents for probability weighting."""

def stream_gemini(system, user, key):
    """Streams Gemini 2.5 Flash response — premium feel, faster perceived UX."""
    if not key:
        yield "⚠️ No API key provided."
        return
    try:
        client = genai.Client(api_key=key)
        response = client.models.generate_content_stream(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=system,
                temperature=0.4,
            ),
            contents=user
        )
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        yield f"\n❌ Stream error: {str(e)}"

def send_telegram(text, token, chat_id):
    if not token or not chat_id: return False
    for chunk in [text[i:i+4000] for i in range(0, len(text), 4000)]:
        try:
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id":chat_id,"text":chunk,"parse_mode":"HTML"}, timeout=10)
        except: pass
    return True

# ══════════════════════════════════════════════════════════════════════════════
#  UI HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def key_check():
    if not gemini_key:
        st.warning("👈 Enter your **Gemini API key** in the sidebar.")
        st.info("Get a free key → [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)")
        return False
    return True

def show_result(text, cls=""):
    st.markdown(f'<div class="result-card {cls}">{text}</div>', unsafe_allow_html=True)

def action_buttons(text, prefix="alpha"):
    c1, c2 = st.columns(2)
    with c1:
        fname = f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        st.download_button("⬇️ Download .txt", data=text, file_name=fname, mime="text/plain", use_container_width=True)
    with c2:
        if tg_token and tg_chat:
            if st.button("📱 Send to Telegram", use_container_width=True, key=f"tg_{prefix}_{int(time.time())}"):
                send_telegram(f"🤖 ALPHA MACHINE v3\n{datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n\n{text}", tg_token, tg_chat)
                st.success("✅ Sent!")

# ══════════════════════════════════════════════════════════════════════════════
#  ALL INTELLIGENCE MODE FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

# ── ORIGINAL 5 AGENTS ────────────────────────────────────────────────────────
def _macro_agent(key, macro_data, news):
    return call_gemini("You are a global macro strategist. Think Ray Dalio. Find invisible forces moving markets before the crowd.",
        f"Date:{datetime.now().strftime('%Y-%m-%d')}\nMACRO:{json.dumps({k:{'price':v[0],'chg%':v[1]} for k,v in macro_data.items()},indent=2)}\nNEWS:{json.dumps(news[:10],indent=2)}\n\nFind TOP 3 macro tailwinds creating asymmetric opportunities. For each: theme, assets, timeline, crowding, confidence 1-10, kill risk. Use live web search.", key)

def _sector_agent(key, df_sec, news):
    return call_gemini("You are a sector rotation specialist. Find sectors before ETF inflows show on Bloomberg.",
        f"Date:{datetime.now().strftime('%Y-%m-%d')}\nSECTOR ETF:{df_sec.to_string(index=False) if not df_sec.empty else 'N/A'}\nNEWS:{json.dumps(news[:8],indent=2)}\n\nFind TOP 2 sectors in EARLY accumulation. For each: ETF, theme, why early, macro driver, score 1-10.", key)

def _stocks_agent(key, df_st, news):
    return call_gemini("You are a stock catalyst specialist. Find asymmetric setups where 3+ signals stack.",
        f"Date:{datetime.now().strftime('%Y-%m-%d')}\nSTOCK SIGNALS:{df_st.to_string(index=False) if not df_st.empty else 'N/A'}\nNEWS:{json.dumps(news[:10],indent=2)}\n\nFind TOP 3 stocks with 3+ stacking signals. For each: ticker, signals, catalyst+date, asymmetry score 1-10, horizon.", key)

def _contra_agent(key, df_st, news):
    return call_gemini("You are a contrarian short-seller. Stress-test every bull thesis relentlessly.",
        f"Date:{datetime.now().strftime('%Y-%m-%d')}\nSTOCK DATA:{df_st.to_string(index=False) if not df_st.empty else 'N/A'}\nBEAR NEWS:{json.dumps(news[:8],indent=2)}\n\nStress-test each stock: what's priced in, bear case, kill scenario, crowding 1-10. Verdict: BUY/WATCH/AVOID.", key)

def _thesis_agent(key, macro_r, sector_r, stocks_r, contra_r):
    return call_gemini("You are the CIO of a macro hedge fund. Only surface alpha scoring 7+/10. No fluff.",
        f"""Date:{datetime.now().strftime('%Y-%m-%d')}
MACRO:{macro_r}\nSECTOR:{sector_r}\nSTOCKS:{stocks_r}\nCONTRA:{contra_r}

Synthesize into ASYMMETRIC BET REPORT. Skip AVOID tickers.
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
    macro  = get_macro_prices()
    df_sec = get_sector_table(SECTORS)
    df_st  = get_stock_table(STOCKS)
    nm=get_news("geopolitical risk Federal Reserve inflation 2026",8)
    ns=get_news("sector rotation ETF institutional buying 2026",6)
    nc=get_news("insider buying FDA approval DoD contract earnings 2026",8)
    nb=get_news("overvalued crowded trade short seller 2026",6)
    results = {}
    threads = [
        threading.Thread(target=lambda: results.update({"macro":  _macro_agent(key,macro,nm)})),
        threading.Thread(target=lambda: results.update({"sector": _sector_agent(key,df_sec,ns)})),
        threading.Thread(target=lambda: results.update({"stocks": _stocks_agent(key,df_st,nc)})),
        threading.Thread(target=lambda: results.update({"contra": _contra_agent(key,df_st,nb)})),
    ]
    for t in threads: t.start()
    for t in threads: t.join(timeout=200)
    results["thesis"] = _thesis_agent(key,results.get("macro",""),results.get("sector",""),results.get("stocks",""),results.get("contra",""))
    return results

# ── SUPPLY CHAIN ─────────────────────────────────────────────────────────────
def run_supply_chain(key, target):
    return call_gemini("You are a supply chain intelligence analyst. Map complete supply ecosystems and find hidden asymmetric bets.",
        f"Date:{datetime.now().strftime('%Y-%m-%d')}\nTARGET:{target}\n\nMAP the complete supply chain:\n1. TIER 1 SUPPLIERS (direct, large-cap) — top 5-7 with tickers, what supplied, dependency level\n2. TIER 2 SUPPLIERS (components, mid-cap hidden plays) — 5-7 with tickers, specific component, revenue exposure\n3. TIER 3 RAW MATERIALS — critical inputs, bottlenecks, geographic concentration\n4. PATENT & IP MOAT — who holds critical patents, licensing choke points\n5. TOP 3 ASYMMETRIC PLAYS — obscure/under-followed, catalyst, price target rationale\n6. SUPPLY CHAIN RISKS — geopolitical, concentration, substitution\nSTRICT: End with TICKERS: [all mentioned tickers]", key)

# ── SECTOR DIVE ───────────────────────────────────────────────────────────────
def run_sector_dive(key, sector):
    df_sec = get_sector_table(SECTORS)
    return call_gemini("You are a sector specialist with deep knowledge of industry dynamics, competitive moats, cycle positioning.",
        f"Date:{datetime.now().strftime('%Y-%m-%d')}\nSECTOR:{sector}\nETF DATA:{df_sec.to_string(index=False) if not df_sec.empty else 'N/A'}\n\n1. SECTOR SNAPSHOT — cycle position, ETF signals, institutional positioning\n2. TOP 5 PLAYERS ranked by asymmetry — ticker, why now, valuation vs peers, score 1-10\n3. HIDDEN GEMS sub-$5B — 3 small/mid-cap plays analysts ignore\n4. MACRO TAILWINDS & HEADWINDS\n5. UPCOMING CATALYSTS next 90 days\n6. BEST ASYMMETRIC BET — entry, target, stop, horizon\nSTRICT: End with TICKERS: [all mentioned]", key)

# ── STOCK STRESS TEST ─────────────────────────────────────────────────────────
def run_stock_stress(key, ticker):
    price, chg = get_price_yf(ticker)
    price_str = f"${price} ({chg:+.2f}% today)" if price else "N/A"
    return call_gemini("You are a forensic equity analyst who stress-tests stocks with brutal honesty.",
        f"Date:{datetime.now().strftime('%Y-%m-%d')}\nTICKER:{ticker}\nPRICE:{price_str}\n\n1. BULL CASE 12mo — growth drivers, catalysts, targets: Base/Bull/Ultra-bull\n2. BEAR CASE 12mo — short thesis, valuation flags, downside scenarios\n3. FORENSIC FLAGS — accounting concerns, insider selling, debt structure, customer concentration\n4. ASYMMETRIC PLAY VS SUPPLIERS — Tier 2/3 supplier that's a better bet?\n5. VERDICT — sentiment vs fair value, crowding 1-10, BUY/HOLD/SELL, key assumption to monitor\nSTRICT: End with TICKERS: {ticker}, [SUPPLIER_1], [SUPPLIER_2]", key)

# ── GEO TRADE ────────────────────────────────────────────────────────────────
def run_geo_trade(key, scenario):
    return call_gemini("You are a geopolitical risk analyst specializing in translating macro events into investable trades.",
        f"Date:{datetime.now().strftime('%Y-%m-%d')}\nSCENARIO:{scenario}\n\n1. SCENARIO ANALYSIS — current status, probability, historical precedents\n2. DIRECT WINNERS top 5 — ticker, why, magnitude, timeframe\n3. DIRECT LOSERS top 3 — ticker, exposure, downside\n4. SECOND-ORDER PLAYS (non-obvious) — what market doesn't see yet\n5. HEDGE PLAYS — best hedges against this scenario\n6. HIGHEST ASYMMETRY TRADE — entry, target, stop, catalyst\nSTRICT: End with TICKERS: [all mentioned]", key)

# ── COMMODITY CHAIN ───────────────────────────────────────────────────────────
def run_commodity_chain(key, commodity):
    return call_gemini("You are a commodity markets expert who traces entire value chains.",
        f"Date:{datetime.now().strftime('%Y-%m-%d')}\nCOMMODITY:{commodity}\n\n1. CURRENT MARKET STATE — spot price, trend, supply/demand\n2. UPSTREAM producers — top 5 tickers, production cost, leverage to price\n3. MIDSTREAM refiners/processors — key players, moat, bottlenecks\n4. DOWNSTREAM consumers — top users, price exposure winners/losers\n5. BEST 3 ASYMMETRIC PLAYS — better than commodity ETF, specific catalyst\n6. SUBSTITUTION RISK — what replaces this commodity?\nSTRICT: End with TICKERS: [all mentioned]", key)

# ── PORTFOLIO STRESS ──────────────────────────────────────────────────────────
def run_portfolio_stress(key, holdings):
    return call_gemini("You are a risk manager and portfolio strategist. Stress-test portfolios with brutal honesty.",
        f"Date:{datetime.now().strftime('%Y-%m-%d')}\nPORTFOLIO:{holdings}\n\n1. PORTFOLIO ANALYSIS — sector concentration, factor exposure, correlation risk\n2. SCENARIO STRESS TESTS:\n   a) 2008-style crash (-40%)\n   b) Rate spike +200bps\n   c) Stagflation\n   d) Geopolitical shock\n   e) AI bubble burst\n3. HIGHEST RISK POSITIONS — worst 3 risk/reward right now\n4. GAPS & OPPORTUNITIES — what's missing, what to trim\n5. HEDGING RECOMMENDATIONS — 3 specific cost-effective hedges\n6. VERDICT — health score 1-10, top 3 action items this week", key)

# ── RELATIVE VALUE ────────────────────────────────────────────────────────────
def run_relative_value(key, ta, tb):
    pa,ca = get_price_yf(ta); pb,cb = get_price_yf(tb)
    return call_gemini("You are a fundamental analyst specializing in relative value and pair trade identification.",
        f"Date:{datetime.now().strftime('%Y-%m-%d')}\nCOMPARE:{ta} vs {tb}\n{ta}: ${pa} ({ca:+.2f}%) | {tb}: ${pb} ({cb:+.2f}%)\n\n1. VALUATION TABLE — P/E, Fwd P/E, P/S, EV/EBITDA, PEG (winner each metric)\n2. GROWTH COMPARISON — revenue, EPS, margin trends\n3. MOAT COMPARISON — market share, pricing power, switching costs\n4. BALANCE SHEET — debt, buybacks, capital allocation\n5. CATALYST COMPARISON — next 6 months each\n6. PAIR TRADE — long/short recommendation, entry, target spread, stop\n7. VERDICT — better risk/reward NOW, conviction level, key assumption", key)

# ── ROTATION TIMER ────────────────────────────────────────────────────────────
def run_rotation_timer(key):
    macro=get_macro_prices(); df_sec=get_sector_table(SECTORS)
    return call_gemini("You are a market cycle analyst who identifies economic cycle phase and rotation opportunities.",
        f"Date:{datetime.now().strftime('%Y-%m-%d')}\nMACRO:{json.dumps({k:{'price':v[0],'chg%':v[1]} for k,v in macro.items()},indent=2)}\nSECTOR PERF:{df_sec.to_string(index=False) if not df_sec.empty else 'N/A'}\n\n1. CYCLE POSITION — Early/Mid/Late/Contraction, evidence, confidence\n2. CURRENT SECTOR LEADERSHIP — who's leading/lagging, institutional flow\n3. NEXT ROTATION 0-6mo — what rotates into next, historical pattern\n4. TIMING SIGNALS — 3 specific indicators to confirm/deny rotation\n5. HIGHEST CONVICTION ROTATION TRADE — long/short pair, ETF/stock, entry/target/stop\n6. INTERNATIONAL ROTATION — any country/region offering better positioning?", key)

# ── CATALYST CALENDAR ─────────────────────────────────────────────────────────
def run_catalyst_calendar(key, watchlist):
    return call_gemini("You are an event-driven trading specialist who tracks and ranks catalysts by asymmetric potential.",
        f"Date:{datetime.now().strftime('%Y-%m-%d')}\nWATCHLIST:{watchlist}\n\n1. 90-DAY CATALYST CALENDAR\n   DATE | TICKER | EVENT TYPE | EXPECTED IMPACT | ASYMMETRY SCORE\n2. TOP 5 HIGHEST ASYMMETRY EVENTS next 30 days — what's expected, what's the surprise scenario, how to position\n3. BINARY EVENT PLAYS — FDA/regulatory decisions, earnings where vol is cheap\n4. MACRO CALENDAR — Fed meetings, CPI, jobs reports and watchlist impact\n5. THIS WEEK'S BEST SETUP — single best catalyst trade, entry/target/stop", key)

# ══════ NEW MODES ══════════════════════════════════════════════════════════════

# ── EARNINGS CALL ANALYZER ───────────────────────────────────────────────────
def run_earnings_analyzer(key, ticker):
    return call_gemini("You are a forensic earnings analyst. You read between the lines of management language, detect tone shifts, and find what executives are hiding.",
        f"""Date: {datetime.now().strftime('%Y-%m-%d')}
TICKER: {ticker.upper()}

Use live web search to find the MOST RECENT earnings call transcript, earnings results, and analyst commentary for {ticker}.

1. 📊 HEADLINE NUMBERS vs EXPECTATIONS
   - EPS: actual vs estimate vs prior quarter
   - Revenue: actual vs estimate vs guidance
   - Key metrics: margins, bookings, whatever is sector-specific
   - Beat/miss magnitude and quality

2. 🎭 MANAGEMENT TONE ANALYSIS
   - Tone vs PRIOR QUARTER: more confident / more hedged / same?
   - Language used around guidance: vague or specific?
   - Words that appear MORE vs LESS vs prior call (signals shift)
   - Are they front-running bad news? ("challenging", "headwinds", "transitional period")

3. 🔍 WHAT THEY'RE HIDING (read between the lines)
   - Metrics they STOPPED reporting or mentioned less
   - Metrics they suddenly started highlighting (distractions?)
   - Guidance range width: wide range = uncertainty, narrow = confidence
   - Any analyst questions they dodged or gave non-answers to

4. 💡 ANALYST REACTION
   - What did sell-side analysts say post-call?
   - Any target price changes and direction?
   - Consensus estimate revisions

5. 🎯 TRADING IMPLICATION
   - Is the stock pricing in too much optimism or too much pessimism?
   - Next quarter setup: what to expect based on tone
   - Entry/exit signal based on earnings read
   - Score: Management Credibility 1-10 | Earnings Quality 1-10

6. ⚡ ASYMMETRIC ANGLE
   - Any supply chain beneficiaries or victims mentioned in the call?
   - Competitor implications (if {ticker} wins, who loses?)""", key)

# ── SEC FILING SCANNER ────────────────────────────────────────────────────────
def run_sec_scanner(key, ticker):
    filings = get_sec_filings(ticker)
    filing_str = json.dumps(filings[:8], indent=2) if filings else "Will search live via web"
    return call_gemini("You are an SEC filing forensics expert. You detect insider activity, material events, and regulatory risks from filings.",
        f"""Date: {datetime.now().strftime('%Y-%m-%d')}
TICKER: {ticker.upper()}
RECENT FILINGS FOUND: {filing_str}

Use live web search to find ALL recent SEC filings for {ticker} (last 90 days). Analyze:

1. 📋 FORM 4 — INSIDER TRANSACTIONS (last 90 days)
   For each significant transaction:
   - Insider name and title
   - Buy or sell? Shares and value
   - Open market purchase (strong signal) vs option exercise (weak signal)
   - Cluster buying: multiple insiders buying = VERY bullish
   - Pattern: first buy in 6 months? Accelerating sales?

2. 📢 8-K MATERIAL EVENTS (last 90 days)
   - Any material contracts, partnerships, executive changes?
   - Financing events: dilution risk or buyback announcements?
   - Regulatory decisions, FDA results, government contracts
   - Flag anything that market may not have fully priced in

3. 📊 10-Q / 10-K FLAGS
   - Any new risk factors added vs prior filing?
   - Revenue recognition policy changes
   - Deferred revenue trend (leading indicator)
   - Cash burn rate vs cash on hand (runway months)
   - Related party transactions

4. 🚨 RED FLAGS (if any)
   - Going concern language
   - Auditor change
   - Restatements or material weaknesses
   - Executive departures cluster

5. 🟢 BULLISH SIGNALS (if any)
   - Insider cluster buying
   - Share buyback authorization
   - Large contract awards in 8-K
   - Debt paydown

6. 🎯 NET SIGNAL
   - Overall insider sentiment: BULLISH / NEUTRAL / BEARISH
   - Most important filing to read
   - Trading implication: what do the filings say that price doesn't reflect?""", key)

# ── OPTIONS FLOW WATCHER ──────────────────────────────────────────────────────
def run_options_flow(key, ticker):
    price, chg = get_price_yf(ticker)
    price_str = f"${price} ({chg:+.2f}%)" if price else "N/A"
    return call_gemini("You are an options flow expert and derivatives specialist. You interpret unusual options activity as smart money signals.",
        f"""Date: {datetime.now().strftime('%Y-%m-%d')}
TICKER: {ticker.upper()}
CURRENT PRICE: {price_str}

Use live web search to find unusual options activity, open interest changes, implied volatility data for {ticker}.
Search for: "{ticker} unusual options activity", "{ticker} options flow", "{ticker} implied volatility", "{ticker} put call ratio"

1. 📊 CURRENT OPTIONS LANDSCAPE
   - Put/Call ratio (current vs 30-day average)
   - Implied Volatility (IV) vs Historical Volatility (HV)
   - IV percentile (where is IV vs its 1-year range?)
   - Term structure: is near-term IV elevated vs long-dated?

2. ⚡ UNUSUAL ACTIVITY DETECTED (last 5 trading days)
   For each unusual trade:
   - Date, Strike, Expiry, Call/Put
   - Size (contracts) vs typical daily volume
   - Premium paid (expensive = high conviction)
   - Bullish or bearish directional bet?
   - Block trade vs sweep (institutional vs retail)

3. 🧠 SMART MONEY INTERPRETATION
   - What is "smart money" positioning for?
   - Are they buying protection (defensive) or making directional bets?
   - Any catalyst hedging visible (earnings, FDA, event)?
   - Dark pool activity if detectable

4. 📈 VOLATILITY OPPORTUNITY
   - Is IV cheap or expensive vs expected move?
   - Best options strategy given current IV environment:
     a) If bullish: buy calls or bull call spread?
     b) If bearish: buy puts or bear put spread?
     c) If neutral: sell premium (iron condor/strangle)?
   - Specific trade structure: strike, expiry, target, stop

5. 🎯 OPTIONS SIGNAL VERDICT
   - Net signal: BULLISH FLOW / BEARISH FLOW / MIXED / HEDGING ACTIVITY
   - Conviction level 1-10
   - Key expiry dates to watch
   - How options positioning compares to stock price action""", key)

# ── 13F INSTITUTIONAL TRACKER ─────────────────────────────────────────────────
def run_institutional_tracker(key, ticker_or_manager):
    is_manager = any(x in ticker_or_manager.lower() for x in
                     ["soros","einhorn","ackman","burry","dalio","druckenmiller","tepper","griffin","cohen","baupost"])
    if is_manager:
        prompt = f"""Date: {datetime.now().strftime('%Y-%m-%d')}
MANAGER: {ticker_or_manager}

Use live web search to find the LATEST 13F filing for {ticker_or_manager}'s fund.

1. 📋 LATEST 13F SNAPSHOT
   - Filing date and quarter covered
   - Total portfolio value
   - Number of positions

2. 🆕 NEW POSITIONS (bought this quarter for first time)
   For each: ticker, size, % of portfolio, why they might like it

3. 📈 INCREASED POSITIONS (added to existing)
   For each: ticker, % increase, new total size

4. 📉 REDUCED POSITIONS (trimmed)
   For each: ticker, % reduction, remaining size

5. ❌ EXITED POSITIONS (sold completely)
   For each: ticker, what they sold and what that might signal

6. 💎 HIGHEST CONVICTION PLAYS
   - Top 5 holdings by portfolio weight
   - Any single position >10% of portfolio?

7. 🎯 ACTIONABLE INSIGHT
   - What is this manager betting on right now?
   - Any contrarian angles vs consensus?
   - Best copycat trade from this 13F
   - Important caveat: 13Fs are 45-day delayed"""
    else:
        prompt = f"""Date: {datetime.now().strftime('%Y-%m-%d')}
TICKER: {ticker_or_manager.upper()}

Use live web search to find institutional ownership data for {ticker_or_manager}.

1. 📊 OWNERSHIP OVERVIEW
   - Total institutional ownership %
   - Change in institutional ownership last quarter
   - Insider ownership %

2. 🏦 TOP INSTITUTIONAL HOLDERS
   For each top 10: fund name, shares held, % of float, quarter change

3. 🆕 NEW INSTITUTIONAL BUYERS (this quarter)
   - Who just initiated positions?
   - Are any smart-money names in the new buyer list?

4. 📤 INSTITUTIONAL SELLERS
   - Who's exiting or reducing?
   - Any concerning large seller patterns?

5. 🎯 SMART MONEY SIGNAL
   - Is institutional ownership increasing or decreasing trend?
   - Quality of holders: index funds (neutral) vs active managers (signal)
   - Any hedge fund cluster buying?
   - Net signal: ACCUMULATION / DISTRIBUTION / STABLE
   - Trading implication"""
    return call_gemini("You are a 13F filings analyst and institutional ownership expert. You track smart money positioning.", prompt, key)

# ── SMART WATCHDOG ────────────────────────────────────────────────────────────
def run_watchdog_scan(key, watchlist, triggers):
    df_st = get_stock_table(watchlist)
    alerts = []
    for _, row in df_st.iterrows():
        ticker = row.get("Ticker","")
        rsi    = row.get("RSI","—")
        m1     = row.get("1M%","—")
        price  = row.get("Price","—")
        w52h   = row.get("52W Hi","—")
        triggered = []
        try:
            if "RSI < 30" in triggers and isinstance(rsi,(int,float)) and rsi < 30:
                triggered.append(f"🟢 RSI={rsi} (OVERSOLD)")
            if "RSI > 75" in triggers and isinstance(rsi,(int,float)) and rsi > 75:
                triggered.append(f"🔴 RSI={rsi} (OVERBOUGHT)")
            if "Drop > 8% in 1M" in triggers and isinstance(m1,(int,float)) and m1 < -8:
                triggered.append(f"📉 -1M={m1}% (DIP ALERT)")
            if "52W High Break" in triggers and isinstance(price,(int,float)) and isinstance(w52h,(int,float)) and w52h>0 and price>=w52h*0.98:
                triggered.append(f"🚀 Near 52W High (${price} vs ${w52h})")
            if "Momentum >15%" in triggers and isinstance(m1,(int,float)) and m1 > 15:
                triggered.append(f"⚡ Momentum {m1}%")
        except: pass
        if triggered:
            alerts.append({"ticker":ticker,"price":price,"triggers":triggered})

    alert_str = "\n".join([f"{a['ticker']} @ ${a['price']}: {', '.join(a['triggers'])}" for a in alerts]) if alerts else "No triggers fired on current data."
    ai_analysis = call_gemini("You are an alert triage specialist. Evaluate fired alerts and rank by urgency and opportunity.",
        f"Date:{datetime.now().strftime('%Y-%m-%d')}\nFIRED ALERTS:\n{alert_str}\n\nFor each triggered alert:\n1. Is this signal ACTIONABLE right now or a false positive?\n2. What does live news say about this ticker?\n3. Urgency: ACT NOW / WATCH CLOSELY / LOW PRIORITY\n4. Specific next step\n\nEnd with TOP PRIORITY ALERT and exactly what to do.", key)
    return alerts, ai_analysis

# ── BACKTESTER ────────────────────────────────────────────────────────────────
def run_backtester(key, thesis, ticker):
    price, _ = get_price_yf(ticker)
    return call_gemini("You are a quantitative analyst and market historian. Backtest investment theses against historical market regimes.",
        f"""Date: {datetime.now().strftime('%Y-%m-%d')}
TICKER: {ticker.upper()}
CURRENT PRICE: ${price if price else 'N/A'}
INVESTMENT THESIS: {thesis}

Use live web search to get historical data and context. Run comprehensive BACKTEST:

1. 📊 THESIS SUMMARY
   - Core assumption(s) of this thesis
   - What has to go RIGHT for this to work?
   - What has to go WRONG to break it?

2. 🕐 HISTORICAL REGIME ANALYSIS
   How would this thesis have performed in each regime?

   a) 2008 FINANCIAL CRISIS (Sep 2008 - Mar 2009)
      - Was {ticker} (or equivalent) affected? Drawdown?
      - Did the thesis thesis hold or break?
      
   b) 2020 COVID CRASH (Feb-Mar 2020)
      - Max drawdown for {ticker}?
      - Recovery timeline?
      - Thesis validity during this regime?

   c) 2022 RATE HIKE CYCLE (Jan-Dec 2022)
      - {ticker} performance during rising rates?
      - Thesis impact of valuation compression?

   d) 2023-2024 AI BULL MARKET
      - Did {ticker} benefit or miss the rally?
      - Thesis performance in risk-on environment?

3. 📈 PERFORMANCE METRICS (estimated)
   - Best case scenario return (if thesis plays out perfectly)
   - Base case return (most likely outcome)
   - Worst case drawdown (thesis breaks)
   - Estimated Sharpe ratio quality

4. 🔑 THESIS KILLERS (ranked by probability)
   - #1 most likely thesis breaker
   - #2 tail risk
   - #3 black swan scenario

5. ✅ HISTORICAL VERDICT
   - Has a similar thesis worked before? When and why?
   - What's the historical base rate of success for this type of bet?
   - Confidence level: HIGH / MEDIUM / LOW based on historical evidence

6. 💎 OPTIMAL POSITION SIZING SUGGESTION
   - Based on historical volatility and thesis conviction
   - Stop loss level that would invalidate the thesis
   - Position sizing: % of portfolio based on max drawdown tolerance""", key)

# ── AUTO NEWSLETTER ───────────────────────────────────────────────────────────
def run_newsletter(key, scan_results, author_name, newsletter_name):
    thesis = scan_results.get("thesis","") if scan_results else ""
    macro  = scan_results.get("macro","")  if scan_results else ""
    return call_gemini("You are a professional financial newsletter writer. You write like the best of Substack — sharp, authoritative, contrarian, and actionable.",
        f"""Date: {datetime.now().strftime('%Y-%m-%d')}
NEWSLETTER: {newsletter_name}
AUTHOR: {author_name}
ALPHA SCAN DATA: {thesis[:2000] if thesis else "No scan data — use live web search for current market context"}
MACRO DATA: {macro[:1000] if macro else ""}

Write a FULL WEEKLY NEWSLETTER EDITION. Use live web search for current market data.

FORMAT:

---
{newsletter_name.upper()}
{datetime.now().strftime('%B %d, %Y')} | Weekly Intelligence Brief
By {author_name}
---

## THIS WEEK'S MACRO BACKDROP
[2-3 punchy paragraphs on current market regime, key events this week, what changed]

## THE ASYMMETRIC OPPORTUNITY I'M WATCHING
[Deep dive on ONE high-conviction bet — thesis, catalysts, entry, target, risk. 300-400 words]

## SECTOR ROTATION SIGNAL
[Which sector is rotating in/out and why — 150 words with specific ETF ticker]

## CHART THAT MATTERS THIS WEEK
[Describe the most important chart setup in words — RSI, breakout, support level, etc]

## WHAT I'M READING
[3 bullet points: top financial articles/reports worth reading this week, with brief takeaway each]

## PORTFOLIO MOVES
[What a rational portfolio manager would add/remove/hold right now — 2-3 bullets]

## KEY DATES NEXT WEEK
[Fed meetings, key earnings, economic data releases — bullet format]

## ONE-LINE MARKET TAKE
[A single memorable, quotable sentence summarizing the current opportunity]

---
[Footer: Disclaimer, unsubscribe link placeholder, social media handles]
---

Keep total length: 600-900 words. Tone: confident, data-driven, slightly contrarian, no fluff.""", key)

# ══════════════════════════════════════════════════════════════════════════════
#  TABS
# ══════════════════════════════════════════════════════════════════════════════
tabs = st.tabs([
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
    "🧠 Earnings",
    "📜 SEC Filings",
    "⚡ Options Flow",
    "🏦 13F Tracker",
    "🔔 Watchdog",
    "📊 Backtest",
    "💌 Newsletter",
    "🏛️ Macro Regime",
    "📢 Monetization",
    "ℹ️ Info",
])
(tab_dash, tab_scan, tab_supply, tab_sector, tab_stock, tab_geo,
 tab_commodity, tab_port, tab_compare, tab_rotation, tab_calendar,
 tab_earnings, tab_sec, tab_options, tab_inst, tab_watchdog,
 tab_backtest, tab_newsletter, tab_macro_regime, tab_monetize, tab_info) = tabs

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
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
                st.markdown(f'<div class="mbox"><span class="mlbl">{label}</span><span class="mval">{fmt}</span><span class="{cls}">{sgn}{chg:.2f}%</span></div>', unsafe_allow_html=True)
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
                if isinstance(v,(int,float)): return "color:#10b981;font-weight:600" if v>0 else "color:#ef4444;font-weight:600"
                return ""
            st.dataframe(df_sec.style.map(csec, subset=["1M%","1W%"]), width="stretch", hide_index=True, height=360)
        else:
            st.warning("Sector data temporarily unavailable")
    with right:
        st.markdown('<p class="shdr">🎯 Watchlist Signals</p>', unsafe_allow_html=True)
        with st.spinner(""):
            df_st = get_stock_table(STOCKS)
        if not df_st.empty:
            def crsi(v):
                if isinstance(v,(int,float)):
                    if v<35: return "color:#10b981;font-weight:700"
                    if v>70: return "color:#ef4444;font-weight:700"
                return ""
            def cm1(v):
                if isinstance(v,(int,float)): return "color:#10b981" if v>0 else "color:#ef4444"
                return ""
            st.dataframe(df_st.style.map(crsi,subset=["RSI"]).map(cm1,subset=["1M%"]), width="stretch", hide_index=True, height=360)
        else:
            st.warning("Stock data temporarily unavailable")

    st.markdown('<p class="shdr">📰 Market Intelligence Feed</p>', unsafe_allow_html=True)
    n1, n2 = st.columns(2)
    with n1:
        st.markdown("**📈 Markets & Alpha**")
        for h in get_news("asymmetric investment opportunity alpha 2026",5):
            st.markdown(f'<div class="news-item"><span class="news-title">{h["title"]}</span><br><span style="color:#374151;font-size:0.72rem">{h["source"]}</span></div>', unsafe_allow_html=True)
    with n2:
        st.markdown("**🌍 Geopolitics & Policy**")
        for h in get_news("geopolitical risk Federal Reserve tariff 2026",5):
            st.markdown(f'<div class="news-item"><span class="news-title">{h["title"]}</span><br><span style="color:#374151;font-size:0.72rem">{h["source"]}</span></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ALPHA SCAN
# ══════════════════════════════════════════════════════════════════════════════
with tab_scan:
    st.markdown("### 🎯 Asymmetric Bet Scanner — 5 Parallel Agents")
    st.markdown("Macro Scout · Sector Analyst · Stock Sniper · Contrarian · CIO Synthesis — all run simultaneously")
    if key_check():
        if st.button("🚀 Run Full Alpha Scan", type="primary"):
            prog = st.progress(0, text="Fetching market data...")
            with st.spinner(""): df_stocks=get_stock_table(STOCKS); df_sectors=get_sector_table(SECTORS)
            prog.progress(15, text="4 agents running in parallel (~2-3 min)...")
            stat_cols = st.columns(4)
            for col,lbl in zip(stat_cols,["🌍 Macro","🔄 Sector","🎯 Stocks","⚠️ Contra"]): col.info(f"{lbl}⏳")
            try:
                results = run_asymmetric_scan(gemini_key)
                prog.progress(85, text="CIO synthesizing...")
                for col,lbl,k in zip(stat_cols,["🌍 Macro","🔄 Sector","🎯 Stocks","⚠️ Contra"],["macro","sector","stocks","contra"]):
                    val = results.get(k,"")
                    col.success(f"{lbl} ✅") if not val.startswith("[API") else col.error(f"{lbl} ❌")
                prog.progress(100, text="✅ Complete!")
                st.markdown("## 🏆 Final Alpha Report")
                final = results.get("thesis","[No output]")
                show_result(final)
                action_buttons(f"🤖 ALPHA MACHINE v3\n{datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n\n{final}", "alpha_scan")
                # Store in session state for newsletter
                st.session_state["last_scan"] = results
                with st.expander("🌍 Macro details"): st.write(results.get("macro",""))
                with st.expander("🔄 Sector details"): st.write(results.get("sector",""))
                with st.expander("🎯 Stock Sniper details"): st.write(results.get("stocks",""))
                with st.expander("⚠️ Contrarian details"): st.write(results.get("contra",""))
            except Exception as e:
                prog.empty(); st.error(f"❌ Scan failed: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# SUPPLY CHAIN
# ══════════════════════════════════════════════════════════════════════════════
with tab_supply:
    st.markdown("### 🔗 Supply Chain Forensic Mapper")
    st.markdown("Map the **Nervous System** of any sector — find the one company the giants cannot live without.")
    c1,c2 = st.columns([3,1])
    with c1: supply_target = st.text_input("Company or Sector", placeholder="NVDA · Tesla · EUV Lithography · Solid State Batteries", label_visibility="collapsed")
    with c2: supply_run = st.button("🔍 Map Chain", type="primary")
    st.caption("Examples: `NVDA` `TSLA` `ASML` `Lithium batteries` `Semiconductor fab` `Defense electronics`")
    if supply_run:
        if key_check() and supply_target:
            with st.status(f"🔗 Mapping {supply_target} Nervous System...", expanded=True) as status:
                st.write("Identifying Tier 1 direct suppliers...")
                st.write("Scanning for Tier 2 hidden plays...")
                st.write("Locating IP/bottleneck owners...")
                out = st.empty()
                full = ""
                for chunk in stream_gemini(SUPPLY_SYSTEM,
                    f"Date:{datetime.now().strftime('%Y-%m-%d')}\nTARGET:{supply_target}\n\nMAP the complete supply chain ecosystem:\n1. TIER 1 SUPPLIERS (direct, large-cap) — top 5-7 with **$TICKER**, what supplied, dependency level\n2. TIER 2 SUPPLIERS (components, mid-cap HIDDEN PLAYS) — 5-7 with **$TICKER**, specific component, revenue exposure\n3. TIER 3 RAW MATERIALS — critical inputs, bottlenecks, geographic concentration\n4. THE BOTTLENECK OWNER — who has the IP/process the giants cannot bypass?\n5. TOP 3 ASYMMETRIC PLAYS — obscure/under-followed **$TICKER** with catalyst\n6. SUPPLY CHAIN RISKS — geopolitical, concentration, substitution\nSTRICT: End with TICKERS: [all mentioned tickers]",
                    gemini_key):
                    full += chunk
                    out.markdown(full)
                status.update(label="✅ Ecosystem Mapped", state="complete")
            st.session_state["last_research"] = full
            action_buttons(full, "supply_chain")

# ══════════════════════════════════════════════════════════════════════════════
# SECTOR DIVE
# ══════════════════════════════════════════════════════════════════════════════
with tab_sector:
    st.markdown("### 🏭 Sector Deep Dive")
    st.markdown("Cycle positioning · Hidden gems · Institutional flow · Best asymmetric bet")
    c1,c2 = st.columns([3,1])
    with c1: sector_target = st.text_input("Sector", placeholder="Defense · Biotech · Clean Energy · Semiconductors", label_visibility="collapsed")
    with c2: sector_run = st.button("🔍 Dive Deep", type="primary")
    if sector_run:
        if key_check() and sector_target:
            with st.spinner(f"Analyzing {sector_target}..."): result=run_sector_dive(gemini_key,sector_target)
            show_result(result,"sector"); action_buttons(result,"sector_dive")

# ══════════════════════════════════════════════════════════════════════════════
# STOCK STRESS TEST
# ══════════════════════════════════════════════════════════════════════════════
with tab_stock:
    st.markdown("### 🔬 Single Stock Stress Test")
    st.markdown("Forensic bull/bear · Accounting flags · Insider trends · Supplier alternatives")
    c1,c2 = st.columns([3,1])
    with c1: stress_ticker = st.text_input("Ticker", placeholder="NVDA · PLTR · TSLA · RKLB", label_visibility="collapsed")
    with c2: stress_run = st.button("🔬 Stress Test", type="primary")
    if stress_run:
        if key_check() and stress_ticker:
            t = stress_ticker.strip().upper().replace("$","")
            with st.spinner(f"Stress testing {t}..."): result=run_stock_stress(gemini_key,t)
            show_result(result,"stress"); action_buttons(result,f"stress_{t}")

# ══════════════════════════════════════════════════════════════════════════════
# GEO TRADE
# ══════════════════════════════════════════════════════════════════════════════
with tab_geo:
    st.markdown("### 🌍 Geopolitical Trade Finder")
    st.markdown("Translate any geopolitical scenario into direct winners, losers, second-order plays, and hedges.")
    c1,c2 = st.columns([3,1])
    with c1: geo_scenario = st.text_input("Scenario", placeholder="Taiwan conflict · US-China trade war · Middle East escalation", label_visibility="collapsed")
    with c2: geo_run = st.button("🌍 Find Trades", type="primary")
    if geo_run:
        if key_check() and geo_scenario:
            with st.spinner(f"Mapping trades for: {geo_scenario}..."): result=run_geo_trade(gemini_key,geo_scenario)
            show_result(result,"geo"); action_buttons(result,"geo_trade")

# ══════════════════════════════════════════════════════════════════════════════
# COMMODITY CHAIN
# ══════════════════════════════════════════════════════════════════════════════
with tab_commodity:
    st.markdown("### ⛏️ Commodity Chain Tracer")
    st.markdown("Full upstream/downstream chain — find the bottleneck, the moat, and the best asymmetric play.")
    c1,c2 = st.columns([3,1])
    with c1: commodity_target = st.text_input("Commodity", placeholder="Lithium · Uranium · Copper · Rare Earth · Natural Gas", label_visibility="collapsed")
    with c2: commodity_run = st.button("⛏️ Trace", type="primary")
    if commodity_run:
        if key_check() and commodity_target:
            with st.spinner(f"Tracing {commodity_target} chain..."): result=run_commodity_chain(gemini_key,commodity_target)
            show_result(result,"commodity"); action_buttons(result,"commodity")

# ══════════════════════════════════════════════════════════════════════════════
# PORTFOLIO STRESS
# ══════════════════════════════════════════════════════════════════════════════
with tab_port:
    st.markdown("### ⚖️ Portfolio Stress Tester")
    st.markdown("5-scenario stress test · Concentration risk · Hedging recommendations")
    holdings_input = st.text_area("Your Holdings", placeholder="NVDA 15%, AAPL 10%, MSFT 10%, PLTR 8%, Cash 20%, BTC 5%...\nOr just tickers: NVDA, AAPL, MSFT", height=100)
    if st.button("⚖️ Stress Test Portfolio", type="primary"):
        if key_check() and holdings_input.strip():
            with st.spinner("Running 5-scenario stress test..."): result=run_portfolio_stress(gemini_key,holdings_input)
            show_result(result,"portfolio"); action_buttons(result,"portfolio")

# ══════════════════════════════════════════════════════════════════════════════
# COMPARE
# ══════════════════════════════════════════════════════════════════════════════
with tab_compare:
    st.markdown("### 🆚 Relative Value Comparator")
    st.markdown("Head-to-head forensic analysis · Pair trade setup with entry/stop/target")
    ca,cv,cb = st.columns([2,0.4,2])
    with ca: ticker_a = st.text_input("Ticker A", placeholder="NVDA", key="ta")
    with cv: st.markdown("<br><br>**vs**", unsafe_allow_html=True)
    with cb: ticker_b = st.text_input("Ticker B", placeholder="AMD", key="tb")
    if st.button("🆚 Compare", type="primary"):
        if key_check() and ticker_a and ticker_b:
            ta,tb = ticker_a.strip().upper(),ticker_b.strip().upper()
            with st.spinner(f"Comparing {ta} vs {tb}..."): result=run_relative_value(gemini_key,ta,tb)
            show_result(result,"compare"); action_buttons(result,f"compare_{ta}_{tb}")

# ══════════════════════════════════════════════════════════════════════════════
# ROTATION
# ══════════════════════════════════════════════════════════════════════════════
with tab_rotation:
    st.markdown("### 🔄 Sector Rotation Timer")
    st.markdown("Identify cycle phase · What rotates next · Highest conviction rotation trade")
    if key_check():
        if st.button("🔄 Analyze Current Rotation", type="primary"):
            with st.spinner("Analyzing economic cycle..."): result=run_rotation_timer(gemini_key)
            show_result(result,"rotation"); action_buttons(result,"rotation")

# ══════════════════════════════════════════════════════════════════════════════
# CATALYST CALENDAR
# ══════════════════════════════════════════════════════════════════════════════
with tab_calendar:
    st.markdown("### 📅 Catalyst Calendar")
    st.markdown("90-day event calendar ranked by asymmetric potential · This week's best setup")
    watchlist_input = st.text_input("Watchlist", value=",".join(STOCKS[:8]))
    if st.button("📅 Generate Calendar", type="primary"):
        if key_check() and watchlist_input.strip():
            with st.spinner("Scanning for catalysts..."): result=run_catalyst_calendar(gemini_key,watchlist_input)
            show_result(result,"catalyst"); action_buttons(result,"catalyst_calendar")

# ══════════════════════════════════════════════════════════════════════════════
# EARNINGS ANALYZER (NEW)
# ══════════════════════════════════════════════════════════════════════════════
with tab_earnings:
    st.markdown("### 🧠 Earnings Call Analyzer")
    st.markdown("Detect management tone shifts · Find what the CEO is hiding · Compare vs prior quarter · Trading implication")
    c1,c2 = st.columns([3,1])
    with c1: earnings_ticker = st.text_input("Stock Ticker", placeholder="NVDA · AAPL · MSFT · AMZN", label_visibility="collapsed", key="earnings_t")
    with c2: earnings_run = st.button("🧠 Analyze Call", type="primary")
    st.caption("AI uses live web search to find latest earnings transcript, results, and analyst reactions.")
    if earnings_run:
        if key_check() and earnings_ticker:
            t = earnings_ticker.strip().upper().replace("$","")
            with st.spinner(f"Analyzing {t} earnings call..."): result=run_earnings_analyzer(gemini_key,t)
            show_result(result,"earnings"); action_buttons(result,f"earnings_{t}")

# ══════════════════════════════════════════════════════════════════════════════
# SEC FILING SCANNER (NEW)
# ══════════════════════════════════════════════════════════════════════════════
with tab_sec:
    st.markdown("### 📜 SEC Filing Scanner")
    st.markdown("Form 4 insider transactions · 8-K material events · 10-Q forensic flags · Red flags & bullish signals")
    c1,c2 = st.columns([3,1])
    with c1: sec_ticker = st.text_input("Stock Ticker", placeholder="PLTR · NVDA · TSLA · RKLB", label_visibility="collapsed", key="sec_t")
    with c2: sec_run = st.button("📜 Scan Filings", type="primary")
    st.caption("Scans EDGAR for Form 4 (insider buys/sells), 8-K (material events), 10-Q flags from last 90 days.")
    if sec_run:
        if key_check() and sec_ticker:
            t = sec_ticker.strip().upper().replace("$","")
            with st.spinner(f"Scanning SEC filings for {t}..."): result=run_sec_scanner(gemini_key,t)
            show_result(result,"sec"); action_buttons(result,f"sec_{t}")

# ══════════════════════════════════════════════════════════════════════════════
# OPTIONS FLOW (NEW)
# ══════════════════════════════════════════════════════════════════════════════
with tab_options:
    st.markdown("### ⚡ Options Flow Watcher")
    st.markdown("Unusual options activity · Smart money positioning · IV vs HV analysis · Optimal options strategy")
    c1,c2 = st.columns([3,1])
    with c1: options_ticker = st.text_input("Stock Ticker", placeholder="NVDA · SPY · TSLA · PLTR", label_visibility="collapsed", key="opt_t")
    with c2: options_run = st.button("⚡ Scan Flow", type="primary")
    st.caption("Uses live web search to find unusual options activity, IV data, put/call ratios, and smart money positioning.")
    if options_run:
        if key_check() and options_ticker:
            t = options_ticker.strip().upper().replace("$","")
            with st.spinner(f"Scanning options flow for {t}..."): result=run_options_flow(gemini_key,t)
            show_result(result,"options"); action_buttons(result,f"options_{t}")

# ══════════════════════════════════════════════════════════════════════════════
# 13F INSTITUTIONAL TRACKER (NEW)
# ══════════════════════════════════════════════════════════════════════════════
with tab_inst:
    st.markdown("### 🏦 13F Institutional Tracker")
    st.markdown("Track smart money positioning via 13F filings. Enter a **stock ticker** OR a **fund manager name**.")
    c1,c2 = st.columns([3,1])
    with c1: inst_input = st.text_input("Ticker or Manager", placeholder="NVDA  ·  Soros  ·  Ackman  ·  Burry  ·  Druckenmiller", label_visibility="collapsed", key="inst_t")
    with c2: inst_run = st.button("🏦 Track", type="primary")
    st.caption("**Ticker** → who owns it, who bought/sold this quarter. **Manager name** → their full 13F portfolio changes.")
    if inst_run:
        if key_check() and inst_input:
            with st.spinner(f"Tracking 13F data for {inst_input}..."): result=run_institutional_tracker(gemini_key,inst_input.strip())
            show_result(result,"inst"); action_buttons(result,f"13f_{inst_input.strip()}")

# ══════════════════════════════════════════════════════════════════════════════
# SMART WATCHDOG (NEW)
# ══════════════════════════════════════════════════════════════════════════════
with tab_watchdog:
    st.markdown("### 🔔 Smart Watchdog — Custom Alert Monitor")
    st.markdown("Set your triggers. AI monitors your watchlist, fires only when YOUR conditions are met, and explains why each alert matters.")

    c1,c2 = st.columns([2,1])
    with c1:
        watchdog_list = st.text_input("Watchlist to Monitor", value=",".join(STOCKS))
    with c2:
        triggers = st.multiselect("Alert Triggers",
            ["RSI < 30", "RSI > 75", "Drop > 8% in 1M", "52W High Break", "Momentum >15%"],
            default=["RSI < 30", "Drop > 8% in 1M"])

    watchdog_run = st.button("🔔 Run Watchdog Scan", type="primary")

    if watchdog_run:
        if key_check():
            tickers_list = [t.strip() for t in watchdog_list.split(",") if t.strip()]
            if not tickers_list: st.warning("Add tickers to monitor")
            else:
                with st.spinner("Scanning watchlist against your triggers..."):
                    alerts, ai_analysis = run_watchdog_scan(gemini_key, tickers_list, triggers)

                if alerts:
                    st.markdown(f"### 🚨 {len(alerts)} Alert(s) Fired")
                    for a in alerts:
                        triggers_str = " · ".join(a["triggers"])
                        st.markdown(f'<div class="alert-box"><strong>{a["ticker"]}</strong> @ ${a["price"]} — {triggers_str}</div>', unsafe_allow_html=True)
                    st.markdown("### 🧠 AI Triage")
                    show_result(ai_analysis, "watchdog")

                    # Auto-send to Telegram if configured
                    if tg_token and tg_chat:
                        alert_msg = f"🔔 WATCHDOG ALERT\n{datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n\n"
                        alert_msg += "\n".join([f"• {a['ticker']} @ ${a['price']}: {', '.join(a['triggers'])}" for a in alerts])
                        alert_msg += f"\n\n{ai_analysis[:1500]}"
                        send_telegram(alert_msg, tg_token, tg_chat)
                        st.success("✅ Alerts auto-sent to Telegram!")

                    action_buttons(ai_analysis, "watchdog")
                else:
                    st.markdown('<div class="warn-box">✅ No triggers fired on current data. All clear.</div>', unsafe_allow_html=True)
                    st.info(f"Monitored {len(tickers_list)} tickers against {len(triggers)} trigger(s). Nothing crossed threshold.")

# ══════════════════════════════════════════════════════════════════════════════
# BACKTESTER (NEW)
# ══════════════════════════════════════════════════════════════════════════════
with tab_backtest:
    st.markdown("### 📊 Thesis Backtester")
    st.markdown("Test any investment thesis against 2008, 2020, 2022, and 2024 market regimes. Proof of concept before risking capital.")

    c1,c2 = st.columns([2,1])
    with c1:
        backtest_thesis = st.text_area("Your Investment Thesis",
            placeholder="e.g. PLTR is undervalued due to AI Government contract tailwind and strong insider buying...\ne.g. Uranium miners will re-rate as nuclear energy demand surges from data centers...",
            height=100)
    with c2:
        backtest_ticker = st.text_input("Primary Ticker", placeholder="PLTR · NVDA · CCJ · RKLB", key="bt_t")
        backtest_run = st.button("📊 Backtest Thesis", type="primary")

    if backtest_run:
        if key_check() and backtest_thesis and backtest_ticker:
            t = backtest_ticker.strip().upper().replace("$","")
            with st.spinner(f"Backtesting thesis across 4 market regimes..."): result=run_backtester(gemini_key,backtest_thesis,t)
            show_result(result,"backtest"); action_buttons(result,f"backtest_{t}")

# ══════════════════════════════════════════════════════════════════════════════
# NEWSLETTER GENERATOR (NEW)
# ══════════════════════════════════════════════════════════════════════════════
with tab_newsletter:
    st.markdown("### 💌 Auto Newsletter Generator")
    st.markdown("Generate a full weekly financial newsletter from your alpha scan results. Ready to paste into Substack/Beehiiv.")

    c1,c2 = st.columns(2)
    with c1:
        newsletter_name = st.text_input("Newsletter Name", value="Alpha Intelligence Weekly")
        author_name = st.text_input("Author Name", value="Alpha Machine")
    with c2:
        st.markdown("**Source data:**")
        has_scan = "last_scan" in st.session_state
        if has_scan:
            st.success("✅ Alpha scan data available — will use your latest scan")
        else:
            st.info("ℹ️ No scan run yet — AI will use live web search for current market context")
        st.caption("Run the Alpha Scan tab first for best newsletter quality")

    if st.button("💌 Generate Newsletter", type="primary"):
        if key_check():
            scan_data = st.session_state.get("last_scan", {})
            with st.spinner("Writing your newsletter (this takes ~45 seconds)..."):
                result = run_newsletter(gemini_key, scan_data, author_name, newsletter_name)
            st.markdown("---")
            st.markdown(result)
            st.markdown("---")
            action_buttons(result, "newsletter")

            if tg_token and tg_chat:
                st.info("💡 Tip: Send this to your Telegram channel to preview how it reads as a message.")

# ══════════════════════════════════════════════════════════════════════════════
# MACRO REGIME (v4 NEW — Streaming + Base Case + Black Swan)
# ══════════════════════════════════════════════════════════════════════════════
with tab_macro_regime:
    st.markdown("### 🏛️ Global Macro Regime Analyzer")
    st.markdown("Streaming institutional-grade macro brief — **Base Case + Black Swan** scenarios + Smart Money divergence")

    c1, c2 = st.columns([2, 1])
    with c1:
        macro_query = st.text_input(
            "Specific Macro Focus (optional)",
            placeholder="e.g. DXY and EM assets · Bond yield impact on tech · Fed pivot timing",
            key="macro_regime_q"
        )
    with c2:
        macro_horizon = st.selectbox("Horizon", ["8-hour (intraday)", "1-week", "1-month", "1-quarter"], key="macro_h")

    col_a, col_b = st.columns(2)
    with col_a: macro_run = st.button("⚡ Stream Macro Brief", type="primary", key="macro_regime_btn")
    with col_b: macro_quick = st.button("📊 Quick Snapshot", key="macro_quick_btn")

    if macro_run:
        if key_check():
            focus = macro_query if macro_query else "current global market regime"
            with st.status(f"🏛️ Analyzing {macro_horizon} regime...", expanded=True) as status:
                st.write("Fetching DXY, VIX, yield curve data...")
                st.write("Calculating smart money divergence...")
                st.write("Modeling base case and black swan scenarios...")
                out = st.empty()
                full = ""
                for chunk in stream_gemini(MACRO_SYSTEM,
                    f"""Date: {datetime.now().strftime('%Y-%m-%d')}
FOCUS: {focus}
HORIZON: {macro_horizon}

Use live web search for current yield curve, VIX term structure, DXY levels, and Fed positioning.

Analyze the current macro regime and provide:

🌍 CURRENT REGIME
- Where are we in the global liquidity cycle?
- Yield curve signal (inverted/flat/steepening?)
- Risk appetite: Risk-On / Risk-Off / Transitioning?

📈 BASE CASE (60-70% probability)
- Most likely macro path over {macro_horizon}
- Top 3 asymmetric plays (specific tickers/ETFs)
- Entry levels and catalysts

🦢 BLACK SWAN (10-20% probability)
- Tail risk scenario that market is NOT pricing in
- Which assets get crushed? Which become safe havens?
- Specific hedge: ticker, structure, cost

🧠 SMART MONEY DIVERGENCE
- Where is institutional positioning vs retail consensus?
- Any extreme crowded trades right now?
- The contrarian angle most ignore

🎯 THIS WEEK'S HIGHEST CONVICTION MACRO TRADE
- Specific entry: ticker, price, size
- Catalyst and timing
- Stop loss level""",
                    gemini_key):
                    full += chunk
                    out.markdown(full)
                status.update(label="✅ Macro Brief Complete", state="complete")
            st.session_state["last_macro"] = full
            action_buttons(full, "macro_regime")

    if macro_quick:
        if key_check():
            with st.spinner("Fetching quick macro snapshot..."):
                macro_data = get_macro_prices()
                snap = "\n".join([f"{k}: {v[0]} ({'+' if (v[1] or 0)>=0 else ''}{v[1]:.2f}%)" 
                                   for k,v in macro_data.items() if v[0]])
                result = call_gemini(MACRO_SYSTEM,
                    f"Date:{datetime.now().strftime('%Y-%m-%d')}\nLIVE PRICES:\n{snap}\n\nGive a 5-bullet macro snapshot (max 150 words): regime, biggest risk, best opportunity, key level to watch, this week's event.",
                    gemini_key)
            show_result(result, "macro-regime")
            action_buttons(result, "macro_quick")

# ══════════════════════════════════════════════════════════════════════════════
# MONETIZATION AGENT (v4 NEW — One-click content from any scan result)
# ══════════════════════════════════════════════════════════════════════════════
with tab_monetize:
    st.markdown("### 📢 Monetization Agent")
    st.markdown("One-click: turn any Alpha Machine output into **viral X threads**, **Substack newsletters**, **LinkedIn posts**, or **TikTok scripts**.")

    # Source content selector
    source_options = {}
    if st.session_state.get("last_macro"):    source_options["🏛️ Last Macro Regime Brief"] = st.session_state["last_macro"]
    if st.session_state.get("last_research"): source_options["🔗 Last Supply Chain / Research"] = st.session_state["last_research"]
    if st.session_state.get("last_scan"):
        thesis = st.session_state["last_scan"].get("thesis","")
        if thesis: source_options["🎯 Last Alpha Scan Report"] = thesis

    if source_options:
        source_label = st.selectbox("Source content:", list(source_options.keys()))
        source_content = source_options[source_label]

        with st.expander("Preview source content"):
            st.write(source_content[:800] + "..." if len(source_content) > 800 else source_content)

        st.markdown("---")
        st.markdown("#### Choose your format:")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("🐦 Viral X Thread", type="primary", use_container_width=True, key="x_thread_btn"):
                with st.status("✍️ Drafting viral X thread...", expanded=True) as status:
                    out = st.empty(); full = ""
                    for chunk in stream_gemini(
                        "You are a viral financial content creator on X (Twitter). You write threads that go viral because they share alpha that retail investors can't find elsewhere. Use hooks, numbered lists, and end with a CTA.",
                        f"""Turn this research into a VIRAL 7-tweet X thread:

RESEARCH:
{source_content[:3000]}

FORMAT:
Tweet 1 (HOOK): Start with a shocking stat or contrarian take. Must make people stop scrolling.
Tweet 2-6: One key insight per tweet. Use data, specific tickers (**$TICKER**), and numbers.
Tweet 7 (CTA): Ask for RT + follow if they want more alpha like this.

Rules: Each tweet max 280 chars. Use emojis sparingly. No generic advice.""",
                        gemini_key):
                        full += chunk; out.markdown(full)
                    status.update(label="✅ Thread Ready", state="complete")
                st.session_state["monetize_output"] = full

        with col2:
            if st.button("📝 Substack Post", type="primary", use_container_width=True, key="substack_btn"):
                with st.status("✍️ Writing Substack post...", expanded=True) as status:
                    out = st.empty(); full = ""
                    for chunk in stream_gemini(
                        "You are a top-tier Substack financial analyst. You write like Howard Marks meets Paul Graham — deep, contrarian, and beautifully structured.",
                        f"""Turn this research into a professional Substack research note:

RESEARCH:
{source_content[:3000]}

FORMAT:
# [Compelling Title]
*[One-line hook subtitle]*

## The Setup
[2 paragraphs: context and why this matters now]

## The Alpha
[3-4 paragraphs: the actual insight, specific plays, reasoning]

## The Risk
[1 paragraph: honest bear case and what invalidates this]

## The Trade
[Specific: ticker, entry, target, stop, horizon]

---
*Disclaimer: Not financial advice. DYOR.*""",
                        gemini_key):
                        full += chunk; out.markdown(full)
                    status.update(label="✅ Substack Post Ready", state="complete")
                st.session_state["monetize_output"] = full

        with col3:
            if st.button("💼 LinkedIn Post", type="primary", use_container_width=True, key="linkedin_btn"):
                with st.status("✍️ Writing LinkedIn post...", expanded=True) as status:
                    out = st.empty(); full = ""
                    for chunk in stream_gemini(
                        "You are a professional finance LinkedIn creator. You write posts that get 50k+ impressions by being specific, contrarian, and educational without being boring.",
                        f"""Turn this research into a high-performing LinkedIn post:

RESEARCH:
{source_content[:2000]}

FORMAT:
- Opening line (no 'I am excited to share' — be bold and specific)
- 3-5 key insights as short paragraphs (not bullet lists)
- 1 specific actionable takeaway
- Close with a question to drive comments
- 3-5 relevant hashtags

Tone: Professional but direct. Sound like a CIO, not a salesperson.""",
                        gemini_key):
                        full += chunk; out.markdown(full)
                    status.update(label="✅ LinkedIn Post Ready", state="complete")
                st.session_state["monetize_output"] = full

        with col4:
            if st.button("🎬 TikTok Script", type="primary", use_container_width=True, key="tiktok_btn"):
                with st.status("✍️ Writing TikTok script...", expanded=True) as status:
                    out = st.empty(); full = ""
                    for chunk in stream_gemini(
                        "You are a viral TikTok finance creator. You write 60-second scripts that are engaging, educational, and end with a strong hook to follow for more.",
                        f"""Turn this research into a 60-second TikTok script:

RESEARCH:
{source_content[:2000]}

FORMAT:
[0-3s HOOK]: One shocking sentence to stop the scroll
[3-15s CONTEXT]: Why does this matter right now?
[15-45s THE ALPHA]: The actual insight — keep it simple, use analogies
[45-55s THE TRADE]: What's the specific play?
[55-60s CTA]: "Follow for daily alpha like this"

Style: Conversational. Short sentences. No jargon. Sound like you're texting a friend.""",
                        gemini_key):
                        full += chunk; out.markdown(full)
                    status.update(label="✅ TikTok Script Ready", state="complete")
                st.session_state["monetize_output"] = full

        # Download last output
        if st.session_state.get("monetize_output"):
            st.markdown("---")
            action_buttons(st.session_state["monetize_output"], "monetize")

    else:
        st.info("👈 Run any research mode first (Alpha Scan, Macro Regime, Supply Chain, etc.) — then come back here to monetize it.")
        st.markdown("""
**How it works:**
1. Run **Alpha Scan**, **Macro Regime**, or **Supply Chain** tab
2. Come back here
3. Pick your format — X Thread, Substack, LinkedIn, or TikTok
4. Download and post

**💡 Pro tip:** Run the Alpha Scan first — it generates the richest content for monetization.
        """)

# ══════════════════════════════════════════════════════════════════════════════
# INFO
# ══════════════════════════════════════════════════════════════════════════════
with tab_info:
    st.markdown("## 🏗️ Alpha Machine v3 — All 18 Modes")
    modes = [
        ("📊","Dashboard",            "Live macro pulse, sector momentum, watchlist signals, news feed"),
        ("🎯","Alpha Scan",           "5 parallel agents — macro/sector/stock/contrarian → CIO synthesis"),
        ("🔗","Supply Chain",         "Tier 1/2/3 mapper — finds the obscure supplier that's the real play"),
        ("🏭","Sector Dive",          "Cycle position, hidden gems, institutional flow, best asymmetric bet"),
        ("🔬","Stock Stress",         "Forensic bull/bear, accounting flags, insider trends, alternatives"),
        ("🌍","Geo Trade",            "Scenario → winners/losers/hedges/second-order plays"),
        ("⛏️","Commodity Chain",      "Full upstream/downstream, bottleneck, moat, best play"),
        ("⚖️","Portfolio",            "5-scenario stress test, concentration risk, hedging recs"),
        ("🆚","Compare",              "Head-to-head forensic + pair trade setup"),
        ("🔄","Rotation Timer",       "Cycle phase, what rotates next, highest conviction rotation trade"),
        ("📅","Catalyst Calendar",    "90-day event calendar ranked by asymmetric potential"),
        ("🧠","Earnings Analyzer",    "Tone shift detection, what CEO is hiding, trading implication"),
        ("📜","SEC Filings",          "Form 4 insider activity, 8-K material events, 10-Q forensic flags"),
        ("⚡","Options Flow",         "Unusual activity, smart money positioning, optimal strategy"),
        ("🏦","13F Tracker",          "Institutional ownership changes — by ticker or fund manager"),
        ("🔔","Smart Watchdog",       "Custom RSI/price/momentum triggers — auto-fires Telegram alerts"),
        ("📊","Backtester",           "Stress tests thesis against 2008, 2020, 2022, 2024 regimes"),
        ("💌","Newsletter",           "Full weekly newsletter from scan results, ready for Substack"),
        ("🏛️","Macro Regime",         "Streaming institutional brief — Base Case + Black Swan + Smart Money divergence"),
        ("📢","Monetization Agent",    "One-click: X thread, Substack post, LinkedIn post, TikTok script from any scan"),
    ]
    col1,col2 = st.columns(2)
    for i,(icon,name,desc) in enumerate(modes):
        (col1 if i%2==0 else col2).markdown(f"**{icon} {name}** — {desc}\n")

    st.markdown("---")
    st.markdown("## 🤖 Telegram Two-Way Bot")
    st.markdown("""
Your bot file (`telegram_bot.py`) lets you **text your bot** to run any scan — no need to open the website.

**Commands:**
| Command | What it does |
|---|---|
| `/scan` | Run full alpha scan |
| `/stress NVDA` | Stock stress test |
| `/chain NVDA` | Supply chain map |
| `/sector Defense` | Sector deep dive |
| `/options NVDA` | Options flow |
| `/sec PLTR` | SEC filing scan |
| `/watchdog` | Run your watchlist triggers |
| `/help` | Show all commands |

**Setup:** see `telegram_bot.py` — run on any free server (Railway, Render, or your laptop)
""")

    st.markdown("## 🔑 Setup Guide")
    st.markdown("""
**1. Gemini API Key (free, 2 min):**
- [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) → Create API Key
- Paste in sidebar — starts with `AIza...`

**2. Telegram Bot (optional):**
- Message [@BotFather](https://t.me/BotFather) → `/newbot` → copy token
- Add bot to channel as admin
- Get chat ID via `https://api.telegram.org/bot<TOKEN>/getUpdates`

**3. Two-way Telegram bot:**
- Deploy `telegram_bot.py` on [Railway.app](https://railway.app) (free tier)
- Set env vars: `GEMINI_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
""")
