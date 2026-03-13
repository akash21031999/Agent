"""
Alpha Machine — Streamlit Dashboard
Run: streamlit run streamlit_app.py
"""

import streamlit as st
import yfinance as yf
import json
import subprocess
import sys
from datetime import datetime
import pandas as pd

st.set_page_config(
    page_title="Alpha Machine",
    page_icon="🎯",
    layout="wide",
)

# ─── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem; font-weight: 800;
        background: linear-gradient(90deg, #00f5a0, #00d9f5);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background: #1a1a2e; border-radius: 12px;
        padding: 1rem; border: 1px solid #16213e;
    }
    .bet-card {
        background: #0f3460; border-radius: 12px;
        padding: 1.5rem; margin: 1rem 0;
        border-left: 4px solid #00f5a0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🎯 Alpha Machine — Asymmetric Bet Scanner</p>', unsafe_allow_html=True)
st.caption(f"Last checked: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")

# ─── SIDEBAR CONFIG ────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuration")
    deepseek_key = st.text_input("DeepSeek API Key", type="password", placeholder="sk-...")
    telegram_token = st.text_input("Telegram Bot Token", type="password")
    telegram_chat = st.text_input("Telegram Chat ID", placeholder="-100123456789")

    st.divider()
    st.subheader("📋 Watchlists")
    stocks_input = st.text_area("Stocks (comma-separated)",
        value="NVDA,TSM,ASML,PLTR,IONQ,RKLB,HIMS,CELH,NVO,MELI", height=80)
    sectors_input = st.text_area("Sector ETFs",
        value="XLK,XLE,XLF,XLV,XBI,ARKK,GDX,COPX,ITB,XAR", height=80)

    st.divider()
    run_scan = st.button("🚀 Run Full Alpha Scan", type="primary", use_container_width=True)

# ─── MACRO DASHBOARD ──────────────────────────────────────────────────────────
st.subheader("📊 Live Macro Dashboard")

macro_tickers = {
    "10Y Yield": "^TNX", "Gold": "GC=F", "Oil (WTI)": "CL=F",
    "DXY (USD)": "DX-Y.NYB", "VIX": "^VIX", "BTC": "BTC-USD"
}

cols = st.columns(len(macro_tickers))
for col, (name, ticker) in zip(cols, macro_tickers.items()):
    try:
        data = yf.Ticker(ticker).history(period="2d")
        if not data.empty and len(data) >= 2:
            current = data["Close"].iloc[-1]
            prev = data["Close"].iloc[-2]
            change = (current / prev - 1) * 100
            col.metric(name, f"{current:.2f}", f"{change:+.2f}%")
        else:
            col.metric(name, "N/A", "")
    except:
        col.metric(name, "N/A", "")

st.divider()

# ─── SECTOR HEATMAP ────────────────────────────────────────────────────────────
st.subheader("🗺️ Sector Momentum")

sector_etfs = [s.strip() for s in sectors_input.split(",") if s.strip()]
sector_data = []
for etf in sector_etfs:
    try:
        hist = yf.Ticker(etf).history(period="1mo")
        if not hist.empty and len(hist) > 1:
            m1 = (hist["Close"].iloc[-1] / hist["Close"].iloc[0] - 1) * 100
            w1 = (hist["Close"].iloc[-1] / hist["Close"].iloc[-6] - 1) * 100 if len(hist) >= 6 else 0
            sector_data.append({"ETF": etf, "1M %": round(m1, 2), "1W %": round(w1, 2)})
    except:
        pass

if sector_data:
    df = pd.DataFrame(sector_data).sort_values("1M %", ascending=False)
    def color_val(val):
        if isinstance(val, float):
            color = "#00f5a0" if val > 0 else "#ff4b4b"
            return f"color: {color}; font-weight: bold"
        return ""
    st.dataframe(
        df.style.applymap(color_val, subset=["1M %", "1W %"]),
        use_container_width=True, hide_index=True
    )

st.divider()

# ─── STOCK WATCHLIST ────────────────────────────────────────────────────────────
st.subheader("🎯 Watchlist Signals")

stock_list = [s.strip() for s in stocks_input.split(",") if s.strip()]
stock_rows = []
for sym in stock_list:
    try:
        tk = yf.Ticker(sym)
        info = tk.info
        hist = tk.history(period="3mo")
        if hist.empty:
            continue
        close = hist["Close"]
        # RSI
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = (-delta.clip(upper=0)).rolling(14).mean()
        rsi = float((100 - 100 / (1 + gain/(loss+1e-9))).iloc[-1])
        
        m1 = (close.iloc[-1]/close.iloc[-22]-1)*100 if len(close)>=22 else 0
        w52h = info.get("fiftyTwoWeekHigh", 0)
        price = float(close.iloc[-1])
        dist_52h = ((price / w52h) - 1) * 100 if w52h else 0

        # Simple signal
        signals = []
        if rsi < 35: signals.append("🟢 Oversold")
        if rsi > 70: signals.append("🔴 Overbought")
        short_pct = info.get("shortPercentOfFloat", 0)
        if short_pct and short_pct > 0.15: signals.append("⚡ High Short")
        if dist_52h > -5: signals.append("🚀 Near 52W High")
        if dist_52h < -40: signals.append("💎 Deep Value")

        stock_rows.append({
            "Ticker": sym,
            "Price": round(price, 2),
            "1M %": round(m1, 2),
            "RSI": round(rsi, 1),
            "Short %": f"{short_pct*100:.1f}%" if short_pct else "N/A",
            "52W Dist": f"{dist_52h:.1f}%",
            "Signals": " | ".join(signals) if signals else "—",
        })
    except:
        pass

if stock_rows:
    df2 = pd.DataFrame(stock_rows)
    def color_rsi(val):
        if isinstance(val, float):
            if val < 35: return "color: #00f5a0; font-weight: bold"
            if val > 70: return "color: #ff4b4b; font-weight: bold"
        return ""
    st.dataframe(
        df2.style.applymap(color_rsi, subset=["RSI"])
               .applymap(lambda v: "color: #00f5a0" if isinstance(v, float) and v > 0
                         else ("color: #ff4b4b" if isinstance(v, float) and v < 0 else ""),
                         subset=["1M %"]),
        use_container_width=True, hide_index=True
    )

st.divider()

# ─── AGENT SCAN TRIGGER ────────────────────────────────────────────────────────
st.subheader("🤖 Multi-Agent Alpha Scan")

if run_scan:
    if not deepseek_key:
        st.error("⚠️ Please enter your DeepSeek API key in the sidebar.")
    else:
        with st.spinner("🚀 Launching 5 parallel agents... this takes 2-3 minutes"):
            import os
            env = os.environ.copy()
            env["DEEPSEEK_API_KEY"] = deepseek_key
            if telegram_token: env["TELEGRAM_BOT_TOKEN"] = telegram_token
            if telegram_chat: env["TELEGRAM_CHAT_ID"] = telegram_chat

            try:
                result = subprocess.run(
                    [sys.executable, "main.py"],
                    capture_output=True, text=True, timeout=300, env=env,
                    cwd=str(__import__("pathlib").Path(__file__).parent)
                )
                output = result.stdout + result.stderr

                st.success("✅ Scan complete!")

                # Display formatted output
                lines = output.split("\n")
                report_start = next(
                    (i for i, l in enumerate(lines) if "FINAL ALPHA REPORT" in l or "🎯" in l), 0
                )
                report = "\n".join(lines[report_start:])
                st.markdown("### 📊 Alpha Report")
                st.code(report, language=None)

                if telegram_token and telegram_chat:
                    st.info("📱 Alert sent to Telegram!")

            except subprocess.TimeoutExpired:
                st.error("⏱️ Scan timed out (>5 min). Try reducing watchlist size.")
            except Exception as e:
                st.error(f"❌ Error: {e}")
else:
    st.info("👈 Configure your API keys and click **Run Full Alpha Scan** to start the agent crew.")

    # Show example alert format
    with st.expander("📋 Example Alert Format"):
        st.code("""
🎯 ASYMMETRIC BET: RKLB (Rocket Lab)
📊 THEME: Space defense + smallsat boom + DoD tailwind
🔥 CATALYSTS:
   • RSI 31 — deeply oversold after sector rotation
   • CEO bought $2.1M in shares (Form 4, last week)
   • DoD contract award expected Q2 2025
   • XAR (defense ETF) breaking 52W high
⚠️ KEY RISK: Execution delays on Neutron rocket timeline
📈 SETUP: Entry ~$8.50 | Target $14-18 | Stop $6.80 | Horizon: 9 months
🏆 SCORE: Asymmetry 8/10 | Catalyst 9/10 | Macro 8/10
        """, language=None)

st.caption("Alpha Machine v1.0 — Powered by CrewAI + DeepSeek-R1")
