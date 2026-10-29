"""
AgriSentinel Enterprise API Backend
===================================
FastAPI ingestion service for cryptographically authenticated on-plot telemetry,
meteorological cross-examination, parametric claims evaluation, and voice alerts.
"""

import os
import time
from typing import Dict, Any, Optional

import config  # Loads .env safely at startup
from fastapi import FastAPI, BackgroundTasks, HTTPException, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from farm_registry import (
    FARM_PROFILES,
    DEVICE_REGISTRY,
    get_registered_device,
    get_farm_profile
)
from crypto_engine import CryptoEngine
from satellite_verifier import SatelliteVerifier
from insurance_engine import engine
from advisor_service import GroqAdvisoryService
from telecom_service import TelecomVoiceEngine

app = FastAPI(
    title="AgriSentinel Enterprise API",
    description="Autonomous Parametric Crop Insurance & Hardware-Signed Telemetry Ingestion Platform",
    version="2.1.0",
    docs_url="/docs",
    redoc_url=None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TelemetryData(BaseModel):
    plot_id: str = Field(..., example="plot_1")
    timestamp: float = Field(default_factory=time.time)
    temperature: float = Field(..., example=28.5)
    humidity: float = Field(default=45.0, example=45.0)
    pressure: float = Field(default=1012.0, example=1012.0)
    soil_moisture: float = Field(..., example=32.0)
    rainfall_mm: float = Field(default=0.0, example=0.0)

class TelemetryPayload(BaseModel):
    node_id: str = Field(..., example="node_1")
    plot_id: str = Field(..., example="plot_1")
    signature: str = Field(..., example="30440220...signature_hex...")
    telemetry: TelemetryData

class SimulatorSignRequest(BaseModel):
    node_id: str = Field(..., example="node_1")
    telemetry: Dict[str, Any]

class ManualTriggerPayload(BaseModel):
    plot_id: str
    soil_moisture: float
    temperature: float
    humidity: float = 45.0
    pressure: float = 1012.0
    rainfall_mm: float = 0.0

class TriggerVoicePayload(BaseModel):
    plot_id: str = Field(..., example="plot_1")
    phone_number: str = Field(..., example="+919363849952")
    custom_url: Optional[str] = None
    twilio_sid: Optional[str] = None
    twilio_token: Optional[str] = None
    twilio_phone: Optional[str] = None

@app.get("/health")
async def health_check():
    return {
        "status": "operational",
        "system": "AgriSentinel Enterprise Ingestion Platform",
        "version": "2.1.0",
        "timestamp": time.time(),
        "cryptographic_algorithm": "ECDSA-SECP256k1 (Registered Device Registry)",
        "weather_corroborator": "Active",
        "tamper_attempts_blocked": engine.tamper_blocked_count,
        "monitored_farm_profiles": len(engine.policies)
    }

@app.get("/api/registry")
async def get_device_registry():
    """Returns the authoritative trusted hardware device registry."""
    return {
        "registered_devices": list(DEVICE_REGISTRY.values()),
        "total_count": len(DEVICE_REGISTRY)
    }

@app.post("/api/simulator/sign")
@app.post("/api/crypto/sign")
async def sign_simulator_telemetry(payload: SimulatorSignRequest):
    """
    SIMULATOR HELPER ENDPOINT:
    Uses provisioned test private keys strictly for software simulation.
    In real deployments, private keys reside exclusively inside ESP32 eFuse.
    """
    try:
        signed_pkt = CryptoEngine.create_simulated_signed_packet(payload.node_id, payload.telemetry)
        return signed_pkt
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/telemetry")
async def ingest_telemetry(payload: TelemetryPayload, background_tasks: BackgroundTasks, request: Request):
    """
    Primary Ingestion Gateway:
    1. Verifies ECDSA signature against the device's REGISTERED public key in DEVICE_REGISTRY.
    2. Validates timestamp freshness, monotonic sequence, and prevents replay attacks.
    3. Cross-examines ground readings against independent meteorological observations.
    4. Evaluates parametric insurance policy and generates Claim Intent if breached.
    """
    telemetry_dict = payload.telemetry.model_dump()
    
    # 1. Cryptographic & Device Trust Verification
    sig_valid, sig_notes, crypto_metadata = CryptoEngine.verify_telemetry_packet(
        node_id=payload.node_id,
        claimed_plot_id=payload.plot_id,
        signature_hex=payload.signature,
        telemetry_dict=telemetry_dict,
        enforce_freshness=True
    )

    # 2. Insurance Engine Evaluation
    eval_result = engine.evaluate_telemetry(
        node_id=payload.node_id,
        telemetry=telemetry_dict,
        sig_valid=sig_valid,
        crypto_metadata=crypto_metadata,
        sig_notes=sig_notes
    )

    # If cryptographic verification failed, reject with HTTP 403 Forbidden
    if not sig_valid:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "FORBIDDEN_DATA_TRUST_FAILURE",
                "failure_stage": crypto_metadata.get("failure_stage"),
                "message": sig_notes,
                "node_id": payload.node_id,
                "claimed_plot_id": payload.plot_id,
                "crypto_metadata": crypto_metadata
            }
        )

    # If held for physical divergence / tamper inspection
    if eval_result.get("status") == "HELD_PHYSICAL_DIVERGENCE_AUDIT":
        return {
            "status": "HELD_FOR_FIELD_INSPECTION",
            "cryptographic_verification": "SECP256k1_REGISTERED_DEVICE_VALID",
            "weather_corroboration": "DIVERGENCE_FLAGGED",
            "evaluation": eval_result
        }

    # If parametric claim intent was generated, dispatch voice advisory call
    if eval_result.get("triggered"):
        base_url = str(request.base_url).rstrip("/")
        lang_code = eval_result.get("language_code", "ta-IN")
        background_tasks.add_task(
            TelecomVoiceEngine.dispatch_voice_alert,
            eval_result["farmer_phone"],
            payload.plot_id,
            eval_result["moisture"],
            eval_result["payout_amount"],
            base_url,
            lang_code
        )

    return {
        "status": "success",
        "cryptographic_verification": "SECP256k1_REGISTERED_DEVICE_VALID",
        "weather_corroboration": eval_result.get("weather_corroboration", {}).get("badge", "WEATHER: CORROBORATED"),
        "evaluation": eval_result
    }

