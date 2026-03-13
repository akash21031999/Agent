"""
Alpha Machine — app.py
Streamlit Cloud entry point (must be named app.py)
Python 3.14 compatible | No CrewAI | Self-contained
"""

import nest_asyncio
nest_asyncio.apply()  # Fix asyncio.run() inside Streamlit

import streamlit as st

st.set_page_config(
    page_title="Alpha Machine 🎯",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

import yfinance as yf
import requests
import feedparser
import json
import asyncio
import aiohttp
import pandas as pd
from datetime import datetime

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0a0a0f; color: #e5e7eb; }
[data-testid="stSidebar"]          { background: #0f0f1a; }
[data-testid="stSidebar"] * { color: #e5e7eb !important; }
.block-container { padding-top: 1.2rem; }
h1,h2,h3,p,li,span,label { color: #e5e7eb; }

.alpha-title {
    font-size: 2rem; font-weight: 900; letter-spacing: -1px;
    background: linear-gradient(90deg, #00f5a0, #00d9f5, #a78bfa);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.subtitle { color: #6b7280; font-size: 0.85rem; margin-top: 0; }
.section-hdr {
    color: #d1d5db; font-size: 1rem; font-weight: 700;
    border-bottom: 1px solid #1f2937; padding-bottom: 6px; margin: 14px 0 10px 0;
}
.mbox {
    background: #111827; border: 1px solid #1f2937;
    border-radius: 10px; padding: 12px 16px; text-align: center; min-height: 88px;
}
.mlabel { color: #9ca3af; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; }
.mval   { color: #f9fafb; font-size: 1.3rem; font-weight: 700; margin: 4px 0; }
.mup    { color: #10b981; font-size: 0.8rem; font-weight: 600; }
.mdown  { color: #ef4444; font-size: 0.8rem; font-weight: 600; }
.mna    { color: #6b7280; font-size: 0.8rem; }
.bet-card {
    background: #0d1f10; border: 1px solid #10b981;
    border-left: 4px solid #00f5a0; border-radius: 10px;
    padding: 18px 22px; margin: 10px 0; white-space: pre-wrap;
    font-family: monospace; font-size: 0.88rem; color: #d1fae5;
}
</style>
""", unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown('<p class="alpha-title">🎯 Alpha Machine</p>', unsafe_allow_html=True)
st.markdown(f'<p class="subtitle">Multi-Agent Asymmetric Bet Scanner &nbsp;·&nbsp; {datetime.now().strftime("%Y-%m-%d %H:%M UTC")}</p>', unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Config")
    deepseek_key   = st.text_input("DeepSeek API Key", type="password", placeholder="sk-...")
    st.markdown("### 📱 Telegram")
    telegram_token = st.text_input("Bot Token",  type="password")
    telegram_chat  = st.text_input("Chat ID",    placeholder="-100123456789")
    st.markdown("### 📋 Watchlists")
    stocks_raw  = st.text_area("Stocks",       value="NVDA,TSM,ASML,PLTR,IONQ,RKLB,HIMS,CELH,NVO,MELI", height=85)
    sectors_raw = st.text_area("Sector ETFs",  value="XLK,XLE,XLF,XLV,XBI,ARKK,GDX,COPX,ITB,XAR",      height=85)
    st.markdown("---")
    run_btn = st.button("🚀 Run Alpha Scan", type="primary", use_container_width=True)
    st.caption("~2-3 min · 5 parallel agents · DeepSeek-R1")

STOCKS  = [s.strip() for s in stocks_raw.split(",")  if s.strip()]
SECTORS = [s.strip() for s in sectors_raw.split(",") if s.strip()]
MACRO_TICKERS = {"^TNX":"10Y Yield","GC=F":"Gold","CL=F":"Oil","DX-Y.NYB":"DXY","BTC-USD":"Bitcoin","^VIX":"VIX"}

# ── DATA HELPERS ──────────────────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def get_price(ticker):
    try:
        hist = yf.Ticker(ticker).history(period="5d")
        if hist is None or len(hist) < 2:
            return None, None
        cur, prev = float(hist["Close"].iloc[-1]), float(hist["Close"].iloc[-2])
        return round(cur, 2), round((cur/prev - 1)*100, 2)
    except:
        return None, None

@st.cache_data(ttl=300, show_spinner=False)
def get_stock_table(tickers):
    rows = []
    for sym in tickers:
        try:
            tk   = yf.Ticker(sym)
            info = tk.info or {}
            hist = tk.history(period="3mo")
            if hist is None or len(hist) < 15:
                continue
            c     = hist["Close"]
            delta = c.diff()
            gain  = delta.clip(lower=0).rolling(14).mean()
            loss  = (-delta.clip(upper=0)).rolling(14).mean()
            rsi   = round(float((100 - 100/(1 + gain/(loss+1e-9))).iloc[-1]), 1)
            price = round(float(c.iloc[-1]), 2)
            m1    = round((float(c.iloc[-1])/float(c.iloc[-22])-1)*100, 2) if len(c)>=22 else 0
            w52h  = info.get("fiftyTwoWeekHigh") or 0
            short = info.get("shortPercentOfFloat") or 0
            sigs  = []
            if rsi < 35:              sigs.append("🟢 Oversold")
            if rsi > 70:              sigs.append("🔴 Overbought")
            if short > 0.15:          sigs.append("⚡ High Short")
            if w52h and price >= w52h*0.97: sigs.append("🚀 Near 52W High")
            if w52h and price <= w52h*0.55: sigs.append("💎 Deep Value")
            rows.append({"Ticker":sym,"Price":price,"1M%":m1,"RSI":rsi,
                         "Short%":f"{short*100:.1f}%" if short else "—",
                         "Signals":" ".join(sigs) if sigs else "—"})
        except:
            pass
    return pd.DataFrame(rows) if rows else pd.DataFrame()

@st.cache_data(ttl=300, show_spinner=False)
def get_sector_table(tickers):
    rows = []
    for sym in tickers:
        try:
            hist = yf.Ticker(sym).history(period="1mo")
            if hist is None or len(hist) < 5:
                continue
            m1 = round((float(hist["Close"].iloc[-1])/float(hist["Close"].iloc[0])-1)*100, 2)
            w1 = round((float(hist["Close"].iloc[-1])/float(hist["Close"].iloc[-6])-1)*100, 2) if len(hist)>=6 else 0
            rows.append({"ETF":sym,"1M%":m1,"1W%":w1})
        except:
            pass
    return pd.DataFrame(rows).sort_values("1M%", ascending=False).reset_index(drop=True) if rows else pd.DataFrame()

@st.cache_data(ttl=600, show_spinner=False)
def get_news(query, n=10):
    try:
        url  = f"https://news.google.com/rss/search?q={requests.utils.quote(query)}&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(url)
        return [{"title": e.get("title",""), "source": e.get("source",{}).get("title","")} for e in feed.entries[:n]]
    except:
        return []

# ── DEEPSEEK ASYNC ────────────────────────────────────────────────────────────

async def ask(session, system, user, key):
    hdrs = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    body = {
        "model": "deepseek-reasoner",
        "max_tokens": 2500,
        "temperature": 0.3,
        "messages": [{"role":"system","content":system}, {"role":"user","content":user}],
    }
    try:
        async with session.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=hdrs, json=body,
            timeout=aiohttp.ClientTimeout(total=180)
        ) as r:
            d = await r.json()
            ch = d.get("choices", [])
            if not ch:
                return f"[API error: {d.get('error', d)}]"
            m = ch[0]["message"]
            return m.get("content") or m.get("reasoning_content", "[empty]")
    except Exception as e:
        return f"[Request failed: {e}]"

# ── AGENTS ────────────────────────────────────────────────────────────────────

async def a_macro(session, key):
    prices = {t: get_price(t) for t in MACRO_TICKERS}
    news   = get_news("geopolitical trade war Federal Reserve rate inflation 2026", 10)
    prompt = f"""Date: {datetime.now().strftime('%Y-%m-%d')}

MACRO DATA:
{json.dumps({k: {"price":v[0],"chg%":v[1]} for k,v in prices.items()}, indent=2)}

HEADLINES: {json.dumps(news, indent=2)}

Identify TOP 3 macro tailwinds creating asymmetric opportunities NOW.
For each: theme, beneficiaries, timeline, crowding level, confidence 1-10, kill risk.
Plain text. Be specific and actionable."""
    return await ask(session, "You are a global macro strategist. Think Ray Dalio. Find invisible forces moving markets before the crowd.", prompt, key)

async def a_sector(session, key):
    df   = get_sector_table(SECTORS)
    news = get_news("sector rotation ETF inflows institutional buying 2026", 8)
    prompt = f"""Date: {datetime.now().strftime('%Y-%m-%d')}

SECTOR ETF DATA:
{df.to_string(index=False) if not df.empty else "unavailable"}

HEADLINES: {json.dumps(news, indent=2)}

Find TOP 2 sectors in EARLY accumulation (not yet crowded).
For each: ETF ticker, theme, why early, macro driver, score 1-10. Plain text."""
    return await ask(session, "You are a sector rotation specialist. Find sectors before ETF inflows show on Bloomberg.", prompt, key)

async def a_stocks(session, key):
    df   = get_stock_table(STOCKS)
    news = get_news("insider buying FDA approval DoD contract earnings catalyst 2026", 8)
    prompt = f"""Date: {datetime.now().strftime('%Y-%m-%d')}

STOCK SIGNALS:
{df.to_string(index=False) if not df.empty else "unavailable"}

CATALYST NEWS: {json.dumps(news, indent=2)}

Find TOP 3 stocks with 3+ STACKING signals:
  • Insider buying (Form 4)
  • Oversold RSI <35 or deep vs 52W high
  • High short float (squeeze potential)
  • Upcoming catalyst (earnings, FDA, contract)
  • Sector tailwind

For each: ticker, signals list, catalyst+date, entry rationale, asymmetry score 1-10, horizon. Plain text."""
    return await ask(session, "You are a stock catalyst specialist. Find asymmetric setups where multiple signals stack simultaneously.", prompt, key)

async def a_contra(session, key):
    df   = get_stock_table(STOCKS[:6])
    news = get_news("overvalued bubble crowded trade short seller warning 2026", 8)
    prompt = f"""Date: {datetime.now().strftime('%Y-%m-%d')}

STOCK DATA:
{df.to_string(index=False) if not df.empty else "unavailable"}

BEAR NEWS: {json.dumps(news, indent=2)}

Stress-test each stock:
1. What's already priced in?
2. Biggest bear case
3. Macro scenario that kills this trade
4. Crowding score 1-10
Verdict: BUY / WATCH / AVOID. Flag AVOID clearly. Plain text."""
    return await ask(session, "You are a contrarian short-seller. Stress-test every bull thesis. Only truly asymmetric bets survive.", prompt, key)

async def a_thesis(session, key, m, s, st_, c):
    prompt = f"""Date: {datetime.now().strftime('%Y-%m-%d')}

MACRO SCOUT:
{m}

SECTOR ANALYST:
{s}

STOCK SNIPER:
{st_}

CONTRARIAN AUDIT:
{c}

Synthesize into a final ASYMMETRIC BET REPORT.
Rules:
- Only include bets scoring 7+ average across Asymmetry / Catalyst / Macro Alignment
- Skip any ticker flagged AVOID by contrarian

FORMAT each bet exactly like this:

🎯 ASYMMETRIC BET: [TICKER]
📊 THEME: [one line macro/sector driver]
🔥 CATALYSTS:
   • [signal 1]
   • [signal 2]
   • [signal 3]
⚠️ KEY RISK: [single biggest risk]
📈 SETUP: Entry ~$X | Target $X-$X | Stop $X | Horizon: X months
🏆 SCORE: Asymmetry X/10 | Catalyst X/10 | Macro X/10

End the report with:
📋 PORTFOLIO NOTE: [correlation/concentration note]
🌍 MACRO REGIME: [one sentence current backdrop]"""
    return await ask(session, "You are a hedge fund CIO. Distill 4 analyst reports into razor-sharp actionable theses. No fluff. Only alpha scoring 7+.", prompt, key)

async def run_scan(key):
    async with aiohttp.ClientSession() as session:
        m, s, st_, c = await asyncio.gather(
            a_macro(session, key),
            a_sector(session, key),
            a_stocks(session, key),
            a_contra(session, key),
        )
        final = await a_thesis(session, key, m, s, st_, c)
    return m, s, st_, c, final

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
#  TABS
# ═══════════════════════════════════════════════════════════════════════════════

tab1, tab2, tab3 = st.tabs(["📊 Live Dashboard", "🤖 Alpha Scan", "ℹ️ How It Works"])

# ════════════════════════════════════════
# TAB 1 — DASHBOARD
# ════════════════════════════════════════
with tab1:

    st.markdown('<p class="section-hdr">🌍 Macro Pulse</p>', unsafe_allow_html=True)
    cols = st.columns(6)
    for col, (ticker, label) in zip(cols, MACRO_TICKERS.items()):
        price, chg = get_price(ticker)
        with col:
            if price is not None and chg is not None:
                arrow = "mup" if chg >= 0 else "mdown"
                sign  = "+" if chg >= 0 else ""
                st.markdown(f"""<div class="mbox">
<p class="mlabel">{label}</p>
<p class="mval">{price:,.2f}</p>
<p class="{arrow}">{sign}{chg:.2f}%</p>
</div>""", unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="mbox"><p class="mlabel">{label}</p><p class="mval">—</p><p class="mna">loading...</p></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns([1, 2])

    with left:
        st.markdown('<p class="section-hdr">🔄 Sector Momentum</p>', unsafe_allow_html=True)
        with st.spinner(""):
            df_sec = get_sector_table(SECTORS)
        if not df_sec.empty:
            def csec(v):
                if isinstance(v, float):
                    return "color:#10b981;font-weight:600" if v>0 else "color:#ef4444;font-weight:600"
                return "color:#e5e7eb"
            st.dataframe(df_sec.style.applymap(csec, subset=["1M%","1W%"]),
                         use_container_width=True, hide_index=True, height=360)
        else:
            st.warning("Sector data unavailable")

    with right:
        st.markdown('<p class="section-hdr">🎯 Watchlist Signals</p>', unsafe_allow_html=True)
        with st.spinner(""):
            df_st = get_stock_table(STOCKS)
        if not df_st.empty:
            def crsi(v):
                if isinstance(v, float):
                    if v < 35: return "color:#10b981;font-weight:700"
                    if v > 70: return "color:#ef4444;font-weight:700"
                return "color:#e5e7eb"
            def cm1(v):
                if isinstance(v, float):
                    return "color:#10b981" if v>0 else "color:#ef4444"
                return "color:#e5e7eb"
            st.dataframe(
                df_st.style.applymap(crsi, subset=["RSI"]).applymap(cm1, subset=["1M%"]),
                use_container_width=True, hide_index=True, height=360
            )
        else:
            st.warning("Stock data unavailable")

    st.markdown('<p class="section-hdr">📰 Market Headlines</p>', unsafe_allow_html=True)
    with st.spinner(""):
        news = get_news("asymmetric opportunity stock catalyst market 2026", 8)
    if news:
        for h in news:
            st.markdown(f"• **{h['title']}**  <span style='color:#6b7280;font-size:0.8rem'>— {h['source']}</span>", unsafe_allow_html=True)
    else:
        st.info("Headlines unavailable")

# ════════════════════════════════════════
# TAB 2 — ALPHA SCAN
# ════════════════════════════════════════
with tab2:
    st.markdown('<p class="section-hdr">🤖 5-Agent Parallel Alpha Scan</p>', unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.markdown("**🌍 Macro**\nGeopolitics\nRates · FX")
    c2.markdown("**🔄 Sector**\nRotation\nETF Flow")
    c3.markdown("**🎯 Stocks**\nCatalysts\nInsiders")
    c4.markdown("**⚠️ Contra**\nBear cases\nStress test")
    c5.markdown("**📝 CIO**\nSynthesis\nFinal alert")
    st.markdown("*Agents 1-4 run simultaneously → Agent 5 synthesizes → Telegram alert*")
    st.divider()

    if not run_btn:
        st.info("👈 Enter your **DeepSeek API key** in the sidebar and click **Run Alpha Scan**")
        with st.expander("📋 Example output"):
            st.code("""🎯 ASYMMETRIC BET: RKLB
📊 THEME: Space defense + smallsat boom + DoD tailwind
🔥 CATALYSTS:
   • RSI 31 — deeply oversold after sector selloff
   • CEO bought $2.1M shares (Form 4, Feb 2026)
   • DoD launch contract award expected Q2 2026
   • XAR (aerospace ETF) breaking 52W high
⚠️ KEY RISK: Neutron rocket timeline slippage
📈 SETUP: Entry ~$8.50 | Target $14-18 | Stop $6.80 | Horizon: 9 months
🏆 SCORE: Asymmetry 8/10 | Catalyst 9/10 | Macro 8/10

📋 PORTFOLIO NOTE: RKLB + IONQ uncorrelated; both early-stage tech with binary catalysts
🌍 MACRO REGIME: Risk-on with rate cut expectations supporting growth/tech rotation""", language=None)

    if run_btn:
        if not deepseek_key:
            st.error("⚠️ DeepSeek API key required — add it in the sidebar.")
        else:
            prog = st.progress(0, text="Starting agents...")
            col_s = st.columns(4)
            stat  = [col.status(lbl, expanded=False) for col, lbl in
                     zip(col_s, ["🌍 Macro Scout","🔄 Sector Analyst","🎯 Stock Sniper","⚠️ Contrarian"])]
            synth = st.status("📝 Thesis Writer (synthesizing)", expanded=False)

            for s in stat:
                with s: st.write("Running...")
            prog.progress(15, text="Agents running in parallel...")

            try:
                m_r, s_r, st_r, c_r, final = asyncio.get_event_loop().run_until_complete(
                    run_scan(deepseek_key)
                )
                prog.progress(85, text="Writing final thesis...")

                for s, label, result in zip(stat,
                    ["🌍 Macro Scout","🔄 Sector Analyst","🎯 Stock Sniper","⚠️ Contrarian"],
                    [m_r, s_r, st_r, c_r]):
                    with s:
                        st.success("✅ Done")
                        st.write(result)

                with synth:
                    st.success("✅ Done")
                    st.write(final)

                prog.progress(100, text="✅ Scan complete!")

                st.divider()
                st.markdown("## 🏆 Final Alpha Report")
                st.markdown(f'<div class="bet-card">{final}</div>', unsafe_allow_html=True)

                col_dl, col_tg = st.columns(2)
                with col_dl:
                    st.download_button(
                        "⬇️ Download Report",
                        data=f"ALPHA MACHINE REPORT\n{datetime.now()}\n\n{final}",
                        file_name=f"alpha_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                        mime="text/plain", use_container_width=True
                    )
                with col_tg:
                    if telegram_token and telegram_chat:
                        send_telegram(f"🤖 ALPHA MACHINE\n{datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n{'─'*30}\n\n{final}",
                                      telegram_token, telegram_chat)
                        st.success("📱 Sent to Telegram!")
                    else:
                        st.info("Add Telegram creds in sidebar for auto-alerts")

            except Exception as e:
                prog.progress(0)
                st.error(f"❌ Scan error: {e}")
                st.info("Check your DeepSeek API key is valid and try again.")

# ════════════════════════════════════════
# TAB 3 — HOW IT WORKS
# ════════════════════════════════════════
with tab3:
    st.markdown("## 🏗️ Architecture")
    st.markdown("""
| Agent | Role | Data |
|---|---|---|
| 🌍 Macro Scout | Geopolitics, rates, FX, commodities | Yahoo Finance + Google News RSS |
| 🔄 Sector Analyst | ETF rotation, institutional flow | Sector ETF momentum + headlines |
| 🎯 Stock Sniper | Catalysts, insiders, stacked signals | yfinance + insider data + news |
| ⚠️ Contrarian | Stress-tests every bull thesis | Price data + bear case news |
| 📝 Thesis Writer | CIO synthesis — scores and formats | All 4 agent outputs |

**Asymmetric bet criteria (must pass all):**
- 3+ signals stacking simultaneously
- Catalyst not yet priced in by market
- Contrarian audit: not flagged AVOID
- Score 7+/10 across Asymmetry · Catalyst · Macro Alignment

**Cost:** ~$0.005/scan with DeepSeek-R1 → 3 scans/day ≈ **$0.45/month**
    """)

    st.markdown("## 🔑 API Keys Setup")
    st.markdown("""
**DeepSeek** → [platform.deepseek.com](https://platform.deepseek.com) → API Keys → Create

**Telegram Bot:**
1. Message [@BotFather](https://t.me/BotFather) → `/newbot`
2. Add bot to your channel as admin
3. Get Chat ID: `https://api.telegram.org/bot<TOKEN>/getUpdates`
    """)
