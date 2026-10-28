import os
import sys
import time
from typing import Dict, Any, Optional
from fastapi import FastAPI, BackgroundTasks, HTTPException, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from crypto_engine import CryptoEngine
from satellite_verifier import SatelliteVerifier
from insurance_engine import engine
from advisor_service import GroqAdvisoryService
from telecom_service import TelecomVoiceEngine, VOICE_WEBHOOK_URLS

app = FastAPI(
    title="AgriSentinel Enterprise API",
    description="Autonomous Parametric Crop Insurance & Cryptographic Anti-Fraud Ingestion Engine",
    version="2.0.0",
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
    temperature: float = Field(..., example=32.5)
    humidity: float = Field(default=45.0, example=45.0)
    pressure: float = Field(default=1012.0, example=1012.0)
    soil_moisture: float = Field(..., example=11.2)
    rainfall_mm: float = Field(default=0.0, example=0.0)

class TelemetryPayload(BaseModel):
    node_id: str = Field(..., example="node_1")
    public_key: str = Field(..., example="04b50c128ff0b1a0f9687e35aa19842f778a4869c9b466184a1d48c0a87a8a25c114e9f7833076ecf258a36021200be649f807be1778c8531ebcd7ff514120ec0e")
    signature: str = Field(..., example="30440220668b5774b7858c49e29a393d25ce4aa1d1136b3d4f82877a5b3ee28e67da9c5a022026130424fb2f342721ab8dfb776dc6be2e4cfc3822a16d5e1882d41ab02c0b05")
    telemetry: TelemetryData

class ManualTriggerPayload(BaseModel):
    plot_id: str
    soil_moisture: float
    temperature: float
    humidity: float = 40.0
    pressure: float = 1012.0
    rainfall_mm: float = 0.0

class TriggerVoicePayload(BaseModel):
    plot_id: str = Field(..., example="plot_1")
    phone_number: str = Field(..., example="+919363849952")
    custom_url: Optional[str] = None
    twilio_sid: Optional[str] = None
    twilio_token: Optional[str] = None
    twilio_phone: Optional[str] = None

class CryptoSignRequest(BaseModel):
    node_id: str = Field(default="node_1")
    telemetry: Dict[str, Any]

@app.get("/health")
async def health_check():
    return {
        "status": "operational",
        "system": "AgriSentinel Enterprise Ingestion Platform",
        "version": "2.0.0",
        "timestamp": time.time(),
        "cryptographic_engine": "ECDSA-SECP256k1",
        "satellite_cross_verifier": "Active",
        "tamper_attempts_blocked": engine.tamper_blocked_count,
        "active_monitored_nodes": len(engine.policies)
    }

@app.post("/api/crypto/sign")
async def sign_telemetry_packet(payload: CryptoSignRequest):
    sk, vk = CryptoEngine.get_or_create_node_keypair(payload.node_id)
    signed_packet = CryptoEngine.create_signed_packet(payload.node_id, sk, vk, payload.telemetry)
    return signed_packet

@app.post("/api/telemetry")
async def ingest_telemetry(payload: TelemetryPayload, background_tasks: BackgroundTasks, request: Request):
    telemetry_dict = payload.telemetry.model_dump()
    sig_valid, sig_notes = CryptoEngine.verify_payload(
        public_key_hex=payload.public_key,
        data=telemetry_dict,
        signature_hex=payload.signature,
        check_freshness=False
    )

    result = engine.evaluate_telemetry(
        node_id=payload.node_id,
        telemetry=telemetry_dict,
        sig_valid=sig_valid,
        sig_notes=sig_notes
    )

    if not sig_valid:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "FORBIDDEN_CRYPTOGRAPHIC_TAMPER_DETECTED",
                "message": sig_notes,
                "node_id": payload.node_id,
                "curve": "SECP256k1"
            }
        )

    if result.get("status") == "HELD_PHYSICAL_TAMPERING_AUDIT":
        return {
            "status": "HELD_FOR_AUDIT",
            "cryptographic_verification": "SECP256k1_VALID",
            "satellite_cross_check": "TAMPER_AUDIT_REQUIRED",
            "evaluation": result
        }

    if result.get("triggered"):
        base_url = str(request.base_url).rstrip("/")
        lang_code = result.get("language_code", "en-IN")
        background_tasks.add_task(
            TelecomVoiceEngine.dispatch_voice_alert,
            result["farmer_phone"],
            payload.telemetry.plot_id,
            result["moisture"],
            result["payout_amount"],
            base_url,
            lang_code
        )

    return {
        "status": "success",
        "cryptographic_verification": "SECP256k1_VALID",
        "satellite_cross_check": result.get("satellite_verification", {}).get("status", "SATELLITE_VERIFIED"),
        "evaluation": result
    }

