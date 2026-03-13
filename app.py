import streamlit as st
import requests
import feedparser
import json
import pandas as pd
from datetime import datetime
from google import genai
from google.genai import types

# ══════════════════════════════════════════════════════════════════════════════
#  CONFIG & STATE
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Alpha Machine v2 🎯", layout="wide")

# Initialize Session State for persistence
if "research_results" not in st.session_state:
    st.session_state.research_results = None
if "current_query" not in st.session_state:
    st.session_state.current_query = ""

# ══════════════════════════════════════════════════════════════════════════════
#  CORE RESEARCH ENGINE
# ══════════════════════════════════════════════════════════════════════════════
def run_supply_chain_analysis(query, api_key):
    """Traces bottlenecks and moats across the supply chain."""
    try:
        client = genai.Client(api_key=api_key)
        prompt = f"""
        Act as a Tier-1 Equity Research Analyst specializing in Supply Chain Forensics.
        Topic: {query}
        
        1. UPSTREAM: Identify the raw material/IP providers (the 'Oxygen').
        2. MIDSTREAM: Identify the fabricators/bottlenecks.
        3. DOWNSTREAM: Identify the ultimate price-setters.
        4. ASYMMETRIC PICK: Which specific micro-cap or mid-cap name owns a critical 'Toll Bridge'?
        5. RISK: What breaks this chain (Geopolitical/Regulatory)?
        """
        # UPDATED MODEL: Using 2.5 Flash for stability and performance
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Gemini Error: {str(e)}"

# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.title("🎯 Alpha Machine")
    api_key = st.text_input("Gemini API Key", type="password")
    st.info("Using Model: gemini-2.5-flash")
    
    if st.button("Clear Results"):
        st.session_state.research_results = None
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN INTERFACE
# ══════════════════════════════════════════════════════════════════════════════
st.title("⚡ Multi-Layer Supply Chain Research")

query = st.text_input("Enter Sector or Commodity (e.g., 'Nuclear SMR' or 'Nvidia H200')", 
                     value=st.session_state.current_query)

col1, col2 = st.columns([1, 4])

with col1:
    # Action button
    if st.button("Run Supply Chain Scan", use_container_width=True):
        if not api_key:
            st.error("Please enter an API Key in the sidebar.")
        elif not query:
            st.warning("Enter a query first.")
        else:
            with st.spinner(f"Tracing {query} supply chain..."):
                st.session_state.current_query = query
                result = run_supply_chain_analysis(query, api_key)
                st.session_state.research_results = result

# Display Area (Persists due to session_state)
with col2:
    if st.session_state.research_results:
        st.markdown("### 🔍 Research Output")
        st.markdown(st.session_state.research_results)
        
        # Download button for the report
        st.download_button(
            "Download Report", 
            data=st.session_state.research_results, 
            file_name=f"Alpha_{query.replace(' ', '_')}.md"
        )
    else:
        st.info("Input a sector and click 'Run' to begin analysis.")

# ══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD MODES (Reference)
# ══════════════════════════════════════════════════════════════════════════════
st.divider()
st.subheader("Available Intelligence Layers")
c1, c2, c3 = st.columns(3)
c1.markdown("**⛓️ Supply Chain**\nFinds bottlenecks & toll-bridges.")
c2.markdown("**🏛️ Smart Money**\nInstitutional rotation tracker.")
c3.markdown("**🏗️ Infrastructure**\nCapex cycle analysis.")
