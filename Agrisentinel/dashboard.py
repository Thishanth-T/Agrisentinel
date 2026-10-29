import textwrap
"""
AgriSentinel Insurer Operations Cockpit & Anti-Fraud Dashboard
============================================================
Modern Enterprise Parametric Insurer Operations Cockpit inspired by
modern clean telemetry and IoT monitoring design languages (EnerSol, Crewix, Fyntra).

Key Modules:
1. 9 Regional Indian Farm Profiles & Live Micro-Climate Telemetry
2. Basis Risk Comparative Analysis (Area Weather Station vs On-Plot Node)
3. Cryptographic Data-Trust & Replay Defense Verification
4. Simulated Claims Ledger & Tamper-Evident Audit Trail
5. Underwriter ROI & Statutory Late-Penalty Savings Calculator
"""

import os
import streamlit as st
import pandas as pd
import requests
import time
import json
from datetime import datetime

import config  # Loads .env safely at startup

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AgriSentinel | Parametric Insurer Cockpit",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Enterprise CSS Theme inspired by EnerSol, Crewix & Fyntra
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"], .stApp {
font-family: 'Plus Jakarta Sans', sans-serif !important;
background-color: #f8fafc;
color: #0f172a;
}

/* Sleek Floating Pill Tabs (EnerSol / Crewix style) */
div[data-baseweb="tab-list"] {
gap: 10px !important;
background-color: transparent !important;
padding: 6px 0 18px 0 !important;
border-bottom: none !important;
}
div[data-baseweb="tab-list"] button[data-baseweb="tab"] {
background: #ffffff !important;
border: 1.5px solid #e2e8f0 !important;
border-radius: 9999px !important;
padding: 9px 22px !important;
font-size: 13.5px !important;
font-weight: 600 !important;
color: #475569 !important;
box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04) !important;
transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
div[data-baseweb="tab-list"] button[data-baseweb="tab"]:hover {
background-color: #f1f5f9 !important;
color: #0f172a !important;
border-color: #cbd5e1 !important;
transform: translateY(-1px) !important;
}
div[data-baseweb="tab-list"] button[aria-selected="true"] {
background: #0f172a !important;
color: #ffffff !important;
border-color: #0f172a !important;
box-shadow: 0 6px 16px -2px rgba(15, 23, 42, 0.2) !important;
}
div[data-baseweb="tab-highlight"], div[data-baseweb="tab-border"] {
display: none !important;
}

/* Executive Header Banner */
.top-hero-card {
background: #ffffff;
border: 1px solid #e2e8f0;
border-radius: 20px;
padding: 22px 28px;
margin-bottom: 22px;
box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.04);
display: flex;
justify-content: space-between;
align-items: center;
flex-wrap: wrap;
gap: 16px;
}
.hero-brand {
display: flex;
align-items: center;
gap: 14px;
}
.brand-icon-box {
width: 48px;
height: 48px;
border-radius: 14px;
background: linear-gradient(135deg, #10b981, #059669);
display: flex;
align-items: center;
justify-content: center;
font-size: 24px;
box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}
.hero-title {
font-size: 22px;
font-weight: 800;
color: #0f172a !important;
letter-spacing: -0.5px;
margin: 0;
line-height: 1.2;
}
.hero-subtitle {
font-size: 13px;
color: #64748b !important;
margin-top: 3px;
font-weight: 500;
}
.hero-badges {
display: flex;
gap: 8px;
flex-wrap: wrap;
}
.hero-pill {
background: #f1f5f9;
border: 1px solid #e2e8f0;
padding: 5px 12px;
border-radius: 20px;
font-size: 11.5px;
font-weight: 600;
color: #334155 !important;
display: flex;
align-items: center;
gap: 6px;
}
.hero-pill.live {
background: #ecfdf5;
border-color: #a7f3d0;
color: #065f46 !important;
}
.hero-pill.crypto {
background: #f5f3ff;
border-color: #ddd6fe;
color: #5b21b6 !important;
}

/* Executive KPI Metric Cards (EnerSol / Fyntra style) */
.kpi-card {
background: #ffffff;
border-radius: 18px;
padding: 20px 22px;
border: 1px solid #e2e8f0;
box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.04);
transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.kpi-card:hover {
transform: translateY(-2px);
box-shadow: 0 8px 24px -4px rgba(15, 23, 42, 0.08);
}
.kpi-top {
display: flex;
justify-content: space-between;
align-items: center;
margin-bottom: 8px;
}
.kpi-label {
font-size: 12px;
font-weight: 700;
text-transform: uppercase;
letter-spacing: 0.6px;
color: #64748b !important;
}
.kpi-icon-badge {
width: 34px;
height: 34px;
border-radius: 10px;
display: flex;
align-items: center;
justify-content: center;
font-size: 16px;
}
.kpi-val {
font-size: 26px;
font-weight: 800;
color: #0f172a !important;
letter-spacing: -0.5px;
margin: 4px 0 6px 0;
}
.kpi-sub {
font-size: 12px;
font-weight: 600;
display: flex;
align-items: center;
gap: 5px;
}

/* Regional Farm Profiles Cards (EnerSol Solar Farm Card style) */
.farm-profile-card {
background: #ffffff;
border-radius: 18px;
padding: 18px 20px;
border: 1.5px solid #e2e8f0;
margin-bottom: 16px;
box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.04);
transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
color: #0f172a !important;
}
.farm-profile-card:hover {
transform: translateY(-3px);
box-shadow: 0 12px 28px -4px rgba(15, 23, 42, 0.1);
border-color: #cbd5e1;
}
.farm-profile-card.breach {
border-color: #f43f5e;
background: #fff1f2;
box-shadow: 0 6px 20px -2px rgba(244, 63, 94, 0.15);
}
.farm-profile-card.held {
border-color: #f59e0b;
background: #fffbeb;
box-shadow: 0 6px 20px -2px rgba(245, 158, 11, 0.15);
}
.farm-profile-card.rejected {
border-color: #94a3b8;
background: #f8fafc;
}