@app.get("/api/advisory/{plot_id}")
async def get_advisory(plot_id: str, month: str = ""):
    policy = engine.policies.get(plot_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Farm plot not found in policy registry")

    telemetry = engine.plot_telemetry.get(plot_id, {})
    moisture = telemetry.get("soil_moisture", 14.5)
    temp = telemetry.get("temperature", 38.0)
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
    moisture = telemetry.get("soil_moisture", 11.5)
    amount = policy.get("sum_insured", 50000.0)
    base_url = str(request.base_url).rstrip("/")
    lang_code = policy.get("language_code", "en-IN")

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

@app.get("/api/twilio/voice", operation_id="twilio_voice_get_v2")
@app.post("/api/twilio/voice", operation_id="twilio_voice_post_v2")
async def twilio_voice_webhook(plot_id: str = "plot_1", moisture: float = 14.0, amount: float = 50000.0):
    policy = engine.policies.get(plot_id, {})
    lang = policy.get("language_code", "en-IN")
    twiml_content = TelecomVoiceEngine.generate_breach_twiml(plot_id, moisture, amount, lang)
    return Response(content=twiml_content, media_type="application/xml")

@app.post("/api/twilio/gather")
async def twilio_gather_webhook(request: Request):
    form_data = await request.form()
    digits = form_data.get("Digits", "")
    twiml_content = TelecomVoiceEngine.generate_gather_response(str(digits))
    return Response(content=twiml_content, media_type="application/xml")

@app.post("/api/twilio/call")
async def trigger_legacy_call(payload: Dict[str, Any], request: Request):
    phone = payload.get("phone", "+15550101")
    plot_id = payload.get("plot_id", "plot_1")
    moisture = float(payload.get("moisture", 12.0))
    amount = float(payload.get("amount", 50000.0))
    custom_url = payload.get("voice_url")
    policy = engine.policies.get(plot_id, {})
    lang_code = policy.get("language_code", "en-IN")
    base_url = str(request.base_url).rstrip("/")

    dispatch_result = await TelecomVoiceEngine.dispatch_voice_alert(
        phone, plot_id, moisture, amount, base_url, lang_code, custom_url
    )
    return dispatch_result

@app.get("/api/grid")
async def get_grid_state():
    grid = []
    for pid, policy in engine.policies.items():
        telemetry = engine.plot_telemetry.get(pid, {})
        grid.append({
            "plot_id": pid,
            "grid_x": policy["grid_x"],
            "grid_y": policy["grid_y"],
            "farmer_name": policy["farmer_name"],
            "phone": policy["phone"],
            "crop": policy["crop"],
            "state": policy["state"],
            "region": policy.get("region", ""),
            "language_code": policy["language_code"],
            "language_name": policy["language_name"],
            "sum_insured": policy["sum_insured"],
            "moisture_threshold": policy["moisture_threshold"],
            "temp_threshold": policy["temp_threshold"],
            "flood_moisture_threshold": policy.get("flood_moisture_threshold", 88.0),
            "active": policy["active"],
            "soil_moisture": telemetry.get("soil_moisture", 30.0),
            "temperature": telemetry.get("temperature", 28.0),
            "humidity": telemetry.get("humidity", 45.0),
            "pressure": telemetry.get("pressure", 1012.0),
            "rainfall_mm": telemetry.get("rainfall_mm", 0.0),
            "status": telemetry.get("status", "NORMAL"),
            "crypto_status": telemetry.get("crypto_status", "SECP256k1: VALID"),
            "satellite_status": telemetry.get("satellite_status", "SATELLITE: MATCHED"),
            "satellite_data": telemetry.get("satellite_data", {})
        })
    return {
        "grid": grid,
        "tamper_attempts_blocked": engine.tamper_blocked_count
    }

@app.get("/api/basis-risk-comparison")
async def get_basis_risk_comparison():
    sat_macro = SatelliteVerifier.fetch_macro_satellite_data("plot_1")
    return {
        "pmfby_traditional_station": {
            "name": "District Weather Station (IMD)",
            "distance_from_farm_km": 15.2,
            "recorded_temperature_c": 28.5,
            "recorded_rainfall_24h_mm": 12.0,
            "recorded_relative_humidity": 68.0,
            "macro_status": "NORMAL / NO EXTREME EVENT",
            "payout_status": "CLAIM REJECTED (0 Payout)",
            "basis_risk_failure_explanation": (
                "District station 15 km away recorded light showers. Traditional PMFBY policy "
                "failed to detect localized root-zone drought on the farmer's plot, leaving the farmer uncompensated."
            )
        },
        "agrisentinel_hyperlocal_node": {
            "name": "AgriSentinel Fence Node #1",
            "grid_resolution": "50x50m micro-polygon",
            "on_farm_temperature_c": 43.8,
            "on_farm_soil_moisture_pct": 11.5,
            "drought_threshold_pct": 18.0,
            "crypto_signature_status": "ECDSA-SECP256k1 VALID",
            "satellite_cross_check": "SATELLITE VERIFIED (Thermal anomaly matches)",
            "payout_status": "INSTANT AUTOMATED PAYOUT (Rs. 50,000 DISBURSED)",
            "latency_seconds": 1.4,
            "voice_alert_dispatch": "Tamil Voice Call Dispatched to Farmer Mobile"
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
        "total_disbursed_inr": sum(c.get("payout_amount", 0) for c in engine.claims)
    }

@app.get("/api/audit")
async def get_audit_log():
    return {
        "audit_log": engine.audit_log,
        "tamper_attempts_blocked": engine.tamper_blocked_count
    }

@app.post("/api/policies/reset")
async def reset_policies():
    for pid in engine.policies:
        engine.policies[pid]["active"] = True
        engine.plot_telemetry[pid]["status"] = "NORMAL"
        engine.plot_telemetry[pid]["soil_moisture"] = 32.0
        engine.plot_telemetry[pid]["temperature"] = 28.5
        engine.plot_telemetry[pid]["rainfall_mm"] = 0.0
        engine.plot_telemetry[pid]["crypto_status"] = "SECP256k1: PENDING"
        engine.plot_telemetry[pid]["satellite_status"] = "SATELLITE: SYNCHRONIZED"
    engine.claims.clear()
    engine.audit_log.clear()
    engine.tamper_blocked_count = 0
    return {"status": "reset_successful"}

@app.post("/api/manual-trigger")
async def manual_trigger(payload: ManualTriggerPayload, background_tasks: BackgroundTasks, request: Request):
    telemetry_dict = {
        "plot_id": payload.plot_id,
        "soil_moisture": payload.soil_moisture,
        "temperature": payload.temperature,
        "humidity": payload.humidity,
        "pressure": payload.pressure,
        "rainfall_mm": payload.rainfall_mm,
        "timestamp": time.time()
    }

    result = engine.evaluate_telemetry("manual_override", telemetry_dict, sig_valid=True, sig_notes="Manual override trigger via dashboard")
    if result.get("triggered"):
        base_url = str(request.base_url).rstrip("/")
        lang_code = result.get("language_code", "en-IN")
        background_tasks.add_task(
            TelecomVoiceEngine.dispatch_voice_alert,
            result["farmer_phone"],
            payload.plot_id,
            result["moisture"],
            result["payout_amount"],
            base_url,
            lang_code
        )
    return {"status": "processed", "evaluation": result}

if __name__ == "__main__":
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True, workers=1)
