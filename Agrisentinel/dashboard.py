"""
AgriSentinel Insurer Operations Cockpit & Anti-Fraud Dashboard
============================================================
Streamlit dashboard for insurance underwriters and hackathon judges to inspect:
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
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Enterprise CSS Theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #0d1b2a, #1b263b, #1b4332);
        color: white;
        padding: 22px 28px;
        border-radius: 14px;
        margin-bottom: 20px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        border: 1px solid rgba(255,255,255,0.1);
    }
    .main-header h1 {
        font-size: 26px;
        font-weight: 800;
        margin: 0 0 6px 0;
        letter-spacing: -0.5px;
    }
    .main-header .sub-header {
        font-size: 13px;
        opacity: 0.85;
    }
    
    .status-badge-bar {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        margin-top: 12px;
    }
    .status-pill {
        background: rgba(255,255,255,0.12);
        padding: 4px 10px;
        border-radius: 16px;
        font-size: 11px;
        font-family: 'JetBrains Mono', monospace;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .metric-card {
        background: #ffffff;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        border-left: 5px solid #2d6a4f;
    }
    .metric-card.alert {
        border-left-color: #d90429;
    }
    .metric-card.shield {
        border-left-color: #2b2d42;
    }
    .metric-val {
        font-size: 24px;
        font-weight: 800;
        color: #1a202c;
        margin: 4px 0;
    }
    .metric-lbl {
        font-size: 12px;
        text-transform: uppercase;
        color: #64748b;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    .farm-card {
        background: #ffffff;
        border-radius: 10px;
        padding: 14px 16px;
        border: 1px solid #cbd5e1;
        margin-bottom: 12px;
        transition: transform 0.15s ease;
    }
    .farm-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .farm-card.breach {
        border: 2px solid #ef4444;
        background: #fef2f2;
    }
    .farm-card.held {
        border: 2px solid #f59e0b;
        background: #fffbeb;
    }
    .farm-card.rejected {
        border: 2px solid #6b7280;
        background: #f3f4f6;
    }

    .basis-card {
        padding: 18px 22px;
        border-radius: 12px;
        height: 100%;
    }
    .basis-card.pmfby {
        background: #f8fafc;
        border: 1.5px solid #cbd5e1;
        border-left: 6px solid #64748b;
    }
    .basis-card.agrisentinel {
        background: #f0fdf4;
        border: 1.5px solid #86efac;
        border-left: 6px solid #16a34a;
    }
    .basis-title {
        font-size: 16px;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .basis-subtitle {
        font-size: 11px;
        text-transform: uppercase;
        color: #64748b;
        font-weight: 600;
        margin-bottom: 12px;
    }
    .tag-crypto-ok {
        background: #dcfce7;
        color: #166534;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
    }
    .tag-crypto-fail {
        background: #fee2e2;
        color: #991b1b;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
    }
</style>
""", unsafe_allow_html=True)

# SIDEBAR: Configuration & Integrity Controls
st.sidebar.title("🛡️ Underwriter Controls")
st.sidebar.caption("AgriSentinel v2.1 | Cryptographic Ingestion & Anti-Fraud Engine")

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

# MAIN HEADER BANNER
st.markdown("""
<div class="main-header">
    <h1>🌾 AGRISENTINEL | Parametric Insurer Operations Cockpit</h1>
    <div class="sub-header">
        Decentralized Proof-of-Location & Hardware-Signed Telemetry for Zero-Delay Parametric Crop Insurance
    </div>
    <div class="status-badge-bar">
        <span class="status-pill">🔐 SILICON CRYPTO: ECDSA SECP256k1 (REGISTERED REGISTRY)</span>
        <span class="status-pill">📡 WEATHER: OPENWEATHERMAP STATION GRID & REGIONAL BASELINES</span>
        <span class="status-pill">📞 2G VOICE: TWILIO IVR ADVISORY (TAMIL / HINDI)</span>
        <span class="status-pill">⚖️ UNDERWRITING: PARAMETRIC MICRO-RIDER WORKFLOW</span>
    </div>
</div>
""", unsafe_allow_html=True)

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

