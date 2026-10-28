import os
import streamlit as st
import pandas as pd
import requests
import time
import json
from datetime import datetime
from crypto_engine import CryptoEngine

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AgriSentinel Enterprise | Insurer Cockpit",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables if available
DEFAULT_TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID", "AC7b5b6cc7e83c59d0edc54bcf59a4dee1")
DEFAULT_TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "6af791ff2a26f1c8e69afe984fafcf17")
DEFAULT_TWILIO_PHONE = os.getenv("TWILIO_PHONE_NUMBER", "+17372508034")
DEFAULT_GROQ_KEY = os.getenv("GROQ_API_KEY", "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")
DEFAULT_OWM_KEY = os.getenv("OPENWEATHER_API_KEY", "0f5614e650857443251cbb524550aad8")

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
        padding: 24px 30px;
        border-radius: 16px;
        margin-bottom: 25px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        border: 1px solid rgba(255,255,255,0.1);
    }
    .main-header h1 {
        font-size: 28px;
        font-weight: 800;
        margin: 0 0 6px 0;
        letter-spacing: -0.5px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .main-header .sub-header {
        font-size: 14px;
        opacity: 0.85;
        font-weight: 400;
    }
    
    .status-badge-bar {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
        margin-top: 14px;
    }
    .status-pill {
        background: rgba(255,255,255,0.12);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.5px;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    /* Metric Cards */
    .metric-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 18px 22px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
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
        font-size: 28px;
        font-weight: 800;
        color: #1a202c;
        margin: 4px 0;
    }
    .metric-lbl {
        font-size: 12px;
        font-weight: 600;
        color: #718096;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }
    
    /* Basis Risk Comparative Panel */
    .basis-risk-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        margin: 20px 0;
    }
    .basis-card {
        border-radius: 14px;
        padding: 22px;
        color: white;
        box-shadow: 0 6px 18px rgba(0,0,0,0.12);
    }
    .basis-card.pmfby {
        background: linear-gradient(145deg, #374151, #1f2937);
        border: 1px solid #4b5563;
    }
    .basis-card.agrisentinel {
        background: linear-gradient(145deg, #065f46, #047857);
        border: 1px solid #10b981;
    }
    .basis-title {
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .basis-subtitle {
        font-size: 12px;
        opacity: 0.8;
        margin-bottom: 16px;
        font-family: 'JetBrains Mono', monospace;
    }
    .basis-stat {
        background: rgba(0,0,0,0.2);
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 10px;
        font-size: 13px;
    }
    .basis-payout-box {
        padding: 14px;
        border-radius: 10px;
        font-size: 15px;
        font-weight: 700;
        text-align: center;
        margin-top: 15px;
        letter-spacing: 0.5px;
    }
    .payout-rejected {
        background: rgba(239, 68, 68, 0.2);
        border: 1px solid #ef4444;
        color: #fca5a5;
    }
    .payout-instant {
        background: rgba(16, 185, 129, 0.25);
        border: 1px solid #34d399;
        color: #a7f3d0;
    }
    
    /* Farm Grid Cards */
    .plot-grid-card {
        border-radius: 14px;
        padding: 16px;
        color: white;
        margin-bottom: 12px;
        transition: transform 0.15s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .plot-grid-card:hover {
        transform: translateY(-2px);
    }
    .card-safe {
        background: linear-gradient(135deg, #1b4332, #2d6a4f);
        border: 1px solid #40916c;
    }
    .card-breach {
        background: linear-gradient(135deg, #7f1d1d, #991b1b);
        border: 1px solid #ef4444;
        animation: pulse-breach 2s infinite;
    }
    .card-audit {
        background: linear-gradient(135deg, #78350f, #92400e);
        border: 1px solid #f59e0b;
    }
    .card-warning {
        background: linear-gradient(135deg, #854d0e, #a16207);
        border: 1px solid #eab308;
    }
    @keyframes pulse-breach {
        0%, 100% { box-shadow: 0 0 10px rgba(239, 68, 68, 0.4); }
        50% { box-shadow: 0 0 22px rgba(239, 68, 68, 0.85); }
    }
    
    .badge-pill {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 10px;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        margin-top: 6px;
        margin-right: 4px;
    }
    .badge-crypto {
        background: rgba(59, 130, 246, 0.25);
        border: 1px solid #60a5fa;
        color: #bfdbfe;
    }
    .badge-crypto-tamper {
        background: rgba(239, 68, 68, 0.3);
        border: 1px solid #ef4444;
        color: #fca5a5;
    }
    .badge-sat {
        background: rgba(16, 185, 129, 0.25);
        border: 1px solid #34d399;
        color: #a7f3d0;
    }
    .badge-sat-audit {
        background: rgba(245, 158, 11, 0.3);
        border: 1px solid #f59e0b;
        color: #fde68a;
    }
</style>
""", unsafe_allow_html=True)

# SIDEBAR: Enterprise Insurer Configuration & Keys
st.sidebar.title("🛡️ Enterprise Settings")
st.sidebar.caption("Insurance Carrier Portal / Anti-Fraud Node Registry")

st.sidebar.subheader("🔑 API Key Configuration")
groq_key = st.sidebar.text_input("Groq API Key (LLaMA-3.3-70B)", value=DEFAULT_GROQ_KEY, type="password", help="Used for immediate agronomic advice generation in English & Tamil")
tw_sid = st.sidebar.text_input("Twilio Account SID", value=DEFAULT_TWILIO_SID, type="password", help="Twilio account SID for outbound 2G voice calls")
tw_token = st.sidebar.text_input("Twilio Auth Token", value=DEFAULT_TWILIO_TOKEN, type="password", help="Twilio auth token")
tw_phone = st.sidebar.text_input("Twilio Outbound Phone", value=DEFAULT_TWILIO_PHONE, help="Twilio verified sender phone number")
farmer_test_phone = st.sidebar.text_input("Farmer Test Phone", value="+919363849952", help="Farmer mobile number for automated 2G voice alert dispatch")
owm_key = st.sidebar.text_input("OpenWeatherMap API Key", value=DEFAULT_OWM_KEY, type="password", help="Satellite verification API key (NASA/OWM)")

st.sidebar.markdown("---")
st.sidebar.subheader("📡 Simulated IoT Nodes (ECDSA)")
st.sidebar.caption("Cryptographic keys pre-seeded on SECP256k1 curve:")
for node_name in ["node_1 (TN)", "node_2 (UP)", "node_3 (GJ)"]:
    st.sidebar.code(f"{node_name}\nCurve: SECP256k1\nStatus: Keypair Active", language="text")

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Force Refresh View", use_container_width=True):
    st.rerun()

if st.sidebar.button("⚠️ Reset All Policies & Logs", use_container_width=True):
    try:
        requests.post(f"{API_BASE}/api/policies/reset", timeout=3)
        st.sidebar.success("Policies and logs reset successfully!")
        time.sleep(0.5)
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"Reset failed: {e}")

# Header
st.markdown("""
<div class="main-header">
    <h1>🌾 AgriSentinel &nbsp;<span style="font-size:16px; background:#10b981; color:white; padding:3px 10px; border-radius:20px; font-weight:600;">ENTERPRISE B2B</span></h1>
    <div class="sub-header">Autonomous Parametric Crop Insurance & Cryptographic Anti-Fraud Telemetry Architecture</div>
    <div class="status-badge-bar">
        <span class="status-pill">🔐 SECP256k1 ECDSA: ACTIVE</span>
        <span class="status-pill">🛰️ SATELLITE CROSS-CHECK: ENABLED</span>
        <span class="status-pill">🧠 GROQ LLAMA-3.3-70B: READY</span>
        <span class="status-pill">📞 2G TELECOM VOICE: REGIONAL-9</span>
        <span class="status-pill">⚡ SETTLEMENT LATENCY: &lt; 2.0s</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Fetch backend data
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
    st.error(f"Cannot connect to AgriSentinel Backend on {API_BASE}. Ensure `backend.py` is running.")
    st.info("Run command: `python -m uvicorn backend:app --host 127.0.0.1 --port 8000 --reload`")
    st.stop()

def get_plot_label(pid: str) -> str:
    for p in grid_data:
        if p.get("plot_id") == pid:
            return f"{pid.upper()} - {p.get('farmer_name', '')} ({p.get('crop', '')}, {p.get('state', '')})"
    return pid.upper()

# TOP METRICS ROW
total_grids = len(grid_data)
active_policies = sum(1 for p in grid_data if p.get("active"))
total_underwritten = sum(p.get("sum_insured", 0) for p in grid_data)
total_claims_paid = len(claims_data)
total_disbursed = sum(c.get("payout_amount", 0) for c in claims_data)

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-lbl">Active Farm Grids</div>
        <div class="metric-val">{total_grids}</div>
        <div style="font-size:12px; color:#2d6a4f; font-weight:600;">50x50m Hyperlocal Polygons</div>
    </div>
    """, unsafe_allow_html=True)
with m2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-lbl">Validated Policies Underwritten</div>
        <div class="metric-val">₹{total_underwritten:,.0f}</div>
        <div style="font-size:12px; color:#2d6a4f; font-weight:600;">{active_policies} Active In-Force Contracts</div>
    </div>
    """, unsafe_allow_html=True)
with m3:
    st.markdown(f"""
    <div class="metric-card alert">
        <div class="metric-lbl">Parametric Payouts Disbursed</div>
        <div class="metric-val">₹{total_disbursed:,.0f}</div>
        <div style="font-size:12px; color:#d90429; font-weight:600;">{total_claims_paid} Automated Settlements</div>
    </div>
    """, unsafe_allow_html=True)
with m4:
    st.markdown(f"""
    <div class="metric-card shield">
        <div class="metric-lbl">Tamper Attacks Blocked</div>
        <div class="metric-val">{tamper_blocked_count}</div>
        <div style="font-size:12px; color:#4a5568; font-weight:600;">ECDSA & Satellite Anti-Fraud</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------------------------------------
# SIDE-BY-SIDE BASIS RISK VISUAL PROOF PANEL
# -------------------------------------------------------------
st.subheader("⚖️ Visual Proof: Eliminating Basis Risk in Crop Insurance")
st.caption("Demonstrating how traditional area-yield insurance (PMFBY) fails smallholder farmers vs. AgriSentinel's cryptographic micro-grid.")

pmfby = basis_res.get("pmfby_traditional_station", {})
agri = basis_res.get("agrisentinel_hyperlocal_node", {})

c_left, c_right = st.columns(2)

with c_left:
    st.markdown(f"""
    <div class="basis-card pmfby">
        <div class="basis-title">🏛️ {pmfby.get('name', 'District Weather Station (IMD)')}</div>
        <div class="basis-subtitle">DISTANCE FROM PLOT: {pmfby.get('distance_from_farm_km', 15.2)} KM AWAY (AREA-LEVEL MACRO SENSOR)</div>
        <div class="basis-stat">
            <b>Recorded Ambient Temp:</b> {pmfby.get('recorded_temperature_c', 28.5)}°C<br>
            <b>Recorded 24h Rainfall:</b> {pmfby.get('recorded_rainfall_24h_mm', 12.0)} mm<br>
            <b>Relative Humidity:</b> {pmfby.get('recorded_relative_humidity', 68.0)}%<br>
            <b>Regional Status:</b> {pmfby.get('macro_status', 'NORMAL / NO EXTREME EVENT')}
        </div>
        <div style="font-size:13px; line-height:1.5; opacity:0.9; min-height:60px;">
            ⚠️ <b>Basis Risk Defect:</b> {pmfby.get('basis_risk_failure_explanation', 'District station failed to detect localized micro-climate drought.')}
        </div>
        <div class="basis-payout-box payout-rejected">
            ❌ {pmfby.get('payout_status', 'CLAIM REJECTED (₹0 Payout)')}
        </div>
    </div>
    """, unsafe_allow_html=True)

with c_right:
    st.markdown(f"""
    <div class="basis-card agrisentinel">
        <div class="basis-title">🛡️ {agri.get('name', 'AgriSentinel Fence Node #1')}</div>
        <div class="basis-subtitle">RESOLUTION: {agri.get('grid_resolution', '50x50m micro-polygon')} | REAL-TIME TELEMETRY</div>
        <div class="basis-stat">
            <b>Hyperlocal Root-Zone Temp:</b> {agri.get('on_farm_temperature_c', 43.8)}°C (Thermal Stress)<br>
            <b>Soil Moisture:</b> {agri.get('on_farm_soil_moisture_pct', 11.5)}% (Breached Threshold &lt; {agri.get('drought_threshold_pct', 18.0)}%)<br>
            <b>Cryptographic Signature:</b> <span style="color:#a7f3d0; font-weight:700;">{agri.get('crypto_signature_status', 'ECDSA-SECP256k1 VALID')}</span><br>
            <b>Satellite Validation:</b> <span style="color:#a7f3d0; font-weight:700;">{agri.get('satellite_cross_check', 'SATELLITE VERIFIED')}</span>
        </div>
        <div style="font-size:13px; line-height:1.5; opacity:0.9; min-height:60px;">
            ⚡ <b>Autonomous Settlement:</b> Verified in {agri.get('latency_seconds', 1.4)}s. Zero human paperwork. {agri.get('voice_alert_dispatch', 'Voice alert triggered.')}
        </div>
        <div class="basis-payout-box payout-instant">
            ✅ {agri.get('payout_status', 'INSTANT AUTOMATED PAYOUT (₹50,000 DISBURSED)')}
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# -------------------------------------------------------------
# INTERACTIVE LIVE FARM GRID CARDS WITH ECDSA & SATELLITE BADGES
# -------------------------------------------------------------
st.subheader("🗺️ Live Farm Grid Monitor (Multi-State India Registry)")
st.caption("Real-time telemetry, SECP256k1 signature validation badges, and satellite macro cross-validation status.")

STATE_FLAGS = {
    "Tamil Nadu": "🏛️", "Uttar Pradesh": "🕌", "Gujarat": "🦁",
    "Andhra Pradesh": "🌶️", "West Bengal": "🐅", "Rajasthan": "🏜️",
    "Maharashtra": "⛰️", "Kerala": "🌴", "Karnataka": "🏯"
}

for row_start in range(0, len(grid_data), 3):
    cols = st.columns(3)
    for i, col in enumerate(cols):
        idx = row_start + i
        if idx >= len(grid_data):
            break
        p = grid_data[idx]
        status = p.get("status", "NORMAL")
        moisture = p.get("soil_moisture", 0.0)
        temp = p.get("temperature", 0.0)
        threshold = p.get("moisture_threshold", 18.0)
        state = p.get("state", "")
        lang = p.get("language_name", "")
        flag = STATE_FLAGS.get(state, "🌿")
        crypto_status = p.get("crypto_status", "SECP256k1: VALID")
        satellite_status = p.get("satellite_status", "SATELLITE: MATCHED")

        if status == "PARAMETRIC_BREACH":
            css_class = "card-breach"
            status_text = "🔴 PARAMETRIC BREACH (PAYOUT SENT)"
        elif status == "HELD_PHYSICAL_TAMPERING_AUDIT" or "TAMPER" in status:
            css_class = "card-audit"
            status_text = "⚠️ PHYSICAL TAMPERING AUDIT REQUIRED"
        elif status == "SIG_REJECTED":
            css_class = "card-breach"
            status_text = "❌ SPOOFED PAYLOAD REJECTED"
        elif moisture < threshold + 3.0:
            css_class = "card-warning"
            status_text = "🟡 PRE-BREACH WARNING"
        else:
            css_class = "card-safe"
            status_text = "🟢 SAFE / WITHIN THRESHOLD"

        # Badge styling
        crypto_badge_class = "badge-crypto-tamper" if "REJECTED" in crypto_status or "SPOOF" in crypto_status else "badge-crypto"
        sat_badge_class = "badge-sat-audit" if "TAMPER" in satellite_status or "AUDIT" in satellite_status else "badge-sat"

        with col:
            st.markdown(f"""
            <div class="plot-grid-card {css_class}">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h3 style="margin:0; font-size:17px; font-weight:700;">{flag} {p.get('plot_id', '').upper()}</h3>
                    <span style="font-size:11px; font-weight:700; opacity:0.9;">₹{p.get('sum_insured', 0):,.0f}</span>
                </div>
                <div style="font-size:14px; font-weight:600; margin-top:2px;">{p.get('farmer_name', '')}</div>
                <div style="font-size:12px; opacity:0.85;">📍 {state} ({p.get('region', '')}) &nbsp;|&nbsp; 🗣️ {lang}</div>
                <div style="font-size:12px; opacity:0.85; margin-bottom:6px;">🌾 {p.get('crop', '')}</div>
                <div style="background:rgba(0,0,0,0.22); border-radius:8px; padding:6px 10px; font-size:12px; margin-bottom:8px;">
                    💧 <b>Soil Moisture:</b> {moisture:.1f}% (Limit: &lt;{threshold}%)<br>
                    🌡️ <b>Temperature:</b> {temp:.1f}°C &nbsp;|&nbsp; 🌧️ <b>Rain:</b> {p.get('rainfall_mm', 0.0):.1f}mm
                </div>
                <div style="font-size:11px; font-weight:700;">{status_text}</div>
                <div>
                    <span class="badge-pill {crypto_badge_class}">🔐 {crypto_status}</span>
                    <span class="badge-pill {sat_badge_class}">🛰️ {satellite_status}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("---")

# -------------------------------------------------------------
# ANOMALY TRIGGER & STRESS-TESTING SUITE
# -------------------------------------------------------------
st.subheader("🧪 Anti-Fraud & Anomaly Simulation Testing Suite")
st.caption("Interact directly with the cryptographic and satellite verification engine to test edge cases, tamper scenarios, and payouts.")

tab_drought, tab_tamper, tab_spoof, tab_voice = st.tabs([
    "🚨 1. Legitimate Drought Breach",
    "🪣 2. Physical Tamper (Flood Fraud)",
    "🔓 3. Cryptographic Signature Tamper",
    "📞 4. Telecom Voice & Groq Advisory"
])

# TAB 1: Legitimate Drought Breach
with tab_drought:
    st.markdown("#### Test Autonomous Parametric Payout")
    st.caption("Transmits a verified SECP256k1 signed telemetry packet indicating extreme root-zone soil dryness.")
    col_d1, col_d2 = st.columns([1, 1])
    with col_d1:
        sel_plot_d = st.selectbox(
            "Select Farm Plot for Drought Test",
            [p["plot_id"] for p in grid_data],
            format_func=get_plot_label
        )
        d_moisture = st.slider("Soil Moisture (% - threshold is 18%)", 5.0, 30.0, 11.5, 0.5, key="d_moist")
        d_temp = st.slider("Temperature (°C)", 30.0, 55.0, 43.5, 0.5, key="d_temp")
    with col_d2:
        st.info("When triggered, AgriSentinel generates an ECDSA signature using node's private key, verifies against satellite thermal trends, automatically issues the claim, and queues the 2G voice alert.")
        if st.button("⚡ Execute Verified Drought Payout", type="primary", use_container_width=True):
            node_id = f"node_{sel_plot_d.split('_')[-1]}"
            sk, vk = CryptoEngine.generate_keypair()
            telemetry = {
                "plot_id": sel_plot_d,
                "timestamp": time.time(),
                "temperature": d_temp,
                "humidity": 22.0,
                "pressure": 1012.0,
                "soil_moisture": d_moisture,
                "rainfall_mm": 0.0
            }
            packet = CryptoEngine.create_signed_packet(node_id, sk, vk, telemetry)
            res = requests.post(f"{API_BASE}/api/telemetry", json=packet, timeout=6)
            if res.status_code == 200:
                data = res.json()
                st.success(f"✅ Telemetry Accepted! Crypto: {data.get('cryptographic_verification')} | Satellite: {data.get('satellite_cross_check')}")
                ev = data.get("evaluation", {})
                if ev.get("triggered"):
                    st.balloons()
                    st.success(f"🎉 PAYOUT TRIGGERED! ₹{ev.get('payout_amount', 0):,.0f} disbursed to {ev.get('farmer_phone', '')}")
                else:
                    st.info(f"Condition: {ev.get('reason')}")
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"Error: {res.text}")

# TAB 2: Physical Tamper (Water-Bucket Fraud)
with tab_tamper:
    st.markdown("#### Test Satellite Remote Sensing Cross-Validation (Water-Bucket Attack)")
    st.caption("A dishonest actor submerges an on-farm sensor in a bucket of water to fake a catastrophic flash flood (100% moisture). AgriSentinel queries satellite imagery (0% cloud cover, 0mm precipitation) and freezes the fraudulent payout!")
    col_t1, col_t2 = st.columns([1, 1])
    with col_t1:
        sel_plot_t = st.selectbox(
            "Select Farm Plot for Tamper Attack",
            [p["plot_id"] for p in grid_data],
            key="tamper_plot",
            format_func=get_plot_label
        )
        fake_moisture = st.slider("Simulated Spoofed Moisture (%)", 85.0, 100.0, 96.5, 0.5)
        fake_temp = st.slider("Sensor Temp (°C)", 20.0, 35.0, 27.0, 0.5, key="tamper_temp")
    with col_t2:
        st.warning("⚠️ **Expected Defense Response:** Cryptographic signature is authentic (node hardware wasn't hacked), but satellite cross-validation reveals 0mm rain. System flags `PHYSICAL TAMPERING AUDIT REQUIRED` and rejects the claim.")
        if st.button("🚨 Simulate Water-Bucket Flood Fraud Attack", use_container_width=True):
            node_id = f"node_{sel_plot_t.split('_')[-1]}"
            sk, vk = CryptoEngine.generate_keypair()
            telemetry = {
                "plot_id": sel_plot_t,
                "timestamp": time.time(),
                "temperature": fake_temp,
                "humidity": 60.0,
                "pressure": 1012.0,
                "soil_moisture": fake_moisture,
                "rainfall_mm": 0.0 # Sensor claims 96.5% moisture with zero rain
            }
            packet = CryptoEngine.create_signed_packet(node_id, sk, vk, telemetry)
            res = requests.post(f"{API_BASE}/api/telemetry", json=packet, timeout=6)
            if res.status_code == 200:
                data = res.json()
                if data.get("status") == "HELD_FOR_AUDIT":
                    st.error(f"🛑 FRAUD DETECTED & BLOCKED! Status: {data.get('status')}")
                    st.warning(f"Satellite Cross Check: {data.get('satellite_cross_check')}")
                    st.info(f"Audit Finding: {data.get('evaluation', {}).get('audit_finding')}")
                else:
                    st.json(data)
                time.sleep(1.5)
                st.rerun()

# TAB 3: Cryptographic Signature Tamper
with tab_spoof:
    st.markdown("#### Test Cryptographic Replay / Man-in-the-Middle Spoofing")
    st.caption("An attacker intercepts or forges a telemetry packet without the hardware node's SECP256k1 private key.")
    col_s1, col_s2 = st.columns([1, 1])
    with col_s1:
        st.code("""
// Corrupted Telemetry Signature Payload:
{
  "node_id": "node_1",
  "signature": "3045022100deadbeef...corrupted_signature",
  "telemetry": { "soil_moisture": 5.0, "temperature": 52.0 }
}
        """, language="json")
    with col_s2:
        st.error("🛡️ **Expected Defense Response:** Zero-trust architecture checks ECDSA signature against public key. Reject instantly with HTTP 403 Forbidden and increment blocked counter.")
        if st.button("💀 Inject Tampered / Spoofed Signature", use_container_width=True):
            sk, vk = CryptoEngine.generate_keypair()
            telemetry = {
                "plot_id": "plot_1",
                "timestamp": time.time(),
                "temperature": 48.0,
                "humidity": 20.0,
                "pressure": 1010.0,
                "soil_moisture": 8.0,
                "rainfall_mm": 0.0
            }
            packet = CryptoEngine.create_signed_packet("node_1", sk, vk, telemetry)
            # Tamper with signature
            packet["signature"] = packet["signature"][:-8] + "0000ffff"
            res = requests.post(f"{API_BASE}/api/telemetry", json=packet, timeout=6)
            if res.status_code == 403:
                st.success("🛡️ ATTACK BLOCKED! Server returned HTTP 403 Forbidden:")
                st.code(res.text, language="json")
                time.sleep(1)
                st.rerun()
            else:
                st.warning(f"Response: {res.status_code} - {res.text}")

# TAB 4: Telecom Voice & Groq Advisory
with tab_voice:
    st.markdown("#### Test Outbound 2G Regional Voice Call & Groq Agronomic Advice")
    st.caption("Triggers an outbound telecom phone call reading localized advice in the farmer's native state language.")
    col_v1, col_v2 = st.columns([1, 1])
    with col_v1:
        v_plot = st.selectbox(
            "Select Farm Plot",
            [p["plot_id"] for p in grid_data],
            key="v_plot",
            format_func=get_plot_label
        )
        p_info = next((p for p in grid_data if p["plot_id"] == v_plot), {})
        target_phone = st.text_input("Destination Farmer Phone", value=farmer_test_phone, key="phone_input")
        
        btn_call, btn_adv = st.columns(2)
        with btn_call:
            if st.button(f"📞 Dispatch Call ({p_info.get('language_name')})", type="primary", use_container_width=True):
                call_payload = {
                    "plot_id": v_plot,
                    "phone_number": target_phone
                }
                if tw_sid:
                    call_payload["twilio_sid"] = tw_sid
                if tw_token:
                    call_payload["twilio_token"] = tw_token
                if tw_phone:
                    call_payload["twilio_phone"] = tw_phone

                res = requests.post(
                    f"{API_BASE}/api/telecom/trigger-voice",
                    json=call_payload,
                    timeout=8
                )
                if res.status_code == 200:
                    d = res.json()
                    if d.get("status") == "queued":
                        st.success(f"Call initiated to {target_phone}! SID: {d.get('call_sid')}")
                    elif d.get("status") == "simulated":
                        st.info("Simulated dispatch (No live Twilio credentials found in environment or sidebar). Enter your Twilio credentials in the sidebar to place a live phone call.")
                    else:
                        st.warning(str(d))
                else:
                    st.error(res.text)
        with btn_adv:
            if st.button("🧠 Groq LLaMA Advisory", use_container_width=True):
                with st.spinner("Querying Groq LLaMA-3.3-70B model..."):
                    adv_res = requests.get(f"{API_BASE}/api/advisory/{v_plot}", timeout=10)
                    if adv_res.status_code == 200:
                        st.session_state["advisory_data"] = adv_res.json()
                    else:
                        st.error("Failed to fetch Groq advisory.")

    with col_v2:
        if "advisory_data" in st.session_state:
            adv = st.session_state["advisory_data"]
            st.markdown(f"**Agronomic Mitigation Model:** `{adv.get('model', 'Groq LLaMA-3.3')}` ({adv.get('source', '')})")
            
            c_en, c_reg = st.columns(2)
            with c_en:
                st.markdown("**English Action Plan:**")
                for item in adv.get("actions_english", adv.get("actions", [])):
                    st.markdown(f"- {item}")
            with c_reg:
                target_lang = adv.get("language_name") or p_info.get("language_name", "Regional")
                st.markdown(f"**Regional Action Plan ({target_lang}):**")
                reg_items = adv.get("actions_regional") or adv.get("actions_tamil", [])
                for item in reg_items:
                    st.markdown(f"- {item}")
                    
            with st.expander("🔊 2G Voice Synthesized Audio Script"):
                st.write(adv.get("regional_audio_script") or adv.get("tamil_audio_script", ""))
        else:
            st.info("Click 'Groq LLaMA Advisory' to generate immediate agronomic mitigation steps tailored for this crop and weather state.")

    with st.expander("📜 Preview TwiML Voice XML Webhook Payload"):
        twiml_res = requests.get(f"{API_BASE}/api/twilio/voice?plot_id={v_plot}&moisture=11.5&amount={p_info.get('sum_insured', 50000)}", timeout=3)
        st.code(twiml_res.text, language="xml")

st.markdown("---")

# -------------------------------------------------------------
# AUDIT TRAIL & CLAIMS LEDGER
# -------------------------------------------------------------
c_audit, c_claims = st.columns([1, 1])

with c_audit:
    st.subheader("🛡️ Cryptographic & Anti-Fraud Security Audit Trail")
    st.caption("Immutable ledger of all received telemetry packets, ECDSA signature status, and satellite verification results.")
    if audit_data:
        audit_rows = []
        for a in audit_data[:12]:
            audit_rows.append({
                "Timestamp": datetime.fromtimestamp(a.get("timestamp", time.time())).strftime("%H:%M:%S"),
                "Node ID": a.get("node_id", "N/A"),
                "Plot ID": a.get("plot_id", "").upper(),
                "ECDSA Sig": "✅ VALID" if a.get("sig_valid") else "❌ TAMPERED",
                "Satellite Match": a.get("satellite_status", "MATCHED"),
                "Moisture": f"{a.get('moisture', 0):.1f}%",
                "Verdict": a.get("action", "NORMAL")
            })
        st.dataframe(pd.DataFrame(audit_rows), use_container_width=True, hide_index=True)
    else:
        st.info("No security audit records logged yet.")

with c_claims:
    st.subheader("📑 Parametric Claims Disbursed Ledger")
    st.caption("Automated instant settlements executed via parametric smart trigger.")
    if claims_data:
        claim_rows = []
        for c in claims_data[:12]:
            claim_rows.append({
                "Claim ID": c.get("claim_id", ""),
                "Farmer": c.get("farmer_name", ""),
                "Crop": c.get("crop", ""),
                "Payout": f"₹{c.get('payout_amount', 0):,.0f}",
                "Trigger": c.get("trigger_reason", ""),
                "Status": c.get("status", "SETTLED")
            })
        st.dataframe(pd.DataFrame(claim_rows), use_container_width=True, hide_index=True)
    else:
        st.info("No claims triggered yet. All plots currently within baseline parametric thresholds.")

st.markdown("---")
f1, f2, f3 = st.columns([1, 2, 1])
with f1:
    st.caption("🌾 AgriSentinel Platform v2.0 Enterprise")
with f2:
    st.caption("Architecture: FastAPI Microservices + SECP256k1 Curve + NASA/OWM Remote Sensing + Twilio Regional Voice + Groq LLaMA-3.3")
with f3:
    st.caption("Ready for Hackathon Grand Jury Demonstration")