.farm-card-header {
display: flex;
justify-content: space-between;
align-items: flex-start;
margin-bottom: 12px;
}
.farm-title {
font-size: 15px;
font-weight: 800;
color: #0f172a !important;
letter-spacing: -0.3px;
}
.farm-location {
font-size: 12px;
color: #64748b !important;
margin-top: 2px;
font-weight: 500;
}
.node-tag {
font-size: 11px;
font-weight: 700;
background: #f1f5f9;
color: #334155 !important;
padding: 3px 8px;
border-radius: 8px;
font-family: 'JetBrains Mono', monospace;
border: 1px solid #e2e8f0;
}

/* Gauge / Progress Bar for Moisture */
.moisture-track-box {
background: rgba(241, 245, 249, 0.7);
border-radius: 12px;
padding: 10px 12px;
margin-bottom: 12px;
border: 1px solid rgba(226, 232, 240, 0.8);
}
.moisture-label-row {
display: flex;
justify-content: space-between;
font-size: 11.5px;
font-weight: 600;
color: #475569 !important;
margin-bottom: 6px;
}
.moisture-bar-bg {
width: 100%;
height: 7px;
background: #e2e8f0;
border-radius: 999px;
overflow: hidden;
}
.moisture-bar-fill {
height: 100%;
border-radius: 999px;
transition: width 0.4s ease;
}

/* 3 Micro-Metrics */
.metrics-row {
display: grid;
grid-template-columns: 1fr 1fr 1fr;
gap: 6px;
margin-bottom: 12px;
}
.metric-chip {
background: #ffffff;
border: 1px solid #e2e8f0;
border-radius: 10px;
padding: 6px 8px;
text-align: center;
}
.metric-chip-lbl {
font-size: 10px;
text-transform: uppercase;
color: #64748b !important;
font-weight: 700;
letter-spacing: 0.3px;
display: block;
}
.metric-chip-val {
font-size: 13px;
font-weight: 800;
color: #0f172a !important;
margin-top: 2px;
display: block;
}

/* Card Footer Status Chips */
.card-footer-row {
display: flex;
justify-content: space-between;
align-items: center;
padding-top: 4px;
}
.chip-crypto {
font-size: 10.5px;
font-weight: 700;
font-family: 'JetBrains Mono', monospace;
padding: 3px 8px;
border-radius: 10px;
}
.chip-crypto.ok {
background: #ecfdf5;
color: #059669 !important;
border: 1px solid #a7f3d0;
}
.chip-crypto.pending {
background: #fef3c7;
color: #d97706 !important;
border: 1px solid #fde68a;
}
.chip-status {
font-size: 11px;
font-weight: 800;
text-transform: uppercase;
letter-spacing: 0.4px;
}
.chip-status.normal {
color: #16a34a !important;
}
.chip-status.breach {
color: #e11d48 !important;
}
.chip-status.held {
color: #d97706 !important;
}

