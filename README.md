# AgriSentinel 🌾
> **Autonomous Parametric Crop Insurance & Cryptographic 2G Voice Telemetry Platform**

AgriSentinel provides hyper-local, decentralized proof-of-loss for smallholder farmers, eliminating **Basis Risk** in crop insurance by measuring micro-climates directly at the farm fence line.

---

## 🚀 Quick Start for Teammates & Judges (Zero Setup Hassle)

### Step 1: Clone / Download
Download or clone this repository to your laptop.

### Step 2: One-Time Dependency Install (Windows)
Double-click **`setup_env.bat`** (or open terminal and run `pip install -r requirements.txt`).

This automatically installs:
- `fastapi`, `uvicorn` (Core REST API)
- `streamlit`, `pandas` (Enterprise B2B Insurer Cockpit)
- `ecdsa` (SECP256k1 Cryptographic Anti-Fraud Engine)
- `twilio` (Regional 2G Telecom Voice Dispatch)
- `groq` (LLaMA-3.3-70B Agronomic Mitigation Engine)

### Step 3: Run Everything in 1-Click
Double-click **`start_agrisentinel.bat`**!

It automatically:
1. Launches the FastAPI backend (`http://localhost:8000`)
2. Launches the Streamlit insurer dashboard (`http://localhost:8501`)
3. Opens both in your web browser automatically!

To stop the servers anytime, double-click **`stop_agrisentinel.bat`**.

---

## 🧊 AgriSentinel 3D Hardware Model (OpenSCAD)

Explore the detailed 3D hardware model of the AgriSentinel device.

### How to View the 3D Model

1. **Download OpenSCAD:** Install the free, open-source OpenSCAD application from the [official website](https://openscad.org/downloads.html).
2. **Open the Model:** Download [`AgriSentinel_3D_Model_WIRED.scad`](https://github.com/Thishanth-T/Agrisentinel/blob/main/Agrisentinel%203D%20model/AgriSentinel_3D_Model_WIRED.scad) from this repository.
3. **Launch OpenSCAD:** Open the downloaded `.scad` file in OpenSCAD.
4. **Preview the Model:** Press **F5** to preview the 3D model.
5. **Render (Optional):** Press **F6** for a full render. Rendering may take longer depending on your computer.

**Note:** The `.scad` file is a source model, not a ready-to-view image. You need OpenSCAD to open and interact with it. You can rotate, zoom, and inspect the model inside the application.

---

## 🎮 Godot 4 Hardware Simulator (Optional)

If you want to run the 2D hardware grid simulator:

1. Open **Godot 4**.
2. Click **Import** → Select the `godot_simulator` folder.
3. Press **F5** to run the 50×50 m simulated farm grid with real-time ECDSA signing!

---

## 🛠️ Architecture Highlights

- **Cryptographic Anti-Fraud Engine (`crypto_engine.py`):** ECDSA SECP256k1 signatures verify that telemetry originated from authentic on-farm hardware.
- **Satellite Cross-Validation (`satellite_verifier.py`):** Queries OpenWeatherMap / NASA synthetic aperture radar to detect physical tamper (e.g., water-bucket submersion fraud).
- **Multi-Language Regional Voice (`telecom_service.py`):** Dispatches automated phone calls in Hindi, Tamil, Telugu, Gujarati, and other regional tongues without requiring smartphones or apps.
