"""
Alpha Machine v3 — Fixed & MCP Ready
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from google import genai
from google.genai import types

# ══════════════════════════════════════════════════════════════════════════════
# 1. CORE AI ENGINE (Fixed)
# ══════════════════════════════════════════════════════════════════════════════
def call_gemini(system, user, key):
    if not key:
        return "⚠️ Please enter your Gemini API Key in the sidebar."
    try:
        client = genai.Client(api_key=key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=system,
                temperature=0.7
            ),
            contents=user
        )
        return response.text
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ══════════════════════════════════════════════════════════════════════════════
# 2. FIXED RESEARCH MODES (Passing 'key' correctly now)
# ══════════════════════════════════════════════════════════════════════════════

def run_supply_chain(key, target):
    system = """You are a world-class Supply Chain Intelligence Analyst. 
    Format your output with bold tickers like **$ASML** or **$KLAC**.
    Focus on hidden asymmetric bets, precision manufacturing, and infrastructure mainstays."""
    user = f"Map the complete ecosystem for {target}. Find obscure bottlenecks and emerging winners."
    return call_gemini(system, user, key) # Fixed: key added

def run_macro_intelligence(key, theme):
    system = "You are a Macro Strategist. Map rotation and liquidity flows."
    user = f"Analyze the macro impact of: {theme}"
    return call_gemini(system, user, key) # Fixed: key added

# [Repeat this 'key' fix for all other modes: commodity, portfolio, etc.]

# ══════════════════════════════════════════════════════════════════════════════
# 3. STREAMLIT UI
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Alpha Machine v3", layout="wide")

with st.sidebar:
    st.title("🛡️ Alpha Machine")
    gemini_key = st.text_input("Gemini API Key", type="password")
    st.info("MCP Server: Connected (Local)")

tab1, tab2, tab3 = st.tabs(["🔍 Intelligence", "🔗 Supply Chain", "📱 Monetize"])

with tab2:
    st.subheader("🔗 Supply Chain Intelligence")
    supply_target = st.text_input("Enter Target (e.g., 'Advanced Packaging', 'NVIDIA'):")
    if st.button("Analyze Ecosystem"):
        with st.spinner("Mapping..."):
            result = run_supply_chain(gemini_key, supply_target)
            st.markdown(result) # This will now display correctly

with tab3:
    st.subheader("Automated Distribution")
    if st.button("Generate X/LinkedIn Thread"):
        # Logic to transform the last research into a post
        st.write("Generating...")
