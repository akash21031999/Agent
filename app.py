"""
╔══════════════════════════════════════════════════════════════╗
║           ALPHA MACHINE — Multi-Agent Parallel System        ║
║     CrewAI + DeepSeek + Telegram Asymmetric Bet Alerts       ║
╚══════════════════════════════════════════════════════════════╝

Agents run in PARALLEL:
  Agent 1 — Macro Scout        : Geopolitics, rates, commodities tailwinds
  Agent 2 — Sector Analyst     : Sector rotation, earnings, institutional flow
  Agent 3 — Stock Sniper       : Individual stock catalyst + insider signals
  Agent 4 — Contrarian Check   : Devil's advocate — why NOT to buy
  Agent 5 — Thesis Writer      : Synthesizes all into final asymmetric bet alert

Outputs → Terminal + Telegram alert (if TELEGRAM_BOT_TOKEN set)
"""

import os
import json
import asyncio
import schedule
import time
import yfinance as yf
import requests
import feedparser
from datetime import datetime, timedelta
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool

load_dotenv()

# ─── CONFIG ────────────────────────────────────────────────────────────────────
DEEPSEEK_API_KEY   = os.getenv("DEEPSEEK_API_KEY", "YOUR_DEEPSEEK_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID", "")

# Watchlist — edit freely
WATCHLIST_STOCKS   = ["NVDA","TSM","ASML","PLTR","IONQ","RKLB","HIMS","CELH","NVO","MELI"]
WATCHLIST_SECTORS  = ["XLK","XLE","XLF","XLV","XBI","ARKK","GDX","COPX","ITB","XAR"]
WATCHLIST_MACRO    = ["^TNX","GC=F","CL=F","DX-Y.NYB","BTC-USD","^VIX"]

# ─── LLM SETUP (DeepSeek via OpenAI-compatible endpoint) ───────────────────────
deepseek_llm = LLM(
    model="openai/deepseek-reasoner",      # DeepSeek-R1 — chain-of-thought reasoning
    base_url="https://api.deepseek.com/v1",
    api_key=DEEPSEEK_API_KEY,
    temperature=0.3,
    max_tokens=4000,
)

# ─── TOOLS ─────────────────────────────────────────────────────────────────────

@tool("fetch_stock_data")
def fetch_stock_data(tickers: str) -> str:
    """
    Fetch price, volume, 52w range, RSI proxy, short % for a comma-separated list of tickers.
    Returns a JSON string with key metrics for each ticker.
    """
    results = {}
    ticker_list = [t.strip() for t in tickers.split(",")]
    for sym in ticker_list:
        try:
            tk = yf.Ticker(sym)
            info = tk.info
            hist = tk.history(period="3mo")
            if hist.empty:
                continue
            close = hist["Close"]
            avg_vol = hist["Volume"].mean()

            # Simple RSI (14-day)
            delta = close.diff()
            gain = delta.clip(lower=0).rolling(14).mean()
            loss = (-delta.clip(upper=0)).rolling(14).mean()
            rs = gain / (loss + 1e-9)
            rsi = float((100 - 100 / (1 + rs)).iloc[-1])

            results[sym] = {
                "price":        round(float(close.iloc[-1]), 2),
                "change_1m_%":  round((close.iloc[-1]/close.iloc[-22]-1)*100, 2),
                "change_3m_%":  round((close.iloc[-1]/close.iloc[0]-1)*100, 2),
                "rsi_14":       round(rsi, 1),
                "avg_volume":   int(avg_vol),
                "52w_high":     info.get("fiftyTwoWeekHigh", "N/A"),
                "52w_low":      info.get("fiftyTwoWeekLow", "N/A"),
                "market_cap":   info.get("marketCap", "N/A"),
                "short_float%": info.get("shortPercentOfFloat", "N/A"),
                "pe_ratio":     info.get("trailingPE", "N/A"),
                "sector":       info.get("sector", "N/A"),
                "industry":     info.get("industry", "N/A"),
            }
        except Exception as e:
            results[sym] = {"error": str(e)}
    return json.dumps(results, indent=2)


@tool("fetch_macro_indicators")
def fetch_macro_indicators(tickers: str) -> str:
    """
    Fetch macro indicators: 10Y yield, Gold, Oil, DXY, VIX, BTC.
    Pass comma-separated Yahoo Finance tickers.
    """
    return fetch_stock_data(tickers)


