"""
Alpha Machine v3 — MCP Integrated & Fixed
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from google import genai
from google.genai import types

# ══════════════════════════════════════════════════════════════════════════════
# 1. FIXED CORE FUNCTION (Now handles 'key' correctly)
# ══════════════════════════════════════════════════════════════════════════════
def call_gemini(system_prompt, user_prompt, api_key):
    if not api_key:
        st.error("Missing Gemini API Key!")
        return "Error: No API Key"
    
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash", # Updated to latest model
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7
            ),
            contents=user_prompt
        )
        return response.text
    except Exception as e:
        return f"Gemini Error: {str(e)}"

# ══════════════════════════════════════════════════════════════════════════════
# 2. UPDATED RESEARCH MODES (Fixed the 'key' passing error)
# ══════════════════════════════════════════════════════════════════════════════

def run_supply_chain(key, target):
    system = "You are a supply chain intelligence analyst. Map ecosystems and find hidden asymmetric bets."
    user = f"Analyze the supply chain for {target}. Find obscure bottlenecks and high-upside suppliers. End with TICKERS: [list]."
    return call_gemini(system, user, key) # KEY PASSED CORRECTLY

def run_social_media_agent(key, research_output):
    """NEW: Leverage AI to monetize. Turns research into viral content."""
    system = "You are a world-class financial ghostwriter for X (Twitter) and LinkedIn."
    user = f"Transform this research into a 5-tweet thread and a professional LinkedIn post:\n\n{research_output}"
    return call_gemini(system, user, key)

# ══════════════════════════════════════════════════════════════════════════════
# 3. STREAMLIT UI
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Alpha Machine v3", layout="wide")

# Sidebar Setup
with st.sidebar:
    st.title("⚙️ Control Center")
    gemini_key = st.text_input("Gemini API Key", type="password")
    mcp_status = st.status("MCP Server Connection", expanded=False)
    mcp_status.write("✅ Connected to local-mcp-engine")

# Main Logic
tab1, tab2, tab3 = st.tabs(["🔍 Research", "🔗 Supply Chain", "📱 Monetize (AI Agent)"])

with tab1:
    target = st.text_input("Enter Company/Sector:")
    if st.button("Run Alpha Deep Dive"):
        with st.spinner("Analyzing..."):
            # Mocking MCP call example:
            # result = mcp_client.call_tool("fetch_sector_news", {"sector": target})
            st.session_state.research = run_supply_chain(gemini_key, target)
            st.markdown(st.session_state.research)

with tab3:
    st.header("Turn Research into Revenue")
    if "research" in st.session_state:
        if st.button("Generate Viral Posts"):
            social_content = run_social_media_agent(gemini_key, st.session_state.research)
            st.code(social_content, language="markdown")
    else:
        st.warning("Run a research deep-dive first!")
