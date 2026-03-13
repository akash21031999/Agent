"""
╔══════════════════════════════════════════════════════════════╗
║           ALPHA MACHINE — Multi-Agent Parallel System        ║
║        Pure asyncio + DeepSeek API (No CrewAI needed)        ║
║         Works on Python 3.10+ including 3.14                 ║
╚══════════════════════════════════════════════════════════════╝

5 Agents run in TRUE PARALLEL via asyncio.gather():
  Agent 1 — Macro Scout     : Geopolitics, rates, FX, commodity tailwinds
  Agent 2 — Sector Analyst  : Sector rotation, ETF momentum, institutional flow
  Agent 3 — Stock Sniper    : Catalysts, insider signals, stacking setups
  Agent 4 — Contrarian      : Devil's advocate — what kills these trades
  Agent 5 — Thesis Writer   : Synthesizes all 4 into final scored alert

Output → Terminal + Telegram alert
"""

import os
import json
import asyncio
import aiohttp
import schedule
import time
import yfinance as yf
import requests
import feedparser
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ─── CONFIG ────────────────────────────────────────────────────────────────────
DEEPSEEK_API_KEY   = os.getenv("DEEPSEEK_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID", "")

DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL        = "deepseek-reasoner"   # DeepSeek-R1 chain-of-thought

# ── Watchlists ─────────────────────────────────────────────────────────────────
WATCHLIST_STOCKS  = ["NVDA","TSM","ASML","PLTR","IONQ","RKLB","HIMS","CELH","NVO","MELI"]
WATCHLIST_SECTORS = ["XLK","XLE","XLF","XLV","XBI","ARKK","GDX","COPX","ITB","XAR"]
WATCHLIST_MACRO   = ["^TNX","GC=F","CL=F","DX-Y.NYB","BTC-USD","^VIX"]


# ─── DATA TOOLS ────────────────────────────────────────────────────────────────

def fetch_stock_data(tickers: list) -> dict:
    results = {}
    for sym in tickers:
        try:
            tk   = yf.Ticker(sym)
            info = tk.info
            hist = tk.history(period="3mo")
            if hist.empty:
                continue
            close = hist["Close"]
            delta = close.diff()
            gain  = delta.clip(lower=0).rolling(14).mean()
            loss  = (-delta.clip(upper=0)).rolling(14).mean()
            rsi   = float((100 - 100 / (1 + gain / (loss + 1e-9))).iloc[-1])

            results[sym] = {
                "price":       round(float(close.iloc[-1]), 2),
                "change_1m_%": round((close.iloc[-1] / close.iloc[-22] - 1) * 100, 2) if len(close) >= 22 else 0,
                "change_3m_%": round((close.iloc[-1] / close.iloc[0] - 1) * 100, 2),
                "rsi_14":      round(rsi, 1),
                "52w_high":    info.get("fiftyTwoWeekHigh", "N/A"),
                "52w_low":     info.get("fiftyTwoWeekLow",  "N/A"),
                "market_cap":  info.get("marketCap", "N/A"),
                "short_float": info.get("shortPercentOfFloat", "N/A"),
                "pe_ratio":    info.get("trailingPE", "N/A"),
                "sector":      info.get("sector", "N/A"),
            }
        except Exception as e:
            results[sym] = {"error": str(e)}
    return results


def fetch_news(query: str, n: int = 12) -> list:
    encoded = requests.utils.quote(query)
    url     = f"https://news.google.com/rss/search?q={encoded}&hl=en-US&gl=US&ceid=US:en"
    feed    = feedparser.parse(url)
    return [
        {"title": e.get("title",""), "source": e.get("source",{}).get("title","Unknown"), "published": e.get("published","")}
        for e in feed.entries[:n]
    ]


def fetch_insider(ticker: str) -> list:
    try:
        df = yf.Ticker(ticker).insider_transactions
        if df is None or df.empty:
            return []
        records = []
        for _, row in df.head(8).iterrows():
            records.append({
                "insider": str(row.get("Insider","")),
                "relation": str(row.get("Relation","")),
                "transaction": str(row.get("Transaction","")),
                "shares": str(row.get("Shares","")),
                "date": str(row.get("Start Date","")),
            })
        return records
    except:
        return []


# ─── DEEPSEEK ASYNC CALL ───────────────────────────────────────────────────────

async def call_deepseek(session: aiohttp.ClientSession, system: str, user: str) -> str:
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "max_tokens": 3000,
        "temperature": 0.3,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
    }
    try:
        async with session.post(
            DEEPSEEK_URL, headers=headers, json=payload,
            timeout=aiohttp.ClientTimeout(total=180)
        ) as resp:
            data = await resp.json()
            choices = data.get("choices", [])
            if not choices:
                return f"[API Error: {data}]"
            msg = choices[0]["message"]
            return msg.get("content") or msg.get("reasoning_content", "[No response]")
    except Exception as e:
        return f"[Request failed: {e}]"


