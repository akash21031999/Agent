import streamlit as st
import pandas as pd
import os
import re
from crewai import Agent, Task, Crew, Process
from langchain_groq import ChatGroq
import yfinance as yf

import streamlit as st
from openai import OpenAI

import streamlit as st
from openai import OpenAI

# 1. Retrieve the key securely from Advanced Settings
deepseek_key = st.secrets["DEEPSEEK_API_KEY"]

# 2. Initialize the DeepSeek Client
# DeepSeek uses an OpenAI-compatible base URL
client = OpenAI(
    api_key=deepseek_key,
    base_url="https://api.deepseek.com"
)

st.title("🏦 DeepSeek Alpha Terminal")

# Simple check to see if key is loaded
if deepseek_key:
    st.success("DeepSeek API Key loaded from Secrets.")

# Example function to run a deep research prompt
def run_deepseek_reasoning(prompt):
    response = client.chat.completions.create(
        model="deepseek-reasoner", # This is the R1 Reasoning model
        messages=[
            {"role": "system", "content": "You are a senior investment analyst specializing in asymmetric supply chain bets."},
            {"role": "user", "content": prompt}
        ],
        stream=True
    )
    return response

# UI Input
user_query = st.text_input("Enter Research Query:")

if st.button("Analyze"):
    if user_query:
        with st.chat_message("assistant"):
            response_container = st.empty()
            full_response = ""
            
            # Streaming the response for that "Chain of Thought" look
            for chunk in run_deepseek_reasoning(user_query):
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_container.markdown(full_response + "▌")
            response_container.markdown(full_response)

# 1. Retrieve the key securely from Advanced Settings
deepseek_key = st.secrets["DEEPSEEK_API_KEY"]

# 2. Initialize the DeepSeek Client
# DeepSeek uses an OpenAI-compatible base URL
client = OpenAI(
    api_key=deepseek_key,
    base_url="https://api.deepseek.com"
)

st.title("🏦 DeepSeek Alpha Terminal")

# Simple check to see if key is loaded
if deepseek_key:
    st.success("DeepSeek API Key loaded from Secrets.")

# Example function to run a deep research prompt
def run_deepseek_reasoning(prompt):
    response = client.chat.completions.create(
        model="deepseek-reasoner", # This is the R1 Reasoning model
        messages=[
            {"role": "system", "content": "You are a senior investment analyst specializing in asymmetric supply chain bets."},
            {"role": "user", "content": prompt}
        ],
        stream=True
    )
    return response

# UI Input
user_query = st.text_input("Enter Research Query:")

if st.button("Analyze"):
    if user_query:
        with st.chat_message("assistant"):
            response_container = st.empty()
            full_response = ""
            
            # Streaming the response for that "Chain of Thought" look
            for chunk in run_deepseek_reasoning(user_query):
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_container.markdown(full_response + "▌")
            response_container.markdown(full_response)

# --- 1. CONFIGURATION & AI SETUP ---
# DeepSeek-R1 via Groq is the "Strategist" (Reasoning Layer)
# Gemini-3-Flash is the "Scraper" (High-speed data processing)
llm_reasoner = ChatGroq(
    model_name="deepseek-r1-distill-llama-70b", 
    groq_api_key=st.secrets["GROQ_API_KEY"]
)

# --- 2. AGENT DEFINITIONS ---
def get_research_crew(user_query):
    # Agent A: The Scraper (High-speed discovery)
    scraper = Agent(
        role='Supply Chain Scout',
        goal=f'Identify 3 obscure Tier 2/3 suppliers for {user_query}.',
        backstory='Specialist in industrial bottlenecks and patent-protected small-caps.',
        llm=llm_reasoner, # Using R1 to ensure it "thinks" about the chain
        verbose=True
    )

    # Agent B: The Quant (Crunching numbers)
    quant = Agent(
        role='Quantitative Analyst',
        goal='Analyze the financial health and analyst targets for identified tickers.',
        backstory='CFA Analyst. Focuses on ROE, Debt/Equity, and Projected Upside.',
        llm=llm_reasoner,
        verbose=True
    )

    # Agent C: The Strategist (DeepSeek-R1 reasoning layer)
    strategist = Agent(
        role='CIO / Chief Strategist',
        goal='Synthesize data into a final "Asymmetric Moonshot" recommendation.',
        backstory='Hedge fund manager. Your job is to find the ONE play with the best risk/reward.',
        llm=llm_reasoner,
        verbose=True
    )

    # --- 3. TASK ORCHESTRATION ---
    t1 = Task(description=f"Map the {user_query} supply chain. Find 3 obscure publicly traded tickers.", agent=scraper)
    t2 = Task(description="For those 3 tickers, find their current price and analyst targets. Calculate upside.", agent=quant)
    t3 = Task(description="Write a final institutional memo. Strictly end with 'TICKERS: T1, T2, T3'.", agent=strategist)

    return Crew(agents=[scraper, quant, strategist], tasks=[t1, t2, t3], process=Process.sequential)

# --- 4. STREAMLIT UI ---
st.set_page_config(page_title="Alpha Orchestrator v7", layout="wide")
st.title("🏦 ALPHA ORCHESTRATOR")

query = st.text_input("ENTER SECTOR OR $TICKER:", placeholder="e.g. 'Solid State Batteries' or '$SMR'")

if st.button("KICKOFF AGENTS"):
    with st.status("🤖 Agents are collaborating (DeepSeek Reasoning)...") as status:
        crew = get_research_crew(query)
        final_memo = crew.kickoff()
        status.update(label="Research Complete!", state="complete")
    
    st.markdown("### 📋 INSTITUTIONAL MEMO")
    st.write(final_memo)

    # --- 5. AUTOMATED TABLE CRUNCH ---
    try:
        match = re.search(r'TICKERS:?\s*([\w\s,]+)', str(final_memo), re.IGNORECASE)
        if match:
            tickers = [t.strip().upper() for t in match.group(1).split(',')]
            st.subheader("📊 ANALYST CRUNCH")
            data = []
            for t in tickers:
                s = yf.Ticker(t)
                info = s.info
                data.append({
                    "TICKER": t,
                    "UPSIDE": f"{((info.get('targetMedianPrice',0)/info.get('currentPrice',1))-1)*100:+.2f}%",
                    "PE (FWD)": info.get('forwardPE', 'N/A'),
                    "RATING": info.get('recommendationKey', 'N/A').upper()
                })
            st.table(pd.DataFrame(data))
    except:
        st.info("Crunching numbers manually... Done.")
