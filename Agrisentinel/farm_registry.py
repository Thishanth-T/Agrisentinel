"""
AgriSentinel Authoritative Farm & Device Registry
================================================
Single source of truth for all 9 simulated farm profiles across India,
their registered IoT edge devices, SECP256k1 verification keys, and
calibrated parametric insurance thresholds.
"""

from typing import Dict, Any, Optional

# SECP256k1 verification keys registered for physical/simulated edge devices.
# In production hardware, private keys are permanently fused in ESP32 eFuse.
# These test keys are provided strictly for local software simulation.
DEVICE_REGISTRY: Dict[str, Dict[str, Any]] = {
    "node_1": {
        "device_id": "node_1",
        "plot_id": "plot_1",
        "public_key_hex": "65023d2a4b12187fba8ac1802d186f0fc0840b38b3bec077c84cb1a9b0736eab0b0e4ae41f927e662f07dbdd5f3127346e4c6a8e9641a13598e2710137c101b1",
        "status": "REGISTERED",
        "hardware_model": "AgriSentinel-Edge-ESP32-Rev2",
        "sensor_suite": ["BME280", "Capacitive-Soil-v2", "Tipping-Bucket-Rain"]
    },
    "node_2": {
        "device_id": "node_2",
        "plot_id": "plot_2",
        "public_key_hex": "927f04751648241ff1689114c8bbf60858e7ad87f7fb7b4a14918fb24dd328618841a8de2be9522b4619403ddd42ee0e96806a63bf83db569f6b46bafb367111",
        "status": "REGISTERED",
        "hardware_model": "AgriSentinel-Edge-ESP32-Rev2",
        "sensor_suite": ["BME280", "Capacitive-Soil-v2", "Tipping-Bucket-Rain"]
    },
    "node_3": {
        "device_id": "node_3",
        "plot_id": "plot_3",
        "public_key_hex": "b8c16c58666c04df0c3b9d6782c3274e6a3636d202fcba1b270d0d108a37449b22b79f10a9242925192873f3760da31b969044bcbfe9cf5d9dbceff540f52c5d",
        "status": "REGISTERED",
        "hardware_model": "AgriSentinel-Edge-ESP32-Rev2",
        "sensor_suite": ["BME280", "Capacitive-Soil-v2", "Tipping-Bucket-Rain"]
    },
    "node_4": {
        "device_id": "node_4",
        "plot_id": "plot_4",
        "public_key_hex": "a5d7b991da2ab3b32d2e130197edca4ab45c5d3af9d71d12a57f29aeff4e77228f45489dffb2ee746fdeb1d48db8a6e348e10c60fc7c3c6f0a39e37a64f199d1",
        "status": "REGISTERED",
        "hardware_model": "AgriSentinel-Edge-ESP32-Rev2",
        "sensor_suite": ["BME280", "Capacitive-Soil-v2", "Tipping-Bucket-Rain"]
    },
    "node_5": {
        "device_id": "node_5",
        "plot_id": "plot_5",
        "public_key_hex": "655644d21bdf2e4ee10963a4bd0fcc76cb14d95f04a8d27847b640f81871deea4a7f63f0ee0259ce1b856c07c6faf64833235f94db123656ca368c8daf1f4bcd",
        "status": "REGISTERED",
        "hardware_model": "AgriSentinel-Edge-ESP32-Rev2",
        "sensor_suite": ["BME280", "Capacitive-Soil-v2", "Tipping-Bucket-Rain"]
    },
    "node_6": {
        "device_id": "node_6",
        "plot_id": "plot_6",
        "public_key_hex": "b936cbfa6a05fa2a6595b3312575a853986717a21c751a7c955abc03164dbe9302819ac2598efe0e4d47413183bd16bcc475a49783b598a5455b437aac38c1df",
        "status": "REGISTERED",
        "hardware_model": "AgriSentinel-Edge-ESP32-Rev2",
        "sensor_suite": ["BME280", "Capacitive-Soil-v2", "Tipping-Bucket-Rain"]
    },
    "node_7": {
        "device_id": "node_7",
        "plot_id": "plot_7",
        "public_key_hex": "99191acfa9363e23d62cc416944525700f00bee29909b643335303e1b533b8427a628d198aa3af05eefef3646dc7116939be2b7c275f64f1f2f48741a84c099d",
        "status": "REGISTERED",
        "hardware_model": "AgriSentinel-Edge-ESP32-Rev2",
        "sensor_suite": ["BME280", "Capacitive-Soil-v2", "Tipping-Bucket-Rain"]
    },
    "node_8": {
        "device_id": "node_8",
        "plot_id": "plot_8",
        "public_key_hex": "43079074d4451958ab5315ed17fd5830ec23b75587527eaf245fe23c78f9e022918fd59a4b7b49aa74c44a9963bf08ba75387b37273a02acff0318e537f078d1",
        "status": "REGISTERED",
        "hardware_model": "AgriSentinel-Edge-ESP32-Rev2",
        "sensor_suite": ["BME280", "Capacitive-Soil-v2", "Tipping-Bucket-Rain"]
    },
    "node_9": {
        "device_id": "node_9",
        "plot_id": "plot_9",
        "public_key_hex": "0e2d26866e975b21defb424fd66a6b25543a42fd335cdc8a7adca28d9d1968cc643c017f56e455ae65d557bf745f4d71017d9118e813e6ecc69c5e766b7c448a",
        "status": "REGISTERED",
        "hardware_model": "AgriSentinel-Edge-ESP32-Rev2",
        "sensor_suite": ["BME280", "Capacitive-Soil-v2", "Tipping-Bucket-Rain"]
    }
}

