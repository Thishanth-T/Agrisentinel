/**
 * AgriSentinel API Client
 * Connects the React UI to the authoritative FastAPI backend running on http://127.0.0.1:8000
 */

const API_BASE = 'http://127.0.0.1:8000';

export interface FarmPlot {
  plot_id: string;
  node_id: string;
  farmer_name: string;
  phone: string;
  crop: string;
  state: string;
  district: string;
  region: string;
  language_code: string;
  language_name: string;
  sum_insured_inr: number;
  moisture_drought_threshold: number;
  temp_heatwave_threshold: number;
  rainfall_flood_threshold_mm: number;
  active: boolean;
  soil_moisture: number;
  temperature: number;
  humidity: number;
  pressure: number;
  rainfall_mm: number;
  status: string;
  crypto_status: string;
  weather_status: string;
}

export interface BasisRiskData {
  traditional_pmfby_station: {
    name: string;
    distance_from_farm_km: number;
    recorded_temperature_c: number;
    recorded_rainfall_1h_mm: number;
    station_status: string;
    claim_decision: string;
    basis_risk_explanation: string;
  };
  agrisentinel_hyperlocal_node: {
    name: string;
    on_farm_soil_moisture_pct: number;
    on_farm_temperature_c: number;
    contractual_drought_threshold: number;
    crypto_verification: string;
    weather_corroboration: string;
    simulated_claim_status: string;
    settlement_integration: string;
    voice_dispatch: string;
  };
}

export interface ClaimRecord {
  claim_id: string;
  plot_id: string;
  node_id: string;
  farmer_name: string;
  phone: string;
  crop: string;
  state: string;
  district: string;
  region: string;
  language_name: string;
  payout_calculated_inr: number;
  trigger_reason: string;
  claim_type: string;
  timestamp: number;
  assessment_status: string;
  settlement_status: string;
  settlement_notice: string;
}

export interface AuditRecord {
  timestamp: number;
  event: string;
  plot_id: string;
  node_id?: string;
  details?: any;
  result: string;
}

export interface AdvisoryData {
  status: string;
  plot_id: string;
  crop: string;
  state: string;
  language_name: string;
  month: string;
  condition: string;
  actions_english: string[];
  actions_regional: string[];
  spray_caution: string;
  disclaimer: string;
  source: string;
}

export const api = {
  async getHealth() {
    const res = await fetch(`${API_BASE}/health`);
    return res.json();
  },

  async getGrid(): Promise<{ grid: FarmPlot[]; tamper_attempts_blocked: number }> {
    const res = await fetch(`${API_BASE}/api/grid`);
    return res.json();
  },

  async getBasisRisk(): Promise<BasisRiskData> {
    const res = await fetch(`${API_BASE}/api/basis-risk-comparison`);
    return res.json();
  },

  async getClaims(): Promise<{ claims: ClaimRecord[]; total_claims_count: number; total_benefit_calculated_inr: number }> {
    const res = await fetch(`${API_BASE}/api/claims`);
    return res.json();
  },

  async getAudit(): Promise<{ audit_log: AuditRecord[]; tamper_attempts_blocked: number }> {
    const res = await fetch(`${API_BASE}/api/audit`);
    return res.json();
  },

  async getAdvisory(plotId: string): Promise<AdvisoryData> {
    const res = await fetch(`${API_BASE}/api/advisory/${plotId}`);
    return res.json();
  },

  async manualTrigger(payload: {
    plot_id: string;
    soil_moisture: number;
    temperature: number;
    humidity?: number;
    pressure?: number;
    rainfall_mm?: number;
  }) {
    const res = await fetch(`${API_BASE}/api/manual-trigger`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return res.json();
  },

  async triggerVoice(payload: {
    plot_id: string;
    phone_number: string;
  }) {
    const res = await fetch(`${API_BASE}/api/telecom/trigger-voice`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return res.json();
  },

  async resetState() {
    const res = await fetch(`${API_BASE}/api/policies/reset`, {
      method: 'POST',
    });
    return res.json();
  },

  async signSimulator(nodeId: string, telemetry: any) {
    const res = await fetch(`${API_BASE}/api/crypto/sign`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ node_id: nodeId, telemetry }),
    });
    return res.json();
  }
};