/* Basis Risk Side-by-Side Cards */
.basis-box {
background: #ffffff;
border-radius: 18px;
padding: 22px 24px;
border: 1.5px solid #e2e8f0;
box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.04);
height: 100%;
color: #0f172a !important;
}
.basis-box.pmfby {
border-left: 6px solid #64748b;
background: #f8fafc;
}
.basis-box.agrisentinel {
border-left: 6px solid #10b981;
background: #ffffff;
}
.basis-tag {
font-size: 11px;
font-weight: 700;
text-transform: uppercase;
letter-spacing: 0.5px;
color: #64748b !important;
margin-bottom: 6px;
}
.basis-name {
font-size: 18px;
font-weight: 800;
color: #0f172a !important;
margin-bottom: 12px;
}

/* Buttons styling */
div.stButton > button {
border-radius: 12px !important;
font-weight: 700 !important;
font-size: 13.5px !important;
padding: 10px 20px !important;
transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
border: 1.5px solid #cbd5e1 !important;
background: #ffffff !important;
color: #0f172a !important;
box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04) !important;
}
div.stButton > button:hover {
border-color: #10b981 !important;
color: #059669 !important;
background: #f0fdf4 !important;
transform: translateY(-1px) !important;
box-shadow: 0 4px 12px rgba(16, 185, 129, 0.15) !important;
}
</style>""", unsafe_allow_html=True)

# SIDEBAR: Configuration & Integrity Controls
st.sidebar.title("🛡️ Underwriter Controls")
st.sidebar.caption("AgriSentinel v2.2 | Cryptographic Parametric Cockpit")

# Secrets loaded safely from environment
env_twilio_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
env_twilio_phone = os.getenv("TWILIO_PHONE_NUMBER", "")
env_groq_set = bool(os.getenv("GROQ_API_KEY"))
env_owm_set = bool(os.getenv("OPENWEATHER_API_KEY"))

with st.sidebar.expander("🔑 Integration Credentials", expanded=False):
    st.markdown("**Environment Configuration Status:**")
    st.write(f"- Twilio SID: `{'Configured' if env_twilio_sid else 'Missing (Simulation Mode)'}`")
    st.write(f"- Groq AI Key: `{'Configured' if env_groq_set else 'Missing (Rulebase Mode)'}`")
    st.write(f"- OpenWeatherMap: `{'Configured' if env_owm_set else 'Missing (Baseline Mode)'}`")
    st.caption("Secrets are read strictly from your local `.env` file and are never committed to Git.")

st.sidebar.markdown("---")
st.sidebar.subheader("🔄 Demo Session Reset")
st.sidebar.caption("Restores all 9 farm profiles to nominal baselines and flushes the cryptographic replay cache.")

if st.sidebar.button("🧹 Reset Demo State", use_container_width=True):
    try:
        r = requests.post(f"{API_BASE}/api/policies/reset", timeout=3).json()
        st.sidebar.success(r.get("message", "Reset complete"))
        time.sleep(0.5)
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"Reset failed: {e}")

# MAIN EXECUTIVE HEADER (EnerSol / Fyntra style)
st.markdown("""<div class="top-hero-card">
<div class="hero-brand">
<div class="brand-icon-box">🌾</div>
<div>
<h1 class="hero-title">AgriSentinel</h1>
<div class="hero-subtitle">Decentralized Proof-of-Location & Hardware-Signed Telemetry for Zero-Delay Parametric Crop Insurance</div>
</div>
</div>
<div class="hero-badges">
<span class="hero-pill live">● 9 Regional Nodes Active</span>
<span class="hero-pill crypto">🔐 ECDSA SECP256k1 Silicon Trust</span>
<span class="hero-pill">🛰️ OpenWeather Station Grid</span>
<span class="hero-pill">📞 2G Regional Voice Dispatch</span>
</div>
</div>""", unsafe_allow_html=True)

# Fetch backend state
try:
    grid_res = requests.get(f"{API_BASE}/api/grid", timeout=3).json()
    claims_res = requests.get(f"{API_BASE}/api/claims", timeout=3).json()
    audit_res = requests.get(f"{API_BASE}/api/audit", timeout=3).json()
    basis_res = requests.get(f"{API_BASE}/api/basis-risk-comparison", timeout=3).json()
    
    grid_data = grid_res.get("grid", [])
    claims_data = claims_res.get("claims", [])
    audit_data = audit_res.get("audit_log", [])
    tamper_blocked_count = grid_res.get("tamper_attempts_blocked", 0)
except Exception as e:
    st.error(f"⚠️ Cannot connect to AgriSentinel Backend at `{API_BASE}`.")
    st.info("Start the FastAPI backend: `python -m uvicorn backend:app --host 127.0.0.1 --port 8000 --reload`")
    st.stop()

# TOP KPI METRICS (Fyntra & EnerSol modern cards)
total_farms = len(grid_data)
active_policies = sum(1 for p in grid_data if p.get("active"))
total_underwritten = sum(p.get("sum_insured_inr", 0) for p in grid_data)
total_claims_count = len(claims_data)
total_benefit_calculated = sum(c.get("payout_calculated_inr", 0) for c in claims_data)

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""<div class="kpi-card">
<div class="kpi-top">
<span class="kpi-label">Monitored Profiles</span>
<div class="kpi-icon-badge" style="background:#ecfdf5; color:#059669;">🌱</div>
</div>
<div class="kpi-val">{total_farms} Farms</div>
<div class="kpi-sub" style="color:#059669;">
<span>↑ 100%</span> 9 Indian Agro-Climatic States
</div>
</div>""", unsafe_allow_html=True)