# Private keys for software simulation / testing ONLY.
SIMULATOR_TEST_PRIVATE_KEYS: Dict[str, str] = {
    "node_1": "809b73f26e5a0a30ddfb7723a282fc3fe1fc07654465e1ca06cceefcaa4ae57c",
    "node_2": "0df7dc853ae1acfbc2eab2a6b3d611431c0bbaa409d93f9f4823d2799a7f7396",
    "node_3": "c752762e58522278faab5156f513cd9547114ea3d4befae6710229ee9712006e",
    "node_4": "2acb331fc87fc93a9d0c2aef3b716be82fbfac526ec41179ce58e6662692c460",
    "node_5": "74ef6c30526b34ef07c7dffd45f39888b6c0627173c22a9247e659f679ad0ed1",
    "node_6": "915c9a2bec02b9b6c71130d6e6883e29446b2b66d52c5ddfaf936d5c20ce0ce9",
    "node_7": "235e8ccd0d4aba2bb12e1f41d363a218b02e7fdf33fd888054d21dfff0ba203d",
    "node_8": "6a36b035bb5b856fe9732db7b4d4f2b1947fa1b15a4bd20a3c9284ce8eed0fe1",
    "node_9": "394923f03037653bd1e7beed7fcc06f8c85fc3796397b4789bfb53bc722ff3b7"
}

