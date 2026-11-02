"""
AgriSentinel Database Layer (SQLite + Schema Versioning)
=======================================================
Implements persistent transactional storage for:
- Farms & Plot configurations
- Registered Devices & SECP256k1 Public Keys
- Device State & Monotonic Sequence Tracking
- Raw Authenticated Telemetry & Packet Archives
- Sensor Health, Battery, and Connectivity Events
- External Meteorological Reference Cache
- Evidence Packages & Trust Reconciliation Records
- Parametric Insurance Policies & Claim Intents
- Hash-Linked Tamper-Evident Audit Trail
"""

import os
import sqlite3
import json
import time
import hashlib
from contextlib import contextmanager
from typing import Dict, List, Any, Optional, Tuple

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agrisentinel.db")

SCHEMA_VERSION = 1

CREATE_TABLES_SQL = """
-- Schema migrations table
CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    applied_at REAL NOT NULL,
    description TEXT NOT NULL
);

-- Registered Farm Profiles
CREATE TABLE IF NOT EXISTS farms (
    plot_id TEXT PRIMARY KEY,
    farmer_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    crop TEXT NOT NULL,
    state TEXT NOT NULL,
    district TEXT NOT NULL,
    region TEXT NOT NULL,
    lat REAL NOT NULL,
    lon REAL NOT NULL,
    language_code TEXT NOT NULL,
    language_name TEXT NOT NULL,
    sum_insured_inr REAL NOT NULL,
    moisture_drought_threshold REAL NOT NULL,
    temp_heatwave_threshold REAL NOT NULL,
    rainfall_flood_threshold_mm REAL NOT NULL,
    moisture_saturation_threshold REAL NOT NULL,
    created_at REAL NOT NULL
);

-- Authoritative Hardware Device Registry
CREATE TABLE IF NOT EXISTS devices (
    device_id TEXT PRIMARY KEY,
    plot_id TEXT NOT NULL,
    public_key_hex TEXT NOT NULL,
    hardware_model TEXT NOT NULL,
    status TEXT NOT NULL, -- REGISTERED, PROVISIONED, DECOMMISSIONED
    created_at REAL NOT NULL,
    FOREIGN KEY(plot_id) REFERENCES farms(plot_id)
);

-- Device State & Sequence Tracking (Monotonic counter & replay defense)
CREATE TABLE IF NOT EXISTS device_state (
    device_id TEXT PRIMARY KEY,
    latest_sequence INTEGER NOT NULL DEFAULT 0,
    latest_timestamp REAL NOT NULL DEFAULT 0.0,
    battery_level REAL NOT NULL DEFAULT 100.0,
    solar_charging INTEGER NOT NULL DEFAULT 1,
    signal_strength INTEGER NOT NULL DEFAULT -65,
    lifecycle_state TEXT NOT NULL DEFAULT 'ONLINE',
    consecutive_sensor_faults INTEGER NOT NULL DEFAULT 0,
    last_seen REAL NOT NULL,
    FOREIGN KEY(device_id) REFERENCES devices(device_id)
);

-- Persistent Telemetry Archive
CREATE TABLE IF NOT EXISTS telemetry_archive (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id TEXT NOT NULL,
    plot_id TEXT NOT NULL,
    sequence INTEGER NOT NULL,
    timestamp REAL NOT NULL,
    temperature REAL NOT NULL,
    humidity REAL NOT NULL,
    pressure REAL NOT NULL,
    soil_moisture REAL NOT NULL,
    rainfall_mm REAL NOT NULL,
    battery_level REAL DEFAULT 100.0,
    signature_hex TEXT NOT NULL,
    digest_hex TEXT NOT NULL,
    is_delayed INTEGER DEFAULT 0,
    reception_timestamp REAL NOT NULL,
    FOREIGN KEY(node_id) REFERENCES devices(device_id),
    FOREIGN KEY(plot_id) REFERENCES farms(plot_id)
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_telemetry_digest ON telemetry_archive(digest_hex);
CREATE INDEX IF NOT EXISTS idx_telemetry_plot_time ON telemetry_archive(plot_id, timestamp);

-- Evidence Packages & Spatial-Temporal Reconciliation
CREATE TABLE IF NOT EXISTS evidence_packages (
    evidence_id TEXT PRIMARY KEY,
    plot_id TEXT NOT NULL,
    node_id TEXT NOT NULL,
    timestamp REAL NOT NULL,
    telemetry_json TEXT NOT NULL,
    device_trust_score REAL NOT NULL,
    device_health_status TEXT NOT NULL,
    reconciliation_outcome TEXT NOT NULL, -- CONSISTENT, LOCALISED_EVENT_POSSIBLE, CONFLICTING_EVIDENCE, etc.
    explanation TEXT NOT NULL,
    external_weather_json TEXT,
    created_at REAL NOT NULL,
    FOREIGN KEY(plot_id) REFERENCES farms(plot_id),
    FOREIGN KEY(node_id) REFERENCES devices(device_id)
);

-- Parametric Claim Intents
CREATE TABLE IF NOT EXISTS claims (
    claim_id TEXT PRIMARY KEY,
    evidence_id TEXT NOT NULL,
    plot_id TEXT NOT NULL,
    farmer_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    crop TEXT NOT NULL,
    trigger_reason TEXT NOT NULL,
    claim_type TEXT NOT NULL, -- DROUGHT, HEATWAVE, FLOOD
    payout_calculated_inr REAL NOT NULL,
    assessment_status TEXT NOT NULL,
    settlement_status TEXT NOT NULL,
    settlement_notice TEXT NOT NULL,
    timestamp REAL NOT NULL,
    FOREIGN KEY(evidence_id) REFERENCES evidence_packages(evidence_id),
    FOREIGN KEY(plot_id) REFERENCES farms(plot_id)
);

-- Hash-Linked Tamper-Evident Audit Trail
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL NOT NULL,
    event_type TEXT NOT NULL,
    plot_id TEXT,
    node_id TEXT,
    payload_digest TEXT,
    result TEXT NOT NULL,
    details_json TEXT NOT NULL,
    prev_hash TEXT NOT NULL,
    current_hash TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_audit_time ON audit_log(timestamp);

-- External Meteorological Observation Cache
CREATE TABLE IF NOT EXISTS weather_reference_cache (
    plot_id TEXT PRIMARY KEY,
    lat REAL NOT NULL,
    lon REAL NOT NULL,
    temperature_c REAL NOT NULL,
    humidity_pct REAL NOT NULL,
    pressure_hpa REAL NOT NULL,
    rain_1h_mm REAL NOT NULL,
    source_name TEXT NOT NULL,
    data_type TEXT NOT NULL,
    cached_at REAL NOT NULL
);
"""