@tool("scan_news_rss")
def scan_news_rss(query: str) -> str:
    """
    Scan Google News RSS for geopolitical and financial headlines related to the query.
    Returns top 15 headlines with source and timestamp.
    """
    encoded = requests.utils.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)
    results = []
    for entry in feed.entries[:15]:
        results.append({
            "title":     entry.get("title", ""),
            "source":    entry.get("source", {}).get("title", "Unknown"),
            "published": entry.get("published", ""),
            "summary":   entry.get("summary", "")[:300],
        })
    return json.dumps(results, indent=2)


@tool("fetch_sector_flows")
def fetch_sector_flows(sector_etfs: str) -> str:
    """
    Analyze sector ETF momentum and relative strength to identify sector rotation.
    Pass comma-separated sector ETF tickers.
    """
    return fetch_stock_data(sector_etfs)


@tool("scan_insider_activity")
def scan_insider_activity(ticker: str) -> str:
    """
    Check recent insider transactions for a stock using Yahoo Finance data.
    Returns a summary of insider buying/selling signals.
    """
    try:
        tk = yf.Ticker(ticker.strip())
        insider = tk.insider_transactions
        if insider is None or insider.empty:
            return json.dumps({"ticker": ticker, "signal": "No recent insider data available"})
        recent = insider.head(10)
        records = []
        for _, row in recent.iterrows():
            records.append({
                "insider":     str(row.get("Insider", "")),
                "relation":    str(row.get("Relation", "")),
                "transaction": str(row.get("Transaction", "")),
                "shares":      str(row.get("Shares", "")),
                "value":       str(row.get("Value", "")),
                "date":        str(row.get("Start Date", "")),
            })
        return json.dumps({"ticker": ticker, "insider_transactions": records}, indent=2)
    except Exception as e:
        return json.dumps({"ticker": ticker, "error": str(e)})


# ─── AGENTS ────────────────────────────────────────────────────────────────────

macro_scout = Agent(
    role="Global Macro Scout",
    goal=(
        "Identify geopolitical and macroeconomic TAILWINDS that create asymmetric "
        "opportunities. Focus on: interest rate regime shifts, commodity supercycles, "
        "currency flows, military/trade conflicts, and central bank policy pivots."
    ),
    backstory=(
        "You are a former macro strategist from a global macro hedge fund. "
        "You think like Ray Dalio — debt cycles, geopolitics, and capital flows. "
        "You scan news and macro data to find the invisible forces moving markets "
        "BEFORE the crowd notices."
    ),
    tools=[fetch_macro_indicators, scan_news_rss],
    llm=deepseek_llm,
    verbose=True,
    allow_delegation=False,
)

sector_analyst = Agent(
    role="Sector Rotation Analyst",
    goal=(
        "Identify which sectors are at the EARLY stage of institutional accumulation "
        "before the mainstream rotation. Find sectors with improving fundamentals + "
        "relative strength breakouts + favorable macro backdrop."
    ),
    backstory=(
        "You are a sector specialist who spent 10 years at a quantitative fund. "
        "You understand that stocks don't move in isolation — they move with their "
        "sector, and sectors move with macro. You find the sector BEFORE the ETF "
        "inflows show up on Bloomberg."
    ),
    tools=[fetch_sector_flows, scan_news_rss],
    llm=deepseek_llm,
    verbose=True,
    allow_delegation=False,
)

stock_sniper = Agent(
    role="Individual Stock Catalyst Sniper",
    goal=(
        "Find specific stocks with multiple STACKING catalysts: insider buying + "
        "technical breakout + sector tailwind + upcoming catalyst (earnings, FDA, "
        "contract, product launch). Prioritize asymmetric risk/reward setups."
    ),
    backstory=(
        "You are a fundamental + technical hybrid analyst. You look for the specific "
        "stock that will 3-5x because it sits at the intersection of a great macro "
        "theme, a turning sector, and a company-specific ignition event. You read "
        "insider filings obsessively."
    ),
    tools=[fetch_stock_data, scan_insider_activity, scan_news_rss],
    llm=deepseek_llm,
    verbose=True,
    allow_delegation=False,
)