with k2:
    st.markdown(f"""<div class="kpi-card">
<div class="kpi-top">
<span class="kpi-label">Total Underwritten</span>
<div class="kpi-icon-badge" style="background:#eff6ff; color:#2563eb;">🛡️</div>
</div>
<div class="kpi-val">₹{total_underwritten:,.0f}</div>
<div class="kpi-sub" style="color:#2563eb;">
<span>● {active_policies} Active</span> Micro-Riders In Force
</div>
</div>""", unsafe_allow_html=True)

with k3:
    st.markdown(f"""<div class="kpi-card">
<div class="kpi-top">
<span class="kpi-label">Claims Assessed</span>
<div class="kpi-icon-badge" style="background:#fff1f2; color:#e11d48;">📑</div>
</div>
<div class="kpi-val">₹{total_benefit_calculated:,.0f}</div>
<div class="kpi-sub" style="color:#e11d48;">
<span>{total_claims_count} Intents</span> Zero-Delay Parametric Trigger
</div>
</div>""", unsafe_allow_html=True)

with k4:
    st.markdown(f"""<div class="kpi-card">
<div class="kpi-top">
<span class="kpi-label">Fraud Defense Gateway</span>
<div class="kpi-icon-badge" style="background:#f5f3ff; color:#7c3aed;">🔐</div>
</div>
<div class="kpi-val">{tamper_blocked_count} Blocked</div>
<div class="kpi-sub" style="color:#7c3aed;">
<span>ECDSA + Weather</span> Silicon Root-of-Trust
</div>
</div>""", unsafe_allow_html=True)

st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

# MAIN TAB NAVIGATION (Styled as floating modern pills)
tab_cockpit, tab_basis_risk, tab_antifraud, tab_claims, tab_roi = st.tabs([
    "🌾 Regional Profiles",
    "⚖️ Basis Risk Comparison",
    "🛡️ Cryptographic Anti-Fraud",
    "📑 Claims & Audit Ledger",
    "💰 Insurer Unit Economics"
])