# Authoritative Farm Profiles: 9 distinct regional agricultural profiles across India
FARM_PROFILES: Dict[str, Dict[str, Any]] = {
    "plot_1": {
        "plot_id": "plot_1",
        "assigned_node_id": "node_1",
        "farmer_name": "Murugan K.",
        "phone": "+919363849952",
        "crop": "Paddy",
        "state": "Tamil Nadu",
        "district": "Madurai",
        "region": "Vaigai Basin",
        "lat": 9.9252,
        "lon": 78.1198,
        "language_code": "ta-IN",
        "language_name": "Tamil",
        "sum_insured_inr": 50000.0,
        "moisture_drought_threshold": 18.0,
        "temp_heatwave_threshold": 41.5,
        "rainfall_flood_threshold_mm": 70.0,
        "moisture_saturation_threshold": 88.0,
        "baseline_moisture": 32.0,
        "baseline_temp": 28.5
    },
    "plot_2": {
        "plot_id": "plot_2",
        "assigned_node_id": "node_2",
        "farmer_name": "Ram Prasad",
        "phone": "+919876500002",
        "crop": "Wheat",
        "state": "Uttar Pradesh",
        "district": "Varanasi",
        "region": "Gangetic Plain",
        "lat": 25.3176,
        "lon": 82.9739,
        "language_code": "hi-IN",
        "language_name": "Hindi",
        "sum_insured_inr": 65000.0,
        "moisture_drought_threshold": 18.0,
        "temp_heatwave_threshold": 40.0,
        "rainfall_flood_threshold_mm": 75.0,
        "moisture_saturation_threshold": 88.0,
        "baseline_moisture": 30.0,
        "baseline_temp": 29.0
    },
    "plot_3": {
        "plot_id": "plot_3",
        "assigned_node_id": "node_3",
        "farmer_name": "Patel Bhai",
        "phone": "+919876500003",
        "crop": "Cotton",
        "state": "Gujarat",
        "district": "Anand",
        "region": "Saurashtra Arid Basin",
        "lat": 22.5645,
        "lon": 72.9289,
        "language_code": "gu-IN",
        "language_name": "Gujarati",
        "sum_insured_inr": 75000.0,
        "moisture_drought_threshold": 16.0,
        "temp_heatwave_threshold": 44.0,
        "rainfall_flood_threshold_mm": 65.0,
        "moisture_saturation_threshold": 88.0,
        "baseline_moisture": 28.0,
        "baseline_temp": 31.0
    },
    "plot_4": {
        "plot_id": "plot_4",
        "assigned_node_id": "node_4",
        "farmer_name": "Siva Reddy",
        "phone": "+919876500004",
        "crop": "Chilli",
        "state": "Andhra Pradesh",
        "district": "Guntur",
        "region": "Krishna River Delta",
        "lat": 16.3067,
        "lon": 80.4365,
        "language_code": "te-IN",
        "language_name": "Telugu",
        "sum_insured_inr": 60000.0,
        "moisture_drought_threshold": 18.0,
        "temp_heatwave_threshold": 41.0,
        "rainfall_flood_threshold_mm": 70.0,
        "moisture_saturation_threshold": 88.0,
        "baseline_moisture": 35.0,
        "baseline_temp": 29.5
    },
    "plot_5": {
        "plot_id": "plot_5",
        "assigned_node_id": "node_5",
        "farmer_name": "Debabrata D.",
        "phone": "+919876500005",
        "crop": "Jute",
        "state": "West Bengal",
        "district": "Burdwan",
        "region": "Lower Gangetic Delta",
        "lat": 23.2324,
        "lon": 87.8615,
        "language_code": "bn-IN",
        "language_name": "Bengali",
        "sum_insured_inr": 45000.0,
        "moisture_drought_threshold": 22.0,
        "temp_heatwave_threshold": 39.0,
        "rainfall_flood_threshold_mm": 90.0,
        "moisture_saturation_threshold": 94.0,
        "baseline_moisture": 38.0,
        "baseline_temp": 27.0
    },
    "plot_6": {
        "plot_id": "plot_6",
        "assigned_node_id": "node_6",
        "farmer_name": "Kailash M.",
        "phone": "+919876500006",
        "crop": "Mustard",
        "state": "Rajasthan",
        "district": "Kota",
        "region": "Chambal Arid Corridor",
        "lat": 25.2138,
        "lon": 75.8648,
        "language_code": "hi-IN",
        "language_name": "Hindi",
        "sum_insured_inr": 40000.0,
        "moisture_drought_threshold": 14.0,
        "temp_heatwave_threshold": 45.0,
        "rainfall_flood_threshold_mm": 60.0,
        "moisture_saturation_threshold": 86.0,
        "baseline_moisture": 22.0,
        "baseline_temp": 33.0
    },
    "plot_7": {
        "plot_id": "plot_7",
        "assigned_node_id": "node_7",
        "farmer_name": "Eknath P.",
        "phone": "+919876500007",
        "crop": "Sugarcane",
        "state": "Maharashtra",
        "district": "Nashik",
        "region": "Deccan Plateau",
        "lat": 19.9975,
        "lon": 73.7898,
        "language_code": "mr-IN",
        "language_name": "Marathi",
        "sum_insured_inr": 70000.0,
        "moisture_drought_threshold": 20.0,
        "temp_heatwave_threshold": 42.0,
        "rainfall_flood_threshold_mm": 80.0,
        "moisture_saturation_threshold": 90.0,
        "baseline_moisture": 34.0,
        "baseline_temp": 28.0
    },
    "plot_8": {
        "plot_id": "plot_8",
        "assigned_node_id": "node_8",
        "farmer_name": "Mathew K.",
        "phone": "+919876500008",
        "crop": "Rubber",
        "state": "Kerala",
        "district": "Kottayam",
        "region": "Western Ghats Lowland",
        "lat": 9.4981,
        "lon": 76.3388,
        "language_code": "ml-IN",
        "language_name": "Malayalam",
        "sum_insured_inr": 60000.0,
        "moisture_drought_threshold": 22.0,
        "temp_heatwave_threshold": 38.0,
        "rainfall_flood_threshold_mm": 100.0,
        "moisture_saturation_threshold": 95.0,
        "baseline_moisture": 42.0,
        "baseline_temp": 26.5
    },
    "plot_9": {
        "plot_id": "plot_9",
        "assigned_node_id": "node_9",
        "farmer_name": "Basavaraj B.",
        "phone": "+919876500009",
        "crop": "Maize",
        "state": "Karnataka",
        "district": "Raichur",
        "region": "Tungabhadra Semi-Arid",
        "lat": 16.2076,
        "lon": 77.3463,
        "language_code": "kn-IN",
        "language_name": "Kannada",
        "sum_insured_inr": 48000.0,
        "moisture_drought_threshold": 16.0,
        "temp_heatwave_threshold": 43.0,
        "rainfall_flood_threshold_mm": 70.0,
        "moisture_saturation_threshold": 88.0,
        "baseline_moisture": 31.0,
        "baseline_temp": 29.0
    }
}

def get_registered_device(node_id: str) -> Optional[Dict[str, Any]]:
    return DEVICE_REGISTRY.get(node_id)

def get_farm_profile(plot_id: str) -> Optional[Dict[str, Any]]:
    return FARM_PROFILES.get(plot_id)

def get_node_for_plot(plot_id: str) -> Optional[str]:
    profile = FARM_PROFILES.get(plot_id)
    return profile["assigned_node_id"] if profile else None
