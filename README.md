# 🤖 Alpha Machine — Multi-Agent Asymmetric Bet Hunter

A parallel CrewAI system powered by DeepSeek-R1 that scans macro, sector, 
and stock layers simultaneously to surface asymmetric bets with upcoming tailwinds.
Alerts delivered to Telegram automatically.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  PARALLEL AGENTS                     │
├──────────────┬──────────────┬───────────────────────┤
│ Macro Scout  │Sector Analyst│  Stock Sniper          │
│ (Geopolitics │ (Rotation +  │  (Catalysts +          │
│  Rates FX)   │  Flow data)  │   Insider signals)     │
└──────┬───────┴──────┬───────┴──────┬────────────────┘
       │              │              │
       ▼              ▼              ▼
┌─────────────────────────────────────────────────────┐
│              Contrarian Risk Auditor                 │
│         (Stress-tests all 3 bull theses)             │
└─────────────────────┬───────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────┐
│             Thesis Writer (CIO Layer)                │
│    Scores bets 1-10, filters <7, formats alerts      │
└─────────────────────┬───────────────────────────────┘
                      ▼
              📱 Telegram Alert
```

---

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API keys
```bash
cp .env.template .env
# Edit .env with your actual keys
```

**Keys you need:**
| Key | Where to get it | Cost |
|-----|----------------|------|
| `DEEPSEEK_API_KEY` | platform.deepseek.com | ~$0.55/M tokens (R1) |
| `TELEGRAM_BOT_TOKEN` | @BotFather on Telegram | Free |
| `TELEGRAM_CHAT_ID` | Your channel/group ID | Free |

### 3. Get your Telegram Chat ID
```bash
# After creating bot and adding to channel:
curl https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
# Find "chat":{"id": -XXXXXXXXX} — that's your CHAT_ID
```

---

## Usage

### Run once (immediate scan)
```bash
python main.py
```

### Run on schedule (6 AM / 12 PM / 4 PM daily)
```bash
python main.py --schedule
```

### Run in background (Linux/Mac)
```bash
nohup python main.py --schedule > alpha_log.txt 2>&1 &
```

### Run on Streamlit (visual dashboard)
```bash
streamlit run streamlit_app.py
```

---

## Customization

### Add your own watchlists (in main.py)
```python
WATCHLIST_STOCKS   = ["NVDA","TSM","ASML",...]  # Your picks
WATCHLIST_SECTORS  = ["XLK","XLE","XLF",...]    # Sector ETFs
WATCHLIST_MACRO    = ["^TNX","GC=F","CL=F",...]  # Macro tickers
```

### Change scan schedule
```python
schedule.every().day.at("06:00").do(run_alpha_scan)
schedule.every().day.at("12:00").do(run_alpha_scan)
```

### Add more news queries (in task descriptions)
Edit the `scan_news_rss` tool calls inside each task to target
specific geopolitical themes relevant to your thesis.

---

## Cost Estimate (DeepSeek-R1)
- ~5,000-8,000 tokens per scan (5 agents)  
- Cost per scan: ~$0.004–$0.006
- 3 scans/day × 30 days = **~$0.45/month**

---

## Extending the System

### Add options flow (Unusual Whales API)
```python
@tool("fetch_options_flow")
def fetch_options_flow(ticker: str) -> str:
    # Plug in Unusual Whales or Market Chameleon API
    pass
```

### Add SEC Form 4 insider parsing (OpenInsider)
```python
@tool("scan_sec_filings")
def scan_sec_filings(ticker: str) -> str:
    url = f"https://openinsider.com/search?q={ticker}"
    # Parse the table
    pass
```

### Sell the API (RapidAPI)
Wrap `run_alpha_scan()` in a FastAPI endpoint:
```python
from fastapi import FastAPI
app = FastAPI()

@app.get("/scan")
def scan():
    return {"result": run_alpha_scan()}
```