# -------------------------------------------------------------
# TAB 1: 9 REGIONAL FARM PROFILES
# -------------------------------------------------------------
with tab_cockpit:
    c_head, c_btn = st.columns([3, 1])
    with c_head:
        st.subheader("9 Calibrated Regional Farm Profiles Across India")
        st.caption("Each farm is bound to an SECP256k1 hardware node measuring on-plot micro-climate telemetry. Updates from Godot appear here in real-time.")
    with c_btn:
        if st.button("🔄 Refresh Live Telemetry", use_container_width=True):
            st.rerun()

    cols = st.columns(3)
    for i, farm in enumerate(grid_data):
        col_idx = i % 3
        status = farm.get("status", "NORMAL")
        moisture = float(farm.get("soil_moisture", 30.0))
        temp = float(farm.get("temperature", 28.0))
        rainfall = float(farm.get("rainfall_mm", 0.0))
        cover = float(farm.get("sum_insured_inr", 50000.0))
        crypto_status = farm.get("crypto_status", "PENDING")

        card_class = "farm-profile-card"
        gauge_gradient = "linear-gradient(90deg, #10b981, #34d399)"
        status_label = "● NORMAL"
        status_class = "normal"

        if status == "PARAMETRIC_BREACH":
            card_class += " breach"
            gauge_gradient = "linear-gradient(90deg, #f43f5e, #fb7185)"
            status_label = "🚨 BREACH DETECTED"
            status_class = "breach"
        elif status == "HELD_FOR_INSPECTION":
            card_class += " held"
            gauge_gradient = "linear-gradient(90deg, #f59e0b, #fbbf24)"
            status_label = "⚠️ AUDIT HELD"
            status_class = "held"
        elif status == "SECURITY_REJECTED":
            card_class += " rejected"
            gauge_gradient = "linear-gradient(90deg, #94a3b8, #cbd5e1)"
            status_label = "🛑 REJECTED"
            status_class = "held"
        elif moisture < 20.0:
            gauge_gradient = "linear-gradient(90deg, #f59e0b, #fbbf24)"

        # Calculate gauge percent (clamp 0 to 100)
        gauge_pct = min(100.0, max(5.0, moisture))

        with cols[col_idx]:
            st.markdown(f"""<div class="{card_class}">
<div class="farm-card-header">
<div>
<div class="farm-title">{farm['plot_id'].upper()}: {farm['farmer_name']}</div>
<div class="farm-location">🌾 <b>{farm['crop']}</b> • {farm['district']}, {farm['state']}</div>
</div>
<span class="node-tag">{farm['node_id']}</span>
</div>

<div class="moisture-track-box">
<div class="moisture-label-row">
<span>SOIL MOISTURE</span>
<b style="color:#0f172a !important;">{moisture:.1f}%</b>
</div>
<div class="moisture-bar-bg">
<div class="moisture-bar-fill" style="width:{gauge_pct}%; background:{gauge_gradient};"></div>
</div>
</div>

<div class="metrics-row">
<div class="metric-chip">
<span class="metric-chip-lbl">TEMP</span>
<span class="metric-chip-val">{temp:.1f}°C</span>
</div>
<div class="metric-chip">
<span class="metric-chip-lbl">RAIN</span>
<span class="metric-chip-val">{rainfall:.1f} mm</span>
</div>
<div class="metric-chip">
<span class="metric-chip-lbl">COVER</span>
<span class="metric-chip-val">₹{cover/1000:.0f}k</span>
</div>
</div>

<div class="card-footer-row">
<span class="chip-crypto {'ok' if 'VALID' in crypto_status else 'pending'}">{crypto_status}</span>
<span class="chip-status {status_class}">{status_label}</span>
</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
    st.subheader("🌾 Regional Farm Agronomic Advisory & 2G Voice Broadcast")
    st.caption("Inspect dynamic ICAR agronomic recommendations or dispatch automated 2G IVR voice phone calls in regional languages.")

    sel_plot = st.selectbox(
        "Select a Farm Profile to Inspect Advisory & Telecom Broadcast:",
        [f"{p['plot_id']} - {p['farmer_name']} ({p['crop']}, {p['state']})" for p in grid_data]
    )
    selected_pid = sel_plot.split(" - ")[0]
    curr_farm = next((p for p in grid_data if p['plot_id'] == selected_pid), {})

    col_adv_left, col_adv_right = st.columns([1.2, 1])
    with col_adv_left:
        st.markdown(f"**🌱 Agronomic Advisory Engine: {curr_farm.get('crop')} ({curr_farm.get('state')})**")
        if st.button(f"🔍 Generate Live Agronomic Advisory for {selected_pid.upper()}", use_container_width=True):
            try:
                adv = requests.get(f"{API_BASE}/api/advisory/{selected_pid}", timeout=5).json()
                st.markdown(f"""<div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:14px; padding:16px; margin-top:10px;">
<div style="font-size:13px; color:#64748b; font-weight:600;">STATUS: <b style="color:#0f172a;">{adv.get('condition')}</b></div>
<div style="margin-top:10px; font-weight:700; font-size:13px; color:#0f172a;">Recommended Field Actions (English):</div>
<ul style="margin:4px 0 10px 18px; font-size:12.5px; color:#334155;">
{''.join(f'<li>{act}</li>' for act in adv.get('actions_english', []))}
</ul>
<div style="margin-top:8px; font-weight:700; font-size:13px; color:#059669;">Regional Language Guidance ({adv.get('language_name')}):</div>
<ul style="margin:4px 0 10px 18px; font-size:12.5px; color:#065f46;">
{''.join(f'<li>{act}</li>' for act in adv.get('actions_regional', []))}
</ul>
<div style="background:#fff7ed; border-left:4px solid #f97316; padding:8px 12px; border-radius:6px; font-size:12px; color:#9a3412;">
⚠️ <b>Caution:</b> {adv.get('spray_caution')}
</div>
</div>""", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Failed to generate advisory: {e}")

    with col_adv_right:
        st.markdown("**📞 2G Regional Telecom Broadcast**")
        st.markdown(f"""<div style="background:#ffffff; border-radius:14px; padding:14px 16px; margin-bottom:12px; font-size:12px; border:1px solid #e2e8f0; color:#0f172a !important; box-shadow:0 2px 8px rgba(15,23,42,0.03);">
<div style="font-weight:700; font-size:13px; margin-bottom:6px; color:#0f172a;">Broadcast Target: {selected_pid.upper()} ({curr_farm.get('farmer_name')})</div>
<div style="display:grid; grid-template-columns:1fr 1fr; gap:6px; color:#475569;">
<div>• Moisture: <b style="color:#0f172a;">{curr_farm.get('soil_moisture', 0.0):.1f}%</b></div>
<div>• Temp: <b style="color:#0f172a;">{curr_farm.get('temperature', 0.0):.1f}°C</b></div>
<div>• Status: <b style="color:#0f172a;">{curr_farm.get('status', 'NORMAL')}</b></div>
<div>• Max Cover: <b style="color:#0f172a;">₹{curr_farm.get('sum_insured_inr', 0):,.0f}</b></div>
</div>
</div>""", unsafe_allow_html=True)
        target_phone = st.text_input("Destination Farmer Mobile (E.164):", value="+919363849952")
        if st.button("📲 Dispatch Outbound Voice Alert", use_container_width=True):
            try:
                voice_res = requests.post(
                    f"{API_BASE}/api/telecom/trigger-voice",
                    json={"plot_id": selected_pid, "phone_number": target_phone},
                    timeout=8
                ).json()
                if voice_res.get("status") == "QUEUED":
                    st.success(f"📞 Live call queued via Twilio to {target_phone} (Call SID: {voice_res.get('call_sid')})")
                elif voice_res.get("status") == "SIMULATED_VOICE_DISPATCH":
                    st.info("🎙️ Call Verified in Simulation Mode. Regional TwiML IVR generated.")
                else:
                    st.warning("⚠️ Live Twilio dispatch not active. Showing generated regional TwiML voice payload below:")
                with st.expander("📜 Preview TwiML Voice XML Webhook Payload", expanded=False):
                    st.code(voice_res.get("twiml_preview", ""), language="xml")
            except Exception as e:
                st.error(f"Voice dispatch failed: {e}")

# -------------------------------------------------------------
# TAB 2: BASIS RISK COMPARATIVE ANALYSIS
# -------------------------------------------------------------
with tab_basis_risk:
    st.subheader("⚖️ The Core Problem: Eliminating Basis Risk in Crop Insurance")
    st.caption("Side-by-side comparison: Why traditional area-approach insurance fails smallholder farmers vs. AgriSentinel's cryptographic micro-grid.")

    pmfby = basis_res.get("traditional_pmfby_station", {})
    agri = basis_res.get("agrisentinel_hyperlocal_node", {})

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""<div class="basis-box pmfby">
<div class="basis-tag">TRADITIONAL AREA-LEVEL INSURANCE (PMFBY)</div>
<div class="basis-name">🏛️ {pmfby.get('name', 'District IMD Weather Station')}</div>
<div style="font-size:12px; color:#64748b; margin-bottom:14px;">
DISTANCE: <b>{pmfby.get('distance_from_farm_km', 15.2)} KM AWAY</b> (COARSE RESOLUTION)
</div>
<div style="font-size:13px; line-height:1.7; color:#334155;">
• <b>Measured Temperature:</b> {pmfby.get('recorded_temperature_c', 28.5)}°C<br>
• <b>Measured Rainfall (1h):</b> {pmfby.get('recorded_rainfall_1h_mm', 0.0)} mm<br>
• <b>Assessment:</b> {pmfby.get('station_status')}
</div>
<div style="background:#fee2e2; border-left:4px solid #ef4444; padding:12px 14px; border-radius:8px; margin-top:16px;">
<b style="color:#991b1b; font-size:14px;">❌ {pmfby.get('claim_decision')}</b>
<div style="font-size:12px; color:#7f1d1d; margin-top:4px;">
{pmfby.get('basis_risk_explanation')}
</div>
</div>
</div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""<div class="basis-box agrisentinel">
<div class="basis-tag" style="color:#059669 !important;">AGRISENTINEL CRYPTOGRAPHIC ON-PLOT NODE</div>
<div class="basis-name">📡 {agri.get('name', 'AgriSentinel Hyperlocal Node')}</div>
<div style="font-size:12px; color:#059669; margin-bottom:14px;">
LOCATION: <b>DIRECTLY ON-PLOT</b> (50m × 50m RESOLUTION)
</div>
<div style="font-size:13px; line-height:1.7; color:#334155;">
• <b>On-Plot Soil Moisture:</b> <b style="color:#e11d48;">{agri.get('on_farm_soil_moisture_pct', 11.2)}%</b> (Contract Threshold: {agri.get('contractual_drought_threshold', 18.0)}%)<br>
• <b>On-Plot Temperature:</b> {agri.get('on_farm_temperature_c', 42.1)}°C<br>
• <b>Cryptographic Verification:</b> <span class="chip-crypto ok">{agri.get('crypto_verification')}</span><br>
• <b>Weather Cross-Check:</b> {agri.get('weather_corroboration')}
</div>
<div style="background:#ecfdf5; border-left:4px solid #10b981; padding:12px 14px; border-radius:8px; margin-top:16px;">
<b style="color:#065f46; font-size:14px;">✅ {agri.get('simulated_claim_status')}</b>
<div style="font-size:12px; color:#047857; margin-top:4px;">
Settlement Status: {agri.get('settlement_integration')}<br>
Voice Dispatch: {agri.get('voice_dispatch')}
</div>
</div>
</div>""", unsafe_allow_html=True)

