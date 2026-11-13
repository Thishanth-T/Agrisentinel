# AgriSentinel 🌾
> **Autonomous Parametric Crop Insurance & Hardware-Signed IoT Telemetry Platform**

AgriSentinel is a prototype parametric crop insurance platform that tackles **Basis Risk** in smallholder agriculture. By evaluating micro-climates directly at the farm fence line with cryptographically authenticated IoT telemetry, adaptive device trust scoring, and spatial evidence reconciliation, AgriSentinel enables rapid, verifiable claim decisions without multi-month audit delays.

> [!NOTE]
> **Hardware & Deployment Status**: AgriSentinel is currently an engineering prototype and software simulation testbed. The physical on-farm edge node is fully specified (OpenSCAD 3D enclosure model, circuit schematic, sensor suite, BOM target) and modeled via a 9-node thermodynamic physics simulation engine with authentic ECDSA SECP256k1 signing. Physical hardware deployment and monetary underwriting integration are planned for future field pilots.

---

## 🚀 Quick Start (Zero Setup Hassle)

### Step 1: Clone Repository
```bash
git clone https://github.com/Thishanth-T/Agrisentinel.git
cd Agrisentinel
```

### Step 2: One-Time Environment Setup
* **Windows**: Double-click **`setup_env.bat`** (or open terminal and run `pip install -r requirements.txt`).
* **macOS / Linux**: Run `./setup_env.sh` (or `pip3 install -r requirements.txt && (cd frontend && npm install)`).

### Step 3: Run Platform in 1-Click
* **Windows**: Double-click **`start_agrisentinel.bat`**
* **macOS / Linux**: Run `./start_agrisentinel.sh`

The launcher automatically starts:
1. **FastAPI Ingestion Engine**: `http://localhost:8000` (API Swagger docs at `/docs`)
2. **Animated React Web Interface**: `http://localhost:3000`
3. *(Optional)* **Streamlit Operations Cockpit**: `streamlit run Agrisentinel/dashboard.py` (available on `http://localhost:8501`)

To terminate running services:
* **Windows**: Double-click `stop_agrisentinel.bat`
* **macOS / Linux**: Run `./stop_agrisentinel.sh` (or press `Ctrl+C`)

---

## 🧪 Running the Automated Verification Suite

AgriSentinel includes 49 automated test cases covering cryptographic integrity, replay defense, hardware fault injection, and spatial reconciliation:

```bash
# Set PYTHONPATH to include backend modules
# Windows PowerShell:
$env:PYTHONPATH="Agrisentinel;."
python -m pytest tests/test_comprehensive_validation.py
python -m pytest tests/test_agrisentinel.py
python tests/run_tests.py

# macOS / Linux:
export PYTHONPATH="Agrisentinel:."
pytest tests/test_comprehensive_validation.py
pytest tests/test_agrisentinel.py
python3 tests/run_tests.py
```

---

## 🛠️ Architectural Components

- **Cryptographic Anti-Fraud Engine (`crypto_engine.py`)**: ECDSA SECP256k1 signatures verify that incoming sensor telemetry originates from provisioned hardware keys. Enforces monotonic sequence numbers and persistent SHA-256 replay defense across backend restarts.
- **Adaptive Device Trust Engine (`evidence_reconciliation.py`)**: Continuously monitors transducer health, battery headroom, historical variance, and sudden moisture jumps. Downgrades trust when sensor faults (stuck/drift/spike) are detected, preventing compromised hardware from triggering false claims.
- **Spatial-Temporal Evidence Reconciliation (`evidence_reconciliation.py`)**: Cross-references plot measurements against neighboring farms and independent regional meteorological stations (OpenWeatherMap API / calibrated agro-climatic baseline) to corroborate localized cloudbursts and drought desiccation.
- **Immutable Audit Trail (`database.py`)**: Transactional SQLite database with SHA-256 hash-linked blocks (`audit_log` table) guaranteeing tamper-evident chain of custody.
- **Regional Telecom Voice Dispatch (`telecom_service.py`)**: Generates localized TwiML voice XML in Tamil, Hindi, and regional languages with DTMF keypad confirmation without requiring a smartphone or internet connection.
- **Agronomic Advisory Service (`advisor_service.py`)**: Ground-truth ICAR/KVK-calibrated crop recommendations with explicit pesticide spray cautions, enhanced via Groq LLaMA-3.3-70B with offline deterministic fallback.

---

## 🧊 3D Hardware Specification (OpenSCAD)

The physical AgriSentinel enclosure model is located in [`Agrisentinel 3D model/`](file:///d:/agri%20sentinels/Agrisentinel%203D%20model/).
To view and render the model:
1. Download [OpenSCAD](https://openscad.org/downloads.html).
2. Open [`AgriSentinel_3D_Model_WIRED.scad`](file:///d:/agri%20sentinels/Agrisentinel%203D%20model/AgriSentinel_3D_Model_WIRED.scad).
3. Press **F5** to preview or **F6** to render.

---

## 🎮 Godot 4 Simulation Grid (Optional)

To interact with the visual 50m × 50m farm simulation:
1. Open **Godot 4**.
2. Click **Import** → Select the `godot_simulator` folder.
3. Press **F5** to run the 2D environmental grid simulator with live signing.
