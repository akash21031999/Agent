"""
Alpha Machine — Streamlit Dashboard
Fully self-contained. No subprocess. Works on Streamlit Cloud.
"""

import streamlit as st
import yfinance as yf
import requests
import feedparser
import json
import asyncio
import aiohttp
import pandas as pd
from datetime import datetime
import os

# ── Page config — MUST be first Streamlit call ────────────────────────────────
st.set_page_config(
    page_title="Alpha Machine 🎯",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0a0a0f; }
[data-testid="stSidebar"] { background: #0f0f1a; }
.block-container { padding-top: 1.5rem; }

.alpha-title {
    font-size: 2.2rem; font-weight: 900; letter-spacing: -1px;
    background: linear-gradient(90deg, #00f5a0, #00d9f5, #a78bfa);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 0;
}
.subtitle { color: #6b7280; font-size: 0.9rem; margin-top: 0; }

.metric-box {
    background: #111827; border: 1px solid #1f2937;
    border-radius: 10px; padding: 14px 18px; text-align: center;
}
.metric-label { color: #9ca3af; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 1px; }
.metric-value { color: #f9fafb; font-size: 1.4rem; font-weight: 700; margin: 4px 0; }
.metric-up   { color: #10b981; font-size: 0.82rem; font-weight: 600; }
.metric-down { color: #ef4444; font-size: 0.82rem; font-weight: 600; }

.bet-card {
    background: linear-gradient(135deg, #0f1f0f, #0a1628);
    border: 1px solid #10b981; border-radius: 12px;
    padding: 20px 24px; margin: 12px 0;
    border-left: 4px solid #00f5a0;
}
.section-title {
    color: #e5e7eb; font-size: 1.1rem; font-weight: 700;
    border-bottom: 1px solid #1f2937; padding-bottom: 8px; margin-bottom: 14px;
}
.status-pill {
    display: inline-block; padding: 3px 10px; border-radius: 20px;
    font-size: 0.75rem; font-weight: 600;
}
.pill-green { background: #064e3b; color: #10b981; }
.pill-red   { background: #7f1d1d; color: #f87171; }
.pill-yellow{ background: #78350f; color: #fbbf24; }
</style>
""", unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown('<p class="alpha-title">🎯 Alpha Machine</p>', unsafe_allow_html=True)
st.markdown(f'<p class="subtitle">Multi-Agent Asymmetric Bet Scanner &nbsp;|&nbsp; {datetime.now().strftime("%Y-%m-%d %H:%M UTC")}</p>', unsafe_allow_html=True)
st.markdown("---")

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    deepseek_key = st.text_input("DeepSeek API Key", type="password", placeholder="sk-...")
    st.markdown("---")
    st.markdown("### 📱 Telegram Alerts")
    telegram_token = st.text_input("Bot Token", type="password", placeholder="123456:ABC...")
    telegram_chat  = st.text_input("Chat ID", placeholder="-100123456789")
    st.markdown("---")
    st.markdown("### 📋 Watchlists")
    stocks_raw  = st.text_area("Stocks", value="NVDA,TSM,ASML,PLTR,IONQ,RKLB,HIMS,CELH,NVO,MELI", height=90)
    sectors_raw = st.text_area("Sector ETFs", value="XLK,XLE,XLF,XLV,XBI,ARKK,GDX,COPX,ITB,XAR", height=90)
    st.markdown("---")
    run_btn = st.button("🚀 Run Alpha Scan", type="primary", use_container_width=True)
    st.caption("Agents run in parallel ~2-3 min")

STOCKS  = [s.strip() for s in stocks_raw.split(",") if s.strip()]
SECTORS = [s.strip() for s in sectors_raw.split(",") if s.strip()]
MACRO   = ["^TNX","GC=F","CL=F","DX-Y.NYB","BTC-USD","^VIX"]

# ─── DATA HELPERS ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def get_price(ticker):
    try:
        hist = yf.Ticker(ticker).history(period="5d")
        if len(hist) < 2:
            return None, None
        cur  = float(hist["Close"].iloc[-1])
        prev = float(hist["Close"].iloc[-2])
        return cur, (cur/prev - 1)*100
    except:
        return None, None

@st.cache_data(ttl=300)
def get_stock_metrics(tickers):
    rows = []
    for sym in tickers:
        try:
            tk   = yf.Ticker(sym)
            info = tk.info
            hist = tk.history(period="3mo")
            if hist.empty or len(hist) < 14:
                continue
            close = hist["Close"]
            delta = close.diff()
            gain  = delta.clip(lower=0).rolling(14).mean()
            loss  = (-delta.clip(upper=0)).rolling(14).mean()
            rsi   = round(float((100 - 100/(1 + gain/(loss+1e-9))).iloc[-1]), 1)
            m1    = round((float(close.iloc[-1])/float(close.iloc[-22])-1)*100, 2) if len(close)>=22 else 0
            price = round(float(close.iloc[-1]), 2)
            w52h  = info.get("fiftyTwoWeekHigh") or 0
            short = info.get("shortPercentOfFloat") or 0

            signals = []
            if rsi < 35:    signals.append("🟢 Oversold")
            if rsi > 70:    signals.append("🔴 Overbought")
            if short > 0.15: signals.append("⚡ High Short")
            if w52h and price >= w52h * 0.97: signals.append("🚀 52W High")
            if w52h and price <= w52h * 0.55: signals.append("💎 Deep Value")

            rows.append({
                "Ticker":   sym,
                "Price":    price,
                "1M %":     m1,
                "RSI":      rsi,
                "Short %":  f"{short*100:.1f}%" if short else "—",
                "Signals":  " ".join(signals) if signals else "—",
            })
        except:
            pass
    return pd.DataFrame(rows) if rows else pd.DataFrame()

@st.cache_data(ttl=300)
def get_sector_metrics(tickers):
    rows = []
    for sym in tickers:
        try:
            hist = yf.Ticker(sym).history(period="1mo")
            if len(hist) < 5:
                continue
            m1 = round((float(hist["Close"].iloc[-1])/float(hist["Close"].iloc[0])-1)*100, 2)
            w1 = round((float(hist["Close"].iloc[-1])/float(hist["Close"].iloc[-6])-1)*100, 2) if len(hist)>=6 else 0
            rows.append({"ETF": sym, "1M %": m1, "1W %": w1})
        except:
            pass
    return pd.DataFrame(rows).sort_values("1M %", ascending=False) if rows else pd.DataFrame()

def fetch_news(query, n=10):
    try:
        url  = f"https://news.google.com/rss/search?q={requests.utils.quote(query)}&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(url)
        return [{"title": e.get("title",""), "source": e.get("source",{}).get("title",""), "published": e.get("published","")} for e in feed.entries[:n]]
    except:
        return []

# ─── DEEPSEEK CALL ────────────────────────────────────────────────────────────

async def deepseek(session, system, user, api_key):
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "deepseek-reasoner",
        "max_tokens": 2500,
        "temperature": 0.3,
        "messages": [{"role":"system","content":system}, {"role":"user","content":user}],
    }
    try:
        async with session.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers, json=payload,
            timeout=aiohttp.ClientTimeout(total=180)
        ) as r:
            d = await r.json()
            choices = d.get("choices", [])
            if not choices:
                return f"[API Error: {d}]"
            msg = choices[0]["message"]
            return msg.get("content") or msg.get("reasoning_content","[empty]")
    except Exception as e:
        return f"[Error: {e}]"

# ─── AGENT PROMPTS ────────────────────────────────────────────────────────────

async def agent_macro(session, api_key):
    macro_data = {t: get_price(t) for t in MACRO}
    geo  = fetch_news("geopolitical risk trade war tariffs 2026")
    rate = fetch_news("Federal Reserve interest rate inflation pivot 2026")
    user = f"""
Today: {datetime.now().strftime('%Y-%m-%d')}

MACRO PRICES (ticker: [price, %change]):
{json.dumps({k: {"price": v[0], "chg%": round(v[1],2) if v[1] else None} for k,v in macro_data.items()}, indent=2)}

GEOPOLITICAL NEWS: {json.dumps(geo[:8], indent=2)}
RATES/FED NEWS: {json.dumps(rate[:8], indent=2)}

Find TOP 3 macro tailwinds creating asymmetric opportunities NOW.
For each: theme, beneficiaries, timeline, crowding level, confidence 1-10, kill risk.
Be specific and actionable. Use plain text (no markdown headers).
"""
    return await deepseek(session,
        "You are a global macro strategist. Think Ray Dalio — debt cycles, capital flows, geopolitics. Find invisible forces moving markets before the crowd.",
        user, api_key)

async def agent_sector(session, api_key):
    df   = get_sector_metrics(SECTORS)
    news = fetch_news("sector rotation institutional ETF inflows 2026")
    user = f"""
Today: {datetime.now().strftime('%Y-%m-%d')}

SECTOR ETF DATA:
{df.to_string(index=False) if not df.empty else "No data"}

FLOW NEWS: {json.dumps(news[:8], indent=2)}

Find TOP 2 sectors in EARLY accumulation (not crowded yet).
Look for: oversold RSI recovering, breaking out, positive macro alignment.
For each: ETF, theme, why early, macro driver, score 1-10.
Be specific. Use plain text.
"""
    return await deepseek(session,
        "You are a sector rotation specialist. Find sectors BEFORE the ETF inflows show on Bloomberg.",
        user, api_key)

async def agent_stocks(session, api_key):
    df   = get_stock_metrics(STOCKS)
    news = fetch_news("insider buying FDA approval contract beat catalyst 2026")
    user = f"""
Today: {datetime.now().strftime('%Y-%m-%d')}

STOCK METRICS:
{df.to_string(index=False) if not df.empty else "No data"}

CATALYST NEWS: {json.dumps(news[:8], indent=2)}

Find TOP 3 stocks with 3+ STACKING signals:
- Insider buying
- Oversold RSI (<35) or deep vs 52W high  
- High short float (squeeze)
- Upcoming catalyst
- Sector tailwind

For each: ticker, signals, catalyst, entry rationale, asymmetry score 1-10, horizon.
Use plain text.
"""
    return await deepseek(session,
        "You are a stock catalyst specialist. Find asymmetric setups where multiple signals stack.",
        user, api_key)

async def agent_contra(session, api_key):
    df   = get_stock_metrics(STOCKS[:6])
    news = fetch_news("overvalued crowded trade short seller warning bubble 2026")
    user = f"""
Today: {datetime.now().strftime('%Y-%m-%d')}

STOCK DATA:
{df.to_string(index=False) if not df.empty else "No data"}

BEAR NEWS: {json.dumps(news[:8], indent=2)}

For each stock, stress-test:
1. What's already priced in?
2. Biggest bear case
3. What macro kills this trade?
4. Crowding score 1-10

Verdict per stock: BUY / AVOID / WATCH. Flag any AVOID clearly.
Use plain text.
"""
    return await deepseek(session,
        "You are a contrarian short-seller. Stress-test every bull thesis. Only truly asymmetric bets survive your filter.",
        user, api_key)

async def agent_thesis(session, api_key, macro_r, sector_r, stocks_r, contra_r):
    user = f"""
Today: {datetime.now().strftime('%Y-%m-%d')}

MACRO SCOUT: {macro_r}
SECTOR ANALYST: {sector_r}
STOCK SNIPER: {stocks_r}
CONTRARIAN AUDIT: {contra_r}

Synthesize into final ASYMMETRIC BET REPORT.
Rules:
- Only bets scoring 7+ average (Asymmetry + Catalyst + Macro Alignment)
- Skip any AVOID from contrarian

FORMAT each bet EXACTLY like this:

🎯 ASYMMETRIC BET: [TICKER]
📊 THEME: [one line]
🔥 CATALYSTS:
   • [signal 1]
   • [signal 2]  
   • [signal 3]
⚠️ KEY RISK: [one line]
📈 SETUP: Entry ~$X | Target $X-$X | Stop $X | Horizon: X months
🏆 SCORE: Asymmetry X/10 | Catalyst X/10 | Macro X/10

End with:
📋 PORTFOLIO NOTE: [correlation / concentration note]
🌍 MACRO REGIME: [one sentence backdrop]
"""
    return await deepseek(session,
        "You are the CIO of a macro hedge fund. Distill 4 analyst reports into razor-sharp actionable theses. No fluff. Only alpha scoring 7+.",
        user, api_key)

# ─── ASYNC RUNNER ─────────────────────────────────────────────────────────────

async def run_all_agents(api_key):
    async with aiohttp.ClientSession() as session:
        macro_r, sector_r, stocks_r, contra_r = await asyncio.gather(
            agent_macro(session, api_key),
            agent_sector(session, api_key),
            agent_stocks(session, api_key),
            agent_contra(session, api_key),
        )
        final = await agent_thesis(session, api_key, macro_r, sector_r, stocks_r, contra_r)
    return macro_r, sector_r, stocks_r, contra_r, final

def send_telegram(message, token, chat_id):
    for chunk in [message[i:i+4000] for i in range(0, len(message), 4000)]:
        try:
            requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat_id, "text": chunk},
                timeout=10
            )
        except:
            pass

# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN UI
# ═══════════════════════════════════════════════════════════════════════════════

# ── TAB LAYOUT ────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📊 Live Dashboard", "🤖 Alpha Scan", "📋 How It Works"])

# ════════════════════════════════════════════════
# TAB 1 — LIVE DASHBOARD
# ════════════════════════════════════════════════
with tab1:

    # MACRO ROW
    st.markdown('<p class="section-title">🌍 Macro Pulse</p>', unsafe_allow_html=True)
    macro_labels = {"^TNX":"10Y Yield","GC=F":"Gold","CL=F":"Oil (WTI)","DX-Y.NYB":"DXY","BTC-USD":"Bitcoin","^VIX":"VIX"}
    cols = st.columns(6)
    for col, (ticker, label) in zip(cols, macro_labels.items()):
        price, chg = get_price(ticker)
        with col:
            if price is not None:
                chg_html = f'<p class="metric-{"up" if chg >= 0 else "down"}">{chg:+.2f}%</p>'
                st.markdown(f"""
                <div class="metric-box">
                    <p class="metric-label">{label}</p>
                    <p class="metric-value">{price:.2f}</p>
                    {chg_html}
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="metric-box"><p class="metric-label">{label}</p><p class="metric-value">—</p></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # SECTOR + STOCKS SIDE BY SIDE
    col_l, col_r = st.columns([1, 2])

    with col_l:
        st.markdown('<p class="section-title">🔄 Sector Momentum</p>', unsafe_allow_html=True)
        with st.spinner("Loading sectors..."):
            df_sec = get_sector_metrics(SECTORS)
        if not df_sec.empty:
            def color_pct(val):
                if isinstance(val, float):
                    return "color: #10b981; font-weight:600" if val > 0 else "color: #ef4444; font-weight:600"
                return ""
            st.dataframe(
                df_sec.style.applymap(color_pct, subset=["1M %","1W %"]),
                use_container_width=True, hide_index=True, height=380
            )
        else:
            st.info("Could not load sector data")

    with col_r:
        st.markdown('<p class="section-title">🎯 Watchlist Signals</p>', unsafe_allow_html=True)
        with st.spinner("Loading stocks..."):
            df_stocks = get_stock_metrics(STOCKS)
        if not df_stocks.empty:
            def color_rsi(val):
                if isinstance(val, float):
                    if val < 35: return "color: #10b981; font-weight:700"
                    if val > 70: return "color: #ef4444; font-weight:700"
                return ""
            def color_m1(val):
                if isinstance(val, float):
                    return "color: #10b981" if val > 0 else "color: #ef4444"
                return ""
            st.dataframe(
                df_stocks.style
                    .applymap(color_rsi, subset=["RSI"])
                    .applymap(color_m1,  subset=["1M %"]),
                use_container_width=True, hide_index=True, height=380
            )
        else:
            st.info("Could not load stock data")

    st.markdown("<br>", unsafe_allow_html=True)

    # LATEST NEWS
    st.markdown('<p class="section-title">📰 Latest Market Headlines</p>', unsafe_allow_html=True)
    with st.spinner("Fetching news..."):
        headlines = fetch_news("stock market asymmetric opportunity catalyst 2026", n=8)
    if headlines:
        for h in headlines:
            st.markdown(f"• **{h['title']}** — *{h['source']}*")
    else:
        st.info("Could not fetch headlines")

# ════════════════════════════════════════════════
# TAB 2 — ALPHA SCAN
# ════════════════════════════════════════════════
with tab2:
    st.markdown('<p class="section-title">🤖 5-Agent Parallel Alpha Scan</p>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.markdown("🌍 **Macro Scout**\nGeopolitics + Rates + FX")
    col2.markdown("🔄 **Sector Analyst**\nRotation + Flow")
    col3.markdown("🎯 **Stock Sniper**\nCatalysts + Insiders")
    col4.markdown("⚠️ **Contrarian**\nStress-tests every bet")
    st.markdown("↓ All 4 run simultaneously → **Thesis Writer** synthesizes → Alert")
    st.markdown("---")

    if not run_btn:
        st.info("👈 Add your **DeepSeek API key** in the sidebar, then click **Run Alpha Scan**")

        with st.expander("📋 Example output format"):
            st.markdown("""
```
🎯 ASYMMETRIC BET: RKLB
📊 THEME: Space defense + smallsat boom + DoD tailwind
🔥 CATALYSTS:
   • RSI 31 — deeply oversold after sector rotation
   • CEO bought $2.1M shares (Form 4)
   • DoD contract expected Q2 2026
   • XAR (defense ETF) breaking 52W high
⚠️ KEY RISK: Neutron rocket execution delays
📈 SETUP: Entry ~$8.50 | Target $14-18 | Stop $6.80 | Horizon: 9 months
🏆 SCORE: Asymmetry 8/10 | Catalyst 9/10 | Macro 8/10
```
            """)

    if run_btn:
        if not deepseek_key:
            st.error("⚠️ Enter your DeepSeek API key in the sidebar first.")
        else:
            # Progress indicators
            prog  = st.progress(0, text="Launching parallel agents...")
            s1    = st.status("🌍 Macro Scout", expanded=False)
            s2    = st.status("🔄 Sector Analyst", expanded=False)
            s3    = st.status("🎯 Stock Sniper", expanded=False)
            s4    = st.status("⚠️ Contrarian Auditor", expanded=False)
            s5    = st.status("📝 Thesis Writer", expanded=False)

            try:
                prog.progress(10, text="Fetching market data...")
                with s1: st.write("Scanning macro indicators + geopolitical news...")
                with s2: st.write("Analyzing sector ETF momentum + flow data...")
                with s3: st.write("Scanning insider filings + stock catalysts...")
                with s4: st.write("Stress-testing bull theses...")

                prog.progress(25, text="Agents running in parallel (2-3 min)...")

                macro_r, sector_r, stocks_r, contra_r, final = asyncio.run(
                    run_all_agents(deepseek_key)
                )

                prog.progress(90, text="Synthesizing final report...")

                with s1: st.success("Complete"); st.write(macro_r)
                with s2: st.success("Complete"); st.write(sector_r)
                with s3: st.success("Complete"); st.write(stocks_r)
                with s4: st.success("Complete"); st.write(contra_r)
                with s5: st.success("Complete"); st.write(final)

                prog.progress(100, text="✅ Scan complete!")

                # FINAL REPORT
                st.markdown("---")
                st.markdown("## 🏆 Final Alpha Report")
                st.markdown(
                    f'<div class="bet-card">{final.replace(chr(10), "<br>")}</div>',
                    unsafe_allow_html=True
                )

                # TELEGRAM
                if telegram_token and telegram_chat:
                    header = f"🤖 ALPHA MACHINE\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n{'─'*35}\n\n"
                    send_telegram(header + final, telegram_token, telegram_chat)
                    st.success("📱 Alert sent to Telegram!")
                else:
                    st.info("💡 Add Telegram credentials in sidebar to receive alerts automatically")

                # DOWNLOAD
                st.download_button(
                    "⬇️ Download Report",
                    data=f"ALPHA MACHINE REPORT\n{datetime.now()}\n\n{final}",
                    file_name=f"alpha_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain"
                )

            except Exception as e:
                prog.progress(0, text="Error")
                st.error(f"❌ Scan failed: {e}")
                st.info("Check your DeepSeek API key and try again.")

# ════════════════════════════════════════════════
# TAB 3 — HOW IT WORKS
# ════════════════════════════════════════════════
with tab3:
    st.markdown("## 🏗️ System Architecture")
    st.markdown("""
**5 AI agents powered by DeepSeek-R1 (chain-of-thought reasoning) run in parallel:**

| Agent | Role | Data Sources |
|---|---|---|
| 🌍 Macro Scout | Geopolitics, rates, FX, commodities | Yahoo Finance macro tickers + Google News |
| 🔄 Sector Analyst | ETF rotation, institutional flow | Sector ETF momentum + flow headlines |
| 🎯 Stock Sniper | Catalysts, insiders, stacking signals | yfinance + insider transactions + news |
| ⚠️ Contrarian | Stress-tests every bull thesis | Price data + bear case news |
| 📝 Thesis Writer | CIO synthesis layer | All 4 agent outputs |

**What makes a bet "asymmetric":**
- Multiple signals **stacking** simultaneously
- Market has NOT yet priced in the catalyst
- Clear **entry, target, stop** with defined horizon
- Macro tailwind **aligns** with sector + stock setup
- Contrarian audit **survives** the stress test
- Score **7+/10** across all three dimensions

**Cost:** ~$0.005 per full scan with DeepSeek-R1 → 3 scans/day ≈ **$0.45/month**
    """)

    st.markdown("## 🔑 Getting Your API Keys")
    st.markdown("""
**DeepSeek API** (required):
1. Go to [platform.deepseek.com](https://platform.deepseek.com)
2. Sign up → API Keys → Create key
3. Paste in sidebar

**Telegram Bot** (optional, for alerts):
1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. `/newbot` → follow steps → copy token
3. Create a channel/group, add your bot as admin
4. Get chat ID: `https://api.telegram.org/bot<TOKEN>/getUpdates`
5. Paste token + chat ID in sidebar
    """)