# -------------------------------------------------------------
# TAB 3: CRYPTOGRAPHIC VERIFICATION & ANTI-FRAUD
# -------------------------------------------------------------
with tab_antifraud:
    st.subheader("🛡️ Cryptographic Data-Trust & Replay Defense Test Harness")
    st.caption("Demonstrate how the gateway rejects spoofed keys, corrupted payloads, replayed packets, and physical bucket immersion anomalies.")

    t_col1, t_col2 = st.columns(2)
    with t_col1:
        st.markdown(f"""<div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:16px; padding:20px; box-shadow:0 2px 8px rgba(15,23,42,0.03);">
<div style="font-size:15px; font-weight:800; color:#0f172a; margin-bottom:6px;">1. Test Cryptographic Signature Defense</div>
<div style="font-size:12.5px; color:#64748b; margin-bottom:14px;">Submit an altered telemetry packet with corrupted ECDSA signature bytes to verify HTTP 403 rejection:</div>
</div>""", unsafe_allow_html=True)
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        if st.button("🧪 Transmit Corrupted SECP256k1 Signature", use_container_width=True):
            bad_payload = {
                "node_id": "node_1",
                "plot_id": "plot_1",
                "signature": "30440220111111111111111111111111111111111111111111111111111111111111111102202222222222222222222222222222222222222222222222222222222222222222",
                "telemetry": {
                    "plot_id": "plot_1",
                    "timestamp": time.time(),
                    "temperature": 41.5,
                    "humidity": 45.0,
                    "pressure": 1012.0,
                    "soil_moisture": 11.0,
                    "rainfall_mm": 0.0
                }
            }
            try:
                res = requests.post(f"{API_BASE}/api/telemetry", json=bad_payload)
                if res.status_code == 403:
                    st.error("🛡️ HTTP 403 FORBIDDEN: Cryptographic gateway successfully blocked tampered signature!")
                    st.json(res.json())
                else:
                    st.warning(f"Response: {res.status_code}")
            except Exception as e:
                st.error(f"Error testing crypto: {e}")

    with t_col2:
        st.markdown(f"""<div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:16px; padding:20px; box-shadow:0 2px 8px rgba(15,23,42,0.03);">
<div style="font-size:15px; font-weight:800; color:#0f172a; margin-bottom:6px;">2. Test Physical Bucket-Immersion Anomaly Hold</div>
<div style="font-size:12.5px; color:#64748b; margin-bottom:14px;">Simulate sensor submerged in water (95% moisture) while satellite/weather station reports 0 rain and clear skies:</div>
</div>""", unsafe_allow_html=True)
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        if st.button("🪣 Transmit Bucket Immersion Divergence (95% Moisture, 0 Rain)", use_container_width=True):
            try:
                override_payload = {
                    "plot_id": "plot_1",
                    "soil_moisture": 95.0,
                    "temperature": 32.0,
                    "humidity": 40.0,
                    "pressure": 1012.0,
                    "rainfall_mm": 0.0
                }
                res = requests.post(f"{API_BASE}/api/manual-trigger", json=override_payload).json()
                eval_res = res.get("evaluation", {})
                if eval_res.get("status") == "HELD_PHYSICAL_DIVERGENCE_AUDIT":
                    st.warning("🛑 AUDIT HOLD ACTIVATED: Ingestion engine flagged physical divergence!")
                    st.write(f"Reason: {eval_res.get('reason')}")
                else:
                    st.json(eval_res)
            except Exception as e:
                st.error(f"Error: {e}")

