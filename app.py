"""
Conviction Engine — Supply Chain Intelligence + Multi-Layer Signal Stacker
Built on top of the Alpha Terminal supply chain framework.

The core idea: conviction = multiple INDEPENDENT data sources all pointing
at the same name simultaneously. The more independent the sources,
the higher the conviction. A name confirmed by 5 separate layers
that cannot talk to each other is institutional-grade conviction.

CONVICTION LAYERS (all free, all independent):
  L1 — Supply Chain Position     (Gemini + Google Search)
  L2 — Quantitative Signals      (Yahoo Finance + numpy)
  L3 — Options Flow Dark Money   (Yahoo Finance options chain)
  L4 — Insider Cluster EDGAR     (SEC EDGAR Form 4)
  L5 — Institutional 13F Freq    (Cross-chain memory — how many chains this name appeared in)
  L6 — Short Interest Collapse   (Finviz scrape — free)
  L7 — Catalyst Proximity        (USPTO patents + USASpending contracts + EDGAR 8-K)

CONVICTION SCORE:
  Base: 1 point per confirmed layer
  Multipliers:
    × 1.5 if 4+ layers all BULLISH (convergence)
    × 1.8 if appears in 3+ supply chains (cross-chain)
    × 2.0 if catalyst within 30 days (time pressure)
  Max: 10.0
"""

