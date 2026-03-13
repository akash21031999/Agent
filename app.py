"""
Alpha Machine v3 — Institutional Intelligence Dashboard
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from google import genai
from google.genai import types

# ══════════════════════════════════════════════════════════════════════════════
# 1. CORE ENGINE (FIXED)
# ══════════════════════════════════════════════════════════════════════════════
def call_gemini(system_prompt, user_prompt, api_key):
    if not api_key:
        return "⚠️ Please enter your Gemini API Key in the sidebar."
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7
            ),
            contents=user_prompt
        )
        return response.text
    except Exception as e:
        return f"❌ AI Engine Error: {str(e)}"

# ══════════════════════════════════════════════════════════════════════════════
# 2. FIXED RESEARCH MODES
# ══════════════════════════════════════════════════════════════════════════════

def run_supply_chain(key, target):
    system = "You are a Supply Chain Intelligence Analyst. Use bold tickers like **$ASML**."
    user = f"Map the ecosystem for {target}. Identify asymmetric bets and bottlenecks."
    return call_gemini(system, user, key)

def run_macro_intel(key, theme):
    system = "You are a Macro Strategist. Analyze DXY, VIX, and Bond Yield correlations."
    user = f"Analyze the macro regime for: {theme}"
    return call_gemini(system, user, key)

def run_social_agent(key, content):
    system = "You are a viral financial ghostwriter for X and LinkedIn."
    user = f"Convert this research into a viral thread and a LinkedIn post: {content}"
    return call_gemini(system, user, key)

# ══════════════════════════════════════════════════════════════════════════════
# 3. STREAMLIT UI
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Alpha Machine v3", layout="wide")

with st.sidebar:
    st.title("🛡️ Control Center")
    gemini_key = st.text_input("Gemini API Key", type="password")
    st.divider()
    st.info("MCP Server: Connected (Local)")

tab1, tab2, tab3 = st.tabs(["🔍 Intelligence", "🔗 Supply Chain", "📱 Monetize"])

with tab1:
    theme = st.text_input("Macro Theme (e.g., 'Fed Pivot', 'AI Energy'):")
    if st.button("Analyze Macro"):
        with st.spinner("Crunching DXY, VIX, and Yields..."):
            st.markdown(run_macro_intel(gemini_key, theme))

with tab2:
    target = st.text_input("Target Ticker/Sector (e.g., 'ASML', 'Nuclear SMR'):")
    if st.button("Map Supply Chain"):
        with st.spinner("Finding Bottlenecks..."):
            st.session_state.last_research = run_supply_chain(gemini_key, target)
            st.markdown(st.session_state.last_research)

with tab3:
    if "last_research" in st.session_state:
        if st.button("Generate Viral Posts"):
            st.code(run_social_agent(gemini_key, st.session_state.last_research))
    else:
        st.warning("Run research in Tab 1 or 2 first.")