# ─── AGENTS ────────────────────────────────────────────────────────────────────

async def agent_macro_scout(session):
    print("  🌍 Macro Scout running...")
    macro_data  = fetch_stock_data(WATCHLIST_MACRO)
    geo_news    = fetch_news("geopolitical risk trade war tariffs 2026")
    rates_news  = fetch_news("Federal Reserve interest rate pivot inflation 2026")
    commodity   = fetch_news("commodity supercycle oil gold copper uranium 2026")

    user = f"""
Today: {datetime.now().strftime('%Y-%m-%d %H:%M')}

MACRO INDICATORS:
{json.dumps(macro_data, indent=2)}

GEOPOLITICAL HEADLINES: {json.dumps(geo_news, indent=2)}
RATES & FED HEADLINES: {json.dumps(rates_news, indent=2)}
COMMODITY HEADLINES: {json.dumps(commodity, indent=2)}

Identify the TOP 3 macro tailwinds creating asymmetric opportunities RIGHT NOW.
For each: theme, beneficiary asset classes, timeline, crowding level, confidence score 1-10, key kill risk.
Return structured JSON only.
"""
    system = (
        "You are a global macro strategist. Think Ray Dalio — debt cycles, capital flows, "
        "geopolitics. You find invisible forces moving markets BEFORE the crowd does."
    )
    return await call_deepseek(session, system, user)


async def agent_sector_analyst(session):
    print("  🔄 Sector Analyst running...")
    sector_data  = fetch_stock_data(WATCHLIST_SECTORS)
    flow_news    = fetch_news("sector rotation institutional buying ETF inflows 2026")
    earning_news = fetch_news("sector earnings beat guidance raise analyst upgrade 2026")

    user = f"""
Today: {datetime.now().strftime('%Y-%m-%d %H:%M')}

SECTOR ETF DATA:
{json.dumps(sector_data, indent=2)}

FLOW HEADLINES: {json.dumps(flow_news, indent=2)}
EARNINGS HEADLINES: {json.dumps(earning_news, indent=2)}

Identify TOP 2 sectors in EARLY institutional accumulation.
Look for: RSI < 45 recovering, breakout above 52W high, positive news flow, macro alignment.
For each: ETF ticker, theme, why early/not crowded, macro alignment, score 1-10.
Return structured JSON only.
"""
    system = (
        "You are a sector rotation specialist. You find sectors BEFORE the ETF inflows "
        "show up on Bloomberg. Sectors move with macro; stocks move with sectors."
    )
    return await call_deepseek(session, system, user)


async def agent_stock_sniper(session):
    print("  🎯 Stock Sniper running...")
    stock_data = fetch_stock_data(WATCHLIST_STOCKS)

    insider_data = {}
    high_short = [
        s for s, d in stock_data.items()
        if isinstance(d.get("short_float"), float) and d["short_float"] > 0.10
    ]
    for sym in high_short[:4]:
        insider_data[sym] = fetch_insider(sym)

    catalyst_news = fetch_news("insider buying FDA approval DoD contract earnings catalyst 2026")

    user = f"""
Today: {datetime.now().strftime('%Y-%m-%d %H:%M')}

STOCK METRICS:
{json.dumps(stock_data, indent=2)}

INSIDER TRANSACTIONS (high short interest names):
{json.dumps(insider_data, indent=2)}

CATALYST HEADLINES: {json.dumps(catalyst_news, indent=2)}

Find TOP 3 stocks where 3+ signals STACK:
  - Insider buying (Form 4)
  - Oversold RSI <35 or deep vs 52W high
  - High short float (squeeze potential)
  - Upcoming catalyst (earnings, FDA, contract, product launch)
  - Sector tailwind

For each: ticker, stacked signals list, catalyst event+date, entry rationale,
asymmetry score 1-10, time horizon.
Return structured JSON only.
"""
    system = (
        "You are a fundamental + technical hybrid analyst. You find stocks at the intersection "
        "of macro theme, sector rotation, and company-specific ignition event. "
        "You obsess over insider filings and asymmetric risk/reward setups."
    )
    return await call_deepseek(session, system, user)