# -------------------------------------------------------------
# TAB 4: SIMULATED CLAIMS & AUDIT LEDGER
# -------------------------------------------------------------
with tab_claims:
    st.subheader("📑 Parametric Claims & Cryptographic Audit Ledger")
    st.caption("Demonstration ledger: Every event binds on-plot telemetry, SECP256k1 key verification, and meteorological cross-checks.")

    st.markdown("#### 📜 Generated Claim Intents (Simulated Parametric Micro-Riders)")
    if claims_data:
        df_claims = pd.DataFrame(claims_data)
        display_cols = ["claim_id", "plot_id", "farmer_name", "crop", "state", "payout_calculated_inr", "trigger_reason", "assessment_status", "settlement_status"]
        valid_cols = [c for c in display_cols if c in df_claims.columns]
        st.dataframe(df_claims[valid_cols], use_container_width=True)
    else:
        st.info("No parametric breach claims generated yet. Trigger a scenario from Godot or Tab 3.")

    st.markdown("#### 🔒 Cryptographic Audit Trail")
    if audit_data:
        df_audit = pd.DataFrame(audit_data)
        display_audit_cols = ["log_id", "node_id", "plot_id", "crypto_status", "weather_status", "soil_moisture", "temperature", "notes"]
        valid_audit_cols = [c for c in display_audit_cols if c in df_audit.columns]
        st.dataframe(df_audit[valid_audit_cols], use_container_width=True)
    else:
        st.info("Audit log is currently empty.")

