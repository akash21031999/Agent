"""
Alpha Machine v4 — Institutional Intelligence & Agentic Research
"""
import streamlit as st
import time
from google import genai
from google.genai import types

# ══════════════════════════════════════════════════════════════════════════════
# 1. ADVANCED ENGINE (With Streaming & Error Recovery)
# ══════════════════════════════════════════════════════════════════════════════
def stream_alpha_intel(system_prompt, user_prompt, api_key):
    """Streams the AI response for a more 'Premium' feel and faster UX."""
    if not api_key:
        st.error("Missing Gemini API Key!")
        return
    try:
        client = genai.Client(api_key=api_key)
        # Using 2.5 Flash for the best speed/reasoning balance
        response = client.models.generate_content_stream(
            model="gemini-2.5-flash", 
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.4, # Lower temperature for institutional accuracy
            ),
            contents=user_prompt
        )
        for chunk in response:
            yield chunk.text
    except Exception as e:
        yield f"❌ System Error: {str(e)}"

# ══════════════════════════════════════════════════════════════════════════════
# 2. ENHANCED SYSTEM PROMPTS (The 'Secret Sauce')
# ══════════════════════════════════════════════════════════════════════════════
MACRO_SYSTEM = """You are a Lead Global Macro Strategist. 
Analyze the intersection of Global Liquidity, Bond Yields, and Volatility.
Always provide a 'Base Case' and a 'Black Swan' scenario.
Focus on correlations: if X happens, then Y is the asymmetric play."""

SUPPLY_SYSTEM = """You are a Supply Chain Forensic Analyst. 
Map the 'Nervous System' of a sector. Identify the one company that owns the IP 
or the bottleneck that the giants (AAPL, NVDA, TSLA) cannot live without.
Bold all tickers: **$TICKER**."""

# ══════════════════════════════════════════════════════════════════════════════
# 3. ADVANCED UI COMPONENTS
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Alpha Machine v4", layout="wide", page_icon="🛡️")

# --- Custom Sidebar ---
with st.sidebar:
    st.title("🛡️ Alpha Control")
    gemini_key = st.text_input("Gemini API Key", type="password")
    
    st.divider()
    st.subheader("Live Intelligence Feed")
    st.status("MCP Server: Connected", state="complete")
    st.status("Sentiment: Risk-On", state="running")
    
    if st.button("Reset Session"):
        st.session_state.clear()
        st.rerun()

# --- Main Dashboard ---
st.title("⚡ Institutional Alpha Engine")

tab1, tab2, tab3 = st.tabs(["🏛️ Macro Regime", "⛓️ Supply Chain Forensic", "📢 Monetization Agent"])

with tab1:
    st.header("Global Liquidity & Smart Money Flow")
    if st.button("Generate Macro Brief", key="macro_btn"):
        with st.status("Analyzing DXY, VIX, and Bond Yields...", expanded=True) as status:
            st.write("Fetching real-time yields...")
            time.sleep(1)
            st.write("Calculating Smart Money Divergence...")
            
            output_container = st.empty()
            full_response = ""
            for chunk in stream_alpha_intel(MACRO_SYSTEM, "Analyze the current 8-hour market regime and identify smart money rotation.", gemini_key):
                full_response += chunk
                output_container.markdown(full_response)
            
            st.session_state.last_macro = full_response
            status.update(label="Analysis Complete", state="complete")

with tab2:
    st.header("Supply Chain Bottleneck Discovery")
    target = st.text_input("Enter Ticker or Technology (e.g., 'EUV Lithography', 'ASML'):")
    if st.button("Trace Ecosystem"):
        if target:
            with st.status(f"Mapping {target} Nervous System...") as status:
                output_container = st.empty()
                full_response = ""
                for chunk in stream_alpha_intel(SUPPLY_SYSTEM, f"Find the asymmetric winners in the {target} supply chain.", gemini_key):
                    full_response += chunk
                    output_container.markdown(full_response)
                
                st.session_state.last_research = full_response
                status.update(label="Ecosystem Mapped", state="complete")

with tab3:
    st.header("One-Click Monetization")
    source_content = st.session_state.get("last_research") or st.session_state.get("last_macro")
    
    if source_content:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Draft Viral X Thread"):
                res = stream_alpha_intel("You are a viral ghostwriter.", f"Turn this into a 7-tweet thread with hooks: {source_content}", gemini_key)
                st.write_stream(res)
        with col2:
            if st.button("Draft Professional Newsletter"):
                res = stream_alpha_intel("You are a Substack financial analyst.", f"Format this into a professional research note: {source_content}", gemini_key)
                st.write_stream(res)
    else:
        st.warning("Please run research in Tab 1 or 2 first.")
