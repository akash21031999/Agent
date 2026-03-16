"""
Conviction Pro — Institutional Supply Chain Intelligence Terminal
v2 — with Perplexity two-call architecture, 8 conviction layers,
SVG radar, professional financial design, watchlist mode.

Architecture:
  Call 1 — RESEARCHER  (gathers raw evidence packets per layer)
  Call 2 — SYNTHESISER (reads evidence as validated facts, writes thesis)
  Pattern from: Perplexity system prompt — separation of search & synthesis

8 Conviction Layers (all independent, all free APIs):
  L1  Supply Chain Position   — Gemini + Google Search grounding
  L2  Quantitative Signals    — Yahoo Finance + numpy stacking
  L3  Options Dark Money      — Vol/OI ratio + P/C + IV skew
  L4  Insider Cluster         — EDGAR Form 4 + Finnhub open-market buys
  L5  Cross-Chain Frequency   — Session memory: how many independent chains
  L6  Volume / Squeeze Proxy  — Volume surge + price momentum confluence
  L7  Catalyst Proximity      — EDGAR 8-K + USASpending DoD contracts
  L8  News Velocity           — Acceleration of news coverage (Google News RSS)
"""

import streamlit as st
st.set_page_config(
    page_title="Conviction Pro",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

import requests, feedparser, json, re, time, threading, math
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from google import genai
from google.genai import types

# ══════════════════════════════════════════════════════════════════════════════
#  PROFESSIONAL DESIGN SYSTEM
#  Inspired by: Goldman Sachs web terminal, Koyfin, Visible Alpha
#  Principle: data density > decoration. Every pixel earns its place.
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ── RESET ──────────────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; font-style: normal !important; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > section,
[data-testid="stAppViewContainer"] > section > div,
.main, .main > div {
    background-color: #f8f9fb !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: #0a0f1e !important;
    font-size: 14px;
}
[data-testid="stSidebar"], [data-testid="stSidebar"] > div {
    background: #ffffff !important;
    border-right: 1px solid #e4e6ea !important;
}
[data-testid="stSidebar"] * { color: #3d4451 !important; font-style: normal !important; }
[data-testid="stSidebar"] strong, [data-testid="stSidebar"] b { color: #0a0f1e !important; font-weight: 600 !important; }
.block-container { padding: 0 2rem 4rem !important; max-width: 1500px !important; }
em, i { font-style: normal !important; }
strong, b { font-weight: 600 !important; color: #0a0f1e !important; }
a { color: #1a56e8 !important; text-decoration: none !important; }

/* ── TOPBAR ─────────────────────────────────────────────────────────────── */
.cp-topbar {
    display: flex;
    align-items: center;
    padding: 14px 0 12px;
    border-bottom: 2px solid #0a0f1e;
    margin-bottom: 0;
    gap: 24px;
}
.cp-wordmark {
    font-size: 1.05rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: #0a0f1e !important;
    text-transform: uppercase;
    line-height: 1;
}
.cp-wordmark .red { color: #c5221f !important; }
.cp-divider { width: 1px; height: 20px; background: #d0d5dd; flex-shrink: 0; }
.cp-tagline { font-size: 0.68rem; font-weight: 500; color: #6b7280 !important; letter-spacing: 1.2px; text-transform: uppercase; }
.cp-status-row { display: flex; gap: 6px; margin-left: auto; }
.cp-badge {
    font-size: 0.68rem; font-weight: 600; padding: 3px 9px;
    border-radius: 3px; letter-spacing: 0.3px; white-space: nowrap;
}
.badge-live  { background: #e8f5e9; color: #2e7d32 !important; border: 1px solid #a5d6a7; }
.badge-score { background: #fff3e0; color: #e65100 !important; border: 1px solid #ffcc80; }
.badge-gray  { background: #f3f4f6; color: #6b7280 !important; border: 1px solid #e5e7eb; }

/* ── MACRO RIBBON ────────────────────────────────────────────────────────── */
.macro-ribbon {
    display: flex;
    background: #0a0f1e;
    padding: 7px 0;
    margin: 0 -2rem 20px;
    overflow-x: auto;
    gap: 0;
    scrollbar-width: none;
}
.macro-ribbon::-webkit-scrollbar { display: none; }
.mitem {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 0 16px;
    border-right: 1px solid #1e2535;
    flex-shrink: 0;
}
.mitem:last-child { border-right: none; }
.mticker { font-size: 0.65rem; font-weight: 600; color: #6b7280 !important; letter-spacing: 1.2px; text-transform: uppercase; }
.mprice  { font-size: 0.82rem; font-weight: 600; color: #e8eaed !important; font-family: 'JetBrains Mono', monospace; }
.mup  { font-size: 0.68rem; color: #34d399 !important; font-weight: 500; font-family: 'JetBrains Mono', monospace; }
.mdn  { font-size: 0.68rem; color: #f87171 !important; font-weight: 500; font-family: 'JetBrains Mono', monospace; }
.mfl  { font-size: 0.68rem; color: #6b7280 !important; font-family: 'JetBrains Mono', monospace; }

/* ── SEARCH INPUT ─────────────────────────────────────────────────────────── */
.search-panel {
    background: #ffffff;
    border: 1px solid #e4e6ea;
    border-top: 3px solid #0a0f1e;
    border-radius: 0 0 8px 8px;
    padding: 20px 24px 18px;
    margin-bottom: 20px;
}
.search-label {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #9ca3af !important;
    margin-bottom: 10px;
    display: block;
}
.search-hint { font-size: 0.72rem; color: #9ca3af !important; margin-top: 8px; line-height: 1.6; }
.search-hint b { color: #374151 !important; font-weight: 600 !important; }

/* ── SECTION HEADER ─────────────────────────────────────────────────────── */
.sec-hdr {
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #9ca3af !important;
    border-bottom: 1px solid #e4e6ea;
    padding-bottom: 7px;
    margin: 22px 0 14px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.sec-hdr-line { flex: 1; height: 1px; background: #e4e6ea; }

/* ── CONVICTION CARD ─────────────────────────────────────────────────────── */
.cv-card {
    background: #ffffff;
    border: 1px solid #e4e6ea;
    border-radius: 8px;
    padding: 0;
    margin: 10px 0;
    overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    transition: box-shadow 0.15s, border-color 0.15s;
}
.cv-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.1); border-color: #c0c7d4; }

.cv-top-stripe { height: 4px; width: 100%; }
.stripe-ultra { background: linear-gradient(90deg, #c5221f 0%, #ea580c 100%); }
.stripe-high  { background: linear-gradient(90deg, #b45309 0%, #d97706 100%); }
.stripe-med   { background: linear-gradient(90deg, #1a56e8 0%, #3b82f6 100%); }
.stripe-low   { background: #d0d5dd; }

.cv-body { padding: 18px 22px 16px; }

.cv-row1 { display: flex; align-items: flex-start; gap: 16px; margin-bottom: 14px; flex-wrap: wrap; }
.cv-ticker-block { flex: 1; min-width: 120px; }
.cv-ticker { font-size: 1.6rem; font-weight: 800; color: #0a0f1e !important; font-family: 'JetBrains Mono', monospace; line-height: 1; margin-bottom: 4px; letter-spacing: -0.5px; }
.cv-company { font-size: 0.78rem; color: #6b7280 !important; font-weight: 400; }
.cv-price-block { text-align: right; }
.cv-price { font-size: 1.2rem; font-weight: 700; color: #0a0f1e !important; font-family: 'JetBrains Mono', monospace; }
.cv-chg-up { color: #16a34a !important; font-size: 0.78rem; font-weight: 600; }
.cv-chg-dn { color: #dc2626 !important; font-size: 0.78rem; font-weight: 600; }
.cv-score-block { text-align: center; padding: 0 8px; border-left: 1px solid #e4e6ea; }
.cv-score-num { font-size: 2.4rem; font-weight: 800; font-family: 'JetBrains Mono', monospace; line-height: 1; }
.cv-score-num.ultra { color: #c5221f !important; }
.cv-score-num.high  { color: #b45309 !important; }
.cv-score-num.med   { color: #1a56e8 !important; }
.cv-score-num.low   { color: #9ca3af !important; }
.cv-score-denom { font-size: 0.62rem; color: #9ca3af !important; letter-spacing: 1px; text-transform: uppercase; }

.cv-verdict-row { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }
.cv-verdict {
    font-size: 0.7rem; font-weight: 700; letter-spacing: 0.8px;
    padding: 3px 10px; border-radius: 3px; text-transform: uppercase;
}
.verdict-ultra { background: #fee2e2; color: #991b1b !important; }
.verdict-high  { background: #fef3c7; color: #92400e !important; }
.verdict-med   { background: #dbeafe; color: #1e3a8a !important; }
.verdict-low   { background: #f3f4f6; color: #6b7280 !important; }
.cv-chain-tag { font-size: 0.68rem; color: #9ca3af !important; }
.cv-layer-count { font-size: 0.68rem; color: #6b7280 !important; margin-left: auto; font-family: 'JetBrains Mono', monospace; }

/* ── CONVICTION BAR ──────────────────────────────────────────────────────── */
.cv-bar-track { background: #f3f4f6; border-radius: 2px; height: 6px; margin-bottom: 14px; overflow: hidden; }
.cv-bar-fill { height: 100%; border-radius: 2px; }
.fill-ultra { background: linear-gradient(90deg, #c5221f, #ea580c); }
.fill-high  { background: linear-gradient(90deg, #b45309, #d97706); }
.fill-med   { background: linear-gradient(90deg, #1a56e8, #3b82f6); }
.fill-low   { background: #d0d5dd; }

/* ── LEVELS STRIP ─────────────────────────────────────────────────────────── */
.cv-levels {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 1px;
    background: #e4e6ea;
    border: 1px solid #e4e6ea;
    border-radius: 6px;
    overflow: hidden;
    margin-bottom: 14px;
}
.cv-level {
    background: #ffffff;
    padding: 9px 12px;
    text-align: center;
}
.lv-lbl { font-size: 0.56rem; font-weight: 700; letter-spacing: 1.2px; text-transform: uppercase; color: #9ca3af !important; display: block; margin-bottom: 4px; }
.lv-val { font-size: 0.92rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; display: block; }
.lv-entry  { color: #1a56e8 !important; }
.lv-target { color: #15803d !important; }
.lv-stop   { color: #c5221f !important; }
.lv-up     { color: #15803d !important; }
.lv-dn     { color: #c5221f !important; }
.lv-rr     { color: #0a0f1e !important; }

/* ── LAYER EVIDENCE GRID ─────────────────────────────────────────────────── */
.ev-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 8px; margin-bottom: 4px; }
.ev-cell {
    border-radius: 6px;
    padding: 10px 12px;
    border: 1px solid;
    position: relative;
}
.ev-cell.confirmed { background: #f0fdf4; border-color: #86efac; }
.ev-cell.partial   { background: #fffbeb; border-color: #fde68a; }
.ev-cell.absent    { background: #f9fafb; border-color: #e4e6ea; opacity: 0.65; }

.ev-layer-id { font-size: 0.58rem; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: #9ca3af !important; margin-bottom: 2px; display: block; }
.ev-name { font-size: 0.78rem; font-weight: 700; color: #0a0f1e !important; margin-bottom: 4px; }
.ev-detail { font-size: 0.71rem; color: #4b5563 !important; line-height: 1.45; }
.ev-pts {
    position: absolute; top: 8px; right: 10px;
    font-size: 0.68rem; font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
}
.ev-pts.confirmed { color: #15803d !important; }
.ev-pts.partial   { color: #b45309 !important; }
.ev-pts.absent    { color: #d0d5dd !important; }
.ev-icon { font-size: 0.95rem; margin-bottom: 3px; display: block; }

/* ── EVIDENCE PACKET (Perplexity style) ─────────────────────────────────── */
.ep-block {
    background: #ffffff;
    border: 1px solid #e4e6ea;
    border-left: 3px solid #1a56e8;
    border-radius: 0 6px 6px 0;
    padding: 12px 16px;
    margin: 6px 0;
}
.ep-block.ep-high   { border-left-color: #c5221f; }
.ep-block.ep-medium { border-left-color: #d97706; }
.ep-block.ep-low    { border-left-color: #9ca3af; }
.ep-source { font-size: 0.62rem; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: #9ca3af !important; margin-bottom: 4px; display: block; }
.ep-finding { font-size: 0.83rem; color: #1f2937 !important; line-height: 1.55; }
.ep-conf { font-size: 0.65rem; color: #6b7280 !important; margin-top: 5px; display: block; }

/* ── CROSS-CHAIN BADGE ───────────────────────────────────────────────────── */
.xc-badge {
    display: inline-flex; align-items: center; gap: 5px;
    background: #fff7ed; border: 1px solid #fed7aa;
    border-radius: 3px; padding: 3px 9px;
    font-size: 0.7rem; font-weight: 600; color: #9a3412 !important; margin: 3px 3px 3px 0;
}

/* ── MULTI-CHAIN CARD ────────────────────────────────────────────────────── */
.mc-card {
    background: #ffffff;
    border: 1px solid #e4e6ea;
    border-left: 4px solid #b45309;
    border-radius: 0 8px 8px 0;
    padding: 14px 18px;
    margin: 8px 0;
}
.mc-ticker { font-size: 1.05rem; font-weight: 800; color: #0a0f1e !important; font-family: 'JetBrains Mono', monospace; }
.mc-count { font-size: 0.72rem; font-weight: 700; color: #b45309 !important; margin-left: 10px; }

/* ── THESIS BLOCK ────────────────────────────────────────────────────────── */
.thesis-block {
    background: #ffffff;
    border: 1px solid #e4e6ea;
    border-radius: 8px;
    padding: 24px 28px;
    margin: 12px 0;
    overflow-x: hidden;
}
.thesis-block h2 { color: #0a0f1e !important; font-weight: 700 !important; font-size: 0.95rem !important; margin: 18px 0 6px !important; padding-bottom: 4px !important; border-bottom: 1px solid #f3f4f6 !important; }
.thesis-block h3 { color: #1a56e8 !important; font-weight: 700 !important; font-size: 0.85rem !important; margin: 14px 0 4px !important; }
.thesis-block p  { color: #374151 !important; line-height: 1.75 !important; font-size: 0.88rem !important; margin: 6px 0 !important; }
.thesis-block li { color: #374151 !important; line-height: 1.65 !important; font-size: 0.88rem !important; margin: 3px 0 !important; }
.thesis-block strong { color: #0a0f1e !important; font-weight: 700 !important; }
.thesis-block code { background: #f3f4f6 !important; color: #1f2937 !important; padding: 1px 5px !important; border-radius: 3px !important; font-family: 'JetBrains Mono', monospace !important; font-size: 0.82em !important; }
.thesis-block table { display: block !important; overflow-x: auto !important; border-collapse: collapse !important; width: 100% !important; font-size: 0.83rem !important; }
.thesis-block th { background: #f8f9fb !important; color: #0a0f1e !important; padding: 7px 11px !important; border: 1px solid #e4e6ea !important; font-weight: 600 !important; }
.thesis-block td { padding: 6px 11px !important; border: 1px solid #e4e6ea !important; color: #374151 !important; }
.thesis-block tr:nth-child(even) td { background: #fafafa !important; }

/* ── WATCHLIST ITEM ─────────────────────────────────────────────────────── */
.wl-row {
    display: flex; align-items: center; gap: 12px;
    padding: 10px 16px; background: #ffffff;
    border: 1px solid #e4e6ea; border-radius: 6px; margin: 4px 0;
}
.wl-ticker { font-size: 0.9rem; font-weight: 700; color: #0a0f1e !important; font-family: 'JetBrains Mono', monospace; min-width: 70px; }
.wl-score-pill {
    font-size: 0.7rem; font-weight: 700; padding: 2px 8px; border-radius: 3px;
    font-family: 'JetBrains Mono', monospace;
}

/* ── INPUTS / BUTTONS ────────────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #ffffff !important;
    border: 1.5px solid #d0d5dd !important;
    border-radius: 6px !important;
    color: #0a0f1e !important;
    font-size: 0.9rem !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #0a0f1e !important;
    box-shadow: 0 0 0 3px rgba(10,15,30,0.08) !important;
    outline: none !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    background: #ffffff !important;
    border: 1.5px solid #d0d5dd !important;
    border-radius: 6px !important;
}
div.stButton > button {
    border-radius: 6px !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.3px !important;
    padding: 7px 18px !important;
    transition: all 0.12s !important;
}
div.stButton > button[kind="primary"] {
    background: #0a0f1e !important;
    border: 1px solid #0a0f1e !important;
    color: #ffffff !important;
}
div.stButton > button[kind="primary"]:hover {
    background: #1e293b !important;
    border-color: #1e293b !important;
    box-shadow: 0 2px 8px rgba(10,15,30,0.3) !important;
}
div.stButton > button[kind="secondary"] {
    background: #ffffff !important;
    border: 1.5px solid #d0d5dd !important;
    color: #374151 !important;
}
div.stButton > button[kind="secondary"]:hover {
    border-color: #0a0f1e !important;
    color: #0a0f1e !important;
}

/* ── STREAMLIT COMPONENTS ────────────────────────────────────────────────── */
[data-testid="stDataFrame"] { border: 1px solid #e4e6ea !important; border-radius: 6px !important; overflow: hidden !important; }
[data-testid="metric-container"] { background: #ffffff !important; border: 1px solid #e4e6ea !important; border-radius: 6px !important; padding: 12px !important; }
[data-testid="stMetricValue"] { color: #0a0f1e !important; font-weight: 700 !important; font-family: 'JetBrains Mono', monospace !important; }
[data-testid="stMetricLabel"] { color: #6b7280 !important; font-size: 0.72rem !important; font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 1px !important; }
details[data-testid="stExpander"] { border: 1px solid #e4e6ea !important; border-radius: 6px !important; background: #ffffff !important; }
[data-testid="stStatusWidget"] { border-radius: 6px !important; }
div[data-testid="stInfo"], div[data-testid="stWarning"] { border-radius: 6px !important; font-size: 0.85rem !important; }

/* ── TABS ─────────────────────────────────────────────────────────────────── */
[data-testid="stTabs"] [role="tablist"] { border-bottom: 2px solid #e4e6ea !important; gap: 0; }
[data-testid="stTabs"] button {
    font-size: 0.78rem !important; font-weight: 500 !important;
    color: #6b7280 !important; padding: 10px 20px !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important; background: transparent !important;
    margin-bottom: -2px !important; letter-spacing: 0.2px !important;
}
[data-testid="stTabs"] button:hover { color: #374151 !important; }
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #0a0f1e !important; font-weight: 700 !important;
    border-bottom: 2px solid #0a0f1e !important;
}

/* ── MARKDOWN ────────────────────────────────────────────────────────────── */
div[data-testid="stMarkdownContainer"] * { font-style: normal !important; }
div[data-testid="stMarkdownContainer"] em { font-style: normal !important; color: #374151 !important; }
div[data-testid="stMarkdownContainer"] p  { color: #374151 !important; line-height: 1.75 !important; font-size: 0.88rem !important; margin: 5px 0 !important; }
div[data-testid="stMarkdownContainer"] li { color: #374151 !important; line-height: 1.65 !important; font-size: 0.88rem !important; }
div[data-testid="stMarkdownContainer"] strong { color: #0a0f1e !important; font-weight: 700 !important; }
div[data-testid="stMarkdownContainer"] h2 { color: #0a0f1e !important; font-weight: 700 !important; font-size: 0.95rem !important; border-bottom: 1px solid #f3f4f6 !important; padding-bottom: 4px !important; margin: 16px 0 6px !important; }
div[data-testid="stMarkdownContainer"] h3 { color: #1a56e8 !important; font-weight: 700 !important; font-size: 0.85rem !important; margin: 12px 0 4px !important; }
div[data-testid="stMarkdownContainer"] code { background: #f3f4f6 !important; color: #1f2937 !important; padding: 1px 5px !important; border-radius: 3px !important; font-family: 'JetBrains Mono', monospace !important; font-size: 0.83em !important; }
div[data-testid="stMarkdownContainer"] table { display: block !important; overflow-x: auto !important; border-collapse: collapse !important; width: 100% !important; font-size: 0.85rem !important; margin: 10px 0 !important; }
div[data-testid="stMarkdownContainer"] th { background: #f3f4f6 !important; color: #0a0f1e !important; padding: 7px 11px !important; border: 1px solid #e4e6ea !important; font-weight: 600 !important; }
div[data-testid="stMarkdownContainer"] td { padding: 6px 11px !important; border: 1px solid #e4e6ea !important; color: #374151 !important; }
div[data-testid="stMarkdownContainer"] tr:nth-child(even) td { background: #f9fafb !important; }
div[data-testid="stMarkdownContainer"] ul, div[data-testid="stMarkdownContainer"] ol { padding-left: 20px !important; margin: 8px 0 !important; }
div[data-testid="stMarkdownContainer"] hr { border: none !important; border-top: 1px solid #e4e6ea !important; margin: 14px 0 !important; }

/* ── DIVIDER ─────────────────────────────────────────────────────────────── */
hr { border: none !important; border-top: 1px solid #e4e6ea !important; }
[data-testid="stDivider"] { border-color: #e4e6ea !important; }

/* ── SCROLLBARS ─────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #d0d5dd; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #9ca3af; }

/* ── MOBILE ─────────────────────────────────────────────────────────────── */
@media (max-width: 768px) {
    .block-container { padding: 0 0.8rem 2rem !important; }
    .ev-grid { grid-template-columns: 1fr 1fr; }
    .cv-levels { grid-template-columns: repeat(3, 1fr); }
    .cv-score-num { font-size: 1.8rem; }
    .macro-ribbon { margin: 0 -0.8rem 16px; }
    .cp-status-row { display: none; }
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
for k, v in [
    ("chain_memory", {}),
    ("conviction_results", []),
    ("last_chain_map", ""),
    ("watchlist", "NVDA,PLTR,RKLB,IONQ,AXTI,CELH,MELI,TSM,ASML,NVO"),
    ("scan_history", []),
]:
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("**◈ Conviction Pro**")
    st.divider()
    gemini_key  = st.text_input("Gemini API Key", type="password", placeholder="AIza...", key="si_gemini",
                                help="Free at aistudio.google.com/app/apikey")
    finnhub_key = st.text_input("Finnhub (optional)", type="password", placeholder="Enhances insider data", key="si_finnhub")
    tg_token    = st.text_input("Telegram Token", type="password", placeholder="optional", key="si_tg")
    tg_chat     = st.text_input("Telegram Chat ID", placeholder="optional", key="si_tgchat")

    st.divider()
    st.markdown("**Conviction Thresholds**")
    ultra_thresh = st.slider("Ultra conviction ≥", 7.0, 9.5, 8.0, 0.5, key="sl_ultra")
    high_thresh  = st.slider("High conviction ≥",  4.0, 7.5, 6.0, 0.5, key="sl_high")
    min_layers   = st.slider("Min confirmed layers", 1, 8, 2, 1, key="sl_minlayers")

    st.divider()
    st.markdown("**Database**")
    n_tickers = len(st.session_state.get("chain_memory", {}))
    n_results = len(st.session_state.get("conviction_results", []))
    n_apps = sum(len(v) for v in st.session_state.get("chain_memory", {}).values())
    st.markdown(f'<div style="font-size:0.78rem;color:#374151;line-height:1.8">'
                f'{n_results} conviction scores<br>{n_tickers} tickers in memory<br>{n_apps} chain appearances</div>',
                unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Clear results", key="btn_clr_r", use_container_width=True):
            st.session_state["conviction_results"] = []
            st.rerun()
    with c2:
        if st.button("Clear memory", key="btn_clr_m", use_container_width=True):
            st.session_state["chain_memory"] = {}
            st.rerun()

    st.divider()
    if gemini_key:
        st.markdown('<span style="font-size:0.78rem;color:#16a34a">● Gemini ready</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span style="font-size:0.78rem;color:#dc2626">● No API key</span>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  DATA LAYER
# ══════════════════════════════════════════════════════════════════════════════
YF = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      "Accept": "application/json"}

@st.cache_data(ttl=180, show_spinner=False)
def yf_price(sym):
    try:
        r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range=5d",
                         headers=YF, timeout=6)
        c = [x for x in r.json()["chart"]["result"][0]["indicators"]["quote"][0]["close"] if x]
        return (round(c[-1],2), round((c[-1]/c[-2]-1)*100,2)) if len(c)>=2 else (None,None)
    except: return None, None

@st.cache_data(ttl=300, show_spinner=False)
def yf_history(sym, rng="6mo"):
    try:
        r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range={rng}",
                         headers=YF, timeout=8)
        d  = r.json()["chart"]["result"][0]
        closes = [c for c in d["indicators"]["quote"][0]["close"]  if c is not None]
        vols   = [v for v in d["indicators"]["quote"][0].get("volume",[]) if v is not None]
        return closes, vols, d.get("meta",{})
    except: return [], [], {}

@st.cache_data(ttl=600, show_spinner=False)
def yf_options_flow(sym):
    try:
        r = requests.get(f"https://query1.finance.yahoo.com/v7/finance/options/{sym}",
                         headers=YF, timeout=8)
        root = r.json().get("optionChain",{}).get("result",[])
        if not root: return {}
        cv=pv=co=po=0; otm_c_iv=[]; otm_p_iv=[]
        price,_ = yf_price(sym)
        for block in root[:3]:
            for ob in block.get("options",[]):
                for c in ob.get("calls",[]):
                    cv+=c.get("volume") or 0; co+=c.get("openInterest") or 0
                    if price and c.get("strike",0)>price*1.05:
                        otm_c_iv.append(float(c.get("impliedVolatility") or 0)*100)
                for p in ob.get("puts",[]):
                    pv+=p.get("volume") or 0; po+=p.get("openInterest") or 0
                    if price and p.get("strike",0)<price*0.95:
                        otm_p_iv.append(float(p.get("impliedVolatility") or 0)*100)
        total_vol=cv+pv; total_oi=co+po
        iv_skew=round(float(np.mean(otm_p_iv)-np.mean(otm_c_iv)),1) if otm_c_iv and otm_p_iv else 0
        return {"call_vol":cv,"put_vol":pv,"call_oi":co,"put_oi":po,
                "total_vol":total_vol,"total_oi":total_oi,
                "vol_oi":round(total_vol/max(total_oi,1),3),
                "pc_vol":round(pv/max(cv,1),3),"iv_skew":iv_skew}
    except: return {}

@st.cache_data(ttl=600, show_spinner=False)
def edgar_form4(ticker):
    try:
        start=(datetime.now()-timedelta(days=45)).strftime("%Y-%m-%d")
        r=requests.get(
            f"https://efts.sec.gov/LATEST/search-index?q=%22{ticker}%22&dateRange=custom&startdt={start}&forms=4",
            headers={"User-Agent":"ConvictionPro research@conviction.ai"},timeout=10)
        hits=r.json().get("hits",{}).get("hits",[])
        filings=[{"filed":h["_source"].get("file_date",""),"company":h["_source"].get("entity_name","")} for h in hits[:10]]
        return {"filings":filings,"count":len(filings),"unique_dates":len(set(f["filed"] for f in filings))}
    except: return {"filings":[],"count":0,"unique_dates":0}

@st.cache_data(ttl=600, show_spinner=False)
def finnhub_insider_buys(sym, key):
    if not key: return {"buys":0,"sells":0,"net_val":0,"names":[]}
    try:
        r=requests.get(f"https://finnhub.io/api/v1/stock/insider-transactions?symbol={sym}&token={key}",timeout=6)
        data=r.json().get("data",[])
        cutoff=(datetime.now()-timedelta(days=45)).strftime("%Y-%m-%d")
        buys=[t for t in data if str(t.get("transactionType","")).upper() in ["P","BUY","PURCHASE"] and str(t.get("transactionDate",""))>=cutoff]
        sells=[t for t in data if str(t.get("transactionType","")).upper() in ["S","SALE","SELL"] and str(t.get("transactionDate",""))>=cutoff]
        net_val=sum(abs(float(b.get("transactionPrice",0) or 0)*abs(float(b.get("share",0) or 0))) for b in buys)
        return {"buys":len(buys),"sells":len(sells),"net_val":round(net_val/1000,1),"names":[b.get("name","")[:20] for b in buys[:4]]}
    except: return {"buys":0,"sells":0,"net_val":0,"names":[]}

@st.cache_data(ttl=1800, show_spinner=False)
def edgar_8k(ticker):
    try:
        start=(datetime.now()-timedelta(days=30)).strftime("%Y-%m-%d")
        r=requests.get(
            f"https://efts.sec.gov/LATEST/search-index?q=%22{ticker}%22&dateRange=custom&startdt={start}&forms=8-K",
            headers={"User-Agent":"ConvictionPro research@conviction.ai"},timeout=10)
        hits=r.json().get("hits",{}).get("hits",[])[:5]
        return [{"filed":h["_source"].get("file_date",""),"desc":h["_source"].get("period_of_report","")} for h in hits]
    except: return []

@st.cache_data(ttl=1800, show_spinner=False)
def usaspending_contracts(company_name):
    try:
        end=datetime.now().strftime("%Y-%m-%d")
        start=(datetime.now()-timedelta(days=30)).strftime("%Y-%m-%d")
        payload={"filters":{"time_period":[{"start_date":start,"end_date":end}],
            "agencies":[{"type":"awarding_agency","tier":"toptier","name":"Department of Defense"}],
            "award_type_codes":["A","B","C","D"],
            "recipient_search_text":[company_name[:30]]},
            "fields":["recipient_name","total_obligated_amount","action_date","award_description"],
            "sort":"total_obligated_amount","order":"desc","limit":3,"page":1}
        r=requests.post("https://api.usaspending.gov/api/v2/search/spending_by_award/",
                        json=payload,timeout=12,headers={"Content-Type":"application/json"})
        results=r.json().get("results",[])
        return [{"amount_m":round(float(x.get("total_obligated_amount",0))/1e6,1),
                 "date":x.get("action_date",""),"desc":x.get("award_description","")[:80]} for x in results]
    except: return []

@st.cache_data(ttl=600, show_spinner=False)
def news_velocity(ticker):
    """
    News velocity = number of articles mentioning ticker in last 48h vs 7d average.
    High velocity (recent spike) = catalyst forming or news cycle accelerating.
    Returns (recent_count, avg_daily, velocity_ratio, headlines)
    """
    try:
        url = f"https://news.google.com/rss/search?q={requests.utils.quote(ticker+' stock')}&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(url)
        entries = feed.entries[:20]
        cutoff_48h = datetime.now() - timedelta(hours=48)
        cutoff_7d  = datetime.now() - timedelta(days=7)
        recent = []; week = []
        for e in entries:
            try:
                import email.utils
                dt = datetime(*email.utils.parsedate(e.published)[:6])
                if dt > cutoff_48h: recent.append(e.title)
                if dt > cutoff_7d:  week.append(e.title)
            except: week.append(e.title)
        avg_daily = len(week) / 7
        velocity  = round(len(recent) / max(avg_daily * 2, 1), 2)
        headlines = [e.title for e in entries[:4]]
        return len(recent), round(avg_daily, 1), velocity, headlines
    except: return 0, 0, 0, []

@st.cache_data(ttl=300, show_spinner=False)
def get_macro():
    syms={"SPX":"%5EGSPC","VIX":"%5EVIX","10Y":"%5ETNX","DXY":"DX-Y.NYB","Gold":"GC%3DF","Oil":"CL%3DF"}
    out={lbl:yf_price(sym) for lbl,sym in syms.items()}
    try:
        r=requests.get("https://api.coingecko.com/api/v3/simple/price",
            params={"ids":"bitcoin","vs_currencies":"usd","include_24hr_change":"true"},
            timeout=5,headers={"User-Agent":"CP/2.0"})
        d=r.json()["bitcoin"]; out["BTC"]=(round(d["usd"],0),round(d["usd_24h_change"],2))
    except: out["BTC"]=(None,None)
    return out

# ══════════════════════════════════════════════════════════════════════════════
#  QUANTITATIVE ENGINE
# ══════════════════════════════════════════════════════════════════════════════
def calc_rsi(c,n=14):
    if len(c)<n+1: return 50.0
    a=np.array(c,dtype=float); d=np.diff(a)
    g=np.where(d>0,d,0.); l=np.where(d<0,-d,0.)
    return round(float(100-100/(1+np.mean(g[-n:])/(np.mean(l[-n:])+1e-9))),1)

def calc_macd(c):
    if len(c)<35: return None,None,None
    s=pd.Series(c,dtype=float)
    m=s.ewm(span=12,adjust=False).mean()-s.ewm(span=26,adjust=False).mean()
    sig=m.ewm(span=9,adjust=False).mean()
    return round(float(m.iloc[-1]),3),round(float(sig.iloc[-1]),3),round(float((m-sig).iloc[-1]),4)

def calc_bb(c,n=20):
    if len(c)<n: return None,None,None
    a=np.array(c[-n:],dtype=float)
    return round(float(np.mean(a)+2*np.std(a)),2),round(float(np.mean(a)),2),round(float(np.mean(a)-2*np.std(a)),2)

def vol_ratio(vols,n=20):
    if len(vols)<n+1 or not vols[-1]: return None
    return round(vols[-1]/max(float(np.mean(vols[-n-1:-1])),1),2)

def short_ratio_proxy(closes,vols,n=5):
    if len(closes)<n+1 or len(vols)<n+1: return 0.0
    price_up  = closes[-1]>closes[-n]
    vol_spike = vols[-1]>float(np.mean(vols[-n-1:-1]))*1.8 if float(np.mean(vols[-n-1:-1]))>0 else False
    return 1.0 if (price_up and vol_spike) else 0.5 if vol_spike else 0.0

def calc_momentum(c,periods=(5,10,21)):
    out={}
    for p in periods:
        if len(c)>p: out[p]=round((c[-1]/c[-p-1]-1)*100,2)
    return out

def score_quant_layer(closes,vols,meta,price):
    if not closes or not price: return 0,{}
    rsi=calc_rsi(closes); ml,ms,mh=calc_macd(closes); bu,bm,bl=calc_bb(closes)
    vr=vol_ratio(vols); w52h=meta.get("fiftyTwoWeekHigh",0) or 0; w52l=meta.get("fiftyTwoWeekLow",0) or 0
    mom=calc_momentum(closes); ma50=float(np.mean(closes[-50:])) if len(closes)>=50 else None
    squeeze=short_ratio_proxy(closes,vols)
    bullish=0; sigs={"rsi":rsi,"macd_hist":mh,"vol_ratio":vr,"w52pct":0,"ma50_above":None,"squeeze":squeeze}
    if rsi<35: bullish+=1
    elif rsi<45: bullish+=0.5
    if mh and mh>0: bullish+=1
    if w52h and w52l:
        pct=(price-w52l)/max(w52h-w52l,0.01); sigs["w52pct"]=round(pct*100,1)
        if pct<0.25: bullish+=1
    if ma50 and price>ma50: sigs["ma50_above"]=True; bullish+=0.5
    elif ma50: sigs["ma50_above"]=False
    if vr and vr>2.0: bullish+=1
    if squeeze>0.5: bullish+=0.5
    sigs["bullish_count"]=bullish
    return min(2.0,round(bullish*0.4,1)), sigs

# ══════════════════════════════════════════════════════════════════════════════
#  8-LAYER CONVICTION ENGINE
# ══════════════════════════════════════════════════════════════════════════════
def score_conviction(ticker, chain_source, f_key=""):
    """Run all 8 layers. Returns complete conviction dict."""
    result = {
        "ticker":ticker,"chain_source":chain_source,
        "ts":datetime.now().isoformat(),"layers":{},
        "score":0.0,"verdict":"","grade":"",
        "price":None,"chg":None,
        "entry":None,"target":None,"stop":None,
        "upside":None,"downside":None,"rr":None,
        "evidence_packets":[]
    }
    price,chg = yf_price(ticker)
    closes,vols,meta = yf_history(ticker,"6mo")
    result["price"]=price; result["chg"]=chg

    # L1 — Supply Chain Position
    l1_pts=1.0
    result["layers"]["L1_supply_chain"]={"name":"Supply Chain","icon":"⛓","pts":l1_pts,
        "status":"confirmed","detail":f"Named in: {chain_source}"}
    result["evidence_packets"].append({"source":"Supply Chain Map","finding":f"Identified in {chain_source} — requires further analysis","confidence":"MEDIUM"})

    # L2 — Quantitative Signals
    if closes and price:
        l2_pts,qs=score_quant_layer(closes,vols,meta,price)
        rsi=qs.get("rsi",50); vr=qs.get("vol_ratio"); mh=qs.get("macd_hist")
        detail=f"RSI {rsi} · MACD hist {mh} · Vol {vr}× · 52W pos {qs.get('w52pct',0):.0f}%"
        status="confirmed" if l2_pts>=1.0 else "partial" if l2_pts>0 else "absent"
        result["layers"]["L2_quant"]={"name":"Technicals","icon":"📊","pts":l2_pts,"status":status,"detail":detail,"raw":qs}
        result["evidence_packets"].append({"source":"Yahoo Finance / numpy","finding":detail,"confidence":"HIGH" if l2_pts>=1.5 else "MEDIUM"})
        # Levels
        adr=round(float(np.mean([abs(closes[i]-closes[i-1]) for i in range(1,min(14,len(closes)))])),2)
        result["entry"]=round(price*0.998,2); result["stop"]=round(max(price*0.88,price-3*adr),2)
        result["target"]=round(price*(1.15+l2_pts*0.03),2)
        result["upside"]=round((result["target"]/price-1)*100,1)
        result["downside"]=round((result["stop"]/price-1)*100,1)
        result["rr"]=round(result["upside"]/abs(result["downside"]),2) if result["downside"]<0 else 0
    else:
        result["layers"]["L2_quant"]={"name":"Technicals","icon":"📊","pts":0,"status":"absent","detail":"No price data"}

    # L3 — Options Dark Money
    opts=yf_options_flow(ticker)
    if opts and opts.get("total_oi",0)>0:
        vol_oi=opts.get("vol_oi",0); pc=opts.get("pc_vol",1.0); iv_skew=opts.get("iv_skew",0)
        l3_pts=0.0
        if vol_oi>3.0: l3_pts+=1.0
        elif vol_oi>1.5: l3_pts+=0.5
        if pc<0.5: l3_pts+=0.5
        elif pc>1.8: l3_pts-=0.3
        if iv_skew<-5: l3_pts+=0.3
        l3_pts=max(0,min(2.0,l3_pts))
        status="confirmed" if l3_pts>=1.0 else "partial" if l3_pts>0 else "absent"
        detail=f"Vol/OI {vol_oi}× · P/C {pc} · IV skew {iv_skew:+.1f}%"
        result["layers"]["L3_options"]={"name":"Options Flow","icon":"🌑","pts":round(l3_pts,1),"status":status,"detail":detail,"raw":opts}
        result["evidence_packets"].append({"source":"Yahoo Finance Options Chain","finding":detail,"confidence":"HIGH" if l3_pts>=1.5 else "MEDIUM"})
    else:
        result["layers"]["L3_options"]={"name":"Options Flow","icon":"🌑","pts":0,"status":"absent","detail":"No options data"}

    # L4 — Insider Cluster
    if f_key:
        ins=finnhub_insider_buys(ticker,f_key); buys=ins["buys"]; sells=ins["sells"]; net_val=ins["net_val"]
        if buys>=3: l4_pts=2.0; status="confirmed"; detail=f"CLUSTER: {buys} insiders bought ${net_val}K / 45d"
        elif buys>=2: l4_pts=1.5; status="confirmed"; detail=f"{buys} insiders bought ${net_val}K / 45d"
        elif buys==1: l4_pts=0.8; status="partial"; detail=f"1 insider bought ${net_val}K / 45d"
        elif sells>buys: l4_pts=0.0; status="absent"; detail=f"Net selling: {sells} sells vs {buys} buys"
        else: l4_pts=0.3; status="partial"; detail="No recent insider activity"
    else:
        f4=edgar_form4(ticker); count=f4.get("count",0); udates=f4.get("unique_dates",0)
        if count>=5 and udates>=3: l4_pts=1.5; status="confirmed"; detail=f"{count} Form 4s, {udates} dates (cluster)"
        elif count>=2: l4_pts=0.8; status="partial"; detail=f"{count} Form 4 filings / 45d"
        else: l4_pts=0.2; status="absent"; detail=f"{count} Form 4 filings (low)"
        l4_pts=max(0,min(2.0,l4_pts))
    result["layers"]["L4_insider"]={"name":"Insider Cluster","icon":"👤","pts":round(l4_pts,1),"status":status,"detail":detail}
    if l4_pts>0.5:
        result["evidence_packets"].append({"source":"SEC EDGAR Form 4 / Finnhub","finding":detail,"confidence":"HIGH" if l4_pts>=1.5 else "MEDIUM"})

    # L5 — Cross-Chain Frequency
    mem=st.session_state.get("chain_memory",{}); appearances=mem.get(ticker.upper(),[]); n_chains=len(appearances)
    if n_chains>=3: l5_pts=2.0; status="confirmed"; detail=f"{n_chains} independent chains: {', '.join(appearances[-3:])}"
    elif n_chains==2: l5_pts=1.2; status="confirmed"; detail=f"2 chains: {', '.join(appearances)}"
    elif n_chains==1: l5_pts=0.5; status="partial"; detail=f"1 chain ({appearances[0]})"
    else: l5_pts=0.0; status="absent"; detail="First appearance — no cross-chain signal yet"
    result["layers"]["L5_cross_chain"]={"name":"Cross-Chain","icon":"🔗","pts":l5_pts,"status":status,"detail":detail,"n_chains":n_chains,"appearances":appearances}
    if l5_pts>=1.0:
        result["evidence_packets"].append({"source":"Cross-Chain Memory Database","finding":detail,"confidence":"HIGH"})

    # L6 — Volume / Squeeze
    if closes and vols:
        squeeze=short_ratio_proxy(closes,vols); vr=vol_ratio(vols); mom21=calc_momentum(closes).get(21,0)
        if squeeze>=1.0 and (vr or 0)>2.5: l6_pts=1.5; status="confirmed"; detail=f"Vol {vr}×avg + price rising. 1M: {mom21:+.1f}%"
        elif squeeze>=0.5 or (vr or 0)>1.5: l6_pts=0.8; status="partial"; detail=f"Vol {vr}×avg. 1M: {mom21:+.1f}%"
        else: l6_pts=0.0; status="absent"; detail=f"Normal vol. 1M: {mom21:+.1f}%"
    else: l6_pts=0.0; status="absent"; detail="No volume data"
    result["layers"]["L6_squeeze"]={"name":"Vol / Squeeze","icon":"🔥","pts":round(l6_pts,1),"status":status,"detail":detail}
    if l6_pts>0.5:
        result["evidence_packets"].append({"source":"Yahoo Finance Volume Analysis","finding":detail,"confidence":"MEDIUM"})

    # L7 — Catalyst Proximity
    l7_pts=0.0; cat_details=[]
    k8=edgar_8k(ticker)
    if k8: l7_pts+=0.8; cat_details.append(f"{len(k8)} 8-K filings / 30d")
    dod=usaspending_contracts(ticker)
    if dod:
        biggest=dod[0].get("amount_m",0); l7_pts+=1.0 if biggest>100 else 0.5
        cat_details.append(f"DoD contract ${biggest:.0f}M")
    l7_pts=min(2.0,l7_pts)
    status="confirmed" if l7_pts>=1.0 else "partial" if l7_pts>0 else "absent"
    detail=" | ".join(cat_details) if cat_details else "No recent material catalysts"
    result["layers"]["L7_catalyst"]={"name":"Catalysts","icon":"⚡","pts":round(l7_pts,1),"status":status,"detail":detail}
    if l7_pts>0:
        result["evidence_packets"].append({"source":"SEC EDGAR 8-K + USASpending.gov","finding":detail,"confidence":"HIGH" if l7_pts>=1.0 else "MEDIUM"})

    # L8 — News Velocity (NEW — Perplexity-inspired evidence layer)
    recent_n, avg_daily, velocity, headlines = news_velocity(ticker)
    if velocity>2.0: l8_pts=1.5; status="confirmed"; detail=f"News velocity {velocity}× avg · {recent_n} articles / 48h"
    elif velocity>1.2: l8_pts=0.8; status="partial"; detail=f"Elevated news velocity {velocity}× · {recent_n} articles / 48h"
    elif recent_n>0: l8_pts=0.3; status="partial"; detail=f"Normal news flow · {recent_n} articles / 48h"
    else: l8_pts=0.0; status="absent"; detail="No recent news coverage"
    result["layers"]["L8_news_velocity"]={"name":"News Velocity","icon":"📰","pts":round(l8_pts,1),"status":status,"detail":detail,"headlines":headlines}
    if l8_pts>0.3:
        result["evidence_packets"].append({"source":"Google News RSS","finding":detail + (f" — Latest: {headlines[0]}" if headlines else ""),"confidence":"MEDIUM" if velocity>1.5 else "LOW"})

    # ── FINAL SCORE ─────────────────────────────────────────────────────────
    base = sum(l["pts"] for l in result["layers"].values())
    confirmed = sum(1 for l in result["layers"].values() if l["status"]=="confirmed")
    if confirmed>=6: base*=1.6
    elif confirmed>=5: base*=1.4
    elif confirmed>=4: base*=1.2
    elif confirmed>=3: base*=1.1
    if n_chains>=3: base*=1.8
    elif n_chains>=2: base*=1.3
    if l7_pts>=1.0: base*=1.4

    final = round(min(10.0, base/16*10), 1)
    if final>=ultra_thresh: grade="ultra"
    elif final>=high_thresh: grade="high"
    elif final>=4.0: grade="med"
    else: grade="low"

    result["score"]=final; result["grade"]=grade
    result["verdict"]={"ultra":"ULTRA HIGH CONVICTION","high":"HIGH CONVICTION","med":"MODERATE CONVICTION","low":"LOW CONVICTION"}[grade]
    result["confirmed_layers"]=confirmed
    return result

# ══════════════════════════════════════════════════════════════════════════════
#  PERPLEXITY TWO-CALL AI ARCHITECTURE
#  Call 1: RESEARCHER — gathers evidence packets, no conclusions
#  Call 2: SYNTHESISER — reads validated evidence, writes thesis
# ══════════════════════════════════════════════════════════════════════════════
RESEARCHER_SYSTEM = """You are a quantitative evidence gatherer at a hedge fund research desk.

YOUR ONLY JOB: retrieve and structure factual evidence. Do NOT draw investment conclusions.
Do NOT recommend buying or selling. Just report exactly what the data shows.

For each evidence source, report in this exact format:
SOURCE: [data source name]
FINDING: [exactly what the data shows, with specific numbers and dates]
CONFIDENCE: [HIGH if hard data / MEDIUM if derived / LOW if inferred]
TIMESTAMP: [approximate date of data]

Use live web search to verify and supplement the quantitative data provided.
Gather evidence on: recent earnings, analyst targets, short interest, institutional ownership changes,
upcoming catalysts, any material news in last 30 days, options activity context.

End with exactly: EVIDENCE_COMPLETE"""

SYNTHESISER_SYSTEM = """You are the Head of Research at a $10B hedge fund.

A team of analysts has gathered evidence from 8 independent data sources about this company.
You have NOT done the research yourself — you are synthesising validated evidence packets.
Your role is to write a self-contained, institutional-grade investment thesis.

RULES (from Perplexity synthesis architecture):
1. Treat every evidence packet as validated fact — do not second-guess the data
2. Cite specific evidence packets when making claims: [SOURCE: ...]
3. Clearly distinguish what you KNOW from evidence vs what you INFER
4. Every price target, entry, and stop must be backed by a specific rationale
5. State conviction explicitly: the score is not a recommendation, it is a confidence level

STRUCTURE: Write in professional research note format with clear sections.
End with the trade setup: Entry | Target | Stop | Horizon | Conviction: X/10"""

def gather_evidence(conv_result, key):
    """Call 1 — Researcher: supplements quantitative layers with web-sourced evidence."""
    if not key: return conv_result["evidence_packets"]
    layers_summary = "\n".join([
        f"  {l['name']}: {l['pts']}pts ({l['status']}) — {l['detail']}"
        for l in conv_result["layers"].values()])
    prompt = f"""Date: {datetime.now():%Y-%m-%d}
TICKER: {conv_result['ticker']}
PRICE: ${conv_result.get('price','?')} (today: {conv_result.get('chg',0):+.2f}%)
CONVICTION SCORE: {conv_result['score']}/10

QUANTITATIVE EVIDENCE ALREADY GATHERED:
{layers_summary}

SUPPLY CHAIN CONTEXT: {conv_result['chain_source']}

Your job: use Google Search to find additional evidence to supplement the above.
Find: analyst price targets, short interest %, institutional ownership changes last quarter,
upcoming earnings date, any material news last 30 days, patent filings or contract awards
NOT already captured above.

Report each finding in the SOURCE / FINDING / CONFIDENCE / TIMESTAMP format."""
    try:
        client=genai.Client(api_key=key)
        srch=types.Tool(google_search=types.GoogleSearch())
        config=types.GenerateContentConfig(tools=[srch],temperature=0.1,system_instruction=RESEARCHER_SYSTEM)
        resp=client.models.generate_content(model="gemini-2.5-flash",contents=prompt,config=config)
        # Parse evidence packets from response
        raw=resp.text
        packets=list(conv_result["evidence_packets"])
        for block in raw.split("SOURCE:")[1:]:
            lines=[l.strip() for l in block.strip().split("\n") if l.strip()]
            if len(lines)>=2:
                source=lines[0]
                finding=next((l.replace("FINDING:","").strip() for l in lines if l.startswith("FINDING:")),lines[1] if len(lines)>1 else "")
                confidence=next((l.replace("CONFIDENCE:","").strip() for l in lines if l.startswith("CONFIDENCE:")),"MEDIUM")
                if finding: packets.append({"source":source,"finding":finding,"confidence":confidence})
        return packets[:15]  # cap at 15 evidence packets
    except: return conv_result["evidence_packets"]

def stream_synthesised_thesis(conv_result, evidence_packets, key):
    """Call 2 — Synthesiser: writes thesis from evidence packets."""
    if not key: yield "[No API key]"; return
    ep_str="\n\n".join([f"SOURCE: {p['source']}\nFINDING: {p['finding']}\nCONFIDENCE: {p['confidence']}"
                         for p in evidence_packets])
    levels=f"Entry ${conv_result.get('entry','?')} | Target ${conv_result.get('target','?')} | Stop ${conv_result.get('stop','?')} | Upside {conv_result.get('upside','?')}% | R/R {conv_result.get('rr','?')}×"
    try:
        client=genai.Client(api_key=key)
        srch=types.Tool(google_search=types.GoogleSearch())
        config=types.GenerateContentConfig(tools=[srch],temperature=0.3,system_instruction=SYNTHESISER_SYSTEM)
        resp=client.models.generate_content_stream(model="gemini-2.5-flash",
            contents=f"""Date: {datetime.now():%Y-%m-%d}

TICKER: {conv_result['ticker']}
CONVICTION SCORE: {conv_result['score']}/10 — {conv_result['verdict']}
CONFIRMED LAYERS: {conv_result['confirmed_layers']}/8
PRICE: ${conv_result.get('price','?')} | {levels}
CROSS-CHAIN APPEARANCES: {conv_result['layers'].get('L5_cross_chain',{}).get('n_chains',0)}

VALIDATED EVIDENCE PACKETS ({len(evidence_packets)} sources):
{ep_str}

Write the COMPLETE INSTITUTIONAL CONVICTION THESIS:

## Executive Summary
What is the core asymmetric thesis in 2-3 sentences? What is the market missing?

## Evidence Synthesis
Cite specific evidence packets for each claim. What do ALL 8 independent layers
collectively indicate? Where is the convergence pointing?

## Asymmetric Setup — Why Now
What specific catalyst or series of events reprices this company?
When does this play out? (30-90-180 day view)

## Supply Chain Moat
Why is its position in the supply chain defensible against substitution?
What would it cost a giant to replicate or replace this company?

## Risk Assessment
Bear case: what specific event breaks this thesis?
At what price level is the thesis invalidated?
Correlation risk: what else in a portfolio might move the same way?

## Trade Construction
{levels}
Position sizing rationale: why this R/R at this conviction score?

## Conviction Summary
[TICKER]: {conv_result['score']}/10 — [one sentence final call with specific catalyst and timeline]""",
            config=config)
        for chunk in resp:
            if chunk.text: yield chunk.text
    except Exception as e: yield f"[Error: {e}]"

def stream_chain_map(target, key):
    if not key: yield "[No API key]"; return
    try:
        client=genai.Client(api_key=key)
        srch=types.Tool(google_search=types.GoogleSearch())
        config=types.GenerateContentConfig(tools=[srch],temperature=0.2,system_instruction="""
You are a Supply Chain Forensic Analyst. Map the FULL nervous system of any sector, technology, or company.
STRICT RULES: (1) Only publicly traded companies with real tickers.
(2) Bold all tickers: **$TICKER**. (3) End with: TICKERS: T1=$X,T2=$X,T3=$X,BOTTLENECK=$X,MOAT=$X
(4) For each company: WHY asymmetric — what cannot be replicated?""")
        resp=client.models.generate_content_stream(model="gemini-2.5-flash",
            contents=f"""Map FULL supply chain for: {target}

## TIER 1 — Direct Suppliers (3-5, well-known, **$TICKER**)
## TIER 2 — Hidden Asymmetric Plays (3-5, overlooked, **$TICKER**)
## TIER 3 — Raw Material / IP Moat (2-3, deepest value, **$TICKER**)
## BOTTLENECK — The one company giants CANNOT bypass
## HIGHEST CONVICTION BET — single best asymmetric play and exactly why

TICKERS: T1=$X,T2=$X,T3=$X,BOTTLENECK=$X,MOAT=$X""",config=config)
        for chunk in resp:
            if chunk.text: yield chunk.text
    except Exception as e: yield f"[Error: {e}]"

def send_telegram(text,token,chat_id):
    if not token or not chat_id: return
    for chunk in [text[i:i+4000] for i in range(0,len(text),4000)]:
        try: requests.post(f"https://api.telegram.org/bot{token}/sendMessage",json={"chat_id":chat_id,"text":chunk},timeout=10)
        except: pass

# ══════════════════════════════════════════════════════════════════════════════
#  SVG CONVICTION RADAR
# ══════════════════════════════════════════════════════════════════════════════
def make_radar_svg(layers, score, grade):
    """Pure SVG conviction radar — 8 axes, no external libraries."""
    grade_colors={"ultra":"#c5221f","high":"#b45309","med":"#1a56e8","low":"#9ca3af"}
    color=grade_colors.get(grade,"#1a56e8")
    cx=cy=110; r=80; n=len(layers)
    axes_angles=[math.pi/2+2*math.pi*i/n for i in range(n)]
    max_pts=2.0
    # Normalize scores 0-1
    scores=[min(l["pts"]/max_pts,1.0) for l in layers.values()]
    layer_names=[l["name"] for l in layers.values()]
    # Outer polygon (max)
    outer_pts=" ".join([f"{cx+r*math.cos(a):.1f},{cy-r*math.sin(a):.1f}" for a in axes_angles])
    mid_pts=" ".join([f"{cx+r*0.5*math.cos(a):.1f},{cy-r*0.5*math.sin(a):.1f}" for a in axes_angles])
    # Score polygon
    score_pts=" ".join([f"{cx+r*scores[i]*math.cos(axes_angles[i]):.1f},{cy-r*scores[i]*math.sin(axes_angles[i]):.1f}" for i in range(n)])
    # Axis lines
    axis_lines="".join([f'<line x1="{cx}" y1="{cy}" x2="{cx+r*math.cos(a):.1f}" y2="{cy-r*math.sin(a):.1f}" stroke="#e4e6ea" stroke-width="1"/>' for a in axes_angles])
    # Labels
    labels=""
    for i,(a,nm) in enumerate(zip(axes_angles,layer_names)):
        lx=cx+(r+18)*math.cos(a); ly=cy-(r+18)*math.sin(a)
        ta="middle" if abs(lx-cx)<10 else "end" if lx<cx else "start"
        short=nm[:8]
        labels+=f'<text x="{lx:.1f}" y="{ly+4:.1f}" font-size="8" fill="#9ca3af" text-anchor="{ta}" font-family="Inter,sans-serif">{short}</text>'
    return f"""<svg viewBox="0 0 220 220" xmlns="http://www.w3.org/2000/svg">
<polygon points="{outer_pts}" fill="none" stroke="#e4e6ea" stroke-width="1"/>
<polygon points="{mid_pts}" fill="none" stroke="#e4e6ea" stroke-width="1" stroke-dasharray="3,3"/>
{axis_lines}
<polygon points="{score_pts}" fill="{color}" fill-opacity="0.15" stroke="{color}" stroke-width="2"/>
{labels}
<text x="{cx}" y="{cy+5}" font-size="22" font-weight="800" fill="{color}" text-anchor="middle" font-family="JetBrains Mono,monospace">{score}</text>
<text x="{cx}" y="{cy+20}" font-size="8" fill="#9ca3af" text-anchor="middle" font-family="Inter,sans-serif">/ 10</text>
</svg>"""

# ══════════════════════════════════════════════════════════════════════════════
#  UI COMPONENTS
# ══════════════════════════════════════════════════════════════════════════════
def render_conviction_card(cr):
    g=cr["grade"]; score=cr["score"]; bar_pct=int(score*10)
    price_str=f"${cr['price']:,.2f}" if cr.get("price") else "—"
    chg=cr.get("chg",0) or 0
    chg_html=f'<span class="cv-chg-up">▲ {chg:.2f}%</span>' if chg>=0 else f'<span class="cv-chg-dn">▼ {abs(chg):.2f}%</span>'

    # Top stripe + body
    st.markdown(f"""
<div class="cv-card">
  <div class="cv-top-stripe stripe-{g}"></div>
  <div class="cv-body">
    <div class="cv-row1">
      <div class="cv-ticker-block">
        <div class="cv-ticker">{cr['ticker']}</div>
        <div class="cv-company">{cr.get('chain_source','')[:50]}</div>
      </div>
      <div class="cv-price-block">
        <div class="cv-price">{price_str}</div>
        {chg_html}
      </div>
      <div class="cv-score-block">
        <div class="cv-score-num {g}">{score}</div>
        <div class="cv-score-denom">conviction</div>
      </div>
    </div>
    <div class="cv-verdict-row">
      <span class="cv-verdict verdict-{g}">{cr['verdict']}</span>
      <span class="cv-layer-count">{cr['confirmed_layers']}/8 layers · {cr['layers'].get('L5_cross_chain',{}).get('n_chains',0)} chains · {cr['ts'][:10]}</span>
    </div>
    <div class="cv-bar-track"><div class="cv-bar-fill fill-{g}" style="width:{bar_pct}%"></div></div>
  </div>
</div>""", unsafe_allow_html=True)

    # Levels
    if cr.get("entry"):
        st.markdown(f"""
<div class="cv-levels">
  <div class="cv-level"><span class="lv-lbl">Entry</span><span class="lv-val lv-entry">${cr['entry']:,.2f}</span></div>
  <div class="cv-level"><span class="lv-lbl">Target</span><span class="lv-val lv-target">${cr['target']:,.2f}</span></div>
  <div class="cv-level"><span class="lv-lbl">Stop</span><span class="lv-val lv-stop">${cr['stop']:,.2f}</span></div>
  <div class="cv-level"><span class="lv-lbl">Upside</span><span class="lv-val lv-up">{cr['upside']:+.1f}%</span></div>
  <div class="cv-level"><span class="lv-lbl">Downside</span><span class="lv-val lv-dn">{cr['downside']:.1f}%</span></div>
  <div class="cv-level"><span class="lv-lbl">R/R</span><span class="lv-val lv-rr">{cr['rr']}×</span></div>
</div>""", unsafe_allow_html=True)

    # Layer evidence grid
    st.markdown('<div class="ev-grid">', unsafe_allow_html=True)
    for lk,layer in cr["layers"].items():
        s=layer["status"]; pts=layer["pts"]
        pts_str=f"+{pts}pt" if pts>0 else "—"
        st.markdown(f"""
<div class="ev-cell {s}">
  <span class="ev-icon">{layer['icon']}</span>
  <span class="ev-layer-id">{lk.replace('_',' ')}</span>
  <div class="ev-name">{layer['name']}</div>
  <div class="ev-detail">{layer['detail']}</div>
  <span class="ev-pts {s}">{pts_str}</span>
</div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Cross-chain badges
    apps=cr["layers"].get("L5_cross_chain",{}).get("appearances",[])
    if len(apps)>1:
        badges="".join([f'<span class="xc-badge">⛓ {a}</span>' for a in apps])
        st.markdown(f'<div style="margin-top:8px">{badges}</div>', unsafe_allow_html=True)

def render_evidence_packets(packets):
    """Perplexity-style evidence packet display."""
    conf_colors={"HIGH":"ep-high","MEDIUM":"ep-medium","LOW":"ep-low"}
    for p in packets:
        cls=conf_colors.get(p.get("confidence","MEDIUM"),"ep-medium")
        st.markdown(f"""
<div class="ep-block {cls}">
  <span class="ep-source">◆ {p['source']}</span>
  <div class="ep-finding">{p['finding']}</div>
  <span class="ep-conf">Confidence: {p.get('confidence','—')}</span>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN UI
# ══════════════════════════════════════════════════════════════════════════════

# ── TOPBAR ────────────────────────────────────────────────────────────────────
results_all = st.session_state.get("conviction_results",[])
n_ultra = sum(1 for r in results_all if r["grade"]=="ultra")
n_high  = sum(1 for r in results_all if r["grade"]=="high")

st.markdown(f"""
<div class="cp-topbar">
  <div class="cp-wordmark">Conviction<span class="red">Pro</span></div>
  <div class="cp-divider"></div>
  <div class="cp-tagline">Supply Chain Intelligence · 8-Layer Signal Stacker · Perplexity Evidence Architecture</div>
  <div class="cp-status-row">
    <span class="cp-badge badge-live">● LIVE DATA</span>
    <span class="cp-badge badge-score">{n_ultra} ULTRA · {n_high} HIGH</span>
    <span class="cp-badge badge-gray">{datetime.now().strftime("%d %b %Y · %H:%M")}</span>
  </div>
</div>""", unsafe_allow_html=True)

# ── MACRO RIBBON ──────────────────────────────────────────────────────────────
macro = get_macro()
ribbon = ""
for lbl,(p,c) in macro.items():
    if p:
        cls="mup" if (c or 0)>=0 else "mdn"
        fmt=f"{p:,.0f}" if p>500 else f"{p:.2f}"
        sgn="+" if (c or 0)>=0 else ""
        ribbon+=f'<div class="mitem"><span class="mticker">{lbl}</span><span class="mprice">{fmt}</span><span class="{cls}">{sgn}{c:.2f}%</span></div>'
    else:
        ribbon+=f'<div class="mitem"><span class="mticker">{lbl}</span><span class="mprice">—</span></div>'
st.markdown(f'<div class="macro-ribbon">{ribbon}</div>', unsafe_allow_html=True)

# ── TABS ───────────────────────────────────────────────────────────────────────
tab_scan, tab_dash, tab_chain, tab_deep, tab_wl = st.tabs([
    "  Intelligence Scan  ",
    f"  Conviction Dashboard ({len(results_all)})  ",
    f"  Cross-Chain Intelligence ({len(st.session_state.get('chain_memory',{}))} tickers)  ",
    "  Deep Dive  ",
    "  Watchlist  ",
])

# ══════════════════════════════════════════════════════════════════════════════
#  TAB 1 — INTELLIGENCE SCAN
# ══════════════════════════════════════════════════════════════════════════════
with tab_scan:
    st.markdown('<div class="search-panel">', unsafe_allow_html=True)
    st.markdown('<span class="search-label">Intelligence Target</span>', unsafe_allow_html=True)
    sc1,sc2 = st.columns([5,1])
    with sc1:
        scan_target = st.text_input("","",
            placeholder="$NVDA  ·  Solid State Batteries  ·  Hypersonic Weapons  ·  GLP-1 Obesity  ·  EUV Lithography",
            label_visibility="collapsed", key="ti_scan")
    with sc2:
        scan_btn = st.button("◈ Scan", type="primary", key="btn_scan", use_container_width=True)
    st.markdown("""<div class="search-hint">
<b>$TICKER</b> maps that company's full supply chain &nbsp;·&nbsp;
<b>Technology</b> maps who owns the bottleneck &nbsp;·&nbsp;
<b>Sector/Theme</b> finds the hidden Tier 2/3 plays &nbsp;·&nbsp;
<b>Geopolitical event</b> surfaces the asymmetric beneficiaries
</div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if scan_btn and scan_target.strip():
        if not gemini_key:
            st.warning("Add Gemini API key in the sidebar. Free at aistudio.google.com/app/apikey")
            st.stop()

        # STEP 1 — Map supply chain
        with st.status(f"Mapping supply chain for '{scan_target}'...", expanded=True) as s1:
            st.write("Running Gemini with Google Search grounding...")
            chain_out = st.empty(); full_chain=""
            for chunk in stream_chain_map(scan_target, gemini_key):
                full_chain+=chunk; chain_out.markdown(full_chain)
            st.session_state["last_chain_map"]=full_chain
            s1.update(label="✓ Supply chain mapped", state="complete")

        # STEP 2 — Extract tickers
        ticker_match=re.search(r'TICKERS:\s*([^\n]+)', full_chain, re.IGNORECASE)
        raw_tickers=[]
        if ticker_match:
            raw=ticker_match.group(1)
            # Extract values from key=value pairs
            for m in re.finditer(r'=\$?([A-Z][A-Z0-9\-]{0,5})', raw):
                t=m.group(1).upper()
                if t not in ["NA","N/A"] and len(t)>=2: raw_tickers.append(t)
        body_tickers=re.findall(r'\*\*\$([A-Z]{2,6})\*\*', full_chain)
        all_tickers=list(dict.fromkeys(raw_tickers+body_tickers))[:12]

        if not all_tickers:
            st.warning("Could not extract tickers automatically. Look for **$TICKER** in the chain map above.")
            st.stop()

        # Update cross-chain memory
        for t in all_tickers:
            mem=st.session_state.get("chain_memory",{})
            if t not in mem: mem[t]=[]
            if scan_target[:30] not in mem[t]: mem[t].append(scan_target[:30])
            st.session_state["chain_memory"]=mem

        st.markdown(f'<div class="sec-hdr">Running 8-layer conviction analysis on {len(all_tickers)} tickers</div>', unsafe_allow_html=True)

        # STEP 3 — Score in parallel
        scored=[]
        lock=threading.Lock()
        prog=st.progress(0, f"Scoring {len(all_tickers)} tickers...")

        def score_one(t):
            cr=score_conviction(t, scan_target, finnhub_key)
            with lock:
                scored.append(cr)
                prog.progress(len(scored)/len(all_tickers),f"Scored {len(scored)}/{len(all_tickers)} — {t}")

        threads=[threading.Thread(target=score_one,args=(t,),daemon=True) for t in all_tickers]
        for th in threads: th.start()
        for th in threads: th.join(timeout=60)
        prog.empty()

        scored.sort(key=lambda x:x["score"], reverse=True)
        existing=[e for e in st.session_state.get("conviction_results",[]) if e["ticker"] not in [r["ticker"] for r in scored]]
        st.session_state["conviction_results"]=scored+existing

        # STEP 4 — Show top results
        qualified=[r for r in scored if r["confirmed_layers"]>=min_layers][:6]
        if not qualified:
            st.info(f"No tickers met the minimum {min_layers} confirmed layers threshold. Try lowering it in sidebar.")
        else:
            for cr in qualified:
                render_conviction_card(cr)
                # Inline Perplexity-style thesis expander
                with st.expander(f"◈ Full conviction thesis — {cr['ticker']}", expanded=(cr['grade']=='ultra')):
                    if gemini_key:
                        thesis_col, evidence_col = st.columns([3,2])
                        with evidence_col:
                            st.markdown('<div class="sec-hdr">Evidence Packets</div>', unsafe_allow_html=True)
                            with st.spinner("Gathering additional evidence..."):
                                packets=gather_evidence(cr, gemini_key)
                            render_evidence_packets(packets)
                            # Radar
                            st.markdown('<div class="sec-hdr">Conviction Radar</div>', unsafe_allow_html=True)
                            radar_svg=make_radar_svg(cr["layers"],cr["score"],cr["grade"])
                            st.markdown(f'<div style="max-width:220px;margin:0 auto">{radar_svg}</div>', unsafe_allow_html=True)
                        with thesis_col:
                            st.markdown('<div class="sec-hdr">Institutional Thesis</div>', unsafe_allow_html=True)
                            out=st.empty(); full=""
                            for chunk in stream_synthesised_thesis(cr, packets, gemini_key):
                                full+=chunk; out.markdown(full)
                            col_dl,col_tg=st.columns(2)
                            with col_dl:
                                st.download_button("⬇ Download thesis",data=full,
                                    file_name=f"thesis_{cr['ticker']}_{datetime.now():%Y%m%d}.txt",
                                    mime="text/plain",key=f"dl_{cr['ticker']}_scan")
                            with col_tg:
                                if tg_token and tg_chat:
                                    if st.button("→ Telegram",key=f"tg_{cr['ticker']}_scan",use_container_width=True):
                                        send_telegram(f"◈ CONVICTION PRO\n{cr['ticker']} — {cr['score']}/10\n\n{full}",tg_token,tg_chat)
                                        st.success("Sent")
                st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
#  TAB 2 — CONVICTION DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
with tab_dash:
    results_all=st.session_state.get("conviction_results",[])
    if not results_all:
        st.info("Run a supply chain scan to populate the dashboard.")
    else:
        # Summary row
        sm1,sm2,sm3,sm4,sm5 = st.columns(5)
        sm1.metric("Total Tracked", len(results_all))
        sm2.metric("Ultra Conviction", sum(1 for r in results_all if r["grade"]=="ultra"), delta=f"≥ {ultra_thresh}")
        sm3.metric("High Conviction",  sum(1 for r in results_all if r["grade"]=="high"),  delta=f"≥ {high_thresh}")
        sm4.metric("Cross-Chain Hits", sum(1 for r in results_all if r["layers"].get("L5_cross_chain",{}).get("n_chains",0)>=2))
        sm5.metric("Avg R/R", round(float(np.mean([r.get("rr",0) or 0 for r in results_all])),2))

        st.markdown('<div class="sec-hdr">Ranked Conviction Board</div>', unsafe_allow_html=True)
        fc1,fc2,fc3=st.columns([2,2,2])
        with fc1: grade_f=st.selectbox("Grade filter",["All","ultra","high","med","low"],key="sb_grade_f")
        with fc2: sort_f =st.selectbox("Sort by",["Score","R/R","Confirmed layers","Cross-chain","Recent"],key="sb_sort_f")
        with fc3: view_f =st.selectbox("View",["Cards","Table"],key="sb_view_f")

        filtered=[r for r in results_all if grade_f=="All" or r["grade"]==grade_f]
        if sort_f=="R/R":         filtered.sort(key=lambda x:x.get("rr",0) or 0,reverse=True)
        elif sort_f=="Confirmed layers": filtered.sort(key=lambda x:x["confirmed_layers"],reverse=True)
        elif sort_f=="Cross-chain":  filtered.sort(key=lambda x:x["layers"].get("L5_cross_chain",{}).get("n_chains",0),reverse=True)
        elif sort_f=="Recent":    filtered.sort(key=lambda x:x["ts"],reverse=True)
        else:                     filtered.sort(key=lambda x:x["score"],reverse=True)

        if view_f=="Cards":
            for cr in filtered[:12]:
                render_conviction_card(cr)
                c1,c2=st.columns([3,1])
                with c1:
                    if st.button(f"◈ Full thesis — {cr['ticker']}", key=f"th_{cr['ticker']}_{cr['ts'][:10]}"):
                        st.session_state["deep_target"]=cr["ticker"]
                        st.rerun()
                with c2:
                    st.download_button("⬇ JSON",data=json.dumps(cr,indent=2),
                        file_name=f"conviction_{cr['ticker']}.json",mime="application/json",
                        key=f"dl_{cr['ticker']}_{cr['ts'][:10]}")
                st.markdown("---")
        else:
            df=pd.DataFrame([{
                "Ticker":r["ticker"],"Score":r["score"],"Grade":r["grade"].upper(),
                "Layers":r["confirmed_layers"],"Chains":r["layers"].get("L5_cross_chain",{}).get("n_chains",0),
                "Price":r.get("price",""),"Entry":r.get("entry",""),"Target":r.get("target",""),
                "Stop":r.get("stop",""),"Upside%":r.get("upside",""),"R/R":r.get("rr",""),
                "Chain":r["chain_source"][:25],"Date":r["ts"][:10],
            } for r in filtered])
            def _cs(v):
                if not isinstance(v,(int,float)): return ""
                if v>=ultra_thresh: return "color:#c5221f;font-weight:700"
                if v>=high_thresh:  return "color:#b45309;font-weight:700"
                return ""
            def _cu(v):
                if isinstance(v,(int,float)): return "color:#16a34a" if v>0 else "color:#dc2626" if v<0 else ""
                return ""
            st.dataframe(df.style.map(_cs,subset=["Score"]).map(_cu,subset=["Upside%"]),
                         width="stretch",hide_index=True,height=450)
            st.download_button("⬇ Export CSV",data=df.to_csv(index=False),
                file_name=f"conviction_{datetime.now():%Y%m%d_%H%M}.csv",mime="text/csv",key="btn_dl_csv")

# ══════════════════════════════════════════════════════════════════════════════
#  TAB 3 — CROSS-CHAIN INTELLIGENCE
# ══════════════════════════════════════════════════════════════════════════════
with tab_chain:
    st.markdown("""
**The highest-conviction signal in this system.** When Gemini independently maps the supply chains for
`$NVDA`, `Hypersonic Weapons`, and `Satellite Communications` and the same small-cap appears in all three —
that is structural dependency, not coincidence. These are the names no analyst is covering because they
require triangulating across separate domains.
""")
    chain_mem=st.session_state.get("chain_memory",{})
    if not chain_mem:
        st.info("Run multiple supply chain scans. Tickers appearing in 3+ independent chains signal maximum structural conviction.")
    else:
        sorted_mem=sorted(chain_mem.items(),key=lambda x:len(x[1]),reverse=True)
        multi=[(t,c) for t,c in sorted_mem if len(c)>=2]
        single=[(t,c) for t,c in sorted_mem if len(c)==1]

        if multi:
            st.markdown('<div class="sec-hdr">Multi-Chain Convergence — Maximum Structural Conviction</div>', unsafe_allow_html=True)
            for ticker, chains in multi:
                n=len(chains)
                grade_cls="ultra" if n>=3 else "high"
                badges="".join([f'<span class="xc-badge">⛓ {c}</span>' for c in chains])
                st.markdown(f"""
<div class="mc-card">
  <div style="display:flex;align-items:center;gap:6px;margin-bottom:8px">
    <span class="mc-ticker">{ticker}</span>
    <span class="mc-count">{n} independent chain appearances</span>
  </div>
  <div>{badges}</div>
</div>""", unsafe_allow_html=True)
                if st.button(f"◈ Score {ticker} now", key=f"mc_score_{ticker}"):
                    if gemini_key:
                        with st.spinner(f"Running 8-layer conviction on {ticker}..."):
                            cr=score_conviction(ticker,f"Cross-chain: {', '.join(chains[:3])}",finnhub_key)
                        render_conviction_card(cr)
                        existing=[e for e in st.session_state.get("conviction_results",[]) if e["ticker"]!=ticker]
                        st.session_state["conviction_results"]=[cr]+existing

        if single:
            with st.expander(f"Single-chain appearances ({len(single)} tickers)"):
                cols=st.columns(3)
                for i,(t,c) in enumerate(single[:30]):
                    with cols[i%3]:
                        st.markdown(f'<div class="wl-row"><span class="wl-ticker">{t}</span><span style="font-size:0.72rem;color:#6b7280">{c[0]}</span></div>', unsafe_allow_html=True)

        st.download_button("⬇ Export chain memory JSON",
            data=json.dumps(chain_mem,indent=2),
            file_name=f"chain_memory_{datetime.now():%Y%m%d}.json",
            mime="application/json",key="btn_dl_mem")

# ══════════════════════════════════════════════════════════════════════════════
#  TAB 4 — DEEP DIVE (full Perplexity two-call thesis)
# ══════════════════════════════════════════════════════════════════════════════
with tab_deep:
    st.markdown("**Full institutional thesis with Perplexity two-call architecture.** The Researcher gathers evidence packets from 8 independent sources. The Synthesiser reads validated evidence and writes the thesis — it never searches, only synthesises.")

    dd1,dd2,dd3=st.columns([2,2,1])
    with dd1: dd_ticker=st.text_input("Ticker",placeholder="NVDA · AXTI · RKLB · PLTR",key="ti_dd",label_visibility="collapsed")
    with dd2: dd_context=st.text_input("Context",placeholder="e.g. AI chip supply chain, Tier 2 photonics",key="ti_dd_ctx",label_visibility="collapsed")
    with dd3: dd_btn=st.button("◈ Deep Dive",type="primary",key="btn_dd",use_container_width=True)

    # Pre-populate from dashboard click
    if st.session_state.get("deep_target"):
        dd_ticker=st.session_state["deep_target"]

    if dd_btn and dd_ticker.strip():
        if not gemini_key:
            st.warning("Add Gemini API key in sidebar.")
        else:
            t=dd_ticker.strip().upper().replace("$","")
            ctx=dd_context.strip() or "Direct analysis"
            # Update memory
            mem=st.session_state.get("chain_memory",{})
            if t not in mem: mem[t]=[]
            if ctx not in mem[t]: mem[t].append(ctx)
            st.session_state["chain_memory"]=mem

            # Find existing score or compute fresh
            existing_cr=next((r for r in st.session_state.get("conviction_results",[]) if r["ticker"]==t),None)
            with st.spinner(f"Running 8-layer conviction on {t}..."):
                cr=score_conviction(t,ctx,finnhub_key) if not existing_cr else existing_cr

            # Update session
            results=[r for r in st.session_state.get("conviction_results",[]) if r["ticker"]!=t]
            st.session_state["conviction_results"]=[cr]+results
            st.session_state["deep_target"]=None

            render_conviction_card(cr)

            # Two-column thesis layout
            th_left, th_right = st.columns([3,2])
            with th_right:
                st.markdown('<div class="sec-hdr">Evidence Packets (Researcher)</div>', unsafe_allow_html=True)
                with st.spinner("Call 1 — Researcher gathering evidence..."):
                    packets=gather_evidence(cr,gemini_key)
                render_evidence_packets(packets)
                st.markdown('<div class="sec-hdr">Conviction Radar</div>', unsafe_allow_html=True)
                radar_svg=make_radar_svg(cr["layers"],cr["score"],cr["grade"])
                st.markdown(f'<div style="max-width:220px;margin:0 auto">{radar_svg}</div>',unsafe_allow_html=True)

            with th_left:
                st.markdown('<div class="sec-hdr">Institutional Thesis (Synthesiser)</div>', unsafe_allow_html=True)
                st.caption("Call 2 — Synthesiser reads validated evidence packets and writes thesis without searching")
                out=st.empty(); full=""
                with st.spinner("Call 2 — Synthesiser writing thesis from evidence..."):
                    for chunk in stream_synthesised_thesis(cr,packets,gemini_key):
                        full+=chunk; out.markdown(full)

            col_dl,col_tg=st.columns(2)
            with col_dl:
                st.download_button("⬇ Download full thesis",data=full,
                    file_name=f"thesis_{t}_{datetime.now():%Y%m%d_%H%M}.txt",
                    mime="text/plain",key=f"dl_dd_{t}")
            with col_tg:
                if tg_token and tg_chat:
                    if st.button("→ Send to Telegram",key=f"tg_dd_{t}",use_container_width=True):
                        send_telegram(f"◈ CONVICTION PRO DEEP DIVE\n{t} — {cr['score']}/10\n\n{full}",tg_token,tg_chat)
                        st.success("Sent")

# ══════════════════════════════════════════════════════════════════════════════
#  TAB 5 — WATCHLIST (batch scoring)
# ══════════════════════════════════════════════════════════════════════════════
with tab_wl:
    st.markdown("**Batch score your watchlist.** Runs all 8 conviction layers on every ticker simultaneously.")
    wl_raw=st.text_area("Watchlist tickers (comma-separated)",
        value=st.session_state.get("watchlist","NVDA,PLTR,RKLB,IONQ,AXTI,CELH,MELI,TSM"),
        height=70, key="ta_watchlist")
    if st.button("◈ Score Watchlist", type="primary", key="btn_wl"):
        if not gemini_key:
            st.warning("Add Gemini API key.")
        else:
            st.session_state["watchlist"]=wl_raw
            tickers=[t.strip().upper() for t in wl_raw.split(",") if t.strip()]
            scored=[]
            lock=threading.Lock()
            prog=st.progress(0,f"Scoring {len(tickers)} watchlist tickers...")

            def wl_score(t):
                cr=score_conviction(t,"Watchlist",finnhub_key)
                with lock:
                    scored.append(cr)
                    prog.progress(len(scored)/len(tickers),f"{len(scored)}/{len(tickers)} — {t}")

            threads=[threading.Thread(target=wl_score,args=(t,),daemon=True) for t in tickers]
            for th in threads: th.start()
            for th in threads: th.join(timeout=90)
            prog.empty()

            scored.sort(key=lambda x:x["score"],reverse=True)
            existing=[e for e in st.session_state.get("conviction_results",[]) if e["ticker"] not in [r["ticker"] for r in scored]]
            st.session_state["conviction_results"]=scored+existing

            # Summary table
            st.markdown('<div class="sec-hdr">Watchlist Conviction Summary</div>', unsafe_allow_html=True)
            for cr in scored:
                g=cr["grade"]; score=cr["score"]
                sc_cls={"ultra":"verdict-ultra","high":"verdict-high","med":"verdict-med","low":"verdict-low"}[g]
                price_str=f"${cr['price']:,.2f}" if cr.get("price") else "—"
                chg=cr.get("chg",0) or 0
                st.markdown(f"""
<div class="wl-row">
  <span class="wl-ticker">{cr['ticker']}</span>
  <span class="wl-score-pill {sc_cls}">{score}/10</span>
  <span style="font-size:0.78rem;color:#374151;font-family:'JetBrains Mono',monospace">{price_str}</span>
  <span style="font-size:0.73rem;color:{'#16a34a' if chg>=0 else '#dc2626'};font-family:'JetBrains Mono',monospace">{'+' if chg>=0 else ''}{chg:.2f}%</span>
  <span style="font-size:0.72rem;color:#9ca3af;margin-left:auto">{cr['confirmed_layers']}/8 layers · R/R {cr.get('rr',0)}×</span>
</div>""", unsafe_allow_html=True)

            # Export
            df=pd.DataFrame([{"Ticker":r["ticker"],"Score":r["score"],"Grade":r["grade"].upper(),
                "Price":r.get("price"),"Upside%":r.get("upside"),"R/R":r.get("rr"),
                "Layers":r["confirmed_layers"],"Chains":r["layers"].get("L5_cross_chain",{}).get("n_chains",0)}
                for r in scored])
            st.download_button("⬇ Export watchlist CSV",data=df.to_csv(index=False),
                file_name=f"watchlist_{datetime.now():%Y%m%d_%H%M}.csv",mime="text/csv",key="btn_wl_csv")