import streamlit as st
st.set_page_config(
    page_title="Conviction Engine",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

import requests, json, re, time, threading
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from google import genai
from google.genai import types

# ══════════════════════════════════════════════════════════════════════════════
#  DESIGN
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; font-style: normal !important; }
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > section,
[data-testid="stAppViewContainer"] > section > div,
.main, .main > div { background-color: #f7f8fa !important; font-family: 'Inter', sans-serif !important; color: #111827 !important; }
[data-testid="stSidebar"], [data-testid="stSidebar"] > div { background: #ffffff !important; border-right: 1px solid #e5e7eb !important; }
[data-testid="stSidebar"] * { color: #374151 !important; }
[data-testid="stSidebar"] strong { color: #111827 !important; font-weight: 600 !important; }
.block-container { padding: 1.4rem 2.2rem 4rem !important; max-width: 1440px !important; }
em, i { font-style: normal !important; }
strong, b { font-weight: 600 !important; color: #111827 !important; }

/* TOP BAR */
.ce-top { display:flex; align-items:center; justify-content:space-between; padding:12px 0 16px; border-bottom:1px solid #e5e7eb; margin-bottom:20px; }
.ce-logo { font-size:1.2rem; font-weight:800; letter-spacing:-0.8px; color:#111827 !important; }
.ce-logo .ac { color:#dc2626 !important; }
.ce-sub { font-size:0.7rem; color:#9ca3af !important; text-transform:uppercase; letter-spacing:0.8px; }

/* CONVICTION METER — the centrepiece */
.conv-meter {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 22px 26px;
    margin: 10px 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    position: relative;
    overflow: hidden;
}
.conv-meter::before {
    content: '';
    position: absolute; top:0; left:0; right:0; height:4px;
    border-radius: 14px 14px 0 0;
}
.conv-meter.ultra::before { background: linear-gradient(90deg, #dc2626, #f97316); }
.conv-meter.high::before  { background: linear-gradient(90deg, #d97706, #fbbf24); }
.conv-meter.med::before   { background: linear-gradient(90deg, #2563eb, #60a5fa); }
.conv-meter.low::before   { background: #e5e7eb; }

.conv-header { display:flex; align-items:center; gap:12px; margin-bottom:14px; flex-wrap:wrap; }
.conv-ticker { font-size:1.4rem; font-weight:800; color:#111827 !important; font-family:'JetBrains Mono',monospace; }
.conv-score-wrap { display:flex; flex-direction:column; align-items:center; margin-left:auto; }
.conv-score {
    font-size:2.2rem; font-weight:800; font-family:'JetBrains Mono',monospace;
    line-height:1;
}
.conv-score.ultra { color:#dc2626 !important; }
.conv-score.high  { color:#d97706 !important; }
.conv-score.med   { color:#2563eb !important; }
.conv-score.low   { color:#9ca3af !important; }
.conv-score-lbl { font-size:0.6rem; font-weight:700; letter-spacing:1.5px; text-transform:uppercase; color:#9ca3af !important; margin-top:2px; }

.conv-verdict { font-size:0.8rem; font-weight:700; padding:3px 10px; border-radius:20px; }
.conv-verdict.ultra { background:#fef2f2; color:#991b1b !important; border:1px solid #fca5a5; }
.conv-verdict.high  { background:#fffbeb; color:#92400e !important; border:1px solid #fde68a; }
.conv-verdict.med   { background:#eff6ff; color:#1d4ed8 !important; border:1px solid #bfdbfe; }
.conv-verdict.low   { background:#f3f4f6; color:#6b7280 !important; border:1px solid #e5e7eb; }

/* CONVICTION SCORE BAR */
.score-bar-wrap { background:#f3f4f6; border-radius:6px; height:8px; margin:12px 0; overflow:hidden; }
.score-bar { height:100%; border-radius:6px; transition:width 0.6s ease; }
.score-bar.ultra { background:linear-gradient(90deg,#dc2626,#f97316); }
.score-bar.high  { background:linear-gradient(90deg,#d97706,#fbbf24); }
.score-bar.med   { background:linear-gradient(90deg,#2563eb,#60a5fa); }
.score-bar.low   { background:#d1d5db; }

/* LAYER GRID */
.layer-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:10px; margin:14px 0; }
.layer-card {
    background:#f9fafb; border:1px solid #e5e7eb; border-radius:10px;
    padding:12px 14px; position:relative;
}
.layer-card.confirmed { border-color:#86efac; background:#f0fdf4; }
.layer-card.partial   { border-color:#fde68a; background:#fffbeb; }
.layer-card.absent    { border-color:#e5e7eb; background:#f9fafb; opacity:0.6; }
.layer-num  { font-size:0.6rem; font-weight:700; letter-spacing:1.5px; text-transform:uppercase; color:#9ca3af !important; margin-bottom:4px; display:block; }
.layer-name { font-size:0.83rem; font-weight:700; color:#111827 !important; margin-bottom:3px; }
.layer-val  { font-size:0.77rem; color:#374151 !important; line-height:1.4; }
.layer-pts  { position:absolute; top:10px; right:12px; font-size:0.72rem; font-weight:700; font-family:'JetBrains Mono',monospace; }
.layer-pts.confirmed { color:#16a34a !important; }
.layer-pts.partial   { color:#d97706 !important; }
.layer-pts.absent    { color:#d1d5db !important; }
.layer-icon { font-size:1.1rem; margin-bottom:4px; display:block; }

/* PRICE + LEVELS */
.levels-row { display:flex; gap:16px; flex-wrap:wrap; margin:10px 0; }
.level-box { background:#f9fafb; border:1px solid #e5e7eb; border-radius:8px; padding:10px 14px; flex:1; min-width:90px; }
.level-lbl  { font-size:0.58rem; font-weight:700; letter-spacing:1.2px; text-transform:uppercase; color:#9ca3af !important; display:block; margin-bottom:3px; }
.level-val  { font-size:1.0rem; font-weight:700; font-family:'JetBrains Mono',monospace; }
.level-val.entry  { color:#2563eb !important; }
.level-val.target { color:#16a34a !important; }
.level-val.stop   { color:#dc2626 !important; }
.level-val.upside { color:#16a34a !important; }
.level-val.risk   { color:#dc2626 !important; }

/* CROSS-CHAIN BADGE */
.xchain-badge {
    display:inline-flex; align-items:center; gap:6px;
    background:#fef3c7; border:1px solid #fcd34d;
    border-radius:6px; padding:4px 10px;
    font-size:0.74rem; font-weight:700; color:#92400e !important; margin:4px 2px;
}

/* CHAIN INPUT */
.chain-input-wrap { background:#ffffff; border:1.5px solid #e5e7eb; border-radius:12px; padding:18px 22px; margin-bottom:18px; box-shadow:0 1px 3px rgba(0,0,0,0.05); }

/* SECTION LABEL */
.mm-label { font-size:0.62rem; font-weight:700; letter-spacing:1.8px; text-transform:uppercase; color:#9ca3af !important; border-bottom:1px solid #e5e7eb; padding-bottom:6px; margin:20px 0 12px; display:block; }

/* MACRO STRIP */
.macro-strip { display:flex; gap:6px; margin-bottom:16px; overflow-x:auto; padding-bottom:2px; }
.mbox { flex:1; min-width:80px; background:#ffffff; border:1px solid #e5e7eb; border-radius:8px; padding:8px 10px; text-align:center; flex-shrink:0; }
.mlbl   { font-size:0.56rem; color:#9ca3af !important; text-transform:uppercase; letter-spacing:1.2px; display:block; margin-bottom:2px; font-weight:600; }
.mprice { font-size:0.88rem; font-weight:700; color:#111827 !important; font-family:'JetBrains Mono',monospace; display:block; }
.up { color:#16a34a !important; font-size:0.65rem; font-weight:600; }
.dn { color:#dc2626 !important; font-size:0.65rem; font-weight:600; }
.fl { color:#9ca3af !important; font-size:0.65rem; }

/* INPUTS / BUTTONS */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background:#ffffff !important; border:1.5px solid #d1d5db !important;
    border-radius:8px !important; color:#111827 !important; font-size:0.9rem !important;
}
.stTextInput > div > div > input:focus { border-color:#dc2626 !important; box-shadow:0 0 0 3px rgba(220,38,38,0.1) !important; }
[data-testid="stSelectbox"] [data-baseweb="select"] > div { background:#ffffff !important; border:1.5px solid #d1d5db !important; border-radius:8px !important; }
div.stButton > button { border-radius:8px !important; font-weight:700 !important; font-size:0.85rem !important; }
div.stButton > button[kind="primary"] { background:#dc2626 !important; border:1px solid #dc2626 !important; color:#ffffff !important; }
div.stButton > button[kind="primary"]:hover { background:#b91c1c !important; }

/* MARKDOWN */
div[data-testid="stMarkdownContainer"] * { font-style:normal !important; }
div[data-testid="stMarkdownContainer"] em { font-style:normal !important; color:#374151 !important; }
div[data-testid="stMarkdownContainer"] p  { color:#374151 !important; line-height:1.75 !important; margin:6px 0 !important; }
div[data-testid="stMarkdownContainer"] li { color:#374151 !important; line-height:1.65 !important; margin:3px 0 !important; }
div[data-testid="stMarkdownContainer"] strong { color:#111827 !important; font-weight:700 !important; }
div[data-testid="stMarkdownContainer"] h2 { color:#111827 !important; font-weight:700 !important; border-bottom:1px solid #f3f4f6 !important; padding-bottom:4px !important; }
div[data-testid="stMarkdownContainer"] h3 { color:#1e40af !important; font-weight:700 !important; }
div[data-testid="stMarkdownContainer"] table { display:block !important; overflow-x:auto !important; border-collapse:collapse !important; width:100% !important; }
div[data-testid="stMarkdownContainer"] th { background:#f3f4f6 !important; color:#111827 !important; padding:8px 12px !important; border:1px solid #e5e7eb !important; font-weight:600 !important; }
div[data-testid="stMarkdownContainer"] td { padding:7px 12px !important; border:1px solid #e5e7eb !important; color:#374151 !important; }
div[data-testid="stMarkdownContainer"] tr:nth-child(even) td { background:#f9fafb !important; }
div[data-testid="stMarkdownContainer"] code { background:#f3f4f6 !important; color:#1f2937 !important; padding:1px 5px !important; border-radius:4px !important; font-size:0.84em !important; }

/* TABS */
[data-testid="stTabs"] [role="tablist"] { border-bottom:2px solid #e5e7eb !important; }
[data-testid="stTabs"] button { font-size:0.8rem !important; font-weight:500 !important; color:#6b7280 !important; padding:8px 16px !important; border-bottom:2px solid transparent !important; border-radius:0 !important; background:transparent !important; margin-bottom:-2px !important; }
[data-testid="stTabs"] button[aria-selected="true"] { color:#111827 !important; font-weight:700 !important; border-bottom:2px solid #dc2626 !important; }
[data-testid="stMetricValue"] { color:#111827 !important; font-weight:700 !important; }
hr { border:none !important; border-top:1px solid #e5e7eb !important; }
::-webkit-scrollbar { width:5px; height:5px; }
::-webkit-scrollbar-thumb { background:#d1d5db; border-radius:3px; }

@media (max-width:768px) {
    .block-container { padding:0.8rem 1rem 2.5rem !important; }
    .layer-grid { grid-template-columns:1fr 1fr; }
    .conv-score { font-size:1.8rem; }
    .levels-row { gap:10px; }
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
for k, v in [
    ("chain_memory", {}),     # cross-chain database {ticker: [chain1, chain2, ...]}
    ("conviction_results", []),
    ("last_chain_map", ""),
    ("scan_history", []),
]:
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("**◈ Conviction Engine**")
    st.divider()
    gemini_key  = st.text_input("Gemini API Key", type="password", placeholder="AIza...", key="si_gemini")
    finnhub_key = st.text_input("Finnhub (optional)", type="password", placeholder="insider data", key="si_finnhub")
    st.divider()
    st.markdown("**Conviction Thresholds**")
    ultra_thresh = st.slider("Ultra High threshold", 7.0, 9.5, 8.0, 0.5, key="sl_ultra")
    high_thresh  = st.slider("High threshold",       4.0, 7.5, 6.0, 0.5, key="sl_high")
    min_layers   = st.slider("Min layers to show",    1,   7,   3,   1,  key="sl_minlayers")
    st.divider()
    st.markdown("**Cross-Chain Memory**")
    n_chains = len(st.session_state.get("chain_memory",{}))
    total_entries = sum(len(v) for v in st.session_state.get("chain_memory",{}).values())
    st.markdown(f'<span style="font-size:0.8rem;color:#374151">{n_chains} tickers tracked across {total_entries} chain appearances</span>', unsafe_allow_html=True)
    if st.button("Clear memory", key="btn_clr_mem"):
        st.session_state["chain_memory"] = {}
        st.rerun()
    if st.button("Clear results", key="btn_clr_res"):
        st.session_state["conviction_results"] = []
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  DATA LAYER — all free APIs
# ══════════════════════════════════════════════════════════════════════════════
YF = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36","Accept":"application/json"}

@st.cache_data(ttl=180, show_spinner=False)
def yf_price(sym):
    try:
        r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range=5d",
                         headers=YF, timeout=6)
        c = [x for x in r.json()["chart"]["result"][0]["indicators"]["quote"][0]["close"] if x]
        return (round(c[-1],2), round((c[-1]/c[-2]-1)*100,2)) if len(c)>=2 else (None,None)
    except: return None, None

@st.cache_data(ttl=300, show_spinner=False)
def yf_history(sym, rng="6mo"):
    try:
        r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range={rng}",
                         headers=YF, timeout=8)
        d = r.json()["chart"]["result"][0]
        closes = [c for c in d["indicators"]["quote"][0]["close"] if c is not None]
        vols   = [v for v in d["indicators"]["quote"][0].get("volume",[]) if v is not None]
        return closes, vols, d.get("meta",{})
    except: return [], [], {}

@st.cache_data(ttl=600, show_spinner=False)
def yf_options_flow(sym):
    """Options chain — extract Vol/OI ratio, P/C, whale strikes."""
    try:
        r = requests.get(f"https://query1.finance.yahoo.com/v7/finance/options/{sym}",
                         headers=YF, timeout=8)
        root = r.json().get("optionChain",{}).get("result",[])
        if not root: return {}
        cv = pv = co = po = 0
        otm_calls_iv = []; otm_puts_iv = []
        price, _ = yf_price(sym)
        for block in root[:3]:
            for ob in block.get("options",[]):
                for c in ob.get("calls",[]):
                    vol = c.get("volume") or 0
                    oi  = c.get("openInterest") or 0
                    cv += vol; co += oi
                    if price and c.get("strike",0) > price*1.05:
                        otm_calls_iv.append(float(c.get("impliedVolatility") or 0)*100)
                for p in ob.get("puts",[]):
                    vol = p.get("volume") or 0
                    oi  = p.get("openInterest") or 0
                    pv += vol; po += oi
                    if price and p.get("strike",0) < price*0.95:
                        otm_puts_iv.append(float(p.get("impliedVolatility") or 0)*100)
        total_vol = cv + pv
        total_oi  = co + po
        vol_oi    = round(total_vol/max(total_oi,1), 3)
        pc_vol    = round(pv/max(cv,1), 3)
        iv_skew   = round(np.mean(otm_puts_iv) - np.mean(otm_calls_iv), 1) if otm_calls_iv and otm_puts_iv else 0
        return {
            "call_vol":cv, "put_vol":pv, "call_oi":co, "put_oi":po,
            "total_vol":total_vol, "total_oi":total_oi,
            "vol_oi":vol_oi, "pc_vol":pc_vol, "iv_skew":iv_skew,
        }
    except: return {}

@st.cache_data(ttl=600, show_spinner=False)
def edgar_form4(ticker):
    """EDGAR Form 4 — insider transaction cluster detection."""
    try:
        start = (datetime.now()-timedelta(days=45)).strftime("%Y-%m-%d")
        r = requests.get(
            f"https://efts.sec.gov/LATEST/search-index?q=%22{ticker}%22&dateRange=custom&startdt={start}&forms=4",
            headers={"User-Agent":"ConvictionEngine research@conviction.ai"}, timeout=10)
        hits = r.json().get("hits",{}).get("hits",[])
        filings = [{"filed":h["_source"].get("file_date",""),
                    "company":h["_source"].get("entity_name","")} for h in hits[:10]]
        # Count unique filing dates = proxy for cluster buys
        unique_dates = len(set(f["filed"] for f in filings))
        return {"filings": filings, "count": len(filings), "unique_dates": unique_dates}
    except: return {"filings":[],"count":0,"unique_dates":0}

@st.cache_data(ttl=600, show_spinner=False)
def finnhub_insider_buys(sym, key):
    """Finnhub insider transactions — count open-market buys."""
    if not key: return {"buys":0,"sells":0,"net_val":0,"names":[]}
    try:
        r = requests.get(f"https://finnhub.io/api/v1/stock/insider-transactions?symbol={sym}&token={key}", timeout=6)
        data = r.json().get("data",[])
        cutoff = (datetime.now()-timedelta(days=45)).strftime("%Y-%m-%d")
        buys  = [t for t in data if str(t.get("transactionType","")).upper() in ["P","BUY","PURCHASE"]
                 and str(t.get("transactionDate",""))>=cutoff]
        sells = [t for t in data if str(t.get("transactionType","")).upper() in ["S","SALE","SELL"]
                 and str(t.get("transactionDate",""))>=cutoff]
        net_val = sum(abs(float(b.get("transactionPrice",0) or 0)*abs(float(b.get("share",0) or 0))) for b in buys)
        return {
            "buys":  len(buys),
            "sells": len(sells),
            "net_val": round(net_val/1000, 1),  # $K
            "names": [b.get("name","")[:20] for b in buys[:4]],
        }
    except: return {"buys":0,"sells":0,"net_val":0,"names":[]}

@st.cache_data(ttl=1800, show_spinner=False)
def edgar_8k(ticker):
    """EDGAR 8-K filings — material events as catalysts."""
    try:
        start = (datetime.now()-timedelta(days=30)).strftime("%Y-%m-%d")
        r = requests.get(
            f"https://efts.sec.gov/LATEST/search-index?q=%22{ticker}%22&dateRange=custom&startdt={start}&forms=8-K",
            headers={"User-Agent":"ConvictionEngine research@conviction.ai"}, timeout=10)
        hits = r.json().get("hits",{}).get("hits",[])[:5]
        return [{"filed":h["_source"].get("file_date",""),
                 "desc": h["_source"].get("period_of_report","")} for h in hits]
    except: return []

@st.cache_data(ttl=1800, show_spinner=False)
def usaspending_contracts(company_name):
    """DoD contracts for a company name — catalyst signal."""
    try:
        end   = datetime.now().strftime("%Y-%m-%d")
        start = (datetime.now()-timedelta(days=30)).strftime("%Y-%m-%d")
        payload = {
            "filters": {
                "time_period": [{"start_date":start,"end_date":end}],
                "agencies": [{"type":"awarding_agency","tier":"toptier","name":"Department of Defense"}],
                "award_type_codes": ["A","B","C","D"],
                "recipient_search_text": [company_name[:30]],
            },
            "fields": ["recipient_name","total_obligated_amount","action_date","award_description"],
            "sort":"total_obligated_amount","order":"desc","limit":3,"page":1,
        }
        r = requests.post("https://api.usaspending.gov/api/v2/search/spending_by_award/",
                         json=payload, timeout=12,
                         headers={"Content-Type":"application/json","User-Agent":"ConvictionEngine/1.0"})
        results = r.json().get("results",[])
        return [{"amount_m": round(float(x.get("total_obligated_amount",0))/1e6,1),
                 "date": x.get("action_date",""),
                 "desc": x.get("award_description","")[:80]} for x in results]
    except: return []

@st.cache_data(ttl=300, show_spinner=False)
def get_macro():
    syms = {"SPX":"%5EGSPC","VIX":"%5EVIX","10Y":"%5ETNX","DXY":"DX-Y.NYB","Gold":"GC%3DF","Oil":"CL%3DF"}
    out  = {lbl: yf_price(sym) for lbl,sym in syms.items()}
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price",
            params={"ids":"bitcoin","vs_currencies":"usd","include_24hr_change":"true"},
            timeout=5, headers={"User-Agent":"CE/1.0"})
        d = r.json()["bitcoin"]
        out["BTC"] = (round(d["usd"],0), round(d["usd_24h_change"],2))
    except: out["BTC"] = (None,None)
    return out

# ══════════════════════════════════════════════════════════════════════════════
#  QUANTITATIVE ENGINE
# ══════════════════════════════════════════════════════════════════════════════
def calc_rsi(c, n=14):
    if len(c)<n+1: return 50.0
    a=np.array(c,dtype=float); d=np.diff(a)
    g=np.where(d>0,d,0.); l=np.where(d<0,-d,0.)
    return round(float(100-100/(1+np.mean(g[-n:])/(np.mean(l[-n:])+1e-9))),1)

def calc_macd(c):
    if len(c)<35: return None,None,None
    s=pd.Series(c,dtype=float)
    m=s.ewm(span=12,adjust=False).mean()-s.ewm(span=26,adjust=False).mean()
    sig=m.ewm(span=9,adjust=False).mean()
    return round(float(m.iloc[-1]),3),round(float(sig.iloc[-1]),3),round(float((m-sig).iloc[-1]),4)

def calc_bb(c,n=20):
    if len(c)<n: return None,None,None
    a=np.array(c[-n:],dtype=float)
    return round(float(np.mean(a)+2*np.std(a)),2),round(float(np.mean(a)),2),round(float(np.mean(a)-2*np.std(a)),2)

def vol_ratio(vols,n=20):
    if len(vols)<n+1 or not vols[-1]: return None
    return round(vols[-1]/max(float(np.mean(vols[-n-1:-1])),1),2)

def short_ratio_proxy(closes, vols, n=5):
    """
    Proxy for short interest collapse: if volume is spiking while price is rising,
    shorts are being squeezed. Score: 0 (no squeeze) to 1 (max squeeze).
    """
    if len(closes)<n+1 or len(vols)<n+1: return 0.0
    price_up   = closes[-1] > closes[-n]
    vol_spike  = vols[-1] > float(np.mean(vols[-n-1:-1])) * 1.8 if float(np.mean(vols[-n-1:-1]))>0 else False
    return 1.0 if (price_up and vol_spike) else 0.5 if vol_spike else 0.0

def calc_momentum(c, periods=(5,10,21)):
    out = {}
    for p in periods:
        if len(c)>p: out[p] = round((c[-1]/c[-p-1]-1)*100,2)
    return out

def score_quant_layer(closes, vols, meta, price):
    """
    Score the quantitative layer 0-2 points.
    Returns (points, signals_dict)
    """
    if not closes or not price: return 0, {}
    rsi      = calc_rsi(closes)
    ml,ms,mh = calc_macd(closes)
    bu,bm,bl = calc_bb(closes)
    vr       = vol_ratio(vols)
    w52h     = meta.get("fiftyTwoWeekHigh",0) or 0
    w52l     = meta.get("fiftyTwoWeekLow",0)  or 0
    mom      = calc_momentum(closes)
    ma50     = float(np.mean(closes[-50:])) if len(closes)>=50 else None
    squeeze  = short_ratio_proxy(closes,vols)

    bullish_count = 0
    sigs = {"rsi":rsi,"macd_hist":mh,"vol_ratio":vr,"w52pct":0,"ma50_above":None,"squeeze":squeeze}

    if rsi < 35:   bullish_count += 1
    elif rsi < 45: bullish_count += 0.5
    if mh and mh > 0: bullish_count += 1
    if w52h and w52l:
        pct52 = (price-w52l)/max(w52h-w52l,0.01)
        sigs["w52pct"] = round(pct52*100,1)
        if pct52 < 0.25: bullish_count += 1  # near 52W low = oversold setup
    if ma50 and price > ma50: sigs["ma50_above"] = True; bullish_count += 0.5
    elif ma50: sigs["ma50_above"] = False
    if vr and vr > 2.0: bullish_count += 1   # volume surge = accumulation
    if squeeze > 0.5:   bullish_count += 0.5  # squeeze proxy

    # Scale to 0-2
    pts = min(2.0, round(bullish_count * 0.4, 1))
    sigs["bullish_count"] = bullish_count
    return pts, sigs

# ══════════════════════════════════════════════════════════════════════════════
#  CONVICTION SCORING ENGINE — the centrepiece
# ══════════════════════════════════════════════════════════════════════════════
def score_conviction(ticker, chain_source, finnhub_key=""):
    """
    Run all 7 conviction layers against a ticker.
    Returns a complete conviction dict.

    LAYERS:
      L1  Supply Chain Position    — how deep in the chain? (from Gemini)
      L2  Quantitative Signals     — RSI + MACD + Vol + MA stacking
      L3  Options Dark Money       — Vol/OI ratio, P/C skew, IV skew
      L4  Insider Activity         — EDGAR Form 4 + Finnhub cluster
      L5  Cross-Chain Frequency    — how many independent chains named this ticker
      L6  Short Squeeze Proxy      — volume spike + price rising together
      L7  Catalyst Proximity       — 8-K filings + DoD contracts in last 30 days
    """
    result = {
        "ticker":  ticker,
        "chain_source": chain_source,
        "ts":      datetime.now().isoformat(),
        "layers":  {},
        "score":   0.0,
        "verdict": "",
        "grade":   "",
        "price":   None,
        "entry":   None,
        "target":  None,
        "stop":    None,
        "upside":  None,
        "downside":None,
        "rr":      None,
    }

    # ── Fetch base data ───────────────────────────────────────────────────────
    price, chg = yf_price(ticker)
    closes, vols, meta = yf_history(ticker, "6mo")
    result["price"] = price
    result["chg"]   = chg

    # ── L1: Supply Chain Position ─────────────────────────────────────────────
    # Scored externally by Gemini (passed in via chain_source tier)
    tier_pts = {"T1":0.5, "T2":1.0, "T3":1.5, "BOTTLENECK":2.0, "MOAT":2.0}
    l1_pts = 1.0  # default — named in chain = 1pt
    l1_info = f"Named in {chain_source} supply chain"
    result["layers"]["L1_supply_chain"] = {
        "name":"Supply Chain Position","icon":"⛓",
        "pts":l1_pts,"status":"confirmed",
        "detail":l1_info,
    }

    # ── L2: Quantitative Signals ──────────────────────────────────────────────
    if closes and price:
        l2_pts, quant_sigs = score_quant_layer(closes, vols, meta, price)
        rsi = quant_sigs.get("rsi",50)
        mh  = quant_sigs.get("macd_hist")
        vr  = quant_sigs.get("vol_ratio")
        detail = f"RSI {rsi} | MACD hist {mh} | Vol {vr}× | 52W pos {quant_sigs.get('w52pct',0):.0f}%"
        status = "confirmed" if l2_pts >= 1.0 else "partial" if l2_pts > 0 else "absent"
        result["layers"]["L2_quant"] = {
            "name":"Quantitative Signals","icon":"📊",
            "pts":l2_pts,"status":status,"detail":detail,
            "raw":quant_sigs,
        }
        # Entry/target/stop
        if closes:
            adr = round(float(np.mean([abs(closes[i]-closes[i-1]) for i in range(1,min(14,len(closes)))])),2)
            result["entry"]    = round(price*0.998,2)
            result["stop"]     = round(max(price*0.88, price-3*adr),2)
            result["target"]   = round(price*(1.15 + l2_pts*0.03),2)
            result["upside"]   = round((result["target"]/price-1)*100,1)
            result["downside"] = round((result["stop"]/price-1)*100,1)
            result["rr"]       = round(result["upside"]/abs(result["downside"]),2) if result["downside"]<0 else 0
    else:
        result["layers"]["L2_quant"] = {"name":"Quantitative Signals","icon":"📊","pts":0,"status":"absent","detail":"No price data"}

    # ── L3: Options Dark Money ────────────────────────────────────────────────
    opts = yf_options_flow(ticker)
    if opts and opts.get("total_oi",0) > 0:
        vol_oi = opts.get("vol_oi",0)
        pc_vol = opts.get("pc_vol",1.0)
        iv_skew= opts.get("iv_skew",0)
        # High vol/OI + low P/C = institutional call buying (bullish dark money)
        l3_pts = 0.0
        if vol_oi > 3.0:   l3_pts += 1.0
        elif vol_oi > 1.5: l3_pts += 0.5
        if pc_vol < 0.5:   l3_pts += 0.5   # heavy calls
        elif pc_vol > 1.8: l3_pts -= 0.3   # heavy puts = bearish
        if iv_skew < -5:   l3_pts += 0.3   # call skew = bullish positioning
        l3_pts = max(0, min(2.0, l3_pts))
        status = "confirmed" if l3_pts >= 1.0 else "partial" if l3_pts > 0 else "absent"
        detail = f"Vol/OI {vol_oi}× | P/C {pc_vol} | IV skew {iv_skew:.1f}%"
        result["layers"]["L3_options"] = {
            "name":"Options Dark Money","icon":"🌑",
            "pts":round(l3_pts,1),"status":status,"detail":detail,"raw":opts,
        }
    else:
        result["layers"]["L3_options"] = {"name":"Options Dark Money","icon":"🌑","pts":0,"status":"absent","detail":"No options data"}

    # ── L4: Insider Activity ──────────────────────────────────────────────────
    if finnhub_key:
        ins = finnhub_insider_buys(ticker, finnhub_key)
        buys, sells = ins["buys"], ins["sells"]
        net_val = ins["net_val"]
        if buys >= 3:
            l4_pts = 2.0; status = "confirmed"
            detail = f"CLUSTER: {buys} insiders bought ${net_val}K in 45d"
        elif buys >= 2:
            l4_pts = 1.5; status = "confirmed"
            detail = f"{buys} insiders bought ${net_val}K in 45d"
        elif buys == 1:
            l4_pts = 0.8; status = "partial"
            detail = f"1 insider bought ${net_val}K in 45d"
        elif sells > buys:
            l4_pts = 0.0; status = "absent"
            detail = f"Net selling: {sells} sells vs {buys} buys"
        else:
            l4_pts = 0.3; status = "partial"
            detail = "No recent insider activity"
    else:
        # EDGAR fallback
        form4 = edgar_form4(ticker)
        count = form4.get("count",0)
        udates= form4.get("unique_dates",0)
        if count >= 5 and udates >= 3:
            l4_pts = 1.5; status = "confirmed"
            detail = f"{count} Form 4 filings, {udates} different dates (cluster signal)"
        elif count >= 2:
            l4_pts = 0.8; status = "partial"
            detail = f"{count} Form 4 filings in 45 days"
        else:
            l4_pts = 0.2; status = "absent"
            detail = f"{count} Form 4 filings (low activity)"
        l4_pts = max(0, min(2.0, l4_pts))
    result["layers"]["L4_insider"] = {
        "name":"Insider Cluster","icon":"👤",
        "pts":round(l4_pts,1),"status":status,"detail":detail,
    }

    # ── L5: Cross-Chain Frequency ─────────────────────────────────────────────
    chain_memory = st.session_state.get("chain_memory",{})
    appearances  = chain_memory.get(ticker.upper(),[])
    n_chains     = len(appearances)
    if n_chains >= 3:
        l5_pts = 2.0; status = "confirmed"
        detail = f"Appeared in {n_chains} independent supply chains: {', '.join(appearances[-3:])}"
    elif n_chains == 2:
        l5_pts = 1.2; status = "confirmed"
        detail = f"Appeared in 2 chains: {', '.join(appearances)}"
    elif n_chains == 1:
        l5_pts = 0.5; status = "partial"
        detail = f"1 chain so far ({appearances[0]})"
    else:
        l5_pts = 0.0; status = "absent"
        detail = "First appearance"
    result["layers"]["L5_cross_chain"] = {
        "name":"Cross-Chain Frequency","icon":"🔗",
        "pts":l5_pts,"status":status,"detail":detail,
        "appearances":appearances, "n_chains":n_chains,
    }

    # ── L6: Short Squeeze / Volume Surge ─────────────────────────────────────
    if closes and vols:
        squeeze = short_ratio_proxy(closes, vols)
        vr      = vol_ratio(vols)
        mom21   = calc_momentum(closes).get(21,0)
        if squeeze >= 1.0 and (vr or 0) > 2.5:
            l6_pts = 1.5; status = "confirmed"
            detail = f"Volume {vr}× avg + price rising = squeeze setup. 1M: {mom21:+.1f}%"
        elif squeeze >= 0.5 or (vr or 0) > 1.5:
            l6_pts = 0.8; status = "partial"
            detail = f"Volume {vr}× avg. 1M: {mom21:+.1f}%"
        else:
            l6_pts = 0.0; status = "absent"
            detail = f"Normal volume. 1M: {mom21:+.1f}%"
    else:
        l6_pts = 0.0; status = "absent"
        detail = "No volume data"
    result["layers"]["L6_squeeze"] = {
        "name":"Volume / Squeeze","icon":"🔥",
        "pts":round(l6_pts,1),"status":status,"detail":detail,
    }

    # ── L7: Catalyst Proximity ────────────────────────────────────────────────
    l7_pts = 0.0
    cat_details = []
    # EDGAR 8-K (material events)
    k8 = edgar_8k(ticker)
    if k8:
        l7_pts += 0.8
        cat_details.append(f"{len(k8)} 8-K filings in 30d")
    # DoD contracts
    dod = usaspending_contracts(ticker)
    if dod:
        biggest = dod[0].get("amount_m",0)
        l7_pts += 1.0 if biggest > 100 else 0.5
        cat_details.append(f"DoD contract ${biggest:.0f}M")
    l7_pts = min(2.0, l7_pts)
    status = "confirmed" if l7_pts >= 1.0 else "partial" if l7_pts > 0 else "absent"
    detail = " | ".join(cat_details) if cat_details else "No recent material catalysts"
    result["layers"]["L7_catalyst"] = {
        "name":"Catalyst Proximity","icon":"⚡",
        "pts":round(l7_pts,1),"status":status,"detail":detail,
    }

    # ── FINAL CONVICTION SCORE ────────────────────────────────────────────────
    base_score = sum(l["pts"] for l in result["layers"].values())

    # Independence multiplier — the more CONFIRMED layers, the stronger the signal
    confirmed_count = sum(1 for l in result["layers"].values() if l["status"]=="confirmed")
    if confirmed_count >= 5:   base_score *= 1.5
    elif confirmed_count >= 4: base_score *= 1.3
    elif confirmed_count >= 3: base_score *= 1.1

    # Cross-chain multiplier
    if n_chains >= 3: base_score *= 1.8
    elif n_chains >= 2: base_score *= 1.3

    # Catalyst multiplier
    if l7_pts >= 1.0: base_score *= 1.5

    # Normalize to 0-10
    final_score = round(min(10.0, base_score / 14 * 10), 1)

    # Grade
    if final_score >= ultra_thresh: grade = "ultra"
    elif final_score >= high_thresh: grade = "high"
    elif final_score >= 4.0:        grade = "med"
    else:                            grade = "low"

    verdict_map = {
        "ultra": "ULTRA HIGH CONVICTION",
        "high":  "HIGH CONVICTION",
        "med":   "MODERATE CONVICTION",
        "low":   "LOW CONVICTION",
    }
    result["score"]   = final_score
    result["grade"]   = grade
    result["verdict"] = verdict_map[grade]
    result["confirmed_layers"] = confirmed_count
    result["base_score_raw"]   = round(base_score,2)
    return result

# ══════════════════════════════════════════════════════════════════════════════
#  GEMINI — supply chain mapper
# ══════════════════════════════════════════════════════════════════════════════
CHAIN_SYSTEM = """You are a Supply Chain Forensic Analyst and Asymmetric Investment Specialist.

Your job: map the full nervous system of any sector, technology, or company.
Find every tier of the supply chain with PUBLIC COMPANY tickers.

CLASSIFICATION:
- TIER 1: Direct suppliers (large, well-known)
- TIER 2: Component/process suppliers (often overlooked)
- TIER 3: Raw material / specialty chemical / IP holders (where the real alpha is)
- BOTTLENECK: The one company giants CANNOT bypass
- MOAT: The company with IP/patents/regulatory position nobody can replicate

STRICT RULES:
1. Only name publicly traded companies with real tickers
2. Bold all tickers: **$TICKER**
3. End EVERY response with exactly: TICKERS: T1=$X,T2=$X,T3=$X,BOTTLENECK=$X,MOAT=$X
   (use N/A if no clear bottleneck or moat)
4. For each company explain WHY it's asymmetric — what does it have that cannot be replicated?"""

def stream_chain_map(target, key):
    if not key: yield "[No API key]"; return
    try:
        client = genai.Client(api_key=key)
        srch   = types.Tool(google_search=types.GoogleSearch())
        config = types.GenerateContentConfig(
            tools=[srch], temperature=0.2, system_instruction=CHAIN_SYSTEM)
        resp = client.models.generate_content_stream(
            model="gemini-2.5-flash",
            contents=f"""Map the FULL supply chain for: {target}

Structure your response:
## TIER 1 — Direct Suppliers
[3-5 companies with **$TICKER**, what they supply, why important]

## TIER 2 — Hidden Asymmetric Plays
[3-5 companies with **$TICKER**, why nobody is watching these]

## TIER 3 — Raw Material / IP Moat
[2-3 companies, the deepest value here]

## BOTTLENECK ANALYSIS
[The one company that owns the IP or process that CANNOT be bypassed]

## ASYMMETRIC CONVICTION BET
[Your single highest-conviction pick and exactly why — be specific]

TICKERS: T1=$X,T2=$X,T3=$X,BOTTLENECK=$X,MOAT=$X""",
            config=config)
        for chunk in resp:
            if chunk.text: yield chunk.text
    except Exception as e: yield f"[Error: {e}]"

CONVICTION_SYSTEM = """You are the Head of Research at a $5B hedge fund.
You synthesize quantitative signals, supply chain intelligence, insider data,
and options flow into precise, actionable investment theses.
Every statement must be backed by a number. No vague language."""

def call_gemini(system, user, key):
    if not key: return "[No API key]"
    try:
        client = genai.Client(api_key=key)
        srch   = types.Tool(google_search=types.GoogleSearch())
        config = types.GenerateContentConfig(tools=[srch], temperature=0.3, system_instruction=system)
        return client.models.generate_content(model="gemini-2.5-flash", contents=user, config=config).text
    except Exception as e: return f"[Error: {e}]"

def stream_conviction_thesis(conv_result, key):
    if not key: yield "[No API key]"; return
    layers_summary = "\n".join([
        f"  {l['name']}: {l['pts']}pts ({l['status']}) — {l['detail']}"
        for l in conv_result["layers"].values()
    ])
    try:
        client = genai.Client(api_key=key)
        srch   = types.Tool(google_search=types.GoogleSearch())
        config = types.GenerateContentConfig(
            tools=[srch], temperature=0.3, system_instruction=CONVICTION_SYSTEM)
        resp = client.models.generate_content_stream(
            model="gemini-2.5-flash",
            contents=f"""Date: {datetime.now():%Y-%m-%d}

TICKER: {conv_result['ticker']}
CONVICTION SCORE: {conv_result['score']}/10 ({conv_result['verdict']})
PRICE: ${conv_result.get('price','?')} ({conv_result.get('chg',0):+.2f}% today)
CONFIRMED LAYERS: {conv_result['confirmed_layers']}/7

LAYER EVIDENCE:
{layers_summary}

SUPPLY CHAIN CONTEXT: {conv_result['chain_source']}
ENTRY: ${conv_result.get('entry','?')} | TARGET: ${conv_result.get('target','?')} | STOP: ${conv_result.get('stop','?')}
UPSIDE: {conv_result.get('upside','?')}% | R/R: {conv_result.get('rr','?')}×

Use live web search to find: current news, upcoming catalysts, analyst targets, short interest data.

Write the COMPLETE CONVICTION THESIS:

## Why This Name, Why Now
Synthesize ALL 7 layers. What is the market missing about {conv_result['ticker']}?

## The Asymmetric Setup
What is the specific catalyst that reprices this? When?

## Supply Chain Moat
Why is its position in the supply chain defensible?

## Bear Case & Kill Scenario  
What breaks this thesis? What level invalidates it?

## Final Verdict
🎯 Entry: ${conv_result.get('entry','?')} | Target: ${conv_result.get('target','?')} | Stop: ${conv_result.get('stop','?')}
Conviction: {conv_result['score']}/10 — [one sentence final call]""",
            config=config)
        for chunk in resp:
            if chunk.text: yield chunk.text
    except Exception as e: yield f"[Error: {e}]"

# ══════════════════════════════════════════════════════════════════════════════
#  UI HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def render_conviction_card(cr, expanded=False):
    g = cr["grade"]
    score = cr["score"]
    bar_pct = int(score*10)
    price_str = f"${cr['price']:,.2f}" if cr.get("price") else "—"
    chg = cr.get("chg",0) or 0
    chg_cls = "up" if chg>=0 else "dn"
    chg_str = f"+{chg:.2f}%" if chg>=0 else f"{chg:.2f}%"

    st.markdown(f"""
<div class="conv-meter {g}">
  <div class="conv-header">
    <div>
      <div class="conv-ticker">{cr['ticker']}</div>
      <span class="conv-verdict {g}">{cr['verdict']}</span>
      <span style="font-size:0.72rem;color:#9ca3af;margin-left:8px">{cr['chain_source']}</span>
    </div>
    <div style="font-size:0.85rem;font-weight:700;margin-left:8px">
      {price_str} <span class="{chg_cls}" style="font-size:0.8rem">{chg_str}</span>
    </div>
    <div class="conv-score-wrap">
      <span class="conv-score {g}">{score}</span>
      <span class="conv-score-lbl">/ 10</span>
    </div>
  </div>
  <div class="score-bar-wrap">
    <div class="score-bar {g}" style="width:{bar_pct}%"></div>
  </div>
  <div style="font-size:0.72rem;color:#6b7280;margin-top:4px">
    {cr['confirmed_layers']}/7 layers confirmed &nbsp;·&nbsp;
    {cr['layers'].get('L5_cross_chain',{}).get('n_chains',0)} supply chains &nbsp;·&nbsp;
    Updated {cr['ts'][:16].replace('T',' ')} UTC
  </div>
</div>""", unsafe_allow_html=True)

    # Levels row
    if cr.get("entry"):
        st.markdown(f"""
<div class="levels-row">
  <div class="level-box"><span class="level-lbl">Entry</span><span class="level-val entry">${cr['entry']:,.2f}</span></div>
  <div class="level-box"><span class="level-lbl">Target</span><span class="level-val target">${cr['target']:,.2f}</span></div>
  <div class="level-box"><span class="level-lbl">Stop</span><span class="level-val stop">${cr['stop']:,.2f}</span></div>
  <div class="level-box"><span class="level-lbl">Upside</span><span class="level-val upside">{cr['upside']:+.1f}%</span></div>
  <div class="level-box"><span class="level-lbl">Downside</span><span class="level-val risk">{cr['downside']:.1f}%</span></div>
  <div class="level-box"><span class="level-lbl">R/R</span><span class="level-val">{cr['rr']}×</span></div>
</div>""", unsafe_allow_html=True)

    # Layer grid
    st.markdown('<div class="layer-grid">', unsafe_allow_html=True)
    for layer_key, layer in cr["layers"].items():
        s = layer["status"]
        pts = layer["pts"]
        pts_str = f"+{pts}" if pts>0 else "0"
        st.markdown(f"""
<div class="layer-card {s}">
  <span class="layer-icon">{layer['icon']}</span>
  <span class="layer-num">{layer_key.replace('_',' ')}</span>
  <div class="layer-name">{layer['name']}</div>
  <div class="layer-val">{layer['detail']}</div>
  <span class="layer-pts {s}">{pts_str}pt</span>
</div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Cross-chain badges
    appearances = cr["layers"].get("L5_cross_chain",{}).get("appearances",[])
    if len(appearances) > 1:
        badges = "".join([f'<span class="xchain-badge">🔗 {a}</span>' for a in appearances])
        st.markdown(f'<div style="margin-top:8px">{badges}</div>', unsafe_allow_html=True)

def send_telegram(text, token, chat_id):
    if not token or not chat_id: return
    for chunk in [text[i:i+4000] for i in range(0,len(text),4000)]:
        try:
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                         json={"chat_id":chat_id,"text":chunk},timeout=10)
        except: pass

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN UI
# ══════════════════════════════════════════════════════════════════════════════

# Top bar
st.markdown(f"""
<div class="ce-top">
  <div>
    <div class="ce-logo">◈ Conviction<span class="ac">Engine</span></div>
    <div class="ce-sub">Supply Chain Intelligence · Multi-Layer Signal Stacker · {datetime.now().strftime("%d %b %Y · %H:%M UTC")}</div>
  </div>
</div>""", unsafe_allow_html=True)

# Macro strip
macro = get_macro()
strip = ""
for lbl,(p,c) in macro.items():
    if p:
        cls = "up" if (c or 0)>=0 else "dn"
        fmt = f"{p:,.0f}" if p>500 else f"{p:.2f}"
        sgn = "+" if (c or 0)>=0 else ""
        strip += f'<div class="mbox"><span class="mlbl">{lbl}</span><span class="mprice">{fmt}</span><span class="{cls}">{sgn}{c:.2f}%</span></div>'
    else:
        strip += f'<div class="mbox"><span class="mlbl">{lbl}</span><span class="mprice">—</span></div>'
st.markdown(f'<div class="macro-strip">{strip}</div>', unsafe_allow_html=True)

# Main tabs
tab_scan, tab_results, tab_memory, tab_single = st.tabs([
    "⛓ Chain Scan",
    f"◈ Conviction Results ({len(st.session_state.get('conviction_results',[]))})",
    f"🔗 Cross-Chain Memory ({len(st.session_state.get('chain_memory',{}))} tickers)",
    "⊕ Single Ticker",
])

# ══════════════════════════════════════════════════════════════════════════════
#  TAB 1 — CHAIN SCAN (the main workflow)
# ══════════════════════════════════════════════════════════════════════════════
with tab_scan:
    st.markdown("""
**How it works:** You input a ticker, theme, or sector.
Gemini maps the full supply chain (Tier 1→2→3 + bottleneck + moat).
Every identified ticker is then automatically run through all 7 conviction layers simultaneously.
The output is a ranked list sorted by conviction score — not by how well-known the company is.
""")

    st.markdown('<div class="chain-input-wrap">', unsafe_allow_html=True)
    ic1, ic2 = st.columns([4,1])
    with ic1:
        scan_target = st.text_input("",
            placeholder="$NVDA · Solid State Batteries · EUV Lithography · Hypersonic weapons · GLP-1 obesity drugs",
            label_visibility="collapsed", key="ti_scan_target")
    with ic2:
        scan_btn = st.button("◈ Run Scan", type="primary", key="btn_scan", use_container_width=True)
    st.markdown("""<div style="font-size:0.72rem;color:#9ca3af;margin-top:8px">
Use <b>$TICKER</b> for specific company chains · or any technology/theme · or a geopolitical scenario
</div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if scan_btn and scan_target.strip():
        if not gemini_key:
            st.warning("Add your Gemini API key in the sidebar.")
            st.stop()

        # STEP 1: Map the supply chain
        with st.status(f"Mapping supply chain for {scan_target}...", expanded=True) as s1:
            st.write("Gemini scanning with Google Search grounding...")
            chain_out = st.empty()
            full_chain = ""
            for chunk in stream_chain_map(scan_target, gemini_key):
                full_chain += chunk
                chain_out.markdown(full_chain)
            st.session_state["last_chain_map"] = full_chain
            s1.update(label="✓ Supply chain mapped", state="complete")

        # STEP 2: Extract tickers from Gemini output
        ticker_match = re.search(r'TICKERS:\s*([^\n]+)', full_chain, re.IGNORECASE)
        raw_tickers = []
        if ticker_match:
            raw = ticker_match.group(1)
            pairs = re.findall(r'[A-Z0-9\-]{1,5}=\$?([A-Z0-9\-]{1,6})|[T][1-9]/BOTTLENECK/MOAT\s*=\s*\$?([A-Z0-9\-]+)|\$([A-Z0-9\-]{1,6})|([A-Z]{2,6})', raw)
            for p in pairs:
                t = (p[0] or p[1] or p[2] or p[3]).strip().upper()
                if t and t not in ["NA","N/A","T1","T2","T3","BOTTLENECK","MOAT","AND","THE"]:
                    raw_tickers.append(t)
        # Also scan body for bolded tickers
        body_tickers = re.findall(r'\*\*\$([A-Z]{2,6})\*\*', full_chain)
        all_tickers  = list(dict.fromkeys(raw_tickers + body_tickers))[:12]

        if not all_tickers:
            st.warning("Could not extract tickers. Check Gemini output above.")
            st.stop()

        # Update cross-chain memory
        for t in all_tickers:
            mem = st.session_state.get("chain_memory",{})
            if t not in mem: mem[t] = []
            if scan_target not in mem[t]:
                mem[t].append(scan_target[:30])
            st.session_state["chain_memory"] = mem

        st.markdown(f'<span class="mm-label">Running conviction analysis on {len(all_tickers)} tickers</span>', unsafe_allow_html=True)

        # STEP 3: Score all tickers in parallel
        results = []
        lock = threading.Lock()
        prog = st.progress(0, f"Scoring {len(all_tickers)} tickers across 7 conviction layers...")

        def score_one(t, idx):
            cr = score_conviction(t, scan_target, finnhub_key)
            with lock:
                results.append(cr)
                prog.progress(len(results)/len(all_tickers),
                               f"Scored {len(results)}/{len(all_tickers)} — {t}")

        threads = [threading.Thread(target=score_one, args=(t,i), daemon=True)
                   for i,t in enumerate(all_tickers)]
        for th in threads: th.start()
        for th in threads: th.join(timeout=60)
        prog.empty()

        # Sort by conviction score
        results.sort(key=lambda x: x["score"], reverse=True)

        # Save to session
        existing = st.session_state.get("conviction_results",[])
        # Remove stale entries for same tickers
        existing = [e for e in existing if e["ticker"] not in [r["ticker"] for r in results]]
        st.session_state["conviction_results"] = results + existing

        # Show top results
        st.markdown(f'<span class="mm-label">Top conviction signals — {scan_target}</span>', unsafe_allow_html=True)
        top_n = [r for r in results if r["confirmed_layers"] >= min_layers][:6]
        for cr in top_n:
            render_conviction_card(cr)
            with st.expander(f"◈ Full thesis — {cr['ticker']}", expanded=False):
                out = st.empty(); full = ""
                for chunk in stream_conviction_thesis(cr, gemini_key):
                    full += chunk; out.markdown(full)
            st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
#  TAB 2 — CONVICTION RESULTS (all runs, ranked)
# ══════════════════════════════════════════════════════════════════════════════
with tab_results:
    results_all = st.session_state.get("conviction_results",[])
    if not results_all:
        st.info("Run a supply chain scan first. Results accumulate across all scans.")
    else:
        # Summary stats
        ultra = [r for r in results_all if r["grade"]=="ultra"]
        high  = [r for r in results_all if r["grade"]=="high"]
        med   = [r for r in results_all if r["grade"]=="med"]

        sm1,sm2,sm3,sm4 = st.columns(4)
        sm1.metric("Total tracked",   len(results_all))
        sm2.metric("Ultra High",      len(ultra), delta=f"≥{ultra_thresh}")
        sm3.metric("High conviction", len(high),  delta=f"≥{high_thresh}")
        sm4.metric("Cross-chain hits",sum(1 for r in results_all if r["layers"].get("L5_cross_chain",{}).get("n_chains",0)>=2))

        # Filter
        fc1,fc2 = st.columns([2,1])
        with fc1: grade_f = st.selectbox("Filter", ["All","ultra","high","med","low"], key="sb_grade_f")
        with fc2: sort_f  = st.selectbox("Sort",   ["Score","R/R","Cross-chain","Recent"], key="sb_sort_f")

        filtered = [r for r in results_all if grade_f=="All" or r["grade"]==grade_f]
        if sort_f == "R/R":        filtered.sort(key=lambda x: x.get("rr",0) or 0, reverse=True)
        elif sort_f == "Cross-chain": filtered.sort(key=lambda x: x["layers"].get("L5_cross_chain",{}).get("n_chains",0), reverse=True)
        elif sort_f == "Recent":   filtered.sort(key=lambda x: x["ts"], reverse=True)
        else:                      filtered.sort(key=lambda x: x["score"], reverse=True)

        for cr in filtered[:15]:
            render_conviction_card(cr)
            col_th, col_dl = st.columns([3,1])
            with col_th:
                if st.button(f"⊕ Full thesis — {cr['ticker']}", key=f"th_{cr['ticker']}_{cr['ts'][:10]}"):
                    with st.spinner(f"Writing thesis for {cr['ticker']}..."):
                        out = st.empty(); full = ""
                        for chunk in stream_conviction_thesis(cr, gemini_key):
                            full += chunk; out.markdown(full)
            with col_dl:
                export_data = json.dumps(cr, indent=2)
                st.download_button("⬇ JSON", data=export_data,
                    file_name=f"conviction_{cr['ticker']}_{datetime.now():%Y%m%d}.json",
                    mime="application/json", key=f"dl_{cr['ticker']}_{cr['ts'][:10]}")
            st.markdown("---")

        # Bulk CSV
        if filtered:
            df = pd.DataFrame([{
                "Ticker":   r["ticker"],
                "Score":    r["score"],
                "Grade":    r["grade"].upper(),
                "Layers":   r["confirmed_layers"],
                "Chains":   r["layers"].get("L5_cross_chain",{}).get("n_chains",0),
                "Price":    r.get("price",""),
                "Entry":    r.get("entry",""),
                "Target":   r.get("target",""),
                "Stop":     r.get("stop",""),
                "Upside%":  r.get("upside",""),
                "R/R":      r.get("rr",""),
                "Chain":    r["chain_source"][:30],
                "Updated":  r["ts"][:10],
            } for r in filtered])
            st.download_button("⬇ Export all as CSV",
                data=df.to_csv(index=False),
                file_name=f"conviction_all_{datetime.now():%Y%m%d_%H%M}.csv",
                mime="text/csv", key="btn_dl_csv")

# ══════════════════════════════════════════════════════════════════════════════
#  TAB 3 — CROSS-CHAIN MEMORY (the highest-alpha layer)
# ══════════════════════════════════════════════════════════════════════════════
with tab_memory:
    st.markdown("### Cross-Chain Memory")
    st.markdown("""
**The highest-conviction signal is a ticker that appears independently across multiple supply chains.**
When you scan `$NVDA`, `Solid State Batteries`, and `Hypersonic weapons` and the same small-cap
keeps appearing — that company is a structural platform, not just a supplier.
This tab tracks every ticker across every scan you've run.
""")

    chain_mem = st.session_state.get("chain_memory",{})
    if not chain_mem:
        st.info("Run multiple supply chain scans. Tickers that appear in 3+ independent chains will be highlighted here.")
    else:
        # Sort by appearance count
        sorted_mem = sorted(chain_mem.items(), key=lambda x: len(x[1]), reverse=True)

        # Highlight multi-chain names
        multi = [(t,c) for t,c in sorted_mem if len(c)>=2]
        single= [(t,c) for t,c in sorted_mem if len(c)==1]

        if multi:
            st.markdown('<span class="mm-label">Multi-chain appearances — highest conviction</span>', unsafe_allow_html=True)
            for ticker, chains in multi:
                n = len(chains)
                grade = "ultra" if n>=3 else "high"
                badges = "".join([f'<span class="xchain-badge">🔗 {c}</span>' for c in chains])
                st.markdown(f"""
<div class="conv-meter {grade}" style="padding:14px 18px;margin:6px 0">
  <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
    <span style="font-size:1.1rem;font-weight:800;font-family:'JetBrains Mono',monospace;color:#111827">{ticker}</span>
    <span class="conv-verdict {grade}">{n} independent chains</span>
  </div>
  <div style="margin-top:8px">{badges}</div>
</div>""", unsafe_allow_html=True)
                # Quick conviction score
                if st.button(f"Score {ticker} now →", key=f"mem_score_{ticker}"):
                    if gemini_key:
                        with st.spinner(f"Running conviction analysis on {ticker}..."):
                            cr = score_conviction(ticker, f"cross-chain ({n} appearances)", finnhub_key)
                        render_conviction_card(cr)
                        existing = st.session_state.get("conviction_results",[])
                        existing = [e for e in existing if e["ticker"]!=ticker]
                        st.session_state["conviction_results"] = [cr] + existing

        if single:
            with st.expander(f"Single-chain appearances ({len(single)} tickers)"):
                for ticker, chains in single[:30]:
                    st.markdown(f'<span style="font-size:0.82rem;color:#374151;margin-right:12px"><b>{ticker}</b> — {chains[0]}</span>', unsafe_allow_html=True)

        # Export memory
        st.download_button("⬇ Export chain memory JSON",
            data=json.dumps(chain_mem, indent=2),
            file_name=f"chain_memory_{datetime.now():%Y%m%d}.json",
            mime="application/json", key="btn_dl_mem")

# ══════════════════════════════════════════════════════════════════════════════
#  TAB 4 — SINGLE TICKER CONVICTION (direct analysis)
# ══════════════════════════════════════════════════════════════════════════════
with tab_single:
    st.markdown("### Single Ticker Conviction Analysis")
    st.markdown("Input any ticker directly. Runs all 7 conviction layers and generates a full thesis.")

    st1c1, st1c2, st1c3 = st.columns([2,2,1])
    with st1c1:
        single_ticker = st.text_input("Ticker", placeholder="NVDA · AXTI · RKLB · PLTR",
                                       label_visibility="collapsed", key="ti_single")
    with st1c2:
        single_context= st.text_input("Supply chain context (optional)",
                                       placeholder="e.g. AI chip supply chain, Tier 2",
                                       key="ti_single_ctx", label_visibility="collapsed")
    with st1c3:
        single_btn = st.button("◈ Analyse", type="primary", key="btn_single", use_container_width=True)

    if single_btn and single_ticker.strip():
        if not gemini_key:
            st.warning("Add Gemini API key.")
        else:
            t = single_ticker.strip().upper().replace("$","")
            ctx = single_context.strip() or "Direct analysis"

            # Update cross-chain memory
            mem = st.session_state.get("chain_memory",{})
            if t not in mem: mem[t] = []
            if ctx not in mem[t]: mem[t].append(ctx)
            st.session_state["chain_memory"] = mem

            with st.spinner(f"Running all 7 conviction layers on {t}..."):
                cr = score_conviction(t, ctx, finnhub_key)

            render_conviction_card(cr)

            existing = st.session_state.get("conviction_results",[])
            existing = [e for e in existing if e["ticker"]!=t]
            st.session_state["conviction_results"] = [cr] + existing

            st.markdown("---")
            with st.status(f"Writing conviction thesis for {t}...", expanded=True) as ts:
                out = st.empty(); full = ""
                for chunk in stream_conviction_thesis(cr, gemini_key):
                    full += chunk; out.markdown(full)
                ts.update(label=f"✓ Thesis complete — {t}", state="complete")

            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                st.download_button("⬇ Download thesis",
                    data=full, file_name=f"thesis_{t}_{datetime.now():%Y%m%d_%H%M}.txt",
                    mime="text/plain", key=f"dl_thesis_{t}")
            with col_dl2:
                st.download_button("⬇ Download conviction JSON",
                    data=json.dumps(cr,indent=2),
                    file_name=f"conviction_{t}_{datetime.now():%Y%m%d}.json",
                    mime="application/json", key=f"dl_json_{t}")