contrarian_agent = Agent(
    role="Contrarian Risk Auditor",
    goal=(
        "Challenge every bull thesis. Find the hidden risks, overvaluation, "
        "narrative traps, and crowded trades. Ask: what does the market ALREADY "
        "know? What's the bear case? What kills this trade?"
    ),
    backstory=(
        "You are a short-seller and devil's advocate. You've seen dozens of "
        "'asymmetric' bets blow up because the thesis was right but the timing, "
        "valuation, or catalyst was wrong. Your job is to STRESS TEST every idea "
        "until only the truly asymmetric bets survive."
    ),
    tools=[fetch_stock_data, scan_news_rss],
    llm=deepseek_llm,
    verbose=True,
    allow_delegation=False,
)

thesis_writer = Agent(
    role="Alpha Thesis Synthesizer",
    goal=(
        "Synthesize ALL agent findings into a clean, actionable ASYMMETRIC BET ALERT. "
        "Score each idea (1-10) on: Asymmetry, Catalyst Clarity, Macro Alignment, "
        "Risk/Reward. Only surface bets scoring 7+. Format for Telegram alert."
    ),
    backstory=(
        "You are the CIO of the team. You take raw research from 4 analysts and "
        "distill it into razor-sharp investment theses that a fund manager can act on. "
        "You think in terms of: Entry, Catalyst, Target, Stop, Time Horizon. "
        "No fluff. Only alpha."
    ),
    tools=[],
    llm=deepseek_llm,
    verbose=True,
    allow_delegation=False,
)

# ─── TASKS (parallel where possible) ──────────────────────────────────────────

task_macro = Task(
    description=f"""
    TODAY: {datetime.now().strftime('%Y-%m-%d %H:%M')}
    
    1. Fetch macro indicators: {','.join(WATCHLIST_MACRO)}
    2. Scan news for: "geopolitical risk markets 2025", "Federal Reserve rate decision", 
       "commodity supercycle", "trade war tariffs", "currency crisis"
    3. Identify the TOP 3 macro tailwinds creating asymmetric opportunities RIGHT NOW
    4. For each tailwind, specify: Which asset classes benefit? What's the timeline? 
       How crowded is the trade?
    
    Output: Structured JSON with macro_tailwinds[], each with theme, beneficiaries, 
    timeline, crowding_level, confidence_score (1-10)
    """,
    expected_output="JSON object with top 3 macro tailwinds and their beneficiary asset classes",
    agent=macro_scout,
)

task_sector = Task(
    description=f"""
    TODAY: {datetime.now().strftime('%Y-%m-%d %H:%M')}
    
    1. Analyze sector ETF performance: {','.join(WATCHLIST_SECTORS)}
    2. Identify sectors showing: RSI < 50 (early stage) OR breaking out above 52w high
    3. Scan news for: "sector rotation 2025", "institutional buying sector", 
       "ETF inflows sector"
    4. Cross-reference with macro tailwinds (think: if rates dropping → REITs/Utilities; 
       if geopolitical tension → Defense/Energy)
    
    Output: Top 2 sectors in early accumulation phase with rationale and specific ETFs/themes
    """,
    expected_output="Top 2 sector rotation opportunities with ETF tickers and institutional flow signals",
    agent=sector_analyst,
)

task_stocks = Task(
    description=f"""
    TODAY: {datetime.now().strftime('%Y-%m-%d %H:%M')}
    
    1. Pull data on watchlist: {','.join(WATCHLIST_STOCKS)}
    2. For top 5 candidates (high short float OR near 52w low with catalyst), 
       check insider transactions
    3. Scan news for each top candidate: "[TICKER] insider buying", "[TICKER] catalyst 2025"
    4. Find stocks where 3+ signals STACK: insider buying + oversold RSI + sector tailwind 
       + upcoming catalyst
    
    Output: Top 3 stock picks with entry rationale, catalyst date/event, and asymmetry score
    """,
    expected_output="Top 3 asymmetric stock setups with stacked signals and catalyst timeline",
    agent=stock_sniper,
)