# -------------------------------------------------------------
# TAB 5: INSURER UNIT ECONOMICS & LATE-PENALTY SAVINGS
# -------------------------------------------------------------
with tab_roi:
    st.subheader("💰 Insurer Business Model & ROI Calculator")
    st.caption("Why insurers finance the ₹1,200 AgriSentinel edge nodes instead of passing costs to farmers.")

    st.markdown("""Under PMFBY guidelines, insurers face a statutory **12% annual interest penalty** for claim delays exceeding statutory benchmarks, alongside spending **₹400–₹800 per hectare** on dispute-ridden manual Crop Cutting Experiments (CCEs).""")

    c_calc1, c_calc2 = st.columns([1, 1])
    with c_calc1:
        insured_hectares = st.slider("Insured Farm Area (Hectares):", min_value=100, max_value=50000, value=5000, step=500)
        cce_cost_per_ha = st.slider("Average Manual CCE & Surveyor Cost (₹/ha):", min_value=200, max_value=1200, value=600, step=50)
        disputed_claims_pct = st.slider("Historical Disputed / Delayed Claim Rate (%):", min_value=5, max_value=40, value=18, step=1)
        node_cost = 1200.0  # ₹1,200 target BOM per node

    with c_calc2:
        total_nodes = int(insured_hectares / 2)  # 1 node per 2-hectare cluster
        capex_investment = total_nodes * node_cost
        cce_savings = insured_hectares * cce_cost_per_ha * 0.75  # 75% reduction in manual disputes
        penalty_avoidance = (insured_hectares * 25000 * (disputed_claims_pct / 100)) * 0.12  # 12% statutory penalty avoidance
        total_annual_savings = cce_savings + penalty_avoidance
        payback_months = (capex_investment / total_annual_savings) * 12

        st.markdown(f"""<div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:16px; padding:22px; box-shadow:0 4px 16px -2px rgba(15,23,42,0.04);">
<div style="font-size:12px; text-transform:uppercase; color:#64748b; font-weight:800; letter-spacing:0.5px;">Financial Feasibility Model</div>
<div style="margin-top:12px; font-size:14.5px; line-height:1.7; color:#334155;">
• Total Hardware Investment ({total_nodes:,} nodes @ ₹1,200): <b>₹{capex_investment:,.0f}</b><br>
• Manual CCE Survey Cost Savings: <b>₹{cce_savings:,.0f}/year</b><br>
• 12% Statutory Late-Penalty Avoidance: <b>₹{penalty_avoidance:,.0f}/year</b><br>
• <b>Total Insurer Annual Savings:</b> <span style="color:#059669; font-weight:800; font-size:19px;">₹{total_annual_savings:,.0f}</span>
</div>
<div style="margin-top:16px; background:#ecfdf5; padding:14px; border-radius:12px; border:1px solid #a7f3d0;">
<b style="color:#065f46; font-size:16px;">⏱️ Payback Period: {payback_months:.1f} Months</b>
<div style="font-size:12px; color:#047857; margin-top:3px;">
The hardware deployment fully pays for itself in less than one full Kharif-Rabi cropping cycle.
</div>
</div>
</div>""", unsafe_allow_html=True)
