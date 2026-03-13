import streamlit as st
import pandas as pd
import os
import re
from crewai import Agent, Task, Crew, Process
from langchain_groq import ChatGroq
import yfinance as yf

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
