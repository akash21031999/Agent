import streamlit as st
import pandas as pd
from datetime import datetime
from google import genai
from google.genai import types

# ══════════════════════════════════════════════════════════════════════════════
# 1. CORE ENGINE
# ══════════════════════════════════════════════════════════════════════════════
def call_gemini(system_prompt, user_prompt, api_key):
    if not api_key:
        st.error("Missing Gemini API Key in Sidebar!")
        return None
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash", # Use 2.0 for best performance
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7
            ),
            contents=user_prompt
        )
        return response.text
    except Exception as e:
        st.error(f"Gemini Error: {str(e)}")
        return None

# ══════════════════════════════════════════════════════════════════════════════
# 2. INTELLIGENCE MODES
# ══════════════════════════════════════════════════════════════════════════════

def run_supply_chain(key, target):
    system = """You are a Lead Supply Chain Intelligence Analyst. 
    Map complete ecosystems. Find hidden asymmetric bets in obscure suppliers.
    STRICT FORMATTING: 
    - Bold all tickers like **$ASML**, **$KLAC**, **$VRT**.
    - Focus on 'Smart Money' rotation and institutional buying reasons."""
    user = f"Analyze the supply chain for {target}. Identify the 'bottleneck' companies that capture the most value."
    return call_gemini(system, user, key)

def run_macro_brief(key):
    system = "You are a Macro Strategist. Analyze DXY, VIX, Bonds, and Global Liquidity."
    user = "Give me the current market regime. Is it Risk-On or Risk-Off? Predict the next 8 hours based on smart money flow."
    return call_gemini(system, user, key)

# ══════════════════════════════════════════════════════════════════════════════
# 3. STREAMLIT UI (Fixed Display Logic)
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Alpha Machine v3", layout="wide")

with st.sidebar:
    st.title("🛡️ Alpha Machine")
    gemini_key = st.text_input("Gemini API Key", type="password")
    st.divider()
    st.status("MCP Engine: Connected")

tab1, tab2, tab3 = st.tabs(["🔍 Macro Pulse", "🔗 Supply Chain", "📱 Monetize"])

# --- TAB 1: MACRO ---
with tab1:
    st.header("Global Macro & Smart Money")
    if st.button("Generate Market Brief"):
        with st.spinner("Analyzing VIX, DXY, and Bonds..."):
            st.session_state.macro_res = run_macro_brief(gemini_key)
    
    if "macro_res" in st.session_state:
        st.markdown(st.session_state.macro_res)

# --- TAB 2: SUPPLY CHAIN (FIXED: Result stays on page) ---
with tab2:
    st.header("Supply Chain Deep-Dive")
    target = st.text_input("Enter Company/Sector (e.g., 'Advanced Packaging'):")
    
    if st.button("Analyze Asymmetry"):
        if target:
            with st.spinner(f"Mapping {target} Ecosystem..."):
                st.session_state.supply_res = run_supply_chain(gemini_key, target)
        else:
            st.warning("Enter a target first.")

    # This display is OUTSIDE the button so it stays visible
    if "supply_res" in st.session_state:
        st.divider()
        st.markdown(st.session_state.supply_res)

# --- TAB 3: MONETIZE ---
with tab3:
    st.header("Revenue Agent")
    if "supply_res" in st.session_state or "macro_res" in st.session_state:
        if st.button("Generate Social Content"):
            content = st.session_state.get("supply_res") or st.session_state.get("macro_res")
            prompt = "Transform this into a viral 5-tweet thread and a LinkedIn post."
            res = call_gemini("You are a financial ghostwriter.", content + prompt, gemini_key)
            st.code(res, language="markdown")
    else:
        st.info("Run research in Tab 1 or 2 to generate content.")