# TOP KPI METRICS
total_farms = len(grid_data)
active_policies = sum(1 for p in grid_data if p.get("active"))
total_underwritten = sum(p.get("sum_insured_inr", 0) for p in grid_data)
total_claims_count = len(claims_data)
total_benefit_calculated = sum(c.get("payout_calculated_inr", 0) for c in claims_data)

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-lbl">Monitored Farm Profiles</div>
        <div class="metric-val">{total_farms}</div>
        <div style="font-size:12px; color:#2d6a4f; font-weight:600;">9 Indian Agro-Climatic States</div>
    </div>
    """, unsafe_allow_html=True)
with m2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-lbl">Total Underwritten Value</div>
        <div class="metric-val">₹{total_underwritten:,.0f}</div>
        <div style="font-size:12px; color:#2d6a4f; font-weight:600;">{active_policies} Active Micro-Riders</div>
    </div>
    """, unsafe_allow_html=True)
with m3:
    st.markdown(f"""
    <div class="metric-card alert">
        <div class="metric-lbl">Simulated Benefit Assessed</div>
        <div class="metric-val">₹{total_benefit_calculated:,.0f}</div>
        <div style="font-size:12px; color:#d90429; font-weight:600;">{total_claims_count} Claim Intents Generated</div>
    </div>
    """, unsafe_allow_html=True)