class Database:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self.get_connection() as conn:
            conn.executescript(CREATE_TABLES_SQL)
            # Record initial migration
            row = conn.execute("SELECT version FROM schema_migrations WHERE version = ?", (SCHEMA_VERSION,)).fetchone()
            if not row:
                conn.execute(
                    "INSERT INTO schema_migrations (version, applied_at, description) VALUES (?, ?, ?)",
                    (SCHEMA_VERSION, time.time(), "Initial canonical schema v1.0")
                )
            conn.commit()

    def get_latest_audit_hash(self) -> str:
        with self.get_connection() as conn:
            row = conn.execute("SELECT current_hash FROM audit_log ORDER BY id DESC LIMIT 1").fetchone()
            if row:
                return row["current_hash"]
            return "0000000000000000000000000000000000000000000000000000000000000000"

    def record_audit_event(
        self,
        event_type: str,
        plot_id: Optional[str],
        node_id: Optional[str],
        result: str,
        details: Dict[str, Any],
        payload_digest: Optional[str] = None
    ) -> str:
        prev_hash = self.get_latest_audit_hash()
        now = time.time()
        details_str = json.dumps(details, sort_keys=True)
        
        # Calculate SHA256(prev_hash + event_type + timestamp + details)
        hasher = hashlib.sha256()
        hasher.update(prev_hash.encode("utf-8"))
        hasher.update(event_type.encode("utf-8"))
        hasher.update(str(now).encode("utf-8"))
        hasher.update(details_str.encode("utf-8"))
        current_hash = hasher.hexdigest()

        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO audit_log 
                (timestamp, event_type, plot_id, node_id, payload_digest, result, details_json, prev_hash, current_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (now, event_type, plot_id, node_id, payload_digest, result, details_str, prev_hash, current_hash)
            )
            conn.commit()
        return current_hash

    def verify_audit_trail_integrity(self) -> Tuple[bool, int, Optional[str]]:
        """Validates that no historical record has been modified in the database."""
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM audit_log ORDER BY id ASC").fetchall()
            if not rows:
                return True, 0, None
            
            expected_prev = "0000000000000000000000000000000000000000000000000000000000000000"
            for row in rows:
                if row["prev_hash"] != expected_prev:
                    return False, row["id"], f"Audit trail broken at id {row['id']}: prev_hash mismatch"
                
                hasher = hashlib.sha256()
                hasher.update(row["prev_hash"].encode("utf-8"))
                hasher.update(row["event_type"].encode("utf-8"))
                hasher.update(str(row["timestamp"]).encode("utf-8"))
                hasher.update(row["details_json"].encode("utf-8"))
                computed_hash = hasher.hexdigest()

                if computed_hash != row["current_hash"]:
                    return False, row["id"], f"Audit trail broken at id {row['id']}: content hash mismatch"
                expected_prev = row["current_hash"]

            return True, len(rows), None

# Global database instance
db = Database()