async def agent_contrarian(session):
    print("  ⚠️  Contrarian Auditor running...")
    stock_data = fetch_stock_data(WATCHLIST_STOCKS[:6])
    bear_news  = fetch_news("overvalued crowded trade short seller warning 2026")
    risk_news  = fetch_news("recession risk earnings miss guidance cut margin compression 2026")

    user = f"""
Today: {datetime.now().strftime('%Y-%m-%d %H:%M')}

STOCK DATA:
{json.dumps(stock_data, indent=2)}

BEAR HEADLINES: {json.dumps(bear_news, indent=2)}
RISK HEADLINES: {json.dumps(risk_news, indent=2)}

For each stock, stress-test the bull thesis:
1. What does the market already know? (priced in?)
2. Valuation red flags vs growth rate
3. Biggest bear case
4. Macro scenario that kills this trade
5. Narrative trap or true asymmetry?

Flag AVOID trades clearly. Score crowding 1-10.
Return structured JSON: ticker, priced_in_risk, bear_case, kill_scenario, crowding_score, verdict (BUY/AVOID/WATCH).
"""
    system = (
        "You are a short-seller and devil's advocate. You've seen dozens of 'asymmetric' bets "
        "blow up because the thesis was right but timing or valuation was wrong. "
        "Stress-test every idea until only truly asymmetric bets survive."
    )
    return await call_deepseek(session, system, user)


async def agent_thesis_writer(session, macro_out, sector_out, stock_out, contrarian_out):
    print("  📝 Thesis Writer synthesizing all agents...")

    user = f"""
Today: {datetime.now().strftime('%Y-%m-%d %H:%M')}

MACRO SCOUT OUTPUT:
{macro_out}

SECTOR ANALYST OUTPUT:
{sector_out}

STOCK SNIPER OUTPUT:
{stock_out}

CONTRARIAN AUDIT OUTPUT:
{contrarian_out}

Synthesize into a final ASYMMETRIC BET ALERT REPORT.
Rules:
- Only surface bets scoring 7+ average (Asymmetry + Catalyst Clarity + Macro Alignment)
- Skip any stock with AVOID verdict from contrarian
- Format for Telegram (emojis, punchy, actionable)

FORMAT per bet:
🎯 ASYMMETRIC BET: [Ticker / Name]
📊 THEME: [1-line macro/sector driver]
🔥 CATALYSTS STACKING:
   • [signal 1]
   • [signal 2]
   • [signal 3]
⚠️ KEY RISK: [single biggest risk]
📈 SETUP: Entry ~$X | Target $X–$X | Stop $X | Horizon: X months
🏆 SCORE: Asymmetry X/10 | Catalyst X/10 | Macro X/10

End with:
📋 PORTFOLIO NOTE: [correlation between bets, hedged or concentrated?]
🌍 MACRO REGIME: [1-sentence current backdrop]
"""
    system = (
        "You are the CIO of a macro hedge fund. You synthesize raw analyst research into "
        "razor-sharp investment theses. Think: Entry, Catalyst, Target, Stop, Horizon. "
        "No fluff. Only bets scoring 7+. Only alpha."
    )
    return await call_deepseek(session, system, user)


# ─── TELEGRAM ─────────────────────────────────────────────────────────────────

def send_telegram(message: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("\n⚠️  Telegram not configured — add TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID to .env\n")
        return
    for chunk in [message[i:i+4000] for i in range(0, len(message), 4000)]:
        try:
            r = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                json={"chat_id": TELEGRAM_CHAT_ID, "text": chunk, "parse_mode": "Markdown"},
                timeout=10
            )
            print("✅ Telegram sent" if r.status_code == 200 else f"❌ Telegram: {r.text}")
        except Exception as e:
            print(f"❌ Telegram error: {e}")


# ─── ORCHESTRATOR ─────────────────────────────────────────────────────────────

async def run_scan_async() -> str:
    if not DEEPSEEK_API_KEY:
        raise ValueError("❌ DEEPSEEK_API_KEY not set in .env")

    async with aiohttp.ClientSession() as session:
        print("🚀 Launching 4 parallel agents simultaneously...\n")

        # Agents 1-4 run at the SAME TIME
        macro_out, sector_out, stock_out, contrarian_out = await asyncio.gather(
            agent_macro_scout(session),
            agent_sector_analyst(session),
            agent_stock_sniper(session),
            agent_contrarian(session),
        )

        print("\n✅ All 4 agents complete. Thesis Writer synthesizing...\n")

        # Agent 5 synthesizes all 4
        final = await agent_thesis_writer(
            session, macro_out, sector_out, stock_out, contrarian_out
        )

    return final


def run_alpha_scan() -> str:
    print(f"\n{'='*65}")
    print(f"  🚀 ALPHA MACHINE — {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*65}\n")

    result = asyncio.run(run_scan_async())

    print("\n" + "="*65)
    print("  📊 FINAL ALPHA REPORT")
    print("="*65)
    print(result)
    print("="*65 + "\n")

    header = f"🤖 *ALPHA MACHINE*\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n{'─'*40}\n\n"
    send_telegram(header + result)
    return result


def run_scheduled():
    print("⏰ Scheduler active — scans at 06:00 | 12:00 | 16:00 daily\n")
    schedule.every().day.at("06:00").do(run_alpha_scan)
    schedule.every().day.at("12:00").do(run_alpha_scan)
    schedule.every().day.at("16:00").do(run_alpha_scan)
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--schedule":
        run_scheduled()
    else:
        run_alpha_scan()