with m4:
    st.markdown(f"""
    <div class="metric-card shield">
        <div class="metric-lbl">Tamper / Spoof Attempts Blocked</div>
        <div class="metric-val">{tamper_blocked_count}</div>
        <div style="font-size:12px; color:#4a5568; font-weight:600;">SECP256k1 & Meteorological Gate</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# MAIN TAB NAVIGATION
tab_cockpit, tab_basis_risk, tab_antifraud, tab_claims, tab_roi = st.tabs([
    "🌾 1. Regional Farm Profiles",
    "⚖️ 2. Basis Risk Comparison",
    "🛡️ 3. Cryptographic Verification & Anti-Fraud",
    "📑 4. Simulated Claims & Audit Ledger",
    "💰 5. Insurer Unit Economics & Penalty Savings"
])

# -------------------------------------------------------------
# TAB 1: 9 REGIONAL FARM PROFILES
# -------------------------------------------------------------
with tab_cockpit:
    st.subheader("9 Calibrated Regional Farm Profiles Across India")
    st.caption("Each farm is bound to a registered SECP256k1 hardware node measuring on-plot micro-climate telemetry.")

    cols = st.columns(3)
    for i, farm in enumerate(grid_data):
        col_idx = i % 3
        status = farm.get("status", "NORMAL")
        card_class = "farm-card"
        if status == "PARAMETRIC_BREACH":
            card_class += " breach"
        elif status == "HELD_FOR_INSPECTION":
            card_class += " held"
        elif status == "SECURITY_REJECTED":
            card_class += " rejected"

        with cols[col_idx]:
            st.markdown(f"""
            <div class="{card_class}">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="font-size:15px;">{farm['plot_id'].upper()}: {farm['farmer_name']}</b>
                    <span style="font-size:11px; background:#e2e8f0; padding:2px 6px; border-radius:10px; font-weight:600;">{farm['node_id']}</span>
                </div>
                <div style="font-size:12px; color:#475569; margin:3px 0 8px 0;">
                    🌾 <b>{farm['crop']}</b> | 📍 {farm['district']}, {farm['state']}
                </div>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:6px; font-size:12px; background:rgba(0,0,0,0.02); padding:8px; border-radius:6px;">
                    <div>💧 Moisture: <b>{farm['soil_moisture']:.1f}%</b></div>
                    <div>🌡️ Temp: <b>{farm['temperature']:.1f}°C</b></div>
                    <div>🌧️ Rainfall: <b>{farm['rainfall_mm']:.1f} mm</b></div>
                    <div>🛡️ Cover: <b>₹{farm['sum_insured_inr']:,.0f}</b></div>
                </div>
                <div style="margin-top:8px; font-size:11px; display:flex; justify-content:space-between;">
                    <span class="{'tag-crypto-ok' if 'VALID' in farm['crypto_status'] else 'tag-crypto-fail'}">{farm['crypto_status']}</span>
                    <span style="color:#64748b; font-weight:600;">{farm['status']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🌾 Farm Agronomic Advisory & Regional Voice Dispatch")
    sel_plot = st.selectbox(
        "Select a Farm Profile to Inspect Live Agronomic Recommendations:",
        [f"{p['plot_id']} - {p['farmer_name']} ({p['crop']}, {p['state']})" for p in grid_data]
    )
    selected_pid = sel_plot.split(" - ")[0]

    col_adv_left, col_adv_right = st.columns([2, 1])
    with col_adv_left:
        if st.button(f"🔍 Generate Agronomic Advisory for {selected_pid.upper()}"):
            try:
                adv = requests.get(f"{API_BASE}/api/advisory/{selected_pid}", timeout=5).json()
                st.markdown(f"**Crop:** {adv.get('crop')} | **Region:** {adv.get('state')} | **Growth Status:** {adv.get('condition')}")
                st.info(f"💡 **Recommended Field Actions (English):**\n- " + "\n- ".join(adv.get("actions_english", [])))
                st.success(f"🗣️ **Regional Language ({adv.get('language_name')}):**\n- " + "\n- ".join(adv.get("actions_regional", [])))
                st.warning(f"⚠️ **Chemical Spraying Caution:** {adv.get('spray_caution')}")
                st.caption(f"Source: {adv.get('source')} | {adv.get('disclaimer')}")
            except Exception as e:
                st.error(f"Failed to generate advisory: {e}")

    with col_adv_right:
        st.markdown("**📞 2G Regional Voice Call Test**")
        target_phone = st.text_input("Destination Farmer Mobile:", value="+919363849952")
        if st.button("📲 Dispatch Outbound Voice Alert"):
            try:
                voice_res = requests.post(
                    f"{API_BASE}/api/telecom/trigger-voice",
                    json={"plot_id": selected_pid, "phone_number": target_phone},
                    timeout=5
                ).json()
                st.json(voice_res)
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
        st.markdown(f"""
        <div class="basis-card pmfby">
            <div class="basis-title">🏛️ {pmfby.get('name', 'District IMD Weather Station')}</div>
            <div class="basis-subtitle">DISTANCE: {pmfby.get('distance_from_farm_km', 15.2)} KM AWAY (AREA-LEVEL APPROACH)</div>
            <p><b>Measured Temperature:</b> {pmfby.get('recorded_temperature_c', 28.5)}°C</p>
            <p><b>Measured Rainfall (1h):</b> {pmfby.get('recorded_rainfall_1h_mm', 0.0)} mm</p>
            <p><b>Station Assessment:</b> {pmfby.get('station_status')}</p>
            <div style="background:#fee2e2; border-left:4px solid #ef4444; padding:10px; border-radius:6px; margin-top:12px;">
                <b style="color:#991b1b;">❌ {pmfby.get('claim_decision')}</b>
                <div style="font-size:12px; color:#7f1d1d; margin-top:4px;">
                    {pmfby.get('basis_risk_explanation')}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="basis-card agrisentinel">
            <div class="basis-title">📡 {agri.get('name', 'AgriSentinel Hyperlocal Node')}</div>
            <div class="basis-subtitle">LOCATION: DIRECTLY ON-PLOT (50m × 50m RESOLUTION)</div>
            <p><b>On-Plot Soil Moisture:</b> {agri.get('on_farm_soil_moisture_pct', 11.2)}% (Threshold: {agri.get('contractual_drought_threshold', 18.0)}%)</p>
            <p><b>On-Plot Temperature:</b> {agri.get('on_farm_temperature_c', 42.1)}°C</p>
            <p><b>Cryptographic Integrity:</b> <span class="tag-crypto-ok">{agri.get('crypto_verification')}</span></p>
            <p><b>Weather Corroboration:</b> {agri.get('weather_corroboration')}</p>
            <div style="background:#dcfce7; border-left:4px solid #16a34a; padding:10px; border-radius:6px; margin-top:12px;">
                <b style="color:#166534;">✅ {agri.get('simulated_claim_status')}</b>
                <div style="font-size:12px; color:#14532d; margin-top:4px;">
                    Settlement Status: {agri.get('settlement_integration')}<br>
                    Voice Dispatch: {agri.get('voice_dispatch')}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# -------------------------------------------------------------
# TAB 3: CRYPTOGRAPHIC VERIFICATION & ANTI-FRAUD
# -------------------------------------------------------------
with tab_antifraud:
    st.subheader("🛡️ Cryptographic Data-Trust & Replay Defense Test Harness")
    st.caption("Test how the ingestion gateway rejects spoofed keys, tampered payloads, replayed packets, and physical bucket immersion anomalies.")

    t_col1, t_col2 = st.columns(2)
    with t_col1:
        st.markdown("#### 1. Test Cryptographic Signature Defense")
        st.write("Submit an altered telemetry packet with corrupted signature bytes:")
        if st.button("🧪 Transmit Corrupted SECP256k1 Signature"):
            # Construct deliberate invalid signature
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
                    st.error("🛡️ HTTP 403 FORBIDDEN: Cryptographic defense blocked tampered signature!")
                    st.json(res.json())
                else:
                    st.warning(f"Unexpected response code: {res.status_code}")
            except Exception as e:
                st.error(f"Error testing crypto: {e}")

    with t_col2:
        st.markdown("#### 2. Test Physical Bucket-Immersion Anomaly Hold")
        st.write("Simulate a farmer submerging the probe in water while the weather station reports 0 rain and clear skies:")
        if st.button("🪣 Transmit Bucket Immersion Divergence (95% Moisture, 0 Rain)"):
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

    st.markdown("""
    Under PMFBY guidelines, insurers face a statutory **12% annual interest penalty** for claim delays exceeding statutory benchmarks,
    alongside spending **₹400–₹800 per hectare** on dispute-ridden manual Crop Cutting Experiments (CCEs).
    """)

    c_calc1, c_calc2 = st.columns([1, 1])
    with c_calc1:
        insured_hectares = st.slider("Insured Farm Area (Hectares):", min_value=100, max_value=50000, value=5000, step=500)
        cce_cost_per_ha = st.slider("Average Manual CCE & Surveyor Cost (₹/ha):", min_value=200, max_value=1200, value=600, step=50)
        disputed_claims_pct = st.slider("Historical Disputed / Delayed Claim Rate (%):", min_value=5, max_value=40, value=18, step=1)
        node_cost = 1200.0  # ₹1,200 target BOM per node

    with c_calc2:
        total_nodes = int(insured_hectares / 2)  # Assuming 1 node per 2-hectare cluster
        capex_investment = total_nodes * node_cost
        cce_savings = insured_hectares * cce_cost_per_ha * 0.75  # 75% reduction in manual CCE disputes
        penalty_avoidance = (insured_hectares * 25000 * (disputed_claims_pct / 100)) * 0.12  # 12% statutory penalty avoidance
        total_annual_savings = cce_savings + penalty_avoidance
        payback_months = (capex_investment / total_annual_savings) * 12

        st.markdown(f"""
        <div style="background:#f8fafc; border:1.5px solid #cbd5e1; border-radius:10px; padding:20px;">
            <div style="font-size:14px; text-transform:uppercase; color:#64748b; font-weight:700;">Financial Feasibility Model</div>
            <div style="margin-top:12px; font-size:15px;">
                • Total Hardware Investment ({total_nodes:,} nodes @ ₹1,200): <b>₹{capex_investment:,.0f}</b><br>
                • Manual CCE Survey Cost Savings: <b>₹{cce_savings:,.0f}/year</b><br>
                • 12% Statutory Late-Penalty Avoidance: <b>₹{penalty_avoidance:,.0f}/year</b><br>
                • <b>Total Insurer Annual Savings:</b> <span style="color:#16a34a; font-weight:800; font-size:18px;">₹{total_annual_savings:,.0f}</span>
            </div>
            <div style="margin-top:16px; background:#dcfce7; padding:12px; border-radius:8px; border:1px solid #86efac;">
                <b style="color:#166534; font-size:16px;">⏱️ Payback Period: {payback_months:.1f} Months</b>
                <div style="font-size:12px; color:#14532d; margin-top:2px;">
                    The hardware deployment fully pays for itself in less than one full Kharif-Rabi cropping cycle.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
