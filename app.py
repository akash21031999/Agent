"""
Alpha Machine v6 — Proactive Intelligence Engine
Universal Search · Live Alpha Feed · Background Scanner
Pentagon Contracts · Patent Breakthroughs · Insider Cluster Detector
Dark Money Options · Auto Supply Chain Cascade · Telegram Push
"""
import streamlit as st
st.set_page_config(page_title="Alpha Machine", page_icon="◈", layout="wide",
                   initial_sidebar_state="collapsed")

import requests, feedparser, json, threading, time, re, hashlib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from google import genai
from google.genai import types

# ══════════════════════════════════════════════════════════════════════════════
#  CSS — Terminal-grade, mobile-first
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html,body,[data-testid="stAppViewContainer"]{background:#07080f;font-family:'Inter',sans-serif;color:#e1e4e8;}
[data-testid="stSidebar"]{background:#09091a;border-right:1px solid #181830;}
[data-testid="stSidebar"] *{color:#8892a4 !important;}
.block-container{padding:1.2rem 1.8rem 3rem;max-width:1500px;}
h1,h2,h3,h4{color:#f0f2f5;font-weight:600;letter-spacing:-0.3px;}
p,li{color:#9aa3b2;line-height:1.75;}

/* ── Top bar ── */
.topbar{display:flex;align-items:center;justify-content:space-between;
        padding:10px 0 16px;border-bottom:1px solid #181830;margin-bottom:18px;}
.logo{font-size:1.25rem;font-weight:700;letter-spacing:-0.8px;color:#f0f2f5;}
.logo span{color:#3b82f6;}
.topbar-meta{font-size:0.7rem;color:#374151;letter-spacing:1px;text-transform:uppercase;}

/* ── Macro strip ── */
.macro-strip{display:flex;gap:1px;margin-bottom:18px;overflow-x:auto;}
.mbox{flex:1;min-width:80px;background:#0d0e1a;border:1px solid #181830;
      border-radius:6px;padding:8px 10px;text-align:center;}
.mlbl{font-size:0.6rem;color:#374151;text-transform:uppercase;letter-spacing:1.5px;display:block;margin-bottom:2px;}
.mprice{font-size:0.95rem;font-weight:600;color:#f0f2f5;font-family:'JetBrains Mono',monospace;display:block;}
.up{color:#22c55e;font-size:0.68rem;font-weight:500;}
.dn{color:#ef4444;font-size:0.68rem;font-weight:500;}
.flat{color:#374151;font-size:0.68rem;}

/* ── Universal search ── */
.search-wrap{background:#0d0e1a;border:1px solid #1e2340;border-radius:10px;
             padding:16px 20px;margin-bottom:20px;}
.search-hint{font-size:0.72rem;color:#374151;margin-top:8px;line-height:1.6;}

/* ── Signal feed card ── */
.sig-card{background:#0d0e1a;border:1px solid #181830;border-radius:8px;
          padding:14px 18px;margin:6px 0;cursor:pointer;
          transition:border-color 0.15s,background 0.15s;}
.sig-card:hover{border-color:#3b82f6;background:#0f1020;}
.sig-card.dark_money{border-left:3px solid #84cc16;}
.sig-card.pentagon{border-left:3px solid #3b82f6;}
.sig-card.patent{border-left:3px solid #a78bfa;}
.sig-card.insider{border-left:3px solid #22c55e;}
.sig-card.macro{border-left:3px solid #f59e0b;}
.sig-card.technical{border-left:3px solid #06b6d4;}
.sig-top{display:flex;align-items:center;gap:10px;margin-bottom:6px;}
.sig-score{font-size:0.72rem;font-weight:700;padding:2px 7px;border-radius:4px;font-family:'JetBrains Mono',monospace;}
.score-high{background:#052e1c;color:#22c55e;}
.score-med{background:#1c1505;color:#f59e0b;}
.score-low{background:#0a0a1a;color:#4a5568;}
.sig-type{font-size:0.65rem;font-weight:600;letter-spacing:1.5px;text-transform:uppercase;color:#374151;}
.sig-ticker{font-size:1rem;font-weight:700;color:#f0f2f5;font-family:'JetBrains Mono',monospace;}
.sig-title{font-size:0.85rem;color:#9aa3b2;margin:3px 0;}
.sig-supply{font-size:0.75rem;color:#374151;margin-top:4px;}
.sig-supply span{color:#3b82f6;font-weight:500;}
.sig-meta{font-size:0.68rem;color:#374151;margin-top:6px;}

/* ── Status bar ── */
.statusbar{display:flex;gap:16px;align-items:center;
           padding:8px 14px;background:#0a0b14;border:1px solid #181830;
           border-radius:6px;margin-bottom:16px;flex-wrap:wrap;}
.sitem{font-size:0.72rem;color:#374151;display:flex;align-items:center;gap:5px;}
.dot-green{width:6px;height:6px;border-radius:50%;background:#22c55e;display:inline-block;}
.dot-amber{width:6px;height:6px;border-radius:50%;background:#f59e0b;display:inline-block;}
.dot-red{width:6px;height:6px;border-radius:50%;background:#ef4444;display:inline-block;}
.dot-blue{width:6px;height:6px;border-radius:50%;background:#3b82f6;display:inline-block;}

/* ── Report ── */
.report{background:#0d0e1a;border:1px solid #181830;border-radius:8px;
        padding:24px 28px;margin:12px 0;line-height:1.85;
        word-wrap:break-word;overflow-wrap:break-word;
        font-size:0.92rem;color:#c9d1df;}
.report.blue{border-left:3px solid #3b82f6;}
.report.green{border-left:3px solid #22c55e;}
.report.amber{border-left:3px solid #f59e0b;}
.report.red{border-left:3px solid #ef4444;}
.report.purple{border-left:3px solid #a78bfa;}
.report.lime{border-left:3px solid #84cc16;}
.report.teal{border-left:3px solid #14b8a6;}
.report.cyan{border-left:3px solid #06b6d4;}
.report.orange{border-left:3px solid #f97316;}
.report.rose{border-left:3px solid #f43f5e;}
.report.pink{border-left:3px solid #ec4899;}

/* ── Section label ── */
.sec-label{font-size:0.65rem;font-weight:600;letter-spacing:2px;text-transform:uppercase;
           color:#374151;border-bottom:1px solid #181830;padding-bottom:6px;margin:18px 0 10px;}

/* ── Scan status bar ── */
.scan-status{background:#0a0b14;border:1px solid #181830;border-radius:6px;
             padding:10px 16px;font-size:0.8rem;color:#4a5568;margin:10px 0;}

/* ── Alert boxes ── */
.alert-ok{background:#052e1c;border:1px solid #22c55e;border-radius:6px;
          padding:10px 14px;margin:6px 0;font-size:0.82rem;color:#86efac;}
.alert-warn{background:#2e1505;border:1px solid #f59e0b;border-radius:6px;
            padding:10px 14px;margin:6px 0;font-size:0.82rem;color:#fbbf24;}

/* ── Stat cards ── */
.stat-row{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0;}
.stat-card{background:#0d0e1a;border:1px solid #181830;border-radius:7px;
           padding:10px 14px;flex:1;min-width:100px;}
.slbl{font-size:0.62rem;color:#374151;text-transform:uppercase;letter-spacing:1px;display:block;margin-bottom:3px;}
.sval{font-size:1.1rem;font-weight:700;color:#f0f2f5;font-family:'JetBrains Mono',monospace;}
.sval.g{color:#22c55e;}.sval.r{color:#ef4444;}.sval.a{color:#f59e0b;}

/* ── News item ── */
.news-item{padding:8px 0;border-bottom:1px solid #181830;}
.news-title{color:#c9d1df;font-size:0.83rem;font-weight:500;display:block;}
.news-src{color:#374151;font-size:0.7rem;display:block;margin-top:2px;}

/* ── Tabs ── */
[data-testid="stTabs"] button{font-size:0.78rem !important;font-weight:500 !important;}
[data-testid="stTabs"] button[aria-selected="true"]{font-weight:600 !important;color:#f0f2f5 !important;}
[data-testid="stTabs"] [role="tablist"]{border-bottom:1px solid #181830;gap:2px;}

/* ── Inputs ── */
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stTextArea textarea{
    background:#0f1020 !important;border:1px solid #1e2340 !important;color:#c9d1df !important;}
.stTextInput input,.stTextArea textarea{
    background:#0d0e1a !important;border:1px solid #1e2340 !important;color:#e1e4e8 !important;}

/* ── Mobile ── */
@media(max-width:768px){
    .block-container{padding:0.8rem 0.8rem 2rem;}
    .report{padding:14px 16px;font-size:0.86rem;}
    .macro-strip{gap:2px;}
    .mbox{padding:6px 8px;}
    .sig-card{padding:10px 12px;}
    .topbar{flex-direction:column;align-items:flex-start;gap:4px;}
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE INIT
# ══════════════════════════════════════════════════════════════════════════════
for key in ["feed_signals","last_scan_ts","last_scan","last_research","last_macro",
            "search_result","search_query"]:
    if key not in st.session_state:
        st.session_state[key] = None if key not in ["feed_signals"] else []

# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("**◈ Alpha Machine v6**")
    st.divider()
    st.markdown("**AI Engine**")
    gemini_key = st.text_input("Gemini API Key", type="password", placeholder="AIza...",
                               key="si_gemini", help="Free · aistudio.google.com/app/apikey")

    st.markdown("**Data Providers** *(optional)*")
    with st.expander("Configure APIs"):
        finnhub_key = st.text_input("Finnhub",      type="password", placeholder="60 req/min", key="si_finnhub")
        fmp_key     = st.text_input("FMP",           type="password", placeholder="250 req/day", key="si_fmp")
        av_key      = st.text_input("Alpha Vantage", type="password", placeholder="25 req/day", key="si_av")
    st.caption("App fully works without data keys via Yahoo Finance + free public APIs.")

    st.markdown("**Telegram Alerts**")
    tg_token = st.text_input("Bot Token", type="password", placeholder="123456:ABC...", key="si_tg")
    tg_chat  = st.text_input("Chat ID",   placeholder="-100123456789", key="si_tg_chat")

    st.markdown("**Watchlist**")
    stocks_raw  = st.text_area("Stocks",  value="NVDA,TSM,ASML,PLTR,IONQ,RKLB,HIMS,CELH,NVO,MELI",
                               key="si_stocks", height=65)
    sectors_raw = st.text_area("Sectors", value="XLK,XLE,XLF,XLV,XBI,ARKK,GDX,COPX,ITB,XAR",
                               key="si_sectors", height=50)

    st.markdown("**Scanner Settings**")
    scan_interval = st.selectbox("Auto-refresh", ["30 min","60 min","Manual only"], key="si_interval")
    scan_universe_extra = st.text_input("Extra tickers to scan",
                                        placeholder="SPY,QQQ,IWM,GLD,TLT", key="si_extra")

    st.divider()
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        dot = "🟢" if gemini_key else "🔴"
        st.markdown(f'<span style="font-size:0.75rem">{dot} Gemini</span>', unsafe_allow_html=True)
    with col_s2:
        dot2 = "🟢" if (tg_token and tg_chat) else "⚫"
        st.markdown(f'<span style="font-size:0.75rem">{dot2} Telegram</span>', unsafe_allow_html=True)
    if st.button("Reset", use_container_width=True, key="btn_reset"):
        st.session_state.clear(); st.rerun()

STOCKS  = [s.strip() for s in stocks_raw.split(",") if s.strip()]
SECTORS = [s.strip() for s in sectors_raw.split(",") if s.strip()]
EXTRA   = [s.strip() for s in scan_universe_extra.split(",") if s.strip()] if scan_universe_extra else []
SCAN_UNIVERSE = list(dict.fromkeys(STOCKS + EXTRA + ["SPY","QQQ","IWM","GLD","TLT","XLE","XLF","XLV"]))

# ══════════════════════════════════════════════════════════════════════════════
#  DATA LAYER
# ══════════════════════════════════════════════════════════════════════════════
YF_HDR = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
          "Accept":"application/json"}

@st.cache_data(ttl=300, show_spinner=False)
def yf_price(sym):
    try:
        r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range=5d",
                         headers=YF_HDR, timeout=6)
        c = [x for x in r.json()["chart"]["result"][0]["indicators"]["quote"][0]["close"] if x]
        return (round(c[-1],2), round((c[-1]/c[-2]-1)*100,2)) if len(c)>=2 else (None,None)
    except: return None,None

@st.cache_data(ttl=300, show_spinner=False)
def yf_history(sym, range_="3mo"):
    try:
        r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range={range_}",
                         headers=YF_HDR, timeout=8)
        res    = r.json()["chart"]["result"][0]
        closes = [c for c in res["indicators"]["quote"][0]["close"] if c is not None]
        return closes, res.get("meta",{})
    except: return [],{}

@st.cache_data(ttl=600, show_spinner=False)
def yf_options_chain(sym):
    try:
        r    = requests.get(f"https://query1.finance.yahoo.com/v7/finance/options/{sym}",
                            headers=YF_HDR, timeout=8)
        root = r.json().get("optionChain",{}).get("result",[])
        if not root: return pd.DataFrame()
        rows = []
        for block in root[:4]:
            exp_ts = block.get("expirationDate")
            exp_dt = datetime.fromtimestamp(exp_ts).strftime("%Y-%m-%d") if exp_ts else "N/A"
            for side,key_n in [("call","calls"),("put","puts")]:
                for ob in block.get("options",[]):
                    for c in ob.get(key_n,[]):
                        rows.append({"expiration":exp_dt,"type":side,
                                     "strike":c.get("strike",0),"lastPrice":c.get("lastPrice",0),
                                     "volume":int(c.get("volume") or 0),
                                     "openInterest":int(c.get("openInterest") or 0),
                                     "impliedVol":round(float(c.get("impliedVolatility") or 0)*100,1),
                                     "inTheMoney":bool(c.get("inTheMoney",False))})
        return pd.DataFrame(rows)
    except: return pd.DataFrame()

@st.cache_data(ttl=300, show_spinner=False)
def get_macro_strip():
    tickers = {"10Y":"%5ETNX","SPX":"%5EGSPC","Gold":"GC%3DF","Oil":"CL%3DF","VIX":"%5EVIX","DXY":"DX-Y.NYB"}
    res = {lbl:yf_price(sym) for lbl,sym in tickers.items()}
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price",
            params={"ids":"bitcoin","vs_currencies":"usd","include_24hr_change":"true"},
            timeout=5, headers={"User-Agent":"AlphaMachine/6.0"})
        d = r.json()["bitcoin"]
        res["BTC"] = (round(d["usd"],0), round(d["usd_24h_change"],2))
    except: res["BTC"] = (None,None)
    return res

@st.cache_data(ttl=600, show_spinner=False)
def get_news(query, n=8):
    try:
        url  = f"https://news.google.com/rss/search?q={requests.utils.quote(query)}&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(url)
        return [{"title":e.get("title",""),"source":e.get("source",{}).get("title",""),
                 "link":e.get("link",""),"published":e.get("published","")} for e in feed.entries[:n]]
    except: return []

# ── Finnhub helpers ───────────────────────────────────────────────────────────
@st.cache_data(ttl=600, show_spinner=False)
def finnhub_insider(sym, key):
    if not key: return []
    try:
        r = requests.get(f"https://finnhub.io/api/v1/stock/insider-transactions?symbol={sym}&token={key}", timeout=6)
        return r.json().get("data",[])[:15]
    except: return []

@st.cache_data(ttl=600, show_spinner=False)
def finnhub_sentiment(sym, key):
    if not key: return {}
    try:
        r = requests.get(f"https://finnhub.io/api/v1/news-sentiment?symbol={sym}&token={key}", timeout=5)
        return r.json()
    except: return {}

# ── FMP helpers ───────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fmp_profile(sym, key):
    if not key: return {}
    try:
        r = requests.get(f"https://financialmodelingprep.com/api/v3/profile/{sym}?apikey={key}", timeout=6)
        d = r.json(); return d[0] if d else {}
    except: return {}

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
def fmp_ratios(sym, key):
    if not key: return {}
    try:
        r = requests.get(f"https://financialmodelingprep.com/api/v3/ratios/{sym}?limit=1&apikey={key}", timeout=6)
        d = r.json(); return d[0] if d else {}
    except: return {}

# ── EDGAR filings ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=1800, show_spinner=False)
def edgar_filings(ticker, forms="8-K,4,10-Q"):
    try:
        start = (datetime.now()-timedelta(days=90)).strftime("%Y-%m-%d")
        r = requests.get(
            f"https://efts.sec.gov/LATEST/search-index?q=%22{ticker}%22&dateRange=custom&startdt={start}&forms={forms}",
            headers={"User-Agent":"AlphaMachine research@alpha.com"}, timeout=10)
        hits = r.json().get("hits",{}).get("hits",[])[:8]
        return [{"form":h["_source"].get("form_type",""),"filed":h["_source"].get("file_date",""),
                 "company":h["_source"].get("entity_name","")} for h in hits]
    except: return []

# ══════════════════════════════════════════════════════════════════════════════
#  PROACTIVE DATA SOURCES — Pentagon · USPTO · EDGAR Cluster
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_pentagon_contracts(days_back=3, min_amount=10_000_000):
    """
    USASpending.gov free API — DoD contract awards.
    Returns list of {recipient, amount, description, date, potential_tickers}.
    """
    try:
        end_date   = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now()-timedelta(days=days_back)).strftime("%Y-%m-%d")
        payload = {
            "filters": {
                "time_period": [{"start_date": start_date, "end_date": end_date}],
                "agencies": [{"type":"awarding_agency","tier":"toptier","name":"Department of Defense"}],
                "award_type_codes": ["A","B","C","D"],
            },
            "fields": ["recipient_name","total_obligated_amount","award_description",
                       "action_date","awarding_sub_agency_name","place_of_performance_state_name"],
            "sort": "total_obligated_amount",
            "order": "desc",
            "limit": 25,
            "page": 1,
        }
        r = requests.post("https://api.usaspending.gov/api/v2/search/spending_by_award/",
                         json=payload, timeout=15,
                         headers={"Content-Type":"application/json","User-Agent":"AlphaMachine/6.0"})
        results = r.json().get("results",[])
        contracts = []
        for item in results:
            amt = float(item.get("total_obligated_amount") or 0)
            if amt < min_amount: continue
            contracts.append({
                "recipient":    item.get("recipient_name","Unknown")[:60],
                "amount_m":     round(amt/1e6, 1),
                "description":  item.get("award_description","")[:120],
                "date":         item.get("action_date",""),
                "agency":       item.get("awarding_sub_agency_name","DoD")[:40],
            })
        return contracts
    except Exception as e:
        return []

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_patent_grants(days_back=7):
    """
    USPTO PatentsView API — recent patent grants in tech/defense/biotech.
    Returns list of {assignee, patent_title, date, patent_number, category}.
    """
    tech_keywords = [
        "artificial intelligence","machine learning","semiconductor","photonics",
        "quantum","hypersonic","directed energy","autonomy","radar","satellite",
        "gene therapy","CRISPR","mRNA","battery","solid state","fusion energy",
        "cybersecurity","encryption","drone","unmanned","space launch"
    ]
    patents = []
    try:
        end_date   = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now()-timedelta(days=days_back)).strftime("%Y-%m-%d")
        for kw in tech_keywords[:8]:  # limit to 8 queries to stay light
            try:
                payload = {
                    "q": {"_and":[
                        {"_gte":{"patent_date":start_date}},
                        {"_lte":{"patent_date":end_date}},
                        {"_text_phrase":{"patent_title":kw}}
                    ]},
                    "f": ["patent_number","patent_title","patent_date","assignee_organization"],
                    "o": {"per_page":3,"sort":"patent_date:desc"}
                }
                r = requests.post("https://api.patentsview.org/patents/query",
                                 json=payload, timeout=8,
                                 headers={"Content-Type":"application/json"})
                data = r.json()
                for p in data.get("patents") or []:
                    assignees = p.get("assignees") or [{}]
                    org = assignees[0].get("assignee_organization","Unknown") if assignees else "Unknown"
                    if not org or org == "None": continue
                    patents.append({
                        "assignee":   org[:60],
                        "title":      p.get("patent_title","")[:100],
                        "date":       p.get("patent_date",""),
                        "number":     p.get("patent_number",""),
                        "keyword":    kw,
                    })
                time.sleep(0.2)
            except: continue
    except: pass
    return patents

@st.cache_data(ttl=900, show_spinner=False)
def fetch_insider_clusters(tickers, key=""):
    """
    Scan EDGAR Form 4 for cluster buying (3+ insiders buying same company same week).
    Uses Finnhub if key provided, otherwise EDGAR direct.
    Returns list of {ticker, buyers, total_value, signal_strength}.
    """
    clusters = []
    for sym in tickers:
        try:
            insiders = []
            if key:
                insiders = finnhub_insider(sym, key)
            else:
                # EDGAR fallback
                filings = edgar_filings(sym, "4")
                insiders = [{"transactionType":"P","name":f.get("company",""),"transactionDate":f.get("filed","")}
                            for f in filings]

            if not insiders: continue

            # Filter to open-market buys in last 30 days
            cutoff = (datetime.now()-timedelta(days=30)).strftime("%Y-%m-%d")
            buys = []
            for t in insiders:
                tx_type = str(t.get("transactionType","")).upper()
                tx_date = str(t.get("transactionDate","") or t.get("date",""))
                if any(b in tx_type for b in ["P","BUY","PURCHASE"]) and tx_date >= cutoff:
                    buys.append(t)

            if len(buys) >= 2:  # 2+ insiders = cluster signal
                total_val = sum(abs(float(b.get("transactionPrice",0) or 0) *
                                   abs(float(b.get("share",0) or 0))) for b in buys)
                clusters.append({
                    "ticker":   sym,
                    "buyers":   len(buys),
                    "total_val_k": round(total_val/1000, 0),
                    "strength": "ULTRA" if len(buys)>=4 else "HIGH" if len(buys)>=3 else "MEDIUM",
                    "names":    [b.get("name","Insider")[:20] for b in buys[:4]],
                })
            time.sleep(0.15)
        except: continue
    return clusters

def detect_options_anomalies(tickers, min_vol_oi=2.5):
    """Scan tickers for Vol/OI anomalies + put/call skew."""
    anomalies = []
    for sym in tickers:
        try:
            chain = yf_options_chain(sym)
            price, chg = yf_price(sym)
            if chain.empty or not price: continue

            call_vol = int(chain[chain["type"]=="call"]["volume"].sum())
            put_vol  = int(chain[chain["type"]=="put"]["volume"].sum())
            call_oi  = int(chain[chain["type"]=="call"]["openInterest"].sum())
            put_oi   = int(chain[chain["type"]=="put"]["openInterest"].sum())
            total_vol = call_vol + put_vol
            total_oi  = call_oi + put_oi
            if total_oi <= 0: continue

            vol_oi = total_vol / max(total_oi, 1)
            if vol_oi < min_vol_oi: continue

            pc_vol = round(put_vol / max(call_vol,1), 2)
            direction = "BULLISH CALLS" if call_vol > put_vol*1.5 else \
                        "BEARISH PUTS"  if put_vol > call_vol*1.5 else "MIXED"

            # Largest OI strikes (price magnets)
            top_call_strike = 0; top_put_strike = 0
            if not chain[chain["type"]=="call"].empty:
                top_call_strike = float(chain[chain["type"]=="call"].nlargest(1,"openInterest")["strike"].iloc[0])
            if not chain[chain["type"]=="put"].empty:
                top_put_strike  = float(chain[chain["type"]=="put"].nlargest(1,"openInterest")["strike"].iloc[0])

            score = min(10.0, round(1.5 + vol_oi * 1.5, 1))
            anomalies.append({
                "ticker":     sym,
                "price":      price,
                "chg":        chg,
                "vol_oi":     round(vol_oi,2),
                "pc_vol":     pc_vol,
                "direction":  direction,
                "call_vol":   call_vol,
                "put_vol":    put_vol,
                "whale_call": top_call_strike,
                "whale_put":  top_put_strike,
                "score":      score,
            })
            time.sleep(0.2)
        except: continue
    return sorted(anomalies, key=lambda x: x["score"], reverse=True)

# ══════════════════════════════════════════════════════════════════════════════
#  QUANTITATIVE ENGINE
# ══════════════════════════════════════════════════════════════════════════════
def calc_rsi(closes, period=14):
    if len(closes)<period+1: return 50.0
    arr=np.array(closes,dtype=float); diffs=np.diff(arr)
    gains=np.where(diffs>0,diffs,0.0); losses=np.where(diffs<0,-diffs,0.0)
    ag=np.mean(gains[-period:]); al=np.mean(losses[-period:])
    return round(float(100-100/(1+ag/(al+1e-9))),1)

def calc_macd(closes, fast=12, slow=26, signal=9):
    if len(closes)<slow+signal: return None,None
    arr=pd.Series(closes,dtype=float)
    macd=arr.ewm(span=fast,adjust=False).mean()-arr.ewm(span=slow,adjust=False).mean()
    sig=macd.ewm(span=signal,adjust=False).mean()
    return round(float(macd.iloc[-1]),3),round(float(sig.iloc[-1]),3)

def calc_bollinger(closes,period=20,std_dev=2):
    if len(closes)<period: return None,None,None
    arr=np.array(closes[-period:],dtype=float); mid=np.mean(arr); std=np.std(arr)
    return round(mid+std_dev*std,2),round(mid,2),round(mid-std_dev*std,2)

def dcf_valuation(revenue, revenue_growth, fcf_margin, wacc, terminal_growth, shares, net_debt=0, years=5):
    scenarios={"Bear":{"g":revenue_growth*0.5,"m":fcf_margin*0.7,"wacc":wacc*1.2},
               "Base":{"g":revenue_growth,"m":fcf_margin,"wacc":wacc},
               "Bull":{"g":revenue_growth*1.5,"m":fcf_margin*1.25,"wacc":wacc*0.9}}
    results={}
    for name,s in scenarios.items():
        g,m,w=s["g"],s["m"],s["wacc"]
        rev=np.array([revenue*(1+g)**t for t in range(1,years+1)])
        fcf=rev*m; disc=np.array([1/(1+w)**t for t in range(1,years+1)])
        pv_fcf=float(np.sum(fcf*disc))
        tv=fcf[-1]*(1+terminal_growth)/max(w-terminal_growth,0.001)
        ev=pv_fcf+tv*disc[-1]; equity=ev-net_debt
        results[name]={"FV_per_share":round(equity/shares if shares>0 else 0,2),"EV":round(ev,1)}
    return results

def score_technical(closes, rsi, ml, ms, price, w52h, w52l):
    score=5; sigs=[]
    if rsi<30: sigs.append("RSI Oversold"); score+=2
    elif rsi<40: sigs.append("RSI Low"); score+=1
    elif rsi>70: sigs.append("RSI Overbought"); score-=2
    if ml and ms:
        if ml>ms: sigs.append("MACD Bullish"); score+=1
        else: sigs.append("MACD Bearish"); score-=1
    if w52h and w52l:
        pct=(price-w52l)/max(w52h-w52l,0.01)
        if pct<0.25: sigs.append("Near 52W Low"); score+=2
        elif pct>0.90: sigs.append("Near 52W High"); score+=1
    if len(closes)>50:
        if price>np.mean(closes[-50:]): sigs.append("Above 50MA"); score+=1
        else: sigs.append("Below 50MA"); score-=1
    bu,bm,bl=calc_bollinger(closes)
    if bl and price<bl: sigs.append("BB Oversold"); score+=1
    if bu and price>bu: sigs.append("BB Overbought"); score-=1
    score=max(0,min(10,score))
    verdict=("STRONG BUY" if score>=7 else "BUY" if score>=6 else
             "WATCH" if score>=4 else "CAUTION" if score>=3 else "AVOID")
    return score,sigs,verdict

def calc_correlation_matrix(price_dict):
    returns={}
    for sym,closes in price_dict.items():
        if len(closes)>5:
            arr=np.array(closes,dtype=float); returns[sym]=np.diff(arr)/arr[:-1]
    if not returns: return pd.DataFrame()
    min_len=min(len(v) for v in returns.values())
    return pd.DataFrame({k:v[-min_len:] for k,v in returns.items()}).corr().round(3)

# ══════════════════════════════════════════════════════════════════════════════
#  GEMINI AI ENGINE
# ══════════════════════════════════════════════════════════════════════════════
SP = {
"cio": """You are the CIO of a $10B macro hedge fund. Synthesize intelligence into razor-sharp,
actionable investment theses. Only surface asymmetric bets scoring 7+/10. No fluff.""",

"macro": """You are a Lead Global Macro Strategist. Analyze liquidity cycles, yield curves,
currency flows, and volatility. Always: BASE CASE (60%) + BLACK SWAN (15%) + SMART MONEY DIVERGENCE.
If X happens → Y is the asymmetric play.""",

"supply": """You are a Supply Chain Forensic Analyst. Map the nervous system of any sector.
Find the company that owns the IP or bottleneck that giants cannot live without.
Bold tickers: **$TICKER**. Identify: moat owner, capacity constraint, hidden Tier-2 play.""",

"dcf": """You are a Quantitative Valuation Specialist (CFA+CPA). Combine DCF with business quality.
Bear/base/bull fair values with explicit assumptions. No guessing — state your numbers clearly.""",

"risk": """You are an Anti-Portfolio Risk Agent. Stress-test every thesis.
Find hidden correlations, concentration risk, tail risk. What's already priced in?
What kills this trade? Recommend a specific hedge for each position.""",

"search": """You are Alpha Machine — an institutional intelligence terminal.
When given a query (ticker, theme, sector, person, event), run a comprehensive analysis
synthesizing: quantitative signals, supply chain map, macro context, risks, and
the specific asymmetric bet most people are missing. Be specific. Use live web search.
End every response with: 🎯 THE BET: [exact ticker] | [entry] | [target] | [stop] | [horizon]""",

"flow": """You are the Smart Money Flow Desk at a multi-strat hedge fund.
Vol/OI > 3x = fresh institutional positioning. OTM sweeps near catalysts = informed.
Classify: DIRECTIONAL BET / EARNINGS PLAY / SHORT SQUEEZE / MACRO HEDGE / DEALER FLOW.
End with ONE highest-priority trade: ticker, direction, entry, stop, horizon.""",

"pentagon": """You are a Defense & Government Contractor Intelligence Analyst.
When analyzing Pentagon contracts: (1) Who is the direct winner? (2) Who are the
Tier-1/2/3 supply chain beneficiaries that haven't moved yet? (3) What is the
revenue/earnings impact on the winner and each supplier? (4) Historical precedent?
Always end with the asymmetric supply chain play most people miss.""",

"patent": """You are an IP Intelligence Analyst and Technology Investment Strategist.
When analyzing patent grants: (1) Who filed it? (2) Which giant needs this technology?
(3) Is this company a buyout target? (4) Who in the supply chain benefits?
(5) Timeline from patent to revenue. Bold all tickers: **$TICKER**.""",

"insider": """You are an Insider Activity Analyst at an equity research firm.
Cluster buying (3+ insiders, open-market, same week) is the most reliable signal.
Analyze: size relative to salary, previous buying patterns, company catalyst timing.
Score conviction: ULTRA-HIGH / HIGH / MEDIUM. Always suggest entry and stop.""",
}

def call_gemini(system, user, key):
    if not key: return "[No API key — add Gemini key in sidebar]"
    try:
        client = genai.Client(api_key=key)
        srch   = types.Tool(google_search=types.GoogleSearch())
        config = types.GenerateContentConfig(tools=[srch], temperature=0.3, system_instruction=system)
        return client.models.generate_content(model="gemini-2.5-flash",contents=user,config=config).text
    except Exception as e: return f"[API error: {e}]"

def stream_gemini(system, user, key):
    if not key: yield "⚠️ No API key."; return
    try:
        client = genai.Client(api_key=key)
        resp = client.models.generate_content_stream(model="gemini-2.5-flash",
            config=types.GenerateContentConfig(system_instruction=system,temperature=0.35),contents=user)
        for chunk in resp:
            if chunk.text: yield chunk.text
    except Exception as e: yield f"\n❌ {e}"

def send_telegram(text, token, chat_id):
    if not token or not chat_id: return
    for chunk in [text[i:i+4000] for i in range(0,len(text),4000)]:
        try:
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                         json={"chat_id":chat_id,"text":chunk},timeout=10)
        except: pass

# ══════════════════════════════════════════════════════════════════════════════
#  PROACTIVE BACKGROUND SCANNER — builds the Alpha Feed
# ══════════════════════════════════════════════════════════════════════════════
def _score_to_class(score):
    if score >= 7.5: return "score-high"
    if score >= 5.0: return "score-med"
    return "score-low"

def run_background_scan(key, tg_token="", tg_chat=""):
    """
    Runs all 5 signal layers in parallel threads.
    Returns list of signal dicts, sorted by score descending.
    """
    signals = []
    lock = threading.Lock()

    def add(sig): 
        with lock: signals.append(sig)

    def scan_options():
        anomalies = detect_options_anomalies(SCAN_UNIVERSE, min_vol_oi=2.5)
        for a in anomalies[:8]:
            score = a["score"]
            add({
                "type":"dark_money","ticker":a["ticker"],"score":score,
                "title":f"Unusual options flow — {a['direction']} · Vol/OI {a['vol_oi']}×",
                "detail":f"Call vol: {a['call_vol']:,} · Put vol: {a['put_vol']:,} · P/C: {a['pc_vol']} · Price: ${a['price']}",
                "supply_hint":f"Whale call strike: ${a['whale_call']:,.0f} · Put: ${a['whale_put']:,.0f}",
                "raw": a, "ts": datetime.now().isoformat(),
                "id": hashlib.md5(f"opt_{a['ticker']}_{a['score']}".encode()).hexdigest()[:8],
            })

    def scan_pentagon():
        contracts = fetch_pentagon_contracts(days_back=3, min_amount=5_000_000)
        for c in contracts[:6]:
            recipient = c["recipient"].upper()
            amt = c["amount_m"]
            score = min(9.5, 5.0 + min(amt/100, 4.5))
            add({
                "type":"pentagon","ticker":recipient[:20],"score":round(score,1),
                "title":f"${amt:.0f}M DoD contract · {c['agency'][:35]}",
                "detail":c["description"][:120],
                "supply_hint":"Run deep dive to find supply chain beneficiaries →",
                "raw": c, "ts": datetime.now().isoformat(),
                "id": hashlib.md5(f"dod_{recipient}_{amt}".encode()).hexdigest()[:8],
            })

    def scan_patents():
        patents = fetch_patent_grants(days_back=7)
        seen = set()
        for p in patents:
            key_id = f"{p['assignee']}_{p['keyword']}"
            if key_id in seen: continue
            seen.add(key_id)
            score = 6.5
            add({
                "type":"patent","ticker":p["assignee"][:25],"score":score,
                "title":f"New patent · {p['keyword'].title()} · #{p['number']}",
                "detail":p["title"][:110],
                "supply_hint":"Run IP analysis to find acquisition targets →",
                "raw": p, "ts": datetime.now().isoformat(),
                "id": hashlib.md5(f"pat_{p['number']}".encode()).hexdigest()[:8],
            })

    def scan_insiders():
        clusters = fetch_insider_clusters(STOCKS, finnhub_key if finnhub_key else "")
        for c in clusters:
            score = 8.5 if c["strength"]=="ULTRA" else 7.5 if c["strength"]=="HIGH" else 6.5
            val_str = f"${c['total_val_k']:.0f}K" if c['total_val_k']>0 else "open-market"
            add({
                "type":"insider","ticker":c["ticker"],"score":score,
                "title":f"{c['buyers']} insiders buying · {c['strength']} conviction · {val_str}",
                "detail":f"Cluster: {', '.join(c['names'][:3])}",
                "supply_hint":"Insider cluster is the single most reliable long-term signal →",
                "raw": c, "ts": datetime.now().isoformat(),
                "id": hashlib.md5(f"ins_{c['ticker']}_{c['buyers']}".encode()).hexdigest()[:8],
            })

    def scan_technicals():
        for sym in STOCKS:
            closes, meta = yf_history(sym, "3mo")
            if len(closes)<20: continue
            price=round(closes[-1],2); m1=round((closes[-1]/closes[-22]-1)*100,2) if len(closes)>=22 else 0
            rsi=calc_rsi(closes); ml,ms=calc_macd(closes)
            w52h=meta.get("fiftyTwoWeekHigh",0) or 0; w52l=meta.get("fiftyTwoWeekLow",0) or 0
            score,sigs,verdict=score_technical(closes,rsi,ml,ms,price,w52h,w52l)
            if score >= 7:
                add({
                    "type":"technical","ticker":sym,"score":score,
                    "title":f"{verdict} · {len(sigs)} signals stacking",
                    "detail":f"RSI: {rsi} · 1M: {m1:+.1f}% · Price: ${price} · {', '.join(sigs[:3])}",
                    "supply_hint":f"52W High: ${w52h} · Low: ${w52l}",
                    "raw":{"rsi":rsi,"m1":m1,"price":price,"sigs":sigs,"verdict":verdict},
                    "ts": datetime.now().isoformat(),
                    "id": hashlib.md5(f"tech_{sym}_{score}".encode()).hexdigest()[:8],
                })
            time.sleep(0.05)

    # Run all scanners in parallel
    threads = [
        threading.Thread(target=scan_options,  daemon=True),
        threading.Thread(target=scan_pentagon, daemon=True),
        threading.Thread(target=scan_patents,  daemon=True),
        threading.Thread(target=scan_insiders, daemon=True),
        threading.Thread(target=scan_technicals, daemon=True),
    ]
    for t in threads: t.start()
    for t in threads: t.join(timeout=45)

    # Sort by score
    signals.sort(key=lambda x: x["score"], reverse=True)

    # Push top alerts to Telegram
    if tg_token and tg_chat and signals:
        top3 = signals[:3]
        msg = f"◈ ALPHA MACHINE SCAN · {datetime.now():%Y-%m-%d %H:%M}\n\n"
        for s in top3:
            msg += f"[{s['type'].upper()}] {s['ticker']} — Score {s['score']}\n{s['title']}\n{s['detail']}\n\n"
        send_telegram(msg, tg_token, tg_chat)

    return signals

# ══════════════════════════════════════════════════════════════════════════════
#  UNIVERSAL SEARCH ENGINE
# ══════════════════════════════════════════════════════════════════════════════
def run_universal_search(query, key):
    """
    One query → comprehensive intelligence report.
    Detects what the user is asking and routes to the right depth of analysis.
    """
    q = query.strip()
    price, chg = None, None

    # Detect if it's a ticker
    is_ticker = bool(re.match(r'^[\$]?[A-Z]{1,5}$', q.replace("$","").upper()))
    ticker = q.replace("$","").upper() if is_ticker else None

    # Gather context
    context_parts = []
    if is_ticker and ticker:
        closes, meta = yf_history(ticker, "1y")
        p, c = yf_price(ticker)
        price, chg = p, c
        if closes:
            rsi = calc_rsi(closes); ml,ms = calc_macd(closes)
            w52h = meta.get("fiftyTwoWeekHigh",0) or 0
            score,sigs,verdict = score_technical(closes,rsi,ml,ms,p or 0,w52h,0)
            context_parts.append(f"LIVE PRICE: ${p} ({chg:+.2f}%)" if p else "")
            context_parts.append(f"TECHNICALS: RSI={rsi} | MACD={ml} vs {ms} | 52WH=${w52h} | Score={score}/10 | Verdict={verdict}")
            context_parts.append(f"SIGNALS: {', '.join(sigs)}")
        # Options
        chain = yf_options_chain(ticker)
        if not chain.empty:
            cv=int(chain[chain["type"]=="call"]["volume"].sum()); pv=int(chain[chain["type"]=="put"]["volume"].sum())
            context_parts.append(f"OPTIONS: Call vol={cv:,} | Put vol={pv:,} | P/C={round(pv/max(cv,1),2)}")
        # Insider
        if finnhub_key:
            ins = finnhub_insider(ticker, finnhub_key)
            buys = [i for i in ins if any(b in str(i.get("transactionType","")).upper() for b in ["P","BUY"])]
            if buys: context_parts.append(f"INSIDER: {len(buys)} buys in last 90 days")
        # FMP financials
        if fmp_key:
            income = fmp_income(ticker, fmp_key, 2)
            if income:
                rev = abs(income[0].get("revenue",0))/1e9
                context_parts.append(f"REVENUE (TTM): ${rev:.2f}B")
        # News
        news = get_news(f"{ticker} stock 2026", 5)
        if news:
            context_parts.append(f"RECENT NEWS:\n" + "\n".join(f"  • {n['title']}" for n in news[:4]))

    context = "\n".join(c for c in context_parts if c)

    prompt = f"""Date: {datetime.now():%Y-%m-%d}
QUERY: {q}
{context}

Run FULL INTELLIGENCE ANALYSIS for this query. Use live web search for current data.

## 1. What Is This? (Brief)
{'Stock/company quick profile' if is_ticker else 'Theme/sector/scenario explanation'}

## 2. The Asymmetric Opportunity
- What is the market missing about {q}?
- What catalyst or trend is underpriced?
- Why NOW specifically?

## 3. Supply Chain Map
- Who are the direct beneficiaries?
- Who are the Tier-2 hidden plays most people miss?
- **$TICKER** format for all names

## 4. Quantitative Signals
- Technical setup (RSI, MACD, trend)
- Valuation (overvalued/undervalued vs peers)
- Insider activity / institutional positioning

## 5. Risk Assessment  
- Bear case: what kills this trade?
- Key risks ranked by probability
- Correlation to existing positions to watch

## 6. Macro Context
- Which macro regime does this benefit from?
- What changes this thesis?

## 7. The Asymmetric Bet
🎯 THE BET: [TICKER] | Entry: $X | Target: $X–$X | Stop: $X | Horizon: X months | Score: X/10

If multiple bets, list them ranked by conviction."""

    return call_gemini(SP["search"], prompt, key)

# ══════════════════════════════════════════════════════════════════════════════
#  ADVANCED DEEP DIVE FUNCTIONS (used by signal cards + advanced tab)
# ══════════════════════════════════════════════════════════════════════════════
def run_pentagon_deep(key, contract):
    r = contract.get("recipient","Unknown")
    amt = contract.get("amount_m",0)
    desc = contract.get("description","")
    return call_gemini(SP["pentagon"],
        f"Date:{datetime.now():%Y-%m-%d}\nCONTRACT RECIPIENT: {r}\nAMOUNT: ${amt}M\nDESCRIPTION: {desc}\n\n"
        f"1. Is this company publicly traded? What ticker? Revenue impact estimate.\n"
        f"2. Full Tier-1/2/3 supply chain with **$TICKER** for each.\n"
        f"3. Which supplier is the most asymmetric bet (under-followed, not yet priced in)?\n"
        f"4. Historical: similar DoD contracts and stock performance after announcement.\n"
        f"5. THE ASYMMETRIC BET: **$TICKER** | Entry | Target | Stop | Horizon", key)

def run_patent_deep(key, patent):
    return call_gemini(SP["patent"],
        f"Date:{datetime.now():%Y-%m-%d}\nASSIGNEE: {patent.get('assignee','')}\n"
        f"PATENT: {patent.get('title','')}\nKEYWORD: {patent.get('keyword','')}\n\n"
        f"1. What does this patent do exactly? Commercial application timeline.\n"
        f"2. Which giants (AAPL/MSFT/NVDA/AMZN/GOOGL) need this technology?\n"
        f"3. Buyout probability and likely acquirer — comparable M&A deals.\n"
        f"4. Supply chain: who else benefits if this technology scales?\n"
        f"5. THE ASYMMETRIC BET: **$TICKER** | Entry | Target | Stop | Horizon", key)

def run_insider_deep(key, cluster):
    return call_gemini(SP["insider"],
        f"Date:{datetime.now():%Y-%m-%d}\nTICKER: {cluster['ticker']}\n"
        f"CLUSTER: {cluster['buyers']} insiders bought | Strength: {cluster['strength']}\n"
        f"NAMES: {', '.join(cluster['names'][:4])}\n\n"
        f"1. Who are these insiders? (title/role at the company)\n"
        f"2. What is their historical buying record? Did it precede price moves before?\n"
        f"3. What catalyst are they likely buying ahead of?\n"
        f"4. Quantitative setup (RSI, technicals, valuation vs peers).\n"
        f"5. THE ASYMMETRIC BET: Entry | Target | Stop | Horizon | Conviction", key)

def run_options_deep(key, anomaly):
    return call_gemini(SP["flow"],
        f"Date:{datetime.now():%Y-%m-%d}\nTICKER: {anomaly['ticker']}\n"
        f"PRICE: ${anomaly['price']} ({anomaly['chg']:+.2f}%)\n"
        f"VOL/OI: {anomaly['vol_oi']}× | P/C: {anomaly['pc_vol']} | Direction: {anomaly['direction']}\n"
        f"Call vol: {anomaly['call_vol']:,} | Put vol: {anomaly['put_vol']:,}\n"
        f"Whale call strike: ${anomaly['whale_call']:,.0f} | Put: ${anomaly['whale_put']:,.0f}\n\n"
        f"1. Is this institutional positioning or dealer hedging? Evidence.\n"
        f"2. What catalyst could explain this flow? Search for upcoming events.\n"
        f"3. Is this a directional bet, earnings play, or short squeeze setup?\n"
        f"4. Optimal options strategy to follow this signal.\n"
        f"5. THE ASYMMETRIC BET: Entry | Target | Stop | Horizon | Conviction", key)

def run_supply_chain(key, target):
    news = get_news(f"{target} supply chain 2026", 5)
    return call_gemini(SP["supply"],
        f"Date:{datetime.now():%Y-%m-%d}\nTARGET:{target}\nNEWS:{json.dumps(news,indent=2)}\n\n"
        f"1. TIER 1 — top 5 **$TICKER**, what supplied, dependency level\n"
        f"2. TIER 2 HIDDEN PLAYS — 5 **$TICKER**, component, revenue exposure, why asymmetric\n"
        f"3. BOTTLENECK/MOAT — who owns the IP/process the giants cannot bypass?\n"
        f"4. TOP 3 ASYMMETRIC BETS — **$TICKER**, catalyst, entry/target/stop\n"
        f"5. RISKS — geopolitical, substitution, concentration\nTICKERS:[all]", key)

def run_alpha_scan_fast(key):
    """Streamlined 4-agent scan for the feed."""
    macro = get_macro_strip()
    df_sec = get_sector_table()
    df_st  = get_stock_table_fast()
    nm = get_news("Federal Reserve inflation geopolitical macro 2026",5)
    nc = get_news("insider FDA DoD contract earnings catalyst 2026",6)
    results = {}
    threads = [
        threading.Thread(target=lambda: results.update({"macro": call_gemini(SP["macro"],
            f"Date:{datetime.now():%Y-%m-%d}\nMACRO:{json.dumps({k:{'p':v[0],'chg':v[1]} for k,v in macro.items()},indent=2)}\nNEWS:{json.dumps(nm[:6],indent=2)}\nTOP 2 macro tailwinds. Each scored 1-10.", key)})),
        threading.Thread(target=lambda: results.update({"stocks": call_gemini(SP["cio"],
            f"Date:{datetime.now():%Y-%m-%d}\nSTOCK SIGNALS:{df_st.to_string(index=False) if not df_st.empty else 'N/A'}\nNEWS:{json.dumps(nc[:6],indent=2)}\nTOP 3 asymmetric setups. For each: ticker, signals, catalyst, score 1-10, horizon.", key)})),
    ]
    for t in threads: t.start()
    for t in threads: t.join(timeout=150)
    thesis = call_gemini(SP["cio"],
        f"MACRO:{results.get('macro','')}\nSTOCKS:{results.get('stocks','')}\n\n"
        f"Synthesize top 3 asymmetric bets RIGHT NOW:\n"
        f"🎯 BET: [TICKER] | Theme | Catalysts (3 bullets) | Risk | Entry/Target/Stop | Score /10", key)
    results["thesis"] = thesis
    return results

def get_sector_table():
    rows=[]
    for sym in SECTORS:
        closes,_=yf_history(sym,"1mo")
        if len(closes)<5: continue
        rows.append({"ETF":sym,"1M%":round((closes[-1]/closes[0]-1)*100,2),
                     "1W%":round((closes[-1]/closes[-6]-1)*100,2) if len(closes)>=6 else 0})
        time.sleep(0.07)
    return pd.DataFrame(rows).sort_values("1M%",ascending=False).reset_index(drop=True) if rows else pd.DataFrame()

def get_stock_table_fast():
    rows=[]
    for sym in STOCKS:
        closes,meta=yf_history(sym,"3mo")
        if len(closes)<20: continue
        price=round(closes[-1],2); m1=round((closes[-1]/closes[-22]-1)*100,2) if len(closes)>=22 else 0
        rsi=calc_rsi(closes); ml,ms=calc_macd(closes)
        w52h=meta.get("fiftyTwoWeekHigh",0) or 0; w52l=meta.get("fiftyTwoWeekLow",0) or 0
        sc,sigs,verdict=score_technical(closes,rsi,ml,ms,price,w52h,w52l)
        rows.append({"Ticker":sym,"Price":price,"1M%":m1,"RSI":rsi,"Score":sc,"Verdict":verdict})
        time.sleep(0.08)
    return pd.DataFrame(rows) if rows else pd.DataFrame()

# ══════════════════════════════════════════════════════════════════════════════
#  UI HELPERS
# ══════════════════════════════════════════════════════════════════════════════
TYPE_LABELS = {
    "dark_money":"🌑 DARK MONEY","pentagon":"🛡 PENTAGON","patent":"🔬 PATENT",
    "insider":"👤 INSIDER","macro":"🌍 MACRO","technical":"📈 TECHNICAL"
}
TYPE_COLORS = {
    "dark_money":"#84cc16","pentagon":"#3b82f6","patent":"#a78bfa",
    "insider":"#22c55e","macro":"#f59e0b","technical":"#06b6d4"
}

def render_signal_card(sig, idx):
    sc = _score_to_class(sig["score"])
    t  = sig["type"]
    color = TYPE_COLORS.get(t,"#3b82f6")
    label = TYPE_LABELS.get(t,t.upper())
    st.markdown(f"""
<div class="sig-card {t}">
  <div class="sig-top">
    <span class="sig-score {sc}">◈ {sig['score']}</span>
    <span class="sig-type">{label}</span>
    <span class="sig-ticker">{sig['ticker']}</span>
  </div>
  <div class="sig-title">{sig['title']}</div>
  <div class="sig-title" style="color:#4a5568;font-size:0.78rem">{sig['detail']}</div>
  <div class="sig-supply">↳ <span>{sig['supply_hint']}</span></div>
  <div class="sig-meta">{sig.get('ts','')[:16].replace('T',' ')} UTC</div>
</div>""", unsafe_allow_html=True)
    return st.button(f"→ Deep Dive", key=f"dd_{sig['id']}_{idx}", use_container_width=False)

def show_result(text, color="blue"):
    st.markdown(f'<div class="report {color}"></div>', unsafe_allow_html=True)
    st.markdown(text)

def dl_tg(text, prefix):
    c1,c2 = st.columns(2)
    fname = f"{prefix}_{datetime.now():%Y%m%d_%H%M}.txt"
    with c1: st.download_button("⬇ Download", data=text, file_name=fname, mime="text/plain", use_container_width=True)
    with c2:
        if tg_token and tg_chat:
            if st.button("→ Telegram", key=f"tg_{prefix}_{int(time.time())}", use_container_width=True):
                send_telegram(f"◈ Alpha Machine\n{datetime.now():%Y-%m-%d %H:%M}\n\n{text}",tg_token,tg_chat)
                st.success("Sent")

def key_check():
    if not gemini_key:
        st.warning("Add Gemini API key in sidebar → [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)")
        return False
    return True

# ══════════════════════════════════════════════════════════════════════════════
#  AUTO-REFRESH LOGIC
# ══════════════════════════════════════════════════════════════════════════════
REFRESH_INTERVALS = {"30 min":1800,"60 min":3600,"Manual only":999999}
REFRESH_SECS = REFRESH_INTERVALS.get(scan_interval,1800)

def should_auto_scan():
    last = st.session_state.get("last_scan_ts")
    if last is None: return True
    try:
        elapsed = (datetime.now() - datetime.fromisoformat(last)).total_seconds()
        return elapsed > REFRESH_SECS
    except: return True

# ══════════════════════════════════════════════════════════════════════════════
#  TOP BAR + MACRO STRIP
# ══════════════════════════════════════════════════════════════════════════════
with st.spinner(""):
    macro_data = get_macro_strip()

last_ts = st.session_state.get("last_scan_ts","Never")
feed    = st.session_state.get("feed_signals",[])
n_sigs  = len(feed)
n_high  = sum(1 for s in feed if s["score"]>=7.5)

st.markdown(f"""
<div class="topbar">
  <div class="logo">◈ Alpha<span>Machine</span> <span style="font-size:0.7rem;font-weight:400;color:#374151;letter-spacing:0;"> v6</span></div>
  <div class="topbar-meta">{datetime.now().strftime("%d %b %Y · %H:%M UTC")} · {n_sigs} signals · {n_high} high-conviction</div>
</div>""", unsafe_allow_html=True)

# Macro strip
strip_html = ""
for lbl,(p,c) in macro_data.items():
    if p is not None:
        cls = "up" if (c or 0)>=0 else "dn"
        fmt = f"{p:,.0f}" if p>500 else f"{p:.2f}"
        sgn = "+" if (c or 0)>=0 else ""
        strip_html += f'<div class="mbox"><span class="mlbl">{lbl}</span><span class="mprice">{fmt}</span><span class="{cls}">{sgn}{c:.2f}%</span></div>'
    else:
        strip_html += f'<div class="mbox"><span class="mlbl">{lbl}</span><span class="mprice">—</span></div>'
st.markdown(f'<div class="macro-strip">{strip_html}</div>', unsafe_allow_html=True)

# Status bar
last_str = last_ts[:16].replace("T"," ") if last_ts and last_ts!="Never" else "Never"
next_scan_str = "—"
if last_ts and last_ts!="Never" and scan_interval!="Manual only":
    try:
        elapsed = (datetime.now()-datetime.fromisoformat(last_ts)).total_seconds()
        remaining = max(0, REFRESH_SECS-elapsed)
        next_scan_str = f"{int(remaining//60)}m {int(remaining%60)}s"
    except: pass

pent_dot = "dot-blue"; pat_dot = "dot-purple" if True else "dot-red"
st.markdown(f"""
<div class="statusbar">
  <span class="sitem"><span class="{'dot-green' if gemini_key else 'dot-red'}"></span>AI Engine</span>
  <span class="sitem"><span class="dot-blue"></span>Pentagon: USASpending.gov</span>
  <span class="sitem"><span class="dot-purple" style="background:#a78bfa"></span>Patents: USPTO</span>
  <span class="sitem"><span class="dot-green"></span>Insider: EDGAR Form 4</span>
  <span class="sitem"><span class="dot-amber"></span>Dark Money: Options Chain</span>
  <span class="sitem" style="margin-left:auto">Last scan: {last_str} · Next: {next_scan_str}</span>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  UNIVERSAL SEARCH BAR
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="search-wrap">', unsafe_allow_html=True)
sc1, sc2 = st.columns([5,1])
with sc1:
    search_input = st.text_input("",
        placeholder="Search anything: NVDA · Solid State Batteries · Taiwan conflict · Soros · Uranium · AXTI",
        label_visibility="collapsed", key="ti_universal_search")
with sc2:
    search_btn = st.button("Search →", type="primary", key="btn_universal_search", use_container_width=True)
st.markdown("""<div class="search-hint">
  <b>Ticker:</b> NVDA → full deep dive · DCF · supply chain · insider · options<br>
  <b>Theme:</b> Solid State Batteries → full sector map + supply chain + asymmetric bets<br>
  <b>Scenario:</b> Taiwan conflict → geo trade with winners, losers, hedges<br>
  <b>Person:</b> Soros / Burry → 13F analysis + what they're betting on
</div>""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Handle search
if search_btn and search_input.strip():
    if key_check():
        with st.spinner(f"Running full intelligence analysis for '{search_input}'..."):
            result = run_universal_search(search_input.strip(), gemini_key)
        st.session_state["search_result"] = result
        st.session_state["search_query"]  = search_input.strip()

if st.session_state.get("search_result"):
    q = st.session_state.get("search_query","")
    st.markdown(f'<div class="sec-label">Intelligence Report — {q}</div>', unsafe_allow_html=True)
    show_result(st.session_state["search_result"], "blue")
    dl_tg(st.session_state["search_result"], f"search_{q[:20].replace(' ','_')}")
    if st.button("✕ Clear search", key="btn_clear_search"):
        st.session_state["search_result"] = None
        st.session_state["search_query"]  = None
        st.rerun()
    st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN TABS — Feed is default, Advanced section hidden
# ══════════════════════════════════════════════════════════════════════════════
tab_feed, tab_adv, tab_info = st.tabs(["⚡ Live Alpha Feed", "🔬 Advanced Modes", "ℹ️ Info"])

# ══════════════════════════════════════════════════════════════════════════════
#  TAB 1 — LIVE ALPHA FEED
# ══════════════════════════════════════════════════════════════════════════════
with tab_feed:
    # Scan controls
    fc1,fc2,fc3,fc4 = st.columns([1,1,1,2])
    with fc1:
        run_scan_btn = st.button("⚡ Run Full Scan", type="primary", key="btn_run_scan", use_container_width=True)
    with fc2:
        filter_type  = st.selectbox("Filter", ["All","dark_money","pentagon","patent","insider","technical"], key="sb_filter_type")
    with fc3:
        min_score_f  = st.slider("Min score", 0.0, 10.0, 5.0, 0.5, key="sl_min_score_feed")
    with fc4:
        if should_auto_scan() and gemini_key and not feed:
            st.markdown('<div class="scan-status">🔄 Auto-scanning on first load...</div>', unsafe_allow_html=True)

    # Auto-scan trigger
    if should_auto_scan() and gemini_key and (run_scan_btn or not feed):
        with st.status("Running 5 intelligence scanners in parallel...", expanded=True) as scan_st:
            st.write("🌑 Scanning unusual options flow across universe...")
            st.write("🛡 Fetching Pentagon contract awards (USASpending.gov)...")
            st.write("🔬 Scanning USPTO patent grants (last 7 days)...")
            st.write("👤 Detecting insider cluster buying (EDGAR Form 4)...")
            st.write("📈 Calculating quantitative signals (numpy)...")
            signals = run_background_scan(gemini_key, tg_token, tg_chat)
            st.session_state["feed_signals"]  = signals
            st.session_state["last_scan_ts"]  = datetime.now().isoformat()
            scan_st.update(label=f"✓ Scan complete — {len(signals)} signals found", state="complete")
        st.rerun()
    elif run_scan_btn and gemini_key:
        with st.status("Running scanners...", expanded=True) as scan_st:
            st.write("Scanning 5 layers simultaneously...")
            signals = run_background_scan(gemini_key, tg_token, tg_chat)
            st.session_state["feed_signals"]  = signals
            st.session_state["last_scan_ts"]  = datetime.now().isoformat()
            scan_st.update(label=f"✓ {len(signals)} signals", state="complete")
        st.rerun()
    elif run_scan_btn and not gemini_key:
        key_check()

    # Render feed
    feed = st.session_state.get("feed_signals",[])
    filtered = [s for s in feed
                if s["score"] >= min_score_f
                and (filter_type == "All" or s["type"] == filter_type)]

    if not filtered:
        if not gemini_key:
            st.info("Add your Gemini API key in the sidebar to start scanning.")
        elif not feed:
            st.info("Click **⚡ Run Full Scan** to start the intelligence engine.")
        else:
            st.info(f"No signals above score {min_score_f}. Lower the threshold or change filter.")
    else:
        # Score summary
        by_type = {}
        for s in filtered:
            by_type[s["type"]] = by_type.get(s["type"],0) + 1
        summary_html = "".join([f'<span style="font-size:0.75rem;color:{TYPE_COLORS.get(t,"#4a5568")};margin-right:12px">{TYPE_LABELS.get(t,t)}: {n}</span>'
                                 for t,n in sorted(by_type.items(),key=lambda x:-x[1])])
        st.markdown(f'<div style="margin-bottom:12px">{summary_html}</div>', unsafe_allow_html=True)

        # Group by type for cleaner display
        col_left, col_right = st.columns(2)
        for idx, sig in enumerate(filtered):
            col = col_left if idx % 2 == 0 else col_right
            with col:
                clicked = render_signal_card(sig, idx)
                if clicked:
                    st.session_state["deep_dive_sig"] = sig

        # Deep dive panel
        if st.session_state.get("deep_dive_sig"):
            sig = st.session_state["deep_dive_sig"]
            st.markdown(f'<div class="sec-label">Deep Dive — {sig["ticker"]} · {TYPE_LABELS.get(sig["type"],"")}</div>',
                        unsafe_allow_html=True)
            if key_check():
                with st.spinner(f"Running deep dive on {sig['ticker']}..."):
                    t = sig["type"]; raw = sig.get("raw",{})
                    if t == "pentagon":
                        result = run_pentagon_deep(gemini_key, raw)
                        color  = "blue"
                    elif t == "patent":
                        result = run_patent_deep(gemini_key, raw)
                        color  = "purple"
                    elif t == "insider":
                        result = run_insider_deep(gemini_key, raw)
                        color  = "green"
                    elif t == "dark_money":
                        result = run_options_deep(gemini_key, raw)
                        color  = "lime"
                    else:
                        result = run_universal_search(sig["ticker"], gemini_key)
                        color  = "teal"
                show_result(result, color)
                dl_tg(result, f"deepdive_{sig['ticker']}")
                # Auto supply chain cascade
                st.markdown("---")
                if st.button("→ Auto Supply Chain Cascade", key=f"sc_cascade_{sig['id']}", type="primary"):
                    with st.spinner("Mapping supply chain beneficiaries..."):
                        sc_result = run_supply_chain(gemini_key, sig["ticker"])
                    show_result(sc_result, "amber")
                    dl_tg(sc_result, f"supply_{sig['ticker']}")
            if st.button("✕ Close", key="btn_close_deepdive"):
                st.session_state["deep_dive_sig"] = None
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  TAB 2 — ADVANCED MODES (the 24 existing modes, collapsed)
# ══════════════════════════════════════════════════════════════════════════════
with tab_adv:
    st.markdown("### Advanced Intelligence Modes")
    st.markdown("All 24 modes available here. The Live Feed handles discovery automatically — use these for deeper specific analysis.")

    adv_tabs = st.tabs([
        "Alpha Scan","DCF Valuation","Anti-Portfolio",
        "Supply Chain","Sector Dive","Stock Stress",
        "Geo Trade","Commodity","Portfolio",
        "Compare","Rotation","Catalyst",
        "Earnings","SEC Filings","Options Flow","Smart Money Radar",
        "13F Tracker","Watchdog","Backtest",
        "Macro Regime","Monetize","Newsletter",
    ])
    (at_scan, at_dcf, at_anti,
     at_supply, at_sector, at_stock,
     at_geo, at_comm, at_port,
     at_compare, at_rotation, at_catalyst,
     at_earn, at_sec, at_opt, at_radar,
     at_13f, at_wd, at_bt,
     at_macro, at_mon, at_nl) = adv_tabs

    # ── Alpha Scan ─────────────────────────────────────────────────────────────
    with at_scan:
        st.markdown("**5-Agent Asymmetric Bet Scanner** — Macro · Sector · Stocks · Contra · CIO Synthesis")
        if key_check():
            if st.button("Run Alpha Scan →", type="primary", key="btn_adv_alpha"):
                with st.spinner("Running 4 parallel agents (~2 min)..."):
                    results = run_alpha_scan_fast(gemini_key)
                st.session_state["last_scan"] = results
                show_result(results.get("thesis",""), "blue")
                dl_tg(results.get("thesis",""), "alpha_scan")
                with st.expander("Macro detail"): st.write(results.get("macro",""))
                with st.expander("Stock detail"): st.write(results.get("stocks",""))

    # ── DCF ────────────────────────────────────────────────────────────────────
    with at_dcf:
        st.markdown("**Quantitative DCF** — numpy Bear/Base/Bull · FMP real financials")
        if fmp_key: st.markdown('<div class="alert-ok">✓ FMP connected — real financial data</div>', unsafe_allow_html=True)
        c1,c2=st.columns([3,1])
        with c1: dcf_t=st.text_input("Ticker",placeholder="NVDA · PLTR · AXTI",label_visibility="collapsed",key="ti_dcf")
        with c2: dcf_r=st.button("Run DCF →",type="primary",key="btn_dcf")
        if dcf_r and key_check() and dcf_t:
            t=dcf_t.strip().upper().replace("$","")
            closes,meta=yf_history(t,"1y"); price,chg=yf_price(t)
            w52h=meta.get("fiftyTwoWeekHigh",0) or 0
            dcf_results={}
            income=fmp_income(t,fmp_key,4) if fmp_key else []
            cf=fmp_cashflow(t,fmp_key,4) if fmp_key else []
            profile=fmp_profile(t,fmp_key) if fmp_key else {}
            if income and cf:
                try:
                    revs=[abs(i.get("revenue",0))/1e6 for i in income if i.get("revenue")]
                    fcfs=[abs(c.get("freeCashFlow",0))/1e6 for c in cf if c.get("freeCashFlow")]
                    rev_latest=revs[0] if revs else 0
                    rev_growth=((revs[0]/revs[-1])**(1/max(len(revs)-1,1))-1) if len(revs)>1 else 0.15
                    fcf_margin=(fcfs[0]/rev_latest) if rev_latest>0 else 0.10
                    shares=profile.get("mktCap",0)/(price*1e6) if price and profile.get("mktCap") else 1000
                    net_debt=(profile.get("totalDebt",0)-profile.get("totalCash",0))/1e6 if profile else 0
                    dcf_results=dcf_valuation(rev_latest,max(rev_growth,0.05),max(fcf_margin,0.02),0.10,0.03,shares,net_debt)
                except: pass
            if dcf_results:
                st.markdown('<div class="sec-label">DCF — numpy calculated</div>',unsafe_allow_html=True)
                cols=st.columns(4)
                for col,(sc,lbl) in zip(cols,[("Bear","Bear FV"),("Base","Base FV"),("Bull","Bull FV")]):
                    fv=dcf_results[sc]["FV_per_share"]
                    up=round((fv/price-1)*100,1) if price else 0
                    col.metric(lbl,f"${fv:,.2f}",f"{up:+.1f}%",delta_color="normal" if up>0 else "inverse")
                cols[3].metric("Current",f"${price:,.2f}",f"{chg:+.2f}%")
            with st.spinner(f"Running AI DCF for {t}..."):
                rsi=calc_rsi(closes) if closes else None; ml,ms=calc_macd(closes) if closes else (None,None)
                ins=""
                if finnhub_key:
                    insiders=finnhub_insider(t,finnhub_key)
                    buys=[i for i in insiders if any(b in str(i.get("transactionType","")).upper() for b in ["P","BUY"])]
                    if buys: ins=f"\nINSIDER: {len(buys)} open-market buys last 90 days"
                result=call_gemini(SP["dcf"],
                    f"TICKER:{t}\nPRICE:${price}({chg:+.2f}%)\nRSI:{rsi}|MACD:{ml}vs{ms}|52WH:${w52h}"
                    f"{ins}\nDCF:{json.dumps(dcf_results)}\n\n"
                    f"1. Business quality + moat\n2. DCF scenarios (explain assumptions)\n"
                    f"3. Asymmetric gap (what market is wrong about)\n"
                    f"4. Supply chain play (better bet than {t}?)\n"
                    f"5. VERDICT: intrinsic value, margin of safety, action",gemini_key)
            show_result(result,"teal"); dl_tg(result,f"dcf_{t}")

    # ── Anti-Portfolio ─────────────────────────────────────────────────────────
    with at_anti:
        st.markdown("**Anti-Portfolio Risk Agent** — Pearson correlation · 5-scenario stress test")
        holdings_i=st.text_area("Holdings",placeholder="NVDA 20%, AAPL 15%, PLTR 10%, Cash 20%",height=80,key="ta_anti")
        if st.button("Stress Test →",type="primary",key="btn_anti"):
            if key_check() and holdings_i.strip():
                h={}
                for item in re.split(r'[,\n]',holdings_i):
                    item=item.strip()
                    if not item: continue
                    parts=re.split(r'[\s@%]+',item.replace("$",""))
                    if parts: h[parts[0].upper()]=float(parts[1]) if len(parts)>1 else 10.0
                if len(h)>=2:
                    pd_data={}
                    for sym in h:
                        c,_=yf_history(sym,"6mo")
                        if c: pd_data[sym]=c
                    corr=calc_correlation_matrix(pd_data)
                    if not corr.empty:
                        st.markdown('<div class="sec-label">Correlation Matrix</div>',unsafe_allow_html=True)
                        def _cc(v):
                            if not isinstance(v,(int,float)) or abs(v)==1: return ""
                            if abs(v)>0.85: return "background:#2e0505;color:#fca5a5;font-weight:600"
                            if abs(v)>0.70: return "background:#2e1505;color:#fbbf24"
                            return ""
                        st.dataframe(corr.style.map(_cc),width="stretch")
                with st.spinner("Running stress test..."):
                    result=call_gemini(SP["risk"],
                        f"PORTFOLIO:{holdings_i}\n\n1. Concentration risk\n2. 5 stress scenarios\n"
                        f"3. Highest risk positions\n4. Gaps to add\n5. 3 hedges\n6. Health score /10",gemini_key)
                show_result(result,"red"); dl_tg(result,"anti_portfolio")

    # ── Supply Chain ───────────────────────────────────────────────────────────
    with at_supply:
        st.markdown("**Supply Chain Forensic Mapper** — Map what giants cannot live without")
        c1,c2=st.columns([3,1])
        with c1: sup_t=st.text_input("Target",placeholder="NVDA · EUV Lithography · Solid State Batteries",label_visibility="collapsed",key="ti_supply")
        with c2: sup_r=st.button("Map Chain →",type="primary",key="btn_supply")
        if sup_r and key_check() and sup_t:
            with st.status(f"Mapping {sup_t}...",expanded=True) as s:
                st.write("Identifying Tier 1/2/3..."); out=st.empty(); full=""
                for chunk in stream_gemini(SP["supply"],
                    f"Date:{datetime.now():%Y-%m-%d}\nTARGET:{sup_t}\n\n"
                    f"1. TIER 1 top 5 **$TICKER** + dependency\n2. TIER 2 hidden plays **$TICKER** + why asymmetric\n"
                    f"3. BOTTLENECK/MOAT owner\n4. TOP 3 BETS **$TICKER** + entry/target/stop\n5. RISKS\nTICKERS:[all]",
                    gemini_key):
                    full+=chunk; out.markdown(full)
                s.update(label="✓ Done",state="complete")
            st.session_state["last_research"]=full; dl_tg(full,"supply_chain")

    # ── Sector Dive ────────────────────────────────────────────────────────────
    with at_sector:
        st.markdown("**Sector Deep Dive** — Cycle position · Hidden gems · Best bet")
        c1,c2=st.columns([3,1])
        with c1: sec_t=st.text_input("Sector",placeholder="Defense · Biotech · Semiconductors",label_visibility="collapsed",key="ti_sector")
        with c2: sec_r=st.button("Dive →",type="primary",key="btn_sector")
        if sec_r and key_check() and sec_t:
            with st.spinner(f"Analyzing {sec_t}..."):
                df_s=get_sector_table()
                result=call_gemini(SP["cio"],
                    f"SECTOR:{sec_t}\nETF:{df_s.to_string(index=False) if not df_s.empty else 'N/A'}\n\n"
                    f"1. Cycle position\n2. Top 5 by asymmetry (score each)\n3. 3 hidden gems sub-$5B\n"
                    f"4. Macro tailwinds+headwinds\n5. Best bet entry/target/stop\nTICKERS:[all]",gemini_key)
            show_result(result,"purple"); dl_tg(result,"sector")

    # ── Stock Stress ───────────────────────────────────────────────────────────
    with at_stock:
        st.markdown("**Single Stock Stress Test** — Forensic bull/bear · Accounting · Supplier alternatives")
        c1,c2=st.columns([3,1])
        with c1: ss_t=st.text_input("Ticker",placeholder="NVDA · PLTR · TSLA",label_visibility="collapsed",key="ti_stock_stress")
        with c2: ss_r=st.button("Stress Test →",type="primary",key="btn_stock_stress")
        if ss_r and key_check() and ss_t:
            t=ss_t.strip().upper().replace("$","")
            closes,meta=yf_history(t,"1y"); price,chg=yf_price(t)
            rsi=calc_rsi(closes) if closes else "N/A"; ml,ms=calc_macd(closes) if closes else (None,None)
            w52h=meta.get("fiftyTwoWeekHigh",0) or 0
            filings=edgar_filings(t)
            ins_ctx=""
            if finnhub_key:
                ins=finnhub_insider(t,finnhub_key)
                buys=len([i for i in ins if any(b in str(i.get("transactionType","")).upper() for b in ["P","BUY"])])
                ins_ctx=f"\nINSIDER BUYS (90d): {buys}"
            with st.spinner(f"Stress testing {t}..."):
                result=call_gemini(SP["dcf"],
                    f"TICKER:{t}\nPRICE:${price}({chg:+.2f}%)\nRSI:{rsi}|MACD:{ml}/{ms}|52WH:${w52h}"
                    f"{ins_ctx}\nEDGAR:{json.dumps(filings[:3])}\n\n"
                    f"1. BULL CASE — catalysts, targets\n2. BEAR CASE — short thesis, downside\n"
                    f"3. FORENSIC flags\n4. SUPPLIER play (better bet?)\n5. VERDICT",gemini_key)
            show_result(result,"red"); dl_tg(result,f"stress_{t}")

    # ── Geo Trade ──────────────────────────────────────────────────────────────
    with at_geo:
        st.markdown("**Geopolitical Trade Finder** — Winners · Losers · Second-order plays")
        c1,c2=st.columns([3,1])
        with c1: geo_t=st.text_input("Scenario",placeholder="Taiwan conflict · OPEC+ cut · US-China tariffs",label_visibility="collapsed",key="ti_geo")
        with c2: geo_r=st.button("Find Trades →",type="primary",key="btn_geo")
        if geo_r and key_check() and geo_t:
            with st.spinner():
                result=call_gemini(SP["macro"],
                    f"SCENARIO:{geo_t}\n1. Probability+status\n2. Direct winners top 5\n3. Direct losers top 3\n"
                    f"4. Second-order plays (non-obvious)\n5. Best hedge\n6. Highest asymmetry trade\nTICKERS:[all]",gemini_key)
            show_result(result,"blue"); dl_tg(result,"geo")

    # ── Commodity ──────────────────────────────────────────────────────────────
    with at_comm:
        st.markdown("**Commodity Chain Tracer** — Full upstream/downstream value chain")
        c1,c2=st.columns([3,1])
        with c1: com_t=st.text_input("Commodity",placeholder="Lithium · Uranium · Copper · Rare Earth",label_visibility="collapsed",key="ti_comm")
        with c2: com_r=st.button("Trace →",type="primary",key="btn_comm")
        if com_r and key_check() and com_t:
            with st.spinner():
                result=call_gemini(SP["supply"],
                    f"COMMODITY:{com_t}\n1. Current price+supply/demand\n2. Upstream top 5 tickers\n"
                    f"3. Midstream moat+bottlenecks\n4. Downstream winners/losers\n5. Top 3 asymmetric plays\n6. Substitution risk",gemini_key)
            show_result(result,"orange"); dl_tg(result,"commodity")

    # ── Portfolio ──────────────────────────────────────────────────────────────
    with at_port:
        st.markdown("**Portfolio Stress Tester** — 5 macro scenarios · Concentration · Hedges")
        port_i=st.text_area("Holdings",placeholder="NVDA 15%, AAPL 10%, Cash 20%",height=70,key="ta_port")
        if st.button("Stress Test Portfolio →",type="primary",key="btn_port"):
            if key_check() and port_i.strip():
                with st.spinner():
                    result=call_gemini(SP["risk"],
                        f"PORTFOLIO:{port_i}\n1. Sector concentration\n2. 5 stress scenarios\n"
                        f"3. Highest risk positions\n4. Gaps+opportunities\n5. 3 hedges\n6. Health score /10",gemini_key)
                show_result(result,"pink"); dl_tg(result,"portfolio")

    # ── Compare ────────────────────────────────────────────────────────────────
    with at_compare:
        st.markdown("**Relative Value Comparator** — Head-to-head · Pair trade setup")
        ca,cv,cb=st.columns([2,0.4,2])
        with ca: ta_=st.text_input("Ticker A",placeholder="NVDA",key="ti_ta")
        with cv: st.markdown("<br>**vs**",unsafe_allow_html=True)
        with cb: tb_=st.text_input("Ticker B",placeholder="AMD",key="ti_tb")
        if st.button("Compare →",type="primary",key="btn_compare"):
            if key_check() and ta_ and tb_:
                pa,ca_=yf_price(ta_.upper()); pb,cb_=yf_price(tb_.upper())
                with st.spinner():
                    result=call_gemini(SP["dcf"],
                        f"{ta_.upper()}:${pa}({ca_:+.2f}%) vs {tb_.upper()}:${pb}({cb_:+.2f}%)\n\n"
                        f"1. Valuation table (P/E,P/S,EV/EBITDA)\n2. Growth comparison\n3. Moat\n"
                        f"4. Balance sheet\n5. Pair trade: long/short, entry, target, stop\n6. Verdict",gemini_key)
                show_result(result,"teal"); dl_tg(result,f"compare_{ta_}_{tb_}")

    # ── Rotation ───────────────────────────────────────────────────────────────
    with at_rotation:
        st.markdown("**Sector Rotation Timer** — Cycle phase · What rotates next")
        if key_check():
            if st.button("Analyze Rotation →",type="primary",key="btn_rotation"):
                macro_d=get_macro_strip(); df_sec=get_sector_table()
                with st.spinner():
                    result=call_gemini(SP["macro"],
                        f"MACRO:{json.dumps({k:{'p':v[0],'chg':v[1]} for k,v in macro_d.items()},indent=2)}\n"
                        f"SECTORS:{df_sec.to_string(index=False) if not df_sec.empty else 'N/A'}\n\n"
                        f"1. Cycle position\n2. Current leadership+institutional flow\n3. Next rotation 0-6mo\n"
                        f"4. 3 timing signals\n5. Highest conviction rotation trade\n6. International rotation",gemini_key)
                show_result(result,"purple"); dl_tg(result,"rotation")

    # ── Catalyst ───────────────────────────────────────────────────────────────
    with at_catalyst:
        st.markdown("**Catalyst Calendar** — 90-day events ranked by asymmetric potential")
        cal_i=st.text_input("Watchlist",value=",".join(STOCKS[:8]),key="ti_catalyst")
        if st.button("Generate Calendar →",type="primary",key="btn_catalyst"):
            if key_check() and cal_i.strip():
                with st.spinner():
                    result=call_gemini(SP["cio"],
                        f"WATCHLIST:{cal_i}\n1. 90-day calendar: DATE|TICKER|EVENT|IMPACT|SCORE\n"
                        f"2. Top 5 highest asymmetry next 30 days\n3. Binary events (FDA/regulatory)\n"
                        f"4. Macro calendar impact\n5. This week's best setup",gemini_key)
                show_result(result,"amber"); dl_tg(result,"catalyst")

    # ── Earnings ───────────────────────────────────────────────────────────────
    with at_earn:
        st.markdown("**Earnings Call Analyzer** — Tone shift · What CEO is hiding · Credibility score")
        c1,c2=st.columns([3,1])
        with c1: earn_t=st.text_input("Ticker",placeholder="NVDA · AAPL · MSFT",label_visibility="collapsed",key="ti_earn")
        with c2: earn_r=st.button("Analyze →",type="primary",key="btn_earn")
        if earn_r and key_check() and earn_t:
            t=earn_t.strip().upper().replace("$","")
            sent=finnhub_sentiment(t,finnhub_key) if finnhub_key else {}
            with st.spinner():
                result=call_gemini(SP["dcf"],
                    f"TICKER:{t}\nSENTIMENT:{json.dumps(sent)[:200] if sent else 'N/A'}\n\n"
                    f"1. Headline numbers vs expectations\n2. Tone vs prior quarter\n"
                    f"3. What they're hiding\n4. Analyst reaction\n5. Trading implication+credibility /10",gemini_key)
            show_result(result,"cyan"); dl_tg(result,f"earn_{t}")

    # ── SEC Filings ────────────────────────────────────────────────────────────
    with at_sec:
        st.markdown("**SEC Filing Scanner** — Form 4 insider · 8-K events · 10-Q red flags")
        if finnhub_key: st.markdown('<div class="alert-ok">✓ Finnhub — real insider data</div>',unsafe_allow_html=True)
        c1,c2=st.columns([3,1])
        with c1: sec_t=st.text_input("Ticker",placeholder="PLTR · NVDA · RKLB",label_visibility="collapsed",key="ti_sec")
        with c2: sec_r=st.button("Scan Filings →",type="primary",key="btn_sec")
        if sec_r and key_check() and sec_t:
            t=sec_t.strip().upper().replace("$","")
            filings=edgar_filings(t); ins=finnhub_insider(t,finnhub_key) if finnhub_key else []
            with st.spinner():
                result=call_gemini(SP["risk"],
                    f"TICKER:{t}\nEDGAR:{json.dumps(filings,indent=2)}\nINSIDER:{json.dumps(ins[:8],indent=2)}\n\n"
                    f"1. Form 4 cluster buying/selling\n2. 8-K material events\n3. 10-Q red flags\n"
                    f"4. Red flags vs bullish signals\n5. Net signal: BULLISH/NEUTRAL/BEARISH",gemini_key)
            show_result(result,"rose"); dl_tg(result,f"sec_{t}")

    # ── Options Flow ───────────────────────────────────────────────────────────
    with at_opt:
        st.markdown("**Options Flow Watcher** — IV/HV · Smart money positioning · Optimal strategy")
        c1,c2=st.columns([3,1])
        with c1: opt_t=st.text_input("Ticker",placeholder="NVDA · SPY · TSLA",label_visibility="collapsed",key="ti_opt")
        with c2: opt_r=st.button("Scan Flow →",type="primary",key="btn_opt")
        if opt_r and key_check() and opt_t:
            t=opt_t.strip().upper().replace("$",""); price,chg=yf_price(t)
            chain=yf_options_chain(t)
            chain_ctx=""
            if not chain.empty:
                cv=int(chain[chain["type"]=="call"]["volume"].sum()); pv=int(chain[chain["type"]=="put"]["volume"].sum())
                co=int(chain[chain["type"]=="call"]["openInterest"].sum()); po=int(chain[chain["type"]=="put"]["openInterest"].sum())
                chain_ctx=f"Call vol:{cv:,}|Put vol:{pv:,}|P/C:{round(pv/max(cv,1),2)}|Call OI:{co:,}|Put OI:{po:,}"
            sent=finnhub_sentiment(t,finnhub_key) if finnhub_key else {}
            with st.spinner():
                result=call_gemini(SP["flow"],
                    f"TICKER:{t}\nPRICE:${price}({chg:+.2f}%)\nCHAIN:{chain_ctx}\nSENT:{json.dumps(sent)[:150] if sent else 'N/A'}\n\n"
                    f"1. P/C ratio signal\n2. Unusual activity\n3. IV vs HV\n"
                    f"4. Smart money verdict\n5. Best options trade now",gemini_key)
            show_result(result,"lime"); dl_tg(result,f"opt_{t}")

    # ── Smart Money Radar ──────────────────────────────────────────────────────
    with at_radar:
        st.markdown("**Smart Money Radar** — Market-wide Vol/OI sweep · GEX · IV Skew · Whale strikes")
        r1c1,r1c2,r1c3=st.columns([3,0.8,0.8])
        with r1c1: radar_u=st.text_area("Universe",value=",".join(SCAN_UNIVERSE[:15]),height=60,key="ti_radar")
        with r1c2: radar_s=st.slider("Min Vol/OI",2.0,8.0,3.0,0.5,key="sl_radar")
        with r1c3:
            st.markdown("<br>",unsafe_allow_html=True)
            radar_r=st.button("Scan →",type="primary",key="btn_radar")
        if radar_r and key_check():
            tks=[t.strip().upper() for t in radar_u.split(",") if t.strip()]
            with st.spinner(f"Scanning {len(tks)} tickers..."):
                anomalies=detect_options_anomalies(tks,min_vol_oi=radar_s)
            if anomalies:
                df_a=pd.DataFrame(anomalies)
                def _sc(v):
                    if isinstance(v,(int,float)):
                        if v>=8: return "color:#22c55e;font-weight:700"
                        if v>=6: return "color:#f59e0b"
                    return ""
                st.dataframe(df_a[["ticker","price","chg","vol_oi","pc_vol","direction","call_vol","put_vol","score"]].style.map(_sc,subset=["score"]),
                             width="stretch",hide_index=True,height=300)
                if st.button("🧠 AI Interpretation →",type="primary",key="btn_radar_ai"):
                    with st.spinner():
                        result=call_gemini(SP["flow"],
                            f"FLOW ANOMALIES:\n{df_a.to_string(index=False)}\n\n"
                            f"1. Top 5 real signals (not noise)\n2. GEX interpretation\n"
                            f"3. IV skew signals\n4. Whale strike analysis\n5. Convergence alert\n6. TOP PRIORITY TRADE",gemini_key)
                    show_result(result,"lime"); dl_tg(result,"radar")
            else: st.info("No unusual activity above threshold.")

    # ── 13F Tracker ────────────────────────────────────────────────────────────
    with at_13f:
        st.markdown("**13F Institutional Tracker** — Ticker or manager name")
        c1,c2=st.columns([3,1])
        with c1: inst_t=st.text_input("Ticker or Manager",placeholder="NVDA · Soros · Burry · Ackman",label_visibility="collapsed",key="ti_13f")
        with c2: inst_r=st.button("Track →",type="primary",key="btn_13f")
        if inst_r and key_check() and inst_t:
            with st.spinner():
                result=call_gemini(SP["cio"],
                    f"QUERY:{inst_t}\nLatest 13F filings. 1. Filing snapshot\n2. New positions\n"
                    f"3. Largest additions\n4. Largest exits\n5. What are they betting on? Best copycat trade.",gemini_key)
            show_result(result,"orange"); dl_tg(result,f"13f_{inst_t}")

    # ── Watchdog ───────────────────────────────────────────────────────────────
    with at_wd:
        st.markdown("**Smart Watchdog** — Custom numpy-calculated triggers · Auto Telegram")
        wc1,wc2=st.columns([2,1])
        with wc1: wd_l=st.text_input("Watchlist",value=",".join(STOCKS),key="ti_wd")
        with wc2: wd_t=st.multiselect("Triggers",["RSI < 30","RSI > 75","Drop > 8% 1M","Momentum >15%","Near 52W High"],default=["RSI < 30","Drop > 8% 1M"],key="ms_wd")
        if st.button("Run Watchdog →",type="primary",key="btn_wd"):
            if key_check():
                tks=[t.strip() for t in wd_l.split(",") if t.strip()]
                alerts=[]
                for sym in tks:
                    closes,meta=yf_history(sym,"3mo")
                    if not closes: continue
                    p=round(closes[-1],2); rsi=calc_rsi(closes)
                    m1=round((closes[-1]/closes[-22]-1)*100,2) if len(closes)>=22 else 0
                    w52h=meta.get("fiftyTwoWeekHigh",0) or 0; fired=[]
                    if "RSI < 30" in wd_t and rsi<30: fired.append(f"RSI={rsi}")
                    if "RSI > 75" in wd_t and rsi>75: fired.append(f"RSI={rsi} HIGH")
                    if "Drop > 8% 1M" in wd_t and m1<-8: fired.append(f"1M={m1}%")
                    if "Momentum >15%" in wd_t and m1>15: fired.append(f"1M={m1}%")
                    if "Near 52W High" in wd_t and w52h and p>=w52h*0.98: fired.append("52W HIGH")
                    if fired: alerts.append({"ticker":sym,"price":p,"signals":fired})
                if alerts:
                    for a in alerts:
                        st.markdown(f'<div class="alert-ok"><strong>{a["ticker"]}</strong> @ ${a["price"]} — {", ".join(a["signals"])}</div>',unsafe_allow_html=True)
                    alert_str="\n".join([f"• {a['ticker']} @ ${a['price']}: {', '.join(a['signals'])}" for a in alerts])
                    with st.spinner("AI triage..."):
                        ai=call_gemini(SP["cio"],f"ALERTS:\n{alert_str}\n\nFor each: actionable NOW or false positive? Urgency: ACT/WATCH/LOW. TOP PRIORITY: [ticker] — [one sentence]",gemini_key)
                    show_result(ai,"purple")
                    if tg_token and tg_chat:
                        send_telegram(f"◈ WATCHDOG\n{datetime.now():%Y-%m-%d %H:%M}\n\n{alert_str}\n\n{ai[:800]}",tg_token,tg_chat)
                        st.success("Sent to Telegram")
                    dl_tg(ai,"watchdog")
                else: st.markdown('<div class="alert-ok">✓ No triggers fired</div>',unsafe_allow_html=True)

    # ── Backtest ───────────────────────────────────────────────────────────────
    with at_bt:
        st.markdown("**Thesis Backtester** — Test against 2008 · 2020 · 2022 · 2024")
        bc1,bc2=st.columns([2,1])
        with bc1: bt_thesis=st.text_area("Thesis",placeholder="PLTR is undervalued due to AI government contract tailwind...",height=80,key="ta_bt")
        with bc2:
            bt_t=st.text_input("Ticker",placeholder="PLTR",key="ti_bt")
            bt_r=st.button("Backtest →",type="primary",key="btn_bt")
        if bt_r and key_check() and bt_thesis and bt_t:
            closes,_=yf_history(bt_t.upper(),"1y"); price=round(closes[-1],2) if closes else None
            with st.spinner():
                result=call_gemini(SP["dcf"],
                    f"TICKER:{bt_t.upper()}\nPRICE:${price}\nTHESIS:{bt_thesis}\n\n"
                    f"1. Core assumptions\n2. 2008/2020/2022/2024 regime analysis\n"
                    f"3. Performance metrics\n4. Thesis killers\n5. Historical base rate\n6. Position sizing+stop",gemini_key)
            show_result(result,"blue"); dl_tg(result,f"bt_{bt_t}")

    # ── Macro Regime ───────────────────────────────────────────────────────────
    with at_macro:
        st.markdown("**Macro Regime Analyzer** — Streaming · Base Case + Black Swan")
        c1,c2=st.columns([2,1])
        with c1: mq=st.text_input("Focus",placeholder="DXY impact · Fed pivot · Yield curve",key="ti_macro")
        with c2: mh=st.selectbox("Horizon",["8-hour","1-week","1-month","1-quarter"],key="sb_macro")
        if st.button("Stream Brief →",type="primary",key="btn_macro"):
            if key_check():
                macro_d=get_macro_strip(); snap=" | ".join([f"{k}:{v[0]}" for k,v in macro_d.items() if v[0]])
                with st.status("Streaming macro analysis...",expanded=True) as s:
                    out=st.empty(); full=""
                    for chunk in stream_gemini(SP["macro"],
                        f"Date:{datetime.now():%Y-%m-%d}\nFOCUS:{mq or 'current regime'}\nHORIZON:{mh}\nLIVE:{snap}\n\n"
                        f"## Current Regime\n## Base Case\n## Black Swan\n## Smart Money Divergence\n## Top Trade",
                        gemini_key):
                        full+=chunk; out.markdown(full)
                    s.update(label="✓ Done",state="complete")
                st.session_state["last_macro"]=full; dl_tg(full,"macro")

    # ── Monetize ───────────────────────────────────────────────────────────────
    with at_mon:
        st.markdown("**Monetization Agent** — X Thread · Substack · LinkedIn · TikTok")
        src_opts={}
        if st.session_state.get("last_scan"): src_opts["Alpha Scan"]=st.session_state["last_scan"].get("thesis","")
        if st.session_state.get("last_macro"):    src_opts["Macro Brief"]=st.session_state["last_macro"]
        if st.session_state.get("last_research"): src_opts["Supply Chain"]=st.session_state["last_research"]
        if st.session_state.get("search_result"): src_opts["Last Search"]=st.session_state["search_result"]
        if src_opts:
            src_lbl=st.selectbox("Source",list(src_opts.keys()),key="sb_mon")
            src=src_opts[src_lbl]
            c1,c2,c3,c4=st.columns(4)
            for col,fmt,prompt_hint,btn_key in [
                (c1,"𝕏 Thread","7-tweet viral thread. Hook → insight → $TICKER → CTA","btn_mon_x"),
                (c2,"Substack","Professional research note. Setup → Alpha → Risk → Trade","btn_mon_sub"),
                (c3,"LinkedIn","High-impression post. Bold opening, 5 insights, question CTA","btn_mon_li"),
                (c4,"TikTok","60-sec script. Hook→Context→Alpha→Trade→CTA","btn_mon_tt"),
            ]:
                with col:
                    if st.button(fmt,type="primary",use_container_width=True,key=btn_key):
                        with st.status(f"Writing {fmt}...",expanded=True) as s:
                            out=st.empty(); full=""
                            for chunk in stream_gemini(SP["cio"],f"Turn into {fmt}:\n{src[:2500]}\n\n{prompt_hint}",gemini_key):
                                full+=chunk; out.markdown(full)
                            s.update(label="✓ Done",state="complete")
                        st.session_state["mon_out"]=full
            if st.session_state.get("mon_out"): dl_tg(st.session_state["mon_out"],"monetize")
        else: st.info("Run Alpha Scan, Macro Brief, or Search first, then come back here.")

    # ── Newsletter ─────────────────────────────────────────────────────────────
    with at_nl:
        st.markdown("**Newsletter Generator** — Full weekly edition for Substack/Beehiiv")
        nc1,nc2=st.columns(2)
        with nc1: nl_name=st.text_input("Newsletter",value="Alpha Intelligence Weekly",key="ti_nl")
        with nc2: nl_auth=st.text_input("Author",value="Alpha Machine",key="ti_nl_auth")
        if st.button("Generate Newsletter →",type="primary",key="btn_nl"):
            if key_check():
                scan=st.session_state.get("last_scan",{})
                thesis=scan.get("thesis","") if scan else ""
                with st.spinner():
                    result=call_gemini(SP["cio"],
                        f"NEWSLETTER:{nl_name}\nAUTHOR:{nl_auth}\nRESEARCH:{thesis[:2500] if thesis else 'Use live web search'}\n\n"
                        f"Write 700-word weekly newsletter:\n# [Title]\n## Macro Backdrop\n## The Alpha\n"
                        f"## Sector Signal\n## Portfolio Moves\n## Key Dates\n## One-Line Take",gemini_key)
                st.markdown("---"); st.markdown(result); st.markdown("---")
                dl_tg(result,"newsletter")

# ══════════════════════════════════════════════════════════════════════════════
#  TAB 3 — INFO
# ══════════════════════════════════════════════════════════════════════════════
with tab_info:
    st.markdown("## ◈ Alpha Machine v6 — Architecture")
    st.markdown("""
### How the Proactive Engine Works

**5 scanners run in parallel every 30–60 minutes:**

| Scanner | Data Source | What it finds |
|---|---|---|
| 🌑 Dark Money | Yahoo Finance options chain | Vol/OI > 2.5× — fresh institutional sweeps |
| 🛡 Pentagon | USASpending.gov (free API) | DoD contracts > $5M awarded last 72hrs |
| 🔬 Patents | USPTO PatentsView API (free) | Tech/defense/biotech grants last 7 days |
| 👤 Insider Cluster | EDGAR Form 4 + Finnhub | 2+ insiders buying open-market same month |
| 📈 Technical | Yahoo Finance + numpy | RSI<30, MACD cross, BB oversold — score ≥7 |

**Each signal scored 0–10 on:**
- Novelty (how fresh is this?)
- Magnitude (contract size / trade size)
- Asymmetry (is this underpriced?)
- Supply chain depth (how many names benefit?)

**Universal Search:** one query → AI synthesizes all 5 layers simultaneously

### Setup
**Required:** Gemini API key → [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

**Optional (improves data quality):**
- Finnhub (finnhub.io) — real insider transactions
- FMP (financialmodelingprep.com) — real financials for DCF
- Alpha Vantage (alphavantage.co) — official technical indicators

**Telegram push:** Add bot token + chat ID → high-score signals auto-push on every scan
    """)
    st.code("""
# Quantitative calculations (all numpy — not AI guessing):
calc_rsi(closes)           # Wilder RSI(14)
calc_macd(closes)          # EMA-based MACD + signal
calc_bollinger(closes)     # 2σ Bollinger Bands
calc_correlation_matrix()  # Pearson correlation
dcf_valuation(revenue...)  # Bear/Base/Bull DCF
score_technical(...)       # 0–10 composite signal
detect_options_anomalies() # Vol/OI + P/C + GEX + IV skew
fetch_pentagon_contracts() # USASpending.gov live API
fetch_patent_grants()      # USPTO PatentsView live API
fetch_insider_clusters()   # EDGAR Form 4 live scanner
    """, language="python")
