"""
Alpha Machine — app.py
No yfinance. No aiohttp. Uses free public APIs + threading for parallel agents.
Works on Streamlit Cloud Python 3.14.
"""

import streamlit as st

st.set_page_config(
    page_title="Alpha Machine 🎯",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

import requests
import feedparser
import json
import threading
import pandas as pd
from datetime import datetime
import time

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0a0a0f; }
[data-testid="stSidebar"] { background: #0f0f1a; }
.block-container { padding-top: 1.2rem; }
.alpha-title {
    font-size:2rem; font-weight:900;
    background: linear-gradient(90deg,#00f5a0,#00d9f5,#a78bfa);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
.sub { color:#6b7280; font-size:0.85rem; }
.shdr { color:#d1d5db; font-size:0.95rem; font-weight:700;
        border-bottom:1px solid #1f2937; padding-bottom:5px; margin:12px 0 8px; }
.mbox { background:#111827; border:1px solid #1f2937; border-radius:10px;
        padding:12px 10px; text-align:center; min-height:86px; }
.mlbl { color:#9ca3af; font-size:0.68rem; text-transform:uppercase; letter-spacing:1px; }
.mval { color:#f9fafb; font-size:1.25rem; font-weight:700; margin:3px 0; }
.mup  { color:#10b981; font-size:0.78rem; font-weight:600; }
.mdn  { color:#ef4444; font-size:0.78rem; font-weight:600; }
.mna  { color:#4b5563; font-size:0.78rem; }
.bet  { background:#0d1f10; border:1px solid #10b981;
        border-left:4px solid #00f5a0; border-radius:10px;
        padding:18px 22px; margin:10px 0;
        font-family:monospace; font-size:0.87rem;
        color:#d1fae5; white-space:pre-wrap; line-height:1.6; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="alpha-title">🎯 Alpha Machine</p>', unsafe_allow_html=True)
st.markdown(f'<p class="sub">Multi-Agent Asymmetric Bet Scanner &nbsp;·&nbsp; {datetime.now().strftime("%Y-%m-%d %H:%M UTC")}</p>', unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Gemini API (Free)")
    gemini_key = st.text_input("API Key", type="password", placeholder="AIza...")
    st.markdown("### 📱 Telegram Alerts")
    tg_token = st.text_input("Bot Token",  type="password")
    tg_chat  = st.text_input("Chat ID",    placeholder="-100123456789")
    st.markdown("### 📋 Watchlists")
    stocks_raw  = st.text_area("Stocks",      value="NVDA,TSM,ASML,PLTR,IONQ,RKLB,HIMS,CELH,NVO,MELI", height=85)
    sectors_raw = st.text_area("Sector ETFs", value="XLK,XLE,XLF,XLV,XBI,ARKK,GDX,COPX,ITB,XAR",      height=85)
    st.markdown("---")
    run_btn = st.button("🚀 Run Alpha Scan", type="primary", use_container_width=True)
    st.caption("~2-3 min · 5 parallel agents · Gemini 2.0 Flash Lite")

STOCKS  = [s.strip() for s in stocks_raw.split(",")  if s.strip()]
SECTORS = [s.strip() for s in sectors_raw.split(",") if s.strip()]

# ── DATA: FREE PUBLIC APIs (no rate limit issues) ─────────────────────────────

MACRO_SYMBOLS = {
    "BTC/USD":  ("crypto",  "bitcoin"),
    "ETH/USD":  ("crypto",  "ethereum"),
    "Gold":     ("metals",  "XAU"),
    "Oil WTI":  ("energy",  "CL"),
    "DXY":      ("fx",      "DXY"),
    "VIX":      ("index",   "VIX"),
}

@st.cache_data(ttl=300, show_spinner=False)
def get_crypto_price(coin_id):
    """CoinGecko free API — no key needed."""
    try:
        r = requests.get(
            f"https://api.coingecko.com/api/v3/simple/price",
            params={"ids": coin_id, "vs_currencies": "usd", "include_24hr_change": "true"},
            timeout=8, headers={"User-Agent": "AlphaMachine/1.0"}
        )
        d = r.json()
        if coin_id in d:
            return round(d[coin_id]["usd"], 2), round(d[coin_id]["usd_24h_change"], 2)
    except:
        pass
    return None, None

@st.cache_data(ttl=300, show_spinner=False)
def get_macro_prices():
    """Fetch macro prices using Yahoo Finance chart API (different endpoint, not blocked)."""
    results = {}
    tickers = {
        "10Y Yield": "%5ETNX",
        "S&P 500":   "%5EGSPC",
        "Gold":      "GC%3DF",
        "Oil":       "CL%3DF",
        "VIX":       "%5EVIX",
        "DXY":       "DX-Y.NYB",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    }
    for label, sym in tickers.items():
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range=5d"
            r = requests.get(url, headers=headers, timeout=6)
            d = r.json()
            closes = d["chart"]["result"][0]["indicators"]["quote"][0]["close"]
            closes = [c for c in closes if c is not None]
            if len(closes) >= 2:
                price = round(closes[-1], 2)
                chg   = round((closes[-1]/closes[-2] - 1)*100, 2)
                results[label] = (price, chg)
        except:
            results[label] = (None, None)

    # Add crypto from CoinGecko
    btc_p, btc_c = get_crypto_price("bitcoin")
    results["Bitcoin"] = (btc_p, btc_c)
    return results

@st.cache_data(ttl=300, show_spinner=False)
def get_stock_data(tickers):
    """Fetch stock data using Yahoo Finance chart API."""
    rows = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    }
    for sym in tickers:
        try:
            # Price + history
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range=3mo"
            r = requests.get(url, headers=headers, timeout=8)
            d = r.json()
            res    = d["chart"]["result"][0]
            closes = res["indicators"]["quote"][0]["close"]
            closes = [c for c in closes if c is not None]
            if len(closes) < 15:
                continue
            price = round(closes[-1], 2)
            m1    = round((closes[-1]/closes[-22]-1)*100, 2) if len(closes)>=22 else 0

            # RSI
            import statistics
            diffs = [closes[i]-closes[i-1] for i in range(1,len(closes))]
            gains = [max(d,0) for d in diffs[-14:]]
            losses= [abs(min(d,0)) for d in diffs[-14:]]
            ag, al = sum(gains)/14, sum(losses)/14
            rsi = round(100 - 100/(1 + ag/(al+1e-9)), 1)

            # Metadata
            meta  = res.get("meta", {})
            w52h  = meta.get("fiftyTwoWeekHigh", 0) or 0
            w52l  = meta.get("fiftyTwoWeekLow", 0)  or 0

            sigs = []
            if rsi < 35:                        sigs.append("🟢 Oversold")
            if rsi > 70:                        sigs.append("🔴 Overbought")
            if w52h and price >= w52h * 0.97:   sigs.append("🚀 52W High")
            if w52h and price <= w52h * 0.55:   sigs.append("💎 Deep Value")
            if m1 > 15:                         sigs.append("⚡ Momentum")

            rows.append({
                "Ticker": sym,
                "Price":  price,
                "1M%":    m1,
                "RSI":    rsi,
                "52W Hi": w52h,
                "52W Lo": w52l,
                "Signals": " ".join(sigs) if sigs else "—",
            })
            time.sleep(0.15)  # gentle rate limit
        except Exception as e:
            rows.append({"Ticker": sym, "Price": "—", "1M%": "—", "RSI": "—",
                         "52W Hi":"—","52W Lo":"—", "Signals": f"err"})
    return pd.DataFrame(rows) if rows else pd.DataFrame()

@st.cache_data(ttl=300, show_spinner=False)
def get_sector_data(tickers):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    }
    rows = []
    for sym in tickers:
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range=1mo"
            r   = requests.get(url, headers=headers, timeout=8)
            d   = r.json()
            closes = d["chart"]["result"][0]["indicators"]["quote"][0]["close"]
            closes = [c for c in closes if c is not None]
            if len(closes) < 5:
                continue
            m1 = round((closes[-1]/closes[0]-1)*100, 2)
            w1 = round((closes[-1]/closes[-6]-1)*100, 2) if len(closes)>=6 else 0
            rows.append({"ETF": sym, "1M%": m1, "1W%": w1})
            time.sleep(0.1)
        except:
            pass
    return pd.DataFrame(rows).sort_values("1M%", ascending=False).reset_index(drop=True) if rows else pd.DataFrame()

@st.cache_data(ttl=600, show_spinner=False)
def get_news(query, n=10):
    try:
        url  = f"https://news.google.com/rss/search?q={requests.utils.quote(query)}&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(url)
        return [{"title": e.get("title",""), "source": e.get("source",{}).get("title","")}
                for e in feed.entries[:n]]
    except:
        return []

# ── GEMINI — google-genai SDK with Google Search grounding ───────────────────
# Model: gemini-2.5-flash-preview-05-20 (latest, free tier)
# Get free key: https://aistudio.google.com/app/apikey

from google import genai
from google.genai import types

def call_gemini(system, user, key):
    """Call Gemini with Google Search grounding — same pattern as working Alpha Terminal."""
    try:
        client = genai.Client(api_key=key)
        google_search_tool = types.Tool(google_search=types.GoogleSearch())
        config = types.GenerateContentConfig(
            tools=[google_search_tool],
            temperature=0.2,
            system_instruction=system,
        )
        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-05-20",
            contents=user,
            config=config,
        )
        return response.text
    except Exception as e:
        return f"[API error: {e}]"

# ── AGENTS ────────────────────────────────────────────────────────────────────

def agent_macro(key, results, macro_prices, news_geo, news_rates):
    prompt = f"""Date: {datetime.now().strftime('%Y-%m-%d')}

LIVE MACRO PRICES:
{json.dumps({k: {"price": v[0], "24h_chg%": v[1]} for k,v in macro_prices.items()}, indent=2)}

GEOPOLITICAL & RATES NEWS:
{json.dumps((news_geo + news_rates)[:12], indent=2)}

Identify TOP 3 macro tailwinds creating asymmetric opportunities RIGHT NOW.
For each tailwind:
- Theme name
- Specific beneficiary asset classes / sectors
- Timeline (weeks/months/quarters)  
- Crowding level (consensus or contrarian?)
- Confidence score 1-10
- Single kill risk

Be specific and actionable. Plain text only."""
    results["macro"] = call_gemini(
        "You are a global macro strategist. Think Ray Dalio — debt cycles, capital flows, geopolitics. Find invisible forces moving markets before the crowd.",
        prompt, key)

def agent_sector(key, results, df_sector, news_flow):
    prompt = f"""Date: {datetime.now().strftime('%Y-%m-%d')}

SECTOR ETF MOMENTUM:
{df_sector.to_string(index=False) if not df_sector.empty else "Data unavailable"}

SECTOR FLOW HEADLINES:
{json.dumps(news_flow[:10], indent=2)}

Identify TOP 2 sectors in EARLY institutional accumulation (not crowded yet).
Look for: weakest 1M performance that's now turning, positive news flow, macro tailwind alignment.
For each: ETF ticker, theme, why it's early-stage, macro driver, score 1-10.
Plain text only."""
    results["sector"] = call_gemini(
        "You are a sector rotation specialist. Find sectors before ETF inflows show on Bloomberg. Sectors move with macro; stocks move with sectors.", prompt, key)

def agent_stocks(key, results, df_stocks, news_catalyst):
    prompt = f"""Date: {datetime.now().strftime('%Y-%m-%d')}

STOCK SIGNALS:
{df_stocks.to_string(index=False) if not df_stocks.empty else "Data unavailable"}

CATALYST NEWS:
{json.dumps(news_catalyst[:10], indent=2)}

Find TOP 3 stocks where 3+ signals STACK simultaneously:
  • Oversold RSI (<35) or deep value vs 52W high
  • Strong momentum signal
  • Sector tailwind alignment  
  • Upcoming catalyst (earnings, FDA, contract, product launch)
  • Short squeeze potential

For each pick: ticker, stacked signals list, specific catalyst + expected date,
entry rationale, asymmetry score 1-10, time horizon.
Plain text only."""
    results["stocks"] = call_gemini(
        "You are a stock catalyst specialist. Find asymmetric setups where multiple signals stack. You obsess over risk/reward ratios.", prompt, key)

def agent_contra(key, results, df_stocks, news_bear):
    prompt = f"""Date: {datetime.now().strftime('%Y-%m-%d')}

STOCK DATA:
{df_stocks.to_string(index=False) if not df_stocks.empty else "Data unavailable"}

BEAR CASE HEADLINES:
{json.dumps(news_bear[:10], indent=2)}

Stress-test each stock in the watchlist:
1. What is already priced in? (what does market know?)
2. Biggest bear case / short thesis
3. What macro scenario kills this trade?
4. Crowding score 1-10 (10 = very crowded/consensus)
5. Verdict: BUY / WATCH / AVOID

Flag any AVOID verdict prominently. Be the devil's advocate.
Plain text only."""
    results["contra"] = call_gemini(
        "You are a contrarian short-seller. Stress-test every bull thesis relentlessly. Only truly asymmetric bets survive your filter.", prompt, key)

def agent_thesis(key, results):
    prompt = f"""Date: {datetime.now().strftime('%Y-%m-%d')}

═══ MACRO SCOUT OUTPUT ═══
{results.get('macro', 'N/A')}

═══ SECTOR ANALYST OUTPUT ═══
{results.get('sector', 'N/A')}

═══ STOCK SNIPER OUTPUT ═══
{results.get('stocks', 'N/A')}

═══ CONTRARIAN AUDIT OUTPUT ═══
{results.get('contra', 'N/A')}

Synthesize ALL findings into a final ASYMMETRIC BET REPORT.

Rules:
- Only surface bets scoring 7+ average (Asymmetry + Catalyst Clarity + Macro Alignment)
- Skip any ticker the contrarian flagged as AVOID
- Cross-reference: stock bet must align with sector + macro tailwind

FORMAT each qualifying bet EXACTLY like this:

🎯 ASYMMETRIC BET: [TICKER]
📊 THEME: [one-line macro/sector driver]
🔥 CATALYSTS:
   • [stacking signal 1]
   • [stacking signal 2]
   • [stacking signal 3+]
⚠️ KEY RISK: [single biggest risk]
📈 SETUP: Entry ~$X | Target $X–$X | Stop $X | Horizon: X months
🏆 SCORE: Asymmetry X/10 | Catalyst X/10 | Macro X/10

After all bets add:
📋 PORTFOLIO NOTE: [correlation between bets, concentrated or hedged?]
🌍 MACRO REGIME: [one sentence — current market backdrop]"""
    results["thesis"] = call_gemini(
        "You are the CIO of a macro hedge fund. Distill 4 analyst reports into razor-sharp, actionable investment theses. No fluff. Only alpha scoring 7+/10.",
        prompt, key)

# ── PARALLEL RUNNER (threading, no asyncio) ───────────────────────────────────

def run_parallel_scan(key, df_stocks, df_sectors):
    results = {}

    # Prefetch all data
    macro_prices  = get_macro_prices()
    news_geo      = get_news("geopolitical risk trade war tariffs 2026", 8)
    news_rates    = get_news("Federal Reserve interest rate inflation 2026", 6)
    news_flow     = get_news("sector rotation ETF inflows institutional buying 2026", 8)
    news_catalyst = get_news("insider buying FDA approval DoD contract earnings beat 2026", 10)
    news_bear     = get_news("overvalued bubble short seller crowded trade warning 2026", 8)

    # Launch 4 agents in parallel threads
    threads = [
        threading.Thread(target=agent_macro,   args=(key, results, macro_prices, news_geo, news_rates)),
        threading.Thread(target=agent_sector,  args=(key, results, df_sectors, news_flow)),
        threading.Thread(target=agent_stocks,  args=(key, results, df_stocks, news_catalyst)),
        threading.Thread(target=agent_contra,  args=(key, results, df_stocks, news_bear)),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=200)

    # Agent 5 synthesizes
    agent_thesis(key, results)
    return results

# ── TELEGRAM ──────────────────────────────────────────────────────────────────

def send_telegram(text, token, chat_id):
    for chunk in [text[i:i+4000] for i in range(0, len(text), 4000)]:
        try:
            requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat_id, "text": chunk},
                timeout=10
            )
        except:
            pass

# ═══════════════════════════════════════════════════════════════════════════════
#  UI TABS
# ═══════════════════════════════════════════════════════════════════════════════

tab1, tab2, tab3 = st.tabs(["📊 Live Dashboard", "🤖 Alpha Scan", "ℹ️ How It Works"])

# ════════════════════════════════════════
# TAB 1 — LIVE DASHBOARD
# ════════════════════════════════════════
with tab1:

    # MACRO ROW
    st.markdown('<p class="shdr">🌍 Macro Pulse</p>', unsafe_allow_html=True)
    with st.spinner("Fetching live prices..."):
        macro_prices = get_macro_prices()

    cols = st.columns(len(macro_prices))
    for col, (label, (price, chg)) in zip(cols, macro_prices.items()):
        with col:
            if price is not None:
                cls = "mup" if (chg or 0) >= 0 else "mdn"
                sgn = "+" if (chg or 0) >= 0 else ""
                st.markdown(f"""<div class="mbox">
<p class="mlbl">{label}</p>
<p class="mval">{price:,.2f}</p>
<p class="{cls}">{sgn}{chg:.2f}%</p>
</div>""", unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="mbox"><p class="mlbl">{label}</p><p class="mval">—</p><p class="mna">unavailable</p></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns([1, 2])

    with left:
        st.markdown('<p class="shdr">🔄 Sector Momentum</p>', unsafe_allow_html=True)
        with st.spinner(""):
            df_sec = get_sector_data(SECTORS)
        if not df_sec.empty:
            def csec(v):
                if isinstance(v, (int, float)):
                    return "color:#10b981;font-weight:600" if v > 0 else "color:#ef4444;font-weight:600"
                return ""
            st.dataframe(df_sec.style.map(csec, subset=["1M%","1W%"]),
                         width="stretch", hide_index=True, height=370)
        else:
            st.warning("Sector data temporarily unavailable")

    with right:
        st.markdown('<p class="shdr">🎯 Watchlist Signals</p>', unsafe_allow_html=True)
        with st.spinner(""):
            df_st = get_stock_data(STOCKS)
        if not df_st.empty:
            def crsi(v):
                if isinstance(v, (int, float)):
                    if v < 35: return "color:#10b981;font-weight:700"
                    if v > 70: return "color:#ef4444;font-weight:700"
                return ""
            def cm1(v):
                if isinstance(v, (int, float)):
                    return "color:#10b981" if v > 0 else "color:#ef4444"
                return ""
            st.dataframe(
                df_st.style.map(crsi, subset=["RSI"]).map(cm1, subset=["1M%"]),
                width="stretch", hide_index=True, height=370
            )
        else:
            st.warning("Stock data temporarily unavailable")

    st.markdown('<p class="shdr">📰 Market Headlines</p>', unsafe_allow_html=True)
    with st.spinner(""):
        news = get_news("stock market catalyst asymmetric opportunity 2026", 8)
    for h in news:
        st.markdown(f"• **{h['title']}** <span style='color:#4b5563;font-size:0.78rem'>— {h['source']}</span>", unsafe_allow_html=True)

# ════════════════════════════════════════
# TAB 2 — ALPHA SCAN
# ════════════════════════════════════════
with tab2:
    st.markdown('<p class="shdr">🤖 5-Agent Parallel Alpha Scan</p>', unsafe_allow_html=True)

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.markdown("**🌍 Macro**\nGeopolitics\nRates · FX")
    c2.markdown("**🔄 Sector**\nRotation\nETF Flow")
    c3.markdown("**🎯 Stocks**\nCatalysts\nInsiders")
    c4.markdown("**⚠️ Contra**\nBear cases\nStress test")
    c5.markdown("**📝 CIO**\nSynthesis\nFinal alert")
    st.markdown("*Agents 1–4 run simultaneously via threads → Agent 5 synthesizes → Telegram*")
    st.divider()

    if not run_btn:
        st.info("👈 Enter your **Gemini API key** in the sidebar, then click **Run Alpha Scan**")
        with st.expander("📋 Example output"):
            st.code("""🎯 ASYMMETRIC BET: RKLB
📊 THEME: Space defense + smallsat boom + DoD tailwind
🔥 CATALYSTS:
   • RSI 31 — deeply oversold after sector selloff
   • CEO bought $2.1M shares (Form 4, Feb 2026)
   • DoD launch contract award expected Q2 2026
   • XAR (aerospace ETF) breaking 52W high
⚠️ KEY RISK: Neutron rocket timeline slippage
📈 SETUP: Entry ~$8.50 | Target $14–18 | Stop $6.80 | Horizon: 9 months
🏆 SCORE: Asymmetry 8/10 | Catalyst 9/10 | Macro 8/10

📋 PORTFOLIO NOTE: RKLB + IONQ uncorrelated; both early-stage with binary catalysts
🌍 MACRO REGIME: Risk-on, rate cut expectations supporting growth/tech rotation""", language=None)

    if run_btn:
        if not gemini_key:
            st.error("⚠️ Gemini API key required — add it in the sidebar.")
        else:
            # Load market data first
            with st.spinner("📡 Fetching live market data..."):
                df_stocks  = get_stock_data(STOCKS)
                df_sectors = get_sector_data(SECTORS)

            st.success(f"✅ Loaded {len(df_stocks)} stocks · {len(df_sectors)} sectors")

            # Agent progress display
            st.markdown("**🔄 Running agents in parallel...**")
            p1 = st.progress(0, text="Launching 4 parallel agents...")

            col_s = st.columns(4)
            placeholders = {
                "macro":  col_s[0].empty(),
                "sector": col_s[1].empty(),
                "stocks": col_s[2].empty(),
                "contra": col_s[3].empty(),
            }
            for k, label in [("macro","🌍 Macro Scout"),("sector","🔄 Sector Analyst"),
                              ("stocks","🎯 Stock Sniper"),("contra","⚠️ Contrarian")]:
                placeholders[k].info(f"{label}\n⏳ Running...")

            thesis_ph = st.empty()
            thesis_ph.info("📝 Thesis Writer waiting for agents...")

            try:
                p1.progress(20, text="Agents running (2-3 min)...")
                results = run_parallel_scan(gemini_key, df_stocks, df_sectors)
                p1.progress(85, text="Writing final thesis...")

                # Update agent status cards
                for k, label in [("macro","🌍 Macro Scout"),("sector","🔄 Sector Analyst"),
                                  ("stocks","🎯 Stock Sniper"),("contra","⚠️ Contrarian")]:
                    val = results.get(k, "")
                    if val.startswith("["):
                        placeholders[k].error(f"{label}\n❌ {val[:80]}")
                    else:
                        placeholders[k].success(f"{label}\n✅ Complete")

                thesis_ph.success("📝 Thesis Writer ✅ Complete")
                p1.progress(100, text="✅ Scan complete!")

                st.divider()
                st.markdown("## 🏆 Final Alpha Report")

                final = results.get("thesis", "[No thesis generated]")
                st.markdown(f'<div class="bet">{final}</div>', unsafe_allow_html=True)

                # Agent details in expanders
                with st.expander("🌍 Macro Scout full output"):
                    st.write(results.get("macro",""))
                with st.expander("🔄 Sector Analyst full output"):
                    st.write(results.get("sector",""))
                with st.expander("🎯 Stock Sniper full output"):
                    st.write(results.get("stocks",""))
                with st.expander("⚠️ Contrarian full output"):
                    st.write(results.get("contra",""))

                # Actions
                col_dl, col_tg = st.columns(2)
                with col_dl:
                    full_report = "\n\n".join([
                        f"ALPHA MACHINE REPORT — {datetime.now()}",
                        f"=== MACRO ===\n{results.get('macro','')}",
                        f"=== SECTOR ===\n{results.get('sector','')}",
                        f"=== STOCKS ===\n{results.get('stocks','')}",
                        f"=== CONTRARIAN ===\n{results.get('contra','')}",
                        f"=== FINAL THESIS ===\n{final}",
                    ])
                    st.download_button("⬇️ Download Full Report", data=full_report,
                        file_name=f"alpha_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                        mime="text/plain", use_container_width=True)
                with col_tg:
                    if tg_token and tg_chat:
                        header = f"🤖 ALPHA MACHINE\n{datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n{'─'*30}\n\n"
                        send_telegram(header + final, tg_token, tg_chat)
                        st.success("📱 Sent to Telegram!")
                    else:
                        st.info("Add Telegram credentials in sidebar for auto-alerts")

            except Exception as e:
                p1.progress(0)
                st.error(f"❌ Scan failed: {e}")

# ════════════════════════════════════════
# TAB 3 — HOW IT WORKS
# ════════════════════════════════════════
with tab3:
    st.markdown("## 🏗️ Architecture")
    st.markdown("""
| Agent | Role | Data Sources |
|---|---|---|
| 🌍 Macro Scout | Geopolitics, rates, FX, commodities | Yahoo Finance Chart API + Google News RSS |
| 🔄 Sector Analyst | ETF rotation, institutional flow | Yahoo Finance Chart API + headlines |
| 🎯 Stock Sniper | Catalysts, signals, stacked setups | Yahoo Finance Chart API + news |
| ⚠️ Contrarian | Stress-tests every bull thesis | Price data + bear case news |
| 📝 Thesis Writer | CIO synthesis — scores and formats | All 4 agent outputs |

**What makes a bet qualify (must pass all 3):**
- 3+ signals stacking simultaneously on the same ticker
- Catalyst not yet priced in by the market
- Score 7+/10 across: Asymmetry · Catalyst Clarity · Macro Alignment
- Survives the Contrarian stress test (no AVOID verdict)

**Cost:** Gemini 2.0 Flash Lite is **completely FREE** — 1,500 requests/day, no billing needed
    """)
    st.markdown("## 🔑 Setup")
    st.markdown("""
**Gemini API Key** → [aistudio.google.com](https://aistudio.google.com/app/apikey) → **Create API Key** → completely free, no billing needed

**Telegram Bot:**
1. Message [@BotFather](https://t.me/BotFather) on Telegram → `/newbot`
2. Add bot to your channel as admin
3. Get Chat ID: visit `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
    """)