@app.get("/api/advisory/{plot_id}")
async def get_advisory(plot_id: str, month: str = ""):
    policy = engine.policies.get(plot_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Farm plot not found in policy registry")

    telemetry = engine.plot_telemetry.get(plot_id, {})
    moisture = telemetry.get("soil_moisture", 30.0)
    temp = telemetry.get("temperature", 28.5)
    rain = telemetry.get("rainfall_mm", 0.0)

    advisory = await GroqAdvisoryService.get_agronomic_advisory(
        plot_id=plot_id,
        crop=policy["crop"],
        moisture=moisture,
        temp=temp,
        rainfall=rain,
        state=policy.get("state", "Tamil Nadu"),
        language_code=policy.get("language_code", "ta-IN"),
        language_name=policy.get("language_name", "Tamil"),
        month=month
    )
    return advisory

@app.post("/api/telecom/trigger-voice")
async def trigger_voice_call(payload: TriggerVoicePayload, request: Request):
    policy = engine.policies.get(payload.plot_id)
    if not policy:
        raise HTTPException(status_code=404, detail=f"Plot {payload.plot_id} not registered")

    telemetry = engine.plot_telemetry.get(payload.plot_id, {})
    moisture = telemetry.get("soil_moisture", 14.0)
    amount = policy.get("sum_insured_inr", 50000.0)
    base_url = str(request.base_url).rstrip("/")
    lang_code = policy.get("language_code", "ta-IN")

    dispatch_res = await TelecomVoiceEngine.dispatch_voice_alert(
        to_phone=payload.phone_number,
        plot_id=payload.plot_id,
        moisture=moisture,
        payout_amount=amount,
        webhook_base_url=base_url,
        language_code=lang_code,
        custom_url=payload.custom_url,
        account_sid=payload.twilio_sid,
        auth_token=payload.twilio_token,
        from_phone=payload.twilio_phone
    )
    return dispatch_res

@app.get("/api/twilio/voice")
@app.post("/api/twilio/voice")
async def twilio_voice_webhook(plot_id: str = "plot_1", moisture: float = 14.0, amount: float = 50000.0):
    policy = engine.policies.get(plot_id, {})
    lang = policy.get("language_code", "ta-IN")
    twiml_content = TelecomVoiceEngine.generate_breach_twiml(plot_id, moisture, amount, lang)
    return Response(content=twiml_content, media_type="application/xml")

@app.post("/api/twilio/gather")
async def twilio_gather_webhook(request: Request):
    form_data = await request.form()
    digits = form_data.get("Digits", "")
    twiml_content = TelecomVoiceEngine.generate_gather_response(str(digits))
    return Response(content=twiml_content, media_type="application/xml")

@app.get("/api/grid")
async def get_grid_state():
    grid = []
    for pid, policy in engine.policies.items():
        telemetry = engine.plot_telemetry.get(pid, {})
        grid.append({
            "plot_id": pid,
            "node_id": policy["node_id"],
            "farmer_name": policy["farmer_name"],
            "phone": policy["phone"],
            "crop": policy["crop"],
            "state": policy["state"],
            "district": policy["district"],
            "region": policy["region"],
            "language_code": policy["language_code"],
            "language_name": policy["language_name"],
            "sum_insured_inr": policy["sum_insured_inr"],
            "moisture_drought_threshold": policy["moisture_drought_threshold"],
            "temp_heatwave_threshold": policy["temp_heatwave_threshold"],
            "rainfall_flood_threshold_mm": policy["rainfall_flood_threshold_mm"],
            "active": policy["active"],
            "soil_moisture": telemetry.get("soil_moisture", 30.0),
            "temperature": telemetry.get("temperature", 28.5),
            "humidity": telemetry.get("humidity", 45.0),
            "pressure": telemetry.get("pressure", 1012.0),
            "rainfall_mm": telemetry.get("rainfall_mm", 0.0),
            "status": telemetry.get("status", "NORMAL"),
            "crypto_status": telemetry.get("crypto_status", "SECP256k1: PENDING"),
            "weather_status": telemetry.get("weather_corroboration_status", "WEATHER: CORROBORATED")
        })
    return {
        "grid": grid,
        "tamper_attempts_blocked": engine.tamper_blocked_count
    }

@app.get("/api/basis-risk-comparison")
async def get_basis_risk_comparison():
    ref_weather = SatelliteVerifier.fetch_reference_weather("plot_1")
    return {
        "traditional_pmfby_station": {
            "name": "District IMD Weather Station",
            "distance_from_farm_km": 15.2,
            "recorded_temperature_c": ref_weather.get("temperature_c", 28.5),
            "recorded_rainfall_1h_mm": ref_weather.get("rain_1h_mm", 0.0),
            "station_status": "NORMAL / NO EXTREME MACRO EVENT",
            "claim_decision": "CLAIM REJECTED (0 Payout)",
            "basis_risk_explanation": (
                "District station 15 km away recorded light or zero rain and nominal temperatures. "
                "Traditional PMFBY area-approach failed to detect localized root-zone crop stress on the farmer's plot."
            )
        },
        "agrisentinel_hyperlocal_node": {
            "name": "AgriSentinel Edge Node #1 (Plot 1)",
            "on_farm_soil_moisture_pct": 11.2,
            "on_farm_temperature_c": 42.1,
            "contractual_drought_threshold": 18.0,
            "crypto_verification": "ECDSA SECP256k1 Registered Key Verified",
            "weather_corroboration": "Corroborated with dry atmospheric conditions",
            "simulated_claim_status": "CLAIM INTENT GENERATED (₹50,000 Benefit Calculated)",
            "settlement_integration": "DISBURSEMENT_NOT_CONNECTED (Requires Underwriter Core Banking)",
            "voice_dispatch": "Tamil Audio Advisory Queued for Farmer Mobile"
        }
    }

@app.get("/api/policies")
async def get_policies():
    return {"policies": list(engine.policies.values())}

@app.get("/api/claims")
async def get_claims():
    return {
        "claims": engine.claims,
        "total_claims_count": len(engine.claims),
        "total_benefit_calculated_inr": sum(c.get("payout_calculated_inr", 0) for c in engine.claims),
        "notice": "All claims are simulated Claim Intent records under parametric micro-rider terms."
    }

@app.get("/api/audit")
async def get_audit_log():
    return {
        "audit_log": engine.audit_log,
        "tamper_attempts_blocked": engine.tamper_blocked_count
    }

@app.post("/api/policies/reset")
async def reset_demo_state():
    """Predictable demo reset: clears audit log, claims, and resets replay protection."""
    CryptoEngine.reset_replay_cache()
    res = engine.reset_system()
    return res

@app.post("/api/manual-trigger")
async def manual_trigger(payload: ManualTriggerPayload, background_tasks: BackgroundTasks, request: Request):
    """
    Simulation test override from dashboard/Godot.
    Constructs a valid test packet signed with the simulator's test key.
    """
    node_id = get_farm_profile(payload.plot_id)["assigned_node_id"]
    telemetry_dict = {
        "plot_id": payload.plot_id,
        "soil_moisture": payload.soil_moisture,
        "temperature": payload.temperature,
        "humidity": payload.humidity,
        "pressure": payload.pressure,
        "rainfall_mm": payload.rainfall_mm,
        "timestamp": time.time()
    }

    # Sign using simulator test key
    signed_pkt = CryptoEngine.create_simulated_signed_packet(node_id, telemetry_dict)

    # Ingest through primary verification pipeline
    sig_valid, sig_notes, crypto_metadata = CryptoEngine.verify_telemetry_packet(
        node_id=node_id,
        claimed_plot_id=payload.plot_id,
        signature_hex=signed_pkt["signature"],
        telemetry_dict=telemetry_dict,
        enforce_freshness=False
    )

    eval_result = engine.evaluate_telemetry(
        node_id=node_id,
        telemetry=telemetry_dict,
        sig_valid=sig_valid,
        crypto_metadata=crypto_metadata,
        sig_notes=sig_notes
    )

    if eval_result.get("triggered"):
        base_url = str(request.base_url).rstrip("/")
        lang_code = eval_result.get("language_code", "ta-IN")
        background_tasks.add_task(
            TelecomVoiceEngine.dispatch_voice_alert,
            eval_result["farmer_phone"],
            payload.plot_id,
            eval_result["moisture"],
            eval_result["payout_amount"],
            base_url,
            lang_code
        )

    return {"status": "processed", "evaluation": eval_result}