task_contrarian = Task(
    description=f"""
    TODAY: {datetime.now().strftime('%Y-%m-%d %H:%M')}
    
    Review the stock watchlist: {','.join(WATCHLIST_STOCKS[:5])}
    
    For the most hyped names, find:
    1. What does the market ALREADY know? (priced in?)
    2. What's the short thesis / bear case?
    3. Valuation red flags (P/E, P/S vs. growth rate)
    4. What macro scenario KILLS these trades?
    5. Which ideas from the bull side are narrative traps vs. true asymmetry?
    
    Output: Risk audit for top 3 picks — what could go wrong, what's already priced in,
    and which trades to AVOID despite the hype
    """,
    expected_output="Risk audit identifying narrative traps, crowded trades, and 'avoid' signals",
    agent=contrarian_agent,
)

task_synthesis = Task(
    description="""
    You have received research from 4 parallel agents:
    - Macro Scout: identified macro tailwinds
    - Sector Analyst: identified sector rotation opportunities  
    - Stock Sniper: identified specific stock setups
    - Contrarian: identified risks and traps to avoid
    
    YOUR JOB:
    1. Synthesize ALL findings into a final ASYMMETRIC BET REPORT
    2. Score each bet: Asymmetry (1-10), Catalyst Clarity (1-10), Macro Alignment (1-10)
    3. Only surface bets with average score >= 7
    4. Format as a Telegram-ready alert (use emojis, keep under 1500 chars per bet)
    
    REQUIRED OUTPUT FORMAT per bet:
    🎯 ASYMMETRIC BET: [Name/Ticker]
    📊 THEME: [1-line macro/sector theme]
    🔥 CATALYSTS: [bullet list of stacking signals]
    ⚠️ KEY RISK: [single biggest risk]
    📈 SETUP: Entry ~$X | Target $X-$X | Stop $X | Horizon: X months
    🏆 SCORE: Asymmetry X/10 | Catalyst X/10 | Macro X/10
    
    End with a PORTFOLIO NOTE: how these bets relate to each other (correlated? hedged?)
    """,
    expected_output="Final asymmetric bet report with scored opportunities formatted for Telegram alerts",
    agent=thesis_writer,
    context=[task_macro, task_sector, task_stocks, task_contrarian],
)

# ─── CREW (Parallel execution) ─────────────────────────────────────────────────

crew = Crew(
    agents=[macro_scout, sector_analyst, stock_sniper, contrarian_agent, thesis_writer],
    tasks=[task_macro, task_sector, task_stocks, task_contrarian, task_synthesis],
    process=Process.hierarchical,   # manager coordinates parallel agents
    manager_llm=deepseek_llm,
    verbose=True,
    planning=True,                  # CrewAI plans optimal execution order
)

# ─── TELEGRAM ALERT ────────────────────────────────────────────────────────────

def send_telegram_alert(message: str):
    """Send alert to Telegram channel/chat."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("\n⚠️  Telegram not configured. Add TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to .env\n")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    # Split long messages
    chunks = [message[i:i+4000] for i in range(0, len(message), 4000)]
    for chunk in chunks:
        try:
            resp = requests.post(url, json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": chunk,
                "parse_mode": "Markdown",
            }, timeout=10)
            if resp.status_code == 200:
                print("✅ Telegram alert sent")
            else:
                print(f"❌ Telegram error: {resp.text}")
        except Exception as e:
            print(f"❌ Telegram exception: {e}")

# ─── MAIN RUN ──────────────────────────────────────────────────────────────────

def run_alpha_scan():
    print(f"\n{'='*65}")
    print(f"  🚀 ALPHA MACHINE SCAN — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*65}\n")

    result = crew.kickoff()

    output = str(result)

    header = (
        f"🤖 *ALPHA MACHINE REPORT*\n"
        f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n"
        f"{'─'*40}\n\n"
    )
    full_alert = header + output

    print("\n" + "="*65)
    print("  📊 FINAL ALPHA REPORT")
    print("="*65)
    print(output)
    print("="*65 + "\n")

    send_telegram_alert(full_alert)
    return output


def run_scheduled():
    """Schedule scans: 6 AM, 12 PM, and 4 PM daily (market open/midday/close)."""
    print("⏰ Alpha Machine scheduler started...")
    print("   Scans scheduled: 06:00 | 12:00 | 16:00 daily\n")

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
        # Run once immediately
        run_alpha_scan()
