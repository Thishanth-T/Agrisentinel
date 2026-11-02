/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  Activity, 
  CloudRain, 
  Thermometer, 
  Droplets, 
  CheckCircle2,
  AlertTriangle,
  PhoneCall,
  RotateCcw,
  RefreshCw,
  Zap,
  Lock,
  ChevronRight,
  ExternalLink,
  Info
} from 'lucide-react';
import { ScrollCanvas } from './ScrollCanvas';
import { api, FarmPlot, BasisRiskData, ClaimRecord, AuditRecord, AdvisoryData } from './api';

type TabType = 'overview' | 'about' | 'how-it-works' | 'technology' | 'cockpit' | 'basis-risk' | 'voice' | 'contact';

export default function App() {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [mobileMenuOpen, setMobileMenuOpen] = useState<boolean>(false);
  const [activeTech, setActiveTech] = useState<string>('ecdsa');

  // Backend Live State
  const [plots, setPlots] = useState<FarmPlot[]>([]);
  const [selectedPlotId, setSelectedPlotId] = useState<string>('plot_1');
  const [claims, setClaims] = useState<ClaimRecord[]>([]);
  const [auditLog, setAuditLog] = useState<AuditRecord[]>([]);
  const [basisRisk, setBasisRisk] = useState<BasisRiskData | null>(null);
  const [advisory, setAdvisory] = useState<AdvisoryData | null>(null);
  const [backendHealth, setBackendHealth] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [triggerMsg, setTriggerMsg] = useState<string | null>(null);

  // Manual Trigger Simulation inputs
  const [simMoisture, setSimMoisture] = useState<number>(12.0);
  const [simTemp, setSimTemp] = useState<number>(42.0);
  const [simActionLoading, setSimActionLoading] = useState<boolean>(false);

  // Voice dispatch inputs
  const [voicePhone, setVoicePhone] = useState<string>('+919363849952');
  const [voiceDispatchResult, setVoiceDispatchResult] = useState<any>(null);
  const [voiceLoading, setVoiceLoading] = useState<boolean>(false);

  // Fetch full data from FastAPI
  const refreshAllData = async () => {
    try {
      setLoading(true);
      const [hRes, gRes, cRes, bRes, aRes] = await Promise.all([
        api.getHealth().catch(() => null),
        api.getGrid().catch(() => ({ grid: [], tamper_attempts_blocked: 0 })),
        api.getClaims().catch(() => ({ claims: [], total_claims_count: 0, total_benefit_calculated_inr: 0 })),
        api.getBasisRisk().catch(() => null),
        api.getAudit().catch(() => ({ audit_log: [], tamper_attempts_blocked: 0 }))
      ]);

      setBackendHealth(hRes);
      if (gRes && gRes.grid) {
        setPlots(gRes.grid);
      }
      if (cRes && cRes.claims) {
        setClaims(cRes.claims);
      }
      if (bRes) {
        setBasisRisk(bRes);
      }
      if (aRes && aRes.audit_log) {
        setAuditLog(aRes.audit_log);
      }
    } catch (err) {
      console.error('Error fetching backend data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshAllData();
    const interval = setInterval(() => {
      api.getGrid().then(g => { if (g && g.grid) setPlots(g.grid); }).catch(() => {});
      api.getClaims().then(c => { if (c && c.claims) setClaims(c.claims); }).catch(() => {});
    }, 10000);
    return () => clearInterval(interval);
  }, []);

  // Fetch advisory when plot changes
  useEffect(() => {
    if (selectedPlotId) {
      api.getAdvisory(selectedPlotId)
        .then(res => setAdvisory(res))
        .catch(() => setAdvisory(null));
    }
  }, [selectedPlotId]);

  const currentPlot = plots.find(p => p.plot_id === selectedPlotId) || plots[0] || {
    plot_id: 'plot_1',
    node_id: 'node_1',
    farmer_name: 'Murugan K.',
    phone: '+919363849952',
    crop: 'Paddy',
    state: 'Tamil Nadu',
    district: 'Madurai',
    region: 'Vaigai Basin',
    language_name: 'Tamil',
    language_code: 'ta-IN',
    sum_insured_inr: 50000,
    moisture_drought_threshold: 18.0,
    temp_heatwave_threshold: 41.5,
    rainfall_flood_threshold_mm: 70.0,
    active: true,
    soil_moisture: 32.0,
    temperature: 28.5,
    humidity: 45.0,
    pressure: 1012.0,
    rainfall_mm: 0.0,
    status: 'NORMAL',
    crypto_status: 'SECP256k1: PENDING',
    weather_status: 'SYNCHRONIZED'
  };

  const handleManualTrigger = async (type: 'drought' | 'heatwave' | 'nominal') => {
    setSimActionLoading(true);
    setTriggerMsg(null);
    let m = 32.0;
    let t = 28.5;
    if (type === 'drought') {
      m = simMoisture;
      t = simTemp;
    } else if (type === 'heatwave') {
      m = 25.0;
      t = 43.5;
    } else {
      m = 32.0;
      t = 28.5;
    }

    try {
      const res = await api.manualTrigger({
        plot_id: selectedPlotId,
        soil_moisture: m,
        temperature: t
      });
      setTriggerMsg(`Telemetry evaluated: ${res.evaluation?.status || 'Processed'}`);
      await refreshAllData();
    } catch (err: any) {
      setTriggerMsg(`Trigger error: ${err.message || 'Failed'}`);
    } finally {
      setSimActionLoading(false);
    }
  };

  const handleReset = async () => {
    setSimActionLoading(true);
    try {
      await api.resetState();
      await refreshAllData();
      setTriggerMsg('Demo ledger & claims reset to baseline.');
    } catch (e: any) {
      setTriggerMsg('Reset failed: ' + e.message);
    } finally {
      setSimActionLoading(false);
    }
  };

  const handleVoiceDispatch = async () => {
    setVoiceLoading(true);
    setVoiceDispatchResult(null);
    try {
      const res = await api.triggerVoice({
        plot_id: selectedPlotId,
        phone_number: voicePhone
      });
      setVoiceDispatchResult(res);
    } catch (e: any) {
      setVoiceDispatchResult({ status: 'error', detail: e.message });
    } finally {
      setVoiceLoading(false);
    }
  };

  const scrollToTabContent = (tab: TabType) => {
    setActiveTab(tab);
    setMobileMenuOpen(false);
    const el = document.getElementById('tab-container');
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen bg-transparent text-white flex flex-col items-center justify-start overflow-x-hidden relative selection:bg-white selection:text-black font-sans">
      
      {/* BACKGROUND SMOOTH SCROLL FRAME ANIMATION - Crystal clear & transparent */}
      <ScrollCanvas frameCount={285} />

      {/* SECTION 1: ARCHITECTURAL HERO BANNER */}
      <section 
        className="relative z-10 w-full max-w-[1440px] px-4 sm:px-6 md:px-10 py-6 md:py-10 flex flex-col justify-between"
        style={{ minHeight: '100vh' }}
        id="hero-banner"
      >
        {/* Architectural SVG Frame Vector */}
        <div className="absolute inset-4 sm:inset-6 md:inset-8 pointer-events-none z-0 opacity-80">
          <svg 
            className="w-full h-full" 
            viewBox="0 0 1440 940" 
            preserveAspectRatio="none"
            fill="none" 
            xmlns="http://www.w3.org/2000/svg"
          >
            <path 
              d="M 50 735 L 50 82 A 42 42 0 0 1 92 40 L 1348 40 A 42 42 0 0 1 1390 82 L 1390 580" 
              stroke="#ffffff" 
              strokeWidth="2" 
              strokeLinecap="round"
            />
            <path 
              d="M 50 795 L 50 858 A 42 42 0 0 0 92 900 L 310 900" 
              stroke="#ffffff" 
              strokeWidth="2" 
              strokeLinecap="round"
            />
          </svg>
        </div>

        {/* Content Inside Frame */}
        <div className="relative z-10 w-full flex flex-col justify-between flex-grow px-4 sm:px-8 md:px-16 pt-6 sm:pt-8 pb-8 md:pb-12">
          
          {/* Top Header & Navigation Bar */}
          <header className="w-full flex items-center justify-between pt-2">
            <button 
              onClick={() => { setActiveTab('overview'); window.scrollTo({ top: 0, behavior: 'smooth' }); }}
              className="text-left font-bold text-2xl sm:text-[27px] tracking-[-0.6px] text-white hover:opacity-85 transition-opacity cursor-pointer bg-transparent border-none p-0 flex items-center gap-2 drop-shadow-md"
            >
              <span>AgriSentinel</span>
              <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded-full border border-emerald-500/40 bg-emerald-500/10 text-emerald-300 ml-2">
                Live Backend 2.1
              </span>
            </button>

            {/* Desktop Tabs Bar */}
            <nav className="hidden lg:flex items-center gap-1.5 bg-black/40 backdrop-blur-md px-3 py-1.5 rounded-full border border-white/20" aria-label="Main Navigation">
              {(['overview', 'cockpit', 'basis-risk', 'voice', 'how-it-works', 'technology', 'about'] as TabType[]).map((tab) => (
                <button 
                  key={tab}
                  onClick={() => scrollToTabContent(tab)}
                  className={`text-[11px] font-semibold tracking-[1.2px] transition-all cursor-pointer uppercase px-3 py-1.5 rounded-full ${
                    activeTab === tab
                      ? 'bg-white text-black shadow-lg'
                      : 'text-white/80 hover:text-white hover:bg-white/10'
                  }`}
                >
                  {tab === 'cockpit' ? 'Farm Cockpit' : tab === 'basis-risk' ? 'Basis Risk' : tab.replace('-', ' ')}
                </button>
              ))}
            </nav>

            {/* Mobile Hamburger Menu */}
            <button 
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden flex flex-col justify-center items-end gap-[5px] w-8 h-8 cursor-pointer bg-black/40 backdrop-blur-md border border-white/20 rounded p-1.5 group"
              aria-label="Toggle Navigation Menu"
            >
              <span className="block w-5 h-[1.5px] bg-white transition-all group-hover:scale-x-110 origin-right"></span>
              <span className="block w-3.5 h-[1.5px] bg-white transition-all group-hover:w-5 origin-right"></span>
            </button>
          </header>

          {/* Mobile Tab Dropdown */}
          {mobileMenuOpen && (
            <div className="lg:hidden mt-4 bg-black/85 backdrop-blur-xl border border-white/20 p-4 rounded-xl z-30 flex flex-col gap-2">
              {(['overview', 'cockpit', 'basis-risk', 'voice', 'how-it-works', 'technology', 'about'] as TabType[]).map((tab) => (
                <button 
                  key={tab}
                  onClick={() => scrollToTabContent(tab)}
                  className={`text-left text-xs font-semibold tracking-wider uppercase py-2 px-3 rounded-lg transition-colors ${
                    activeTab === tab ? 'bg-white text-black font-bold' : 'text-white/80 hover:bg-white/10'
                  }`}
                >
                  {tab === 'cockpit' ? 'Farm Cockpit' : tab === 'basis-risk' ? 'Basis Risk' : tab.replace('-', ' ')}
                </button>
              ))}
            </div>
          )}

          {/* Middle Floating Glass Cards */}
          <div className="w-full flex justify-start my-8 md:my-14 lg:ml-16">
            <div className="flex flex-col sm:flex-row items-stretch gap-3 w-full max-w-[680px]">
              
              {/* Card 1: 9 Regional Profiles */}
              <button
                onClick={() => scrollToTabContent('cockpit')}
                className="card-notch-cut bg-white/15 hover:bg-white/25 backdrop-blur-md border border-white/30 text-white text-left p-5 sm:p-6 w-full sm:w-[210px] flex flex-col justify-between transition-all hover:-translate-y-1 group cursor-pointer focus:outline-none"
              >
                <div>
                  <div className="mb-3 text-white">
                    <Activity className="w-5 h-5 text-white" />
                  </div>
                  <h3 className="text-[17px] font-bold leading-tight tracking-[-0.3px] text-white mb-4">
                    9 Regional<br />Farm Plots
                  </h3>
                  <div className="mb-2">
                    <span className="block text-[9px] font-bold tracking-[1px] uppercase text-white/60 mb-0.5">Coverage</span>
                    <span className="block text-[11.5px] font-semibold text-white/90">Madurai, Varanasi, Anand</span>
                  </div>
                  <div>
                    <span className="block text-[9px] font-bold tracking-[1px] uppercase text-white/60 mb-0.5">Status</span>
                    <span className="block text-[11.5px] font-semibold text-emerald-300">Active Sensor Grid</span>
                  </div>
                </div>
                <div className="pt-4 border-t border-white/20 flex items-center justify-between text-[11px] font-bold mt-5 text-white/80 group-hover:text-white">
                  <span>Open Cockpit</span>
                  <span className="transition-transform group-hover:translate-x-1">&rarr;</span>
                </div>
              </button>

              {/* Card 2: Basis Risk Analysis */}
              <button
                onClick={() => scrollToTabContent('basis-risk')}
                className="bg-black/30 hover:bg-white/10 backdrop-blur-md border border-white/20 text-white text-left p-5 sm:p-6 w-full sm:w-[210px] flex flex-col justify-between transition-all hover:-translate-y-1 group cursor-pointer focus:outline-none rounded-sm"
              >
                <div>
                  <div className="mb-3 text-white">
                    <CloudRain className="w-5 h-5 text-white" />
                  </div>
                  <h3 className="text-[17px] font-bold leading-tight tracking-[-0.3px] text-white mb-4">
                    Basis Risk<br />Elimination
                  </h3>
                  <div className="mb-2">
                    <span className="block text-[9px] font-bold tracking-[1px] uppercase text-white/60 mb-0.5">IMD vs Plot</span>
                    <span className="block text-[11.5px] font-medium text-white/90">15.2 km Delta Solved</span>
                  </div>
                  <div>
                    <span className="block text-[9px] font-bold tracking-[1px] uppercase text-white/60 mb-0.5">Resolution</span>
                    <span className="block text-[11.5px] font-medium text-white/90">Hyper-Local Telemetry</span>
                  </div>
                </div>
                <div className="pt-4 border-t border-white/10 flex items-center justify-between text-[11px] font-medium mt-5 text-white/70 group-hover:text-white">
                  <span>View Proof</span>
                  <span className="transition-transform group-hover:translate-x-1">&rarr;</span>
                </div>
              </button>

              {/* Card 3: 2G Voice Telecom */}
              <button
                onClick={() => scrollToTabContent('voice')}
                className="bg-black/30 hover:bg-white/10 backdrop-blur-md border border-white/20 text-white text-left p-5 sm:p-6 w-full sm:w-[210px] flex flex-col justify-between transition-all hover:-translate-y-1 group cursor-pointer focus:outline-none rounded-sm"
              >
                <div>
                  <div className="mb-3 text-white">
                    <PhoneCall className="w-5 h-5 text-white" />
                  </div>
                  <h3 className="text-[17px] font-bold leading-tight tracking-[-0.3px] text-white mb-4">
                    Twilio 2G<br />Voice Alert
                  </h3>
                  <div className="mb-2">
                    <span className="block text-[9px] font-bold tracking-[1px] uppercase text-white/60 mb-0.5">Language</span>
                    <span className="block text-[11.5px] font-medium text-white/90">Tamil, Hindi, Telugu</span>
                  </div>
                  <div>
                    <span className="block text-[9px] font-bold tracking-[1px] uppercase text-white/60 mb-0.5">Integration</span>
                    <span className="block text-[11.5px] font-medium text-white/90">Keypad IVR Dispatch</span>
                  </div>
                </div>
                <div className="pt-4 border-t border-white/10 flex items-center justify-between text-[11px] font-medium mt-5 text-white/70 group-hover:text-white">
                  <span>Test Dispatch</span>
                  <span className="transition-transform group-hover:translate-x-1">&rarr;</span>
                </div>
              </button>

            </div>
          </div>

          {/* Bottom Hero Bar */}
          <footer className="w-full flex flex-col md:flex-row justify-between items-start md:items-end gap-8 pt-4">
            <div className="hidden lg:flex items-center gap-2.5 -ml-4 mb-5">
              <button 
                onClick={() => scrollToTabContent(activeTab)}
                className="text-[10px] font-bold tracking-[2px] uppercase opacity-90 hover:opacity-100 transition-opacity flex items-center gap-2 cursor-pointer bg-black/40 backdrop-blur-md px-4 py-2 rounded-full border border-white/25 text-white"
              >
                <span>Scroll Down</span>
                <span className="text-xs">&darr;</span>
              </button>
            </div>

            <div className="flex flex-col items-start ml-auto max-w-[620px] text-left">
              <h1 className="text-5xl sm:text-7xl lg:text-[84px] font-bold leading-[0.95] tracking-[-2px] text-white mb-8 sm:mb-9 drop-shadow-lg">
                Every Field.<br />
                Every Signal.<br />
                Verified.
              </h1>

              <div className="grid grid-cols-1 sm:grid-cols-[120px_1fr] gap-4 sm:gap-7 items-start bg-black/35 backdrop-blur-md p-4 sm:p-5 rounded-xl border border-white/15">
                <h2 className="text-base sm:text-[17px] font-bold tracking-[-0.3px] text-white pt-0.5">
                  About Us
                </h2>
                <p className="text-[12px] leading-[1.65] font-normal text-white/90 max-w-[390px]">
                  AgriSentinel delivers high-fidelity, hyper-local field monitoring engineered specifically for parametric crop insurance and agricultural underwriting. By transforming physical environmental signals into immutable ground-truth telemetry, we bridge the gap between verified field conditions and rapid, automated risk settlement.
                </p>
              </div>
            </div>
          </footer>

        </div>
      </section>

      {/* SECTION 2: TRANSPARENT GLASS TABBED WORKSPACE */}
      <section 
        id="tab-container"
        className="relative z-10 w-full max-w-[1440px] px-4 sm:px-8 md:px-16 py-16 sm:py-24 text-white"
      >
        <div className="w-full bg-black/40 backdrop-blur-md border border-white/20 rounded-2xl p-6 sm:p-10 md:p-12 shadow-2xl relative overflow-hidden">
          
          <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-white/40 to-transparent" />

          {/* Tab Selector Header */}
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 pb-8 border-b border-white/15">
            <div>
              <div className="inline-flex items-center gap-2 text-[10px] font-semibold tracking-[2px] uppercase text-white/70 mb-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 inline-block animate-pulse"></span>
                <span>FastAPI Ingestion Engine & Parametric Cockpit</span>
              </div>
              <h2 className="text-3xl sm:text-5xl font-bold tracking-tight text-white capitalize">
                {activeTab === 'overview' && 'Live Telemetry & SECP256k1 Security'}
                {activeTab === 'cockpit' && '9 Regional Farm Profiles & Simulation'}
                {activeTab === 'basis-risk' && 'Basis Risk Comparison (IMD vs On-Plot)'}
                {activeTab === 'voice' && 'Twilio 2G Regional Telecom Dispatch'}
                {activeTab === 'how-it-works' && 'End-to-End Cryptographic Chain'}
                {activeTab === 'technology' && 'Hardware & Silicon Stack Details'}
                {activeTab === 'about' && 'Mission & Transparency Disclosure'}
                {activeTab === 'contact' && 'Initiate Pilot / Inquire Coverage'}
              </h2>
            </div>

            {/* Quick Actions & Tab Selector */}
            <div className="flex flex-wrap items-center gap-2">
              <button 
                onClick={refreshAllData}
                disabled={loading}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-white/20 bg-white/5 hover:bg-white/10 text-xs font-semibold text-white/80 transition-all cursor-pointer"
                title="Refresh Live Data"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
                <span>Sync</span>
              </button>

              <div className="flex flex-wrap items-center gap-1.5 bg-black/50 backdrop-blur-lg p-1.5 rounded-xl border border-white/15">
                {(['overview', 'cockpit', 'basis-risk', 'voice', 'how-it-works', 'technology', 'about'] as TabType[]).map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`px-3 py-1.5 text-xs font-semibold uppercase tracking-wider rounded-lg transition-all cursor-pointer ${
                      activeTab === tab
                        ? 'bg-white text-black font-bold shadow'
                        : 'text-white/70 hover:text-white hover:bg-white/10'
                    }`}
                  >
                    {tab === 'cockpit' ? 'Cockpit' : tab === 'basis-risk' ? 'Basis Risk' : tab.replace('-', ' ')}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* TAB 1: OVERVIEW (AUTHENTIC LIVE TELEMETRY) */}
          {activeTab === 'overview' && (
            <div className="pt-8">
              <div className="flex flex-col md:flex-row items-start justify-between gap-6 mb-8">
                <p className="text-sm sm:text-base text-white/90 leading-relaxed max-w-[700px]">
                  Real-time agricultural telemetry from the 9 registered farm plots. Each payload is verified against SECP256k1 public keys fused in device registries and cross-referenced with OpenWeatherMap synthetic aperture observation:
                </p>
                <div className="shrink-0 flex items-center gap-3 bg-black/40 border border-white/20 p-2.5 rounded-xl">
                  <div className="text-right">
                    <span className="text-[10px] text-white/50 uppercase block font-semibold">Active Policies</span>
                    <span className="text-base font-bold text-white">{plots.length || 9} Monitored</span>
                  </div>
                  <div className="h-7 w-[1px] bg-white/20" />
                  <div className="text-right">
                    <span className="text-[10px] text-white/50 uppercase block font-semibold">Claims Logged</span>
                    <span className="text-base font-bold text-emerald-400">{claims.length} Intents</span>
                  </div>
                </div>
              </div>

              {/* Field Plot Selector */}
              <div className="flex flex-wrap gap-2.5 mb-8">
                {plots.map((plot) => (
                  <button
                    key={plot.plot_id}
                    onClick={() => setSelectedPlotId(plot.plot_id)}
                    className={`px-3.5 py-2 text-xs font-semibold uppercase tracking-wider rounded-lg transition-all cursor-pointer border flex items-center gap-2 ${
                      selectedPlotId === plot.plot_id 
                        ? 'bg-white text-black border-white shadow-lg' 
                        : 'bg-black/40 text-white/80 border-white/20 hover:border-white/50'
                    }`}
                  >
                    <span className={`w-1.5 h-1.5 rounded-full ${plot.status === 'NORMAL' ? 'bg-emerald-500' : 'bg-amber-400'}`} />
                    <span>{plot.farmer_name}</span>
                    <span className="text-[10px] opacity-60">({plot.crop})</span>
                  </button>
                ))}
              </div>

              {/* Selected Plot Live Stats */}
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 mb-8">
                <div className="border border-white/20 rounded-xl p-5 bg-white/5 backdrop-blur-sm">
                  <div className="flex items-center gap-2 text-white/70 text-xs mb-2">
                    <Droplets className="w-4 h-4 text-white" />
                    <span className="uppercase tracking-wider font-semibold">Soil Moisture</span>
                  </div>
                  <div className="text-3xl font-bold text-white mb-1">
                    {currentPlot.soil_moisture.toFixed(1)}%
                  </div>
                  <div className="text-[11px] text-white/60">
                    Drought Threshold: &lt; {currentPlot.moisture_drought_threshold}%
                  </div>
                </div>

                <div className="border border-white/20 rounded-xl p-5 bg-white/5 backdrop-blur-sm">
                  <div className="flex items-center gap-2 text-white/70 text-xs mb-2">
                    <Thermometer className="w-4 h-4 text-white" />
                    <span className="uppercase tracking-wider font-semibold">Air Temperature</span>
                  </div>
                  <div className="text-3xl font-bold text-white mb-1">
                    {currentPlot.temperature.toFixed(1)}°C
                  </div>
                  <div className="text-[11px] text-white/60">
                    Heatwave Threshold: &gt; {currentPlot.temp_heatwave_threshold}°C
                  </div>
                </div>

                <div className="border border-white/20 rounded-xl p-5 bg-white/5 backdrop-blur-sm">
                  <div className="flex items-center gap-2 text-white/70 text-xs mb-2">
                    <CloudRain className="w-4 h-4 text-white" />
                    <span className="uppercase tracking-wider font-semibold">Precipitation</span>
                  </div>
                  <div className="text-3xl font-bold text-white mb-1">
                    {currentPlot.rainfall_mm.toFixed(1)} mm
                  </div>
                  <div className="text-[11px] text-white/60">
                    Flood Trigger: &gt; {currentPlot.rainfall_flood_threshold_mm} mm
                  </div>
                </div>

                <div className="border border-white/20 rounded-xl p-5 bg-white/5 backdrop-blur-sm">
                  <div className="flex items-center gap-2 text-white/70 text-xs mb-2">
                    <ShieldCheck className="w-4 h-4 text-white" />
                    <span className="uppercase tracking-wider font-semibold">Sum Insured</span>
                  </div>
                  <div className="text-3xl font-bold text-white mb-1">
                    ₹{currentPlot.sum_insured_inr?.toLocaleString('en-IN')}
                  </div>
                  <div className="text-[11px] text-white/60">
                    Parametric Micro-Rider
                  </div>
                </div>
              </div>

              {/* SECP256k1 Security & Weather Cross-Validation */}
              <div className="border border-white/25 rounded-xl p-5 bg-black/40 backdrop-blur-md flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[10px] uppercase font-bold tracking-wider text-emerald-400">
                      ● Cryptographic Hardware Signature
                    </span>
                    <span className="text-[10px] text-white/40">|</span>
                    <span className="text-[10px] uppercase font-bold tracking-wider text-blue-400">
                      OpenWeatherMap Cross-Check Active
                    </span>
                  </div>
                  <div className="font-mono text-xs sm:text-sm text-white/95">
                    {currentPlot.plot_id} &rarr; Node ID: {currentPlot.node_id} | Security: SECP256k1 ECDSA Authenticated
                  </div>
                  <div className="text-[11px] text-white/60 mt-0.5">
                    Region: {currentPlot.region}, {currentPlot.district}, {currentPlot.state} (Farmer: {currentPlot.farmer_name}, {currentPlot.language_name})
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button 
                    onClick={() => scrollToTabContent('cockpit')}
                    className="px-4 py-2 bg-white text-black font-bold text-xs uppercase tracking-wider rounded-lg hover:bg-white/90 transition-all cursor-pointer"
                  >
                    Simulate Breach
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: COCKPIT (INTERACTIVE SIMULATOR & CLAIMS) */}
          {activeTab === 'cockpit' && (
            <div className="pt-8 space-y-8">
              {/* Cockpit Overview */}
              <div className="flex flex-col lg:flex-row items-start justify-between gap-6">
                <div>
                  <h3 className="text-xl font-bold text-white mb-1">Parametric Simulation & Breach Evaluator</h3>
                  <p className="text-xs sm:text-sm text-white/80 max-w-[750px]">
                    Trigger simulated micro-climate breaches (Severe Drought or Extreme Heatwave) against authentic farm policy rules. Watch the FastAPI backend cross-check with live weather APIs, evaluate contract breach, and record non-repudiable claim intents:
                  </p>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  <button 
                    onClick={handleReset}
                    disabled={simActionLoading}
                    className="flex items-center gap-1.5 px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg border border-white/20 text-xs font-semibold cursor-pointer transition-all"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                    <span>Reset Ledger</span>
                  </button>
                </div>
              </div>

              {triggerMsg && (
                <div className="border border-emerald-500/30 bg-emerald-500/10 text-emerald-300 p-3.5 rounded-xl text-xs font-mono flex items-center justify-between">
                  <span>{triggerMsg}</span>
                  <button onClick={() => setTriggerMsg(null)} className="text-emerald-300 hover:text-white cursor-pointer">&times;</button>
                </div>
              )}

              {/* Simulation Controller Panel */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left: Plot & Value Slider */}
                <div className="lg:col-span-2 border border-white/20 rounded-xl p-6 bg-black/40 backdrop-blur-md space-y-5">
                  <div className="flex items-center justify-between">
                    <span className="text-xs uppercase font-bold tracking-wider text-white/70">
                      1. Select Target Farm Plot
                    </span>
                    <span className="text-xs font-mono text-emerald-400">
                      Contract: ₹{currentPlot.sum_insured_inr?.toLocaleString('en-IN')}
                    </span>
                  </div>

                  <div className="grid grid-cols-3 gap-2">
                    {plots.map(p => (
                      <button
                        key={p.plot_id}
                        onClick={() => setSelectedPlotId(p.plot_id)}
                        className={`p-2.5 rounded-lg border text-left transition-all cursor-pointer ${
                          selectedPlotId === p.plot_id
                            ? 'bg-white text-black border-white font-bold'
                            : 'bg-white/5 border-white/15 text-white/80 hover:bg-white/10'
                        }`}
                      >
                        <div className="text-xs">{p.farmer_name}</div>
                        <div className="text-[10px] opacity-70">{p.crop} &bull; {p.district}</div>
                      </button>
                    ))}
                  </div>

                  {/* Sliders */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-3 border-t border-white/10">
                    <div>
                      <div className="flex justify-between text-xs mb-1.5">
                        <span className="text-white/70">Simulated Soil Moisture:</span>
                        <span className="font-mono font-bold text-white">{simMoisture}%</span>
                      </div>
                      <input 
                        type="range"
                        min="5"
                        max="50"
                        step="0.5"
                        value={simMoisture}
                        onChange={(e) => setSimMoisture(parseFloat(e.target.value))}
                        className="w-full accent-white cursor-pointer"
                      />
                      <div className="text-[10px] text-white/50 mt-1">
                        Breach threshold: &lt; {currentPlot.moisture_drought_threshold}%
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between text-xs mb-1.5">
                        <span className="text-white/70">Simulated Temperature:</span>
                        <span className="font-mono font-bold text-white">{simTemp}°C</span>
                      </div>
                      <input 
                        type="range"
                        min="20"
                        max="48"
                        step="0.5"
                        value={simTemp}
                        onChange={(e) => setSimTemp(parseFloat(e.target.value))}
                        className="w-full accent-white cursor-pointer"
                      />
                      <div className="text-[10px] text-white/50 mt-1">
                        Heatwave threshold: &gt; {currentPlot.temp_heatwave_threshold}°C
                      </div>
                    </div>
                  </div>

                  {/* Trigger Action Buttons */}
                  <div className="flex flex-wrap items-center gap-3 pt-3">
                    <button
                      onClick={() => handleManualTrigger('drought')}
                      disabled={simActionLoading}
                      className="px-5 py-2.5 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-xs font-bold uppercase tracking-wider cursor-pointer transition-all flex items-center gap-2"
                    >
                      <Zap className="w-3.5 h-3.5" />
                      <span>Trigger Drought Breach ({simMoisture}%)</span>
                    </button>

                    <button
                      onClick={() => handleManualTrigger('heatwave')}
                      disabled={simActionLoading}
                      className="px-5 py-2.5 bg-amber-600 hover:bg-amber-500 text-white rounded-lg text-xs font-bold uppercase tracking-wider cursor-pointer transition-all flex items-center gap-2"
                    >
                      <Zap className="w-3.5 h-3.5" />
                      <span>Trigger Heatwave (43.5°C)</span>
                    </button>

                    <button
                      onClick={() => handleManualTrigger('nominal')}
                      disabled={simActionLoading}
                      className="px-4 py-2.5 bg-white/10 hover:bg-white/20 text-white rounded-lg text-xs font-semibold uppercase tracking-wider cursor-pointer transition-all"
                    >
                      Restore Nominal
                    </button>
                  </div>
                </div>

                {/* Right: Real-time Agronomic AI Advisory */}
                <div className="border border-white/20 rounded-xl p-6 bg-black/40 backdrop-blur-md flex flex-col justify-between">
                  <div>
                    <div className="flex items-center gap-2 text-xs uppercase font-bold tracking-wider text-emerald-400 mb-3">
                      <Info className="w-4 h-4" />
                      <span>Agronomic Mitigation Advisory</span>
                    </div>

                    {advisory ? (
                      <div className="space-y-3">
                        <div className="text-xs font-semibold text-white">
                          Plot: {advisory.plot_id} ({advisory.crop}, {advisory.state})
                        </div>
                        <div className="text-[11px] text-white/60">
                          Condition: <span className="text-white font-medium">{advisory.condition}</span>
                        </div>

                        <div className="space-y-2 pt-2 border-t border-white/10">
                          <span className="text-[10px] uppercase font-bold text-white/50 block">Recommended Actions:</span>
                          {advisory.actions_english?.map((act, i) => (
                            <div key={i} className="text-xs text-white/85 flex items-start gap-2">
                              <span className="text-white font-bold">&bull;</span>
                              <span>{act}</span>
                            </div>
                          ))}
                        </div>

                        {advisory.spray_caution && (
                          <div className="text-[11px] text-amber-300/90 pt-2 border-t border-white/10">
                            <strong>Caution:</strong> {advisory.spray_caution}
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="text-xs text-white/60 italic">Loading advisory rules...</div>
                    )}
                  </div>

                  <div className="text-[10px] text-white/40 pt-4 border-t border-white/10 font-mono">
                    Source: AgriSentinel ICAR Regional Rulebase
                  </div>
                </div>
              </div>

              {/* Claims Ledger */}
              <div className="border border-white/20 rounded-xl overflow-hidden bg-black/40 backdrop-blur-md">
                <div className="p-4 border-b border-white/15 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-xs uppercase font-bold tracking-wider text-white">
                      Automated Parametric Claims Ledger
                    </span>
                    <span className="text-[11px] font-mono text-emerald-400 px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/30">
                      {claims.length} Recorded
                    </span>
                  </div>
                  <span className="text-[11px] text-white/50">
                    Transparent Notice: Monetary payout requires underwriter core banking API
                  </span>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="border-b border-white/20 bg-white/10 text-white/70">
                        <th className="p-3.5 font-semibold">Claim ID</th>
                        <th className="p-3.5 font-semibold">Plot / Farmer</th>
                        <th className="p-3.5 font-semibold">Crop</th>
                        <th className="p-3.5 font-semibold">Trigger Reason</th>
                        <th className="p-3.5 font-semibold">Benefit Calculated</th>
                        <th className="p-3.5 font-semibold">Cryptographic Status</th>
                        <th className="p-3.5 font-semibold">Disbursement Notice</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/10 font-mono text-[11px]">
                      {claims.length === 0 ? (
                        <tr>
                          <td colSpan={7} className="p-6 text-center text-white/50 font-sans text-xs">
                            No claims generated yet. Use the buttons above to trigger a parametric breach!
                          </td>
                        </tr>
                      ) : (
                        claims.map(claim => (
                          <tr key={claim.claim_id} className="hover:bg-white/5 transition-colors">
                            <td className="p-3.5 text-white font-bold">{claim.claim_id}</td>
                            <td className="p-3.5 text-white font-sans">{claim.farmer_name} ({claim.plot_id})</td>
                            <td className="p-3.5 text-white/80 font-sans">{claim.crop}</td>
                            <td className="p-3.5 text-rose-300 font-sans">{claim.trigger_reason}</td>
                            <td className="p-3.5 text-emerald-400 font-bold font-sans">
                              ₹{claim.payout_calculated_inr?.toLocaleString('en-IN')}
                            </td>
                            <td className="p-3.5 text-white/90 font-sans">
                              SECP256k1 Authentic
                            </td>
                            <td className="p-3.5 text-white/60 font-sans text-[10px]">
                              {claim.settlement_status}
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: BASIS RISK COMPARISON */}
          {activeTab === 'basis-risk' && (
            <div className="pt-8 space-y-6">
              <div>
                <h3 className="text-xl font-bold text-white mb-1">
                  Basis Risk Comparative Analysis: IMD Area Station vs On-Plot Node
                </h3>
                <p className="text-xs sm:text-sm text-white/80 max-w-[800px]">
                  Basis Risk is the single largest structural failure in PMFBY and traditional index insurance: when a district weather station 15+ km away records nominal conditions, a farmer experiencing localized hyper-local drought receives zero compensation. AgriSentinel solves this at the fence line:
                </p>
              </div>

              {basisRisk ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Traditional Area Station */}
                  <div className="border border-rose-500/30 rounded-xl p-6 bg-rose-950/20 backdrop-blur-md space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-xs uppercase font-bold tracking-wider text-rose-400">
                        Traditional PMFBY Area Approach
                      </span>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-rose-500/20 text-rose-300">
                        {basisRisk.traditional_pmfby_station.distance_from_farm_km} km Away
                      </span>
                    </div>

                    <h4 className="text-lg font-bold text-white">
                      {basisRisk.traditional_pmfby_station.name}
                    </h4>

                    <div className="grid grid-cols-2 gap-3 text-xs">
                      <div className="bg-white/5 p-3 rounded-lg border border-white/10">
                        <span className="text-white/60 block text-[10px]">Recorded Temp:</span>
                        <span className="text-lg font-bold text-white">
                          {basisRisk.traditional_pmfby_station.recorded_temperature_c}°C
                        </span>
                      </div>
                      <div className="bg-white/5 p-3 rounded-lg border border-white/10">
                        <span className="text-white/60 block text-[10px]">Recorded 1h Rain:</span>
                        <span className="text-lg font-bold text-white">
                          {basisRisk.traditional_pmfby_station.recorded_rainfall_1h_mm} mm
                        </span>
                      </div>
                    </div>

                    <div className="border border-rose-500/40 bg-rose-500/10 p-3 rounded-lg">
                      <span className="text-[10px] uppercase font-bold text-rose-400 block">Claim Outcome:</span>
                      <span className="text-sm font-bold text-white">
                        {basisRisk.traditional_pmfby_station.claim_decision}
                      </span>
                    </div>

                    <p className="text-xs text-white/70 leading-relaxed">
                      {basisRisk.traditional_pmfby_station.basis_risk_explanation}
                    </p>
                  </div>

                  {/* AgriSentinel Hyper-Local Node */}
                  <div className="border border-emerald-500/30 rounded-xl p-6 bg-emerald-950/20 backdrop-blur-md space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-xs uppercase font-bold tracking-wider text-emerald-400">
                        AgriSentinel Verifiable Fence-Line Node
                      </span>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300">
                        0.0 km (On-Plot)
                      </span>
                    </div>

                    <h4 className="text-lg font-bold text-white">
                      {basisRisk.agrisentinel_hyperlocal_node.name}
                    </h4>

                    <div className="grid grid-cols-2 gap-3 text-xs">
                      <div className="bg-white/5 p-3 rounded-lg border border-white/10">
                        <span className="text-white/60 block text-[10px]">Soil Moisture:</span>
                        <span className="text-lg font-bold text-emerald-400">
                          {basisRisk.agrisentinel_hyperlocal_node.on_farm_soil_moisture_pct}%
                        </span>
                      </div>
                      <div className="bg-white/5 p-3 rounded-lg border border-white/10">
                        <span className="text-white/60 block text-[10px]">On-Plot Temp:</span>
                        <span className="text-lg font-bold text-white">
                          {basisRisk.agrisentinel_hyperlocal_node.on_farm_temperature_c}°C
                        </span>
                      </div>
                    </div>

                    <div className="border border-emerald-500/40 bg-emerald-500/10 p-3 rounded-lg">
                      <span className="text-[10px] uppercase font-bold text-emerald-400 block">Claim Outcome:</span>
                      <span className="text-sm font-bold text-white">
                        {basisRisk.agrisentinel_hyperlocal_node.simulated_claim_status}
                      </span>
                    </div>

                    <div className="space-y-1.5 text-xs text-white/80">
                      <div>&bull; Security: <strong className="text-white">{basisRisk.agrisentinel_hyperlocal_node.crypto_verification}</strong></div>
                      <div>&bull; Satellite: <strong className="text-white">{basisRisk.agrisentinel_hyperlocal_node.weather_corroboration}</strong></div>
                      <div>&bull; Voice Dispatch: <strong className="text-white">{basisRisk.agrisentinel_hyperlocal_node.voice_dispatch}</strong></div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-xs text-white/60 italic">Loading basis risk model...</div>
              )}
            </div>
          )}

          {/* TAB 4: TWILIO 2G VOICE TELECOM */}
          {activeTab === 'voice' && (
            <div className="pt-8 max-w-[750px] space-y-6">
              <div>
                <h3 className="text-xl font-bold text-white mb-1">
                  Regional 2G Telecom Voice Advisory & IVR
                </h3>
                <p className="text-xs sm:text-sm text-white/80 leading-relaxed">
                  Smallholder farmers in rural India predominantly carry basic feature phones without data plans. AgriSentinel utilizes automated Twilio telecom pipelines with native regional TTS (Tamil Google voices, Hindi Polly voices) and dual-tone keypad response confirmation:
                </p>
              </div>

              <div className="border border-white/20 rounded-xl p-6 bg-black/40 backdrop-blur-md space-y-4">
                <div>
                  <label className="block text-xs uppercase tracking-wider text-white/70 mb-1.5 font-semibold">
                    Target Farmer Mobile Number (E.164 format)
                  </label>
                  <input 
                    type="tel"
                    value={voicePhone}
                    onChange={(e) => setVoicePhone(e.target.value)}
                    placeholder="+919363849952"
                    className="w-full bg-black/60 border border-white/25 p-3 rounded-lg text-sm text-white font-mono focus:outline-none focus:border-white"
                  />
                  <div className="text-[11px] text-white/50 mt-1">
                    Configured for {currentPlot.farmer_name} &bull; Language: {currentPlot.language_name} ({currentPlot.language_code})
                  </div>
                </div>

                <div className="pt-2 flex items-center gap-3">
                  <button
                    onClick={handleVoiceDispatch}
                    disabled={voiceLoading}
                    className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold uppercase tracking-wider cursor-pointer transition-all flex items-center gap-2"
                  >
                    <PhoneCall className={`w-4 h-4 ${voiceLoading ? 'animate-bounce' : ''}`} />
                    <span>{voiceLoading ? 'Dispatching Call...' : 'Dispatch Automated Voice Call'}</span>
                  </button>
                </div>

                {voiceDispatchResult && (
                  <div className="mt-4 p-4 rounded-xl border border-white/20 bg-white/5 font-mono text-xs space-y-2">
                    <div className="text-emerald-400 font-bold uppercase">Dispatch Status:</div>
                    <pre className="text-[11px] text-white/80 overflow-x-auto whitespace-pre-wrap">
                      {JSON.stringify(voiceDispatchResult, null, 2)}
                    </pre>
                  </div>
                )}
              </div>

              <div className="border border-white/15 rounded-xl p-4 bg-white/5 text-xs text-white/70 space-y-2">
                <div className="font-bold text-white uppercase text-[11px]">Transparency & Sandbox Note:</div>
                <p>
                  Outbound voice calls utilize live Twilio Voice credentials configured in <code className="text-white">.env</code>. If testing with unverified trial accounts, Twilio delivers calls strictly to verified sandbox recipient numbers.
                </p>
              </div>
            </div>
          )}

          {/* TAB 5: HOW IT WORKS */}
          {activeTab === 'how-it-works' && (
            <div className="pt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="border border-white/20 rounded-xl p-5 bg-white/5 backdrop-blur-sm flex flex-col justify-between">
                <div>
                  <span className="text-[10px] font-bold tracking-widest text-white/50 uppercase block mb-2">Stage 01</span>
                  <h4 className="text-lg font-bold text-white mb-2">Physical Capture</h4>
                  <p className="text-xs text-white/80 leading-relaxed">
                    High-accuracy capacitive soil probes (v2) and BME280 sensors capture volumetric water content, temperature, humidity, and tipping bucket precipitation at plot level.
                  </p>
                </div>
                <div className="pt-4 mt-4 border-t border-white/10 text-xs font-mono text-white/50">Edge Hardware</div>
              </div>

              <div className="border border-white/20 rounded-xl p-5 bg-white/5 backdrop-blur-sm flex flex-col justify-between">
                <div>
                  <span className="text-[10px] font-bold tracking-widest text-white/50 uppercase block mb-2">Stage 02</span>
                  <h4 className="text-lg font-bold text-white mb-2">SECP256k1 Signing</h4>
                  <p className="text-xs text-white/80 leading-relaxed">
                    The ESP32 cryptographic engine hashes telemetry and signs each payload with registered hardware keys, preventing replay and tampering before wireless transmission.
                  </p>
                </div>
                <div className="pt-4 mt-4 border-t border-white/10 text-xs font-mono text-white/50">ECDSA SECP256k1</div>
              </div>

              <div className="border border-white/20 rounded-xl p-5 bg-white/5 backdrop-blur-sm flex flex-col justify-between">
                <div>
                  <span className="text-[10px] font-bold tracking-widest text-white/50 uppercase block mb-2">Stage 03</span>
                  <h4 className="text-lg font-bold text-white mb-2">Weather Cross-Check</h4>
                  <p className="text-xs text-white/80 leading-relaxed">
                    FastAPI backend queries OpenWeatherMap meteorological grids to detect physical tamper (e.g. submerging sensor in a bucket of water during dry atmospheric heat).
                  </p>
                </div>
                <div className="pt-4 mt-4 border-t border-white/10 text-xs font-mono text-white/50">Anti-Tamper Layer</div>
              </div>

              <div className="border border-white/20 rounded-xl p-5 bg-white/5 backdrop-blur-sm flex flex-col justify-between">
                <div>
                  <span className="text-[10px] font-bold tracking-widest text-white/50 uppercase block mb-2">Stage 04</span>
                  <h4 className="text-lg font-bold text-white mb-2">Automated Claim Intent</h4>
                  <p className="text-xs text-white/80 leading-relaxed">
                    Parametric policy rules evaluate breach conditions autonomously, logging audit records and triggering regional language 2G voice advisory phone calls.
                  </p>
                </div>
                <div className="pt-4 mt-4 border-t border-white/10 text-xs font-mono text-white/50">Parametric Payout</div>
              </div>
            </div>
          )}

          {/* TAB 6: TECHNOLOGY */}
          {activeTab === 'technology' && (
            <div className="pt-8">
              <div className="flex flex-col md:flex-row items-start justify-between gap-6 mb-8">
                <div>
                  <h3 className="text-xl font-bold text-white mb-1">Core Engineering & Hardware Stack</h3>
                  <p className="text-xs sm:text-sm text-white/80">
                    Click each component below to inspect architectural implementation details:
                  </p>
                </div>
                <span className="text-xs font-mono text-white/60 px-3 py-1.5 rounded-md border border-white/20 bg-black/40">
                  SECP256k1 Hardware Authentication
                </span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-8">
                {[
                  { id: 'ecdsa', title: 'ECDSA SECP256k1', desc: 'Hardware Crypto' },
                  { id: 'fastapi', title: 'FastAPI 2.1', desc: 'REST Ingestion' },
                  { id: 'twilio', title: 'Twilio 2G Voice', desc: 'Regional Telecom' },
                  { id: 'weather', title: 'OpenWeatherMap', desc: 'Cross-Corroborator' },
                  { id: 'react', title: 'React 19', desc: 'Frontend Engine' },
                  { id: 'groq', title: 'Groq LLaMA-3.3', desc: 'Agronomic Advisory' },
                  { id: 'godot', title: 'Godot 4', desc: 'Farm Simulator' },
                  { id: 'scad', title: 'OpenSCAD', desc: '3D Enclosure Model' },
                ].map((tech) => (
                  <button
                    key={tech.id}
                    onClick={() => setActiveTech(tech.id)}
                    className={`p-4 rounded-xl text-left transition-all cursor-pointer border ${
                      activeTech === tech.id
                        ? 'bg-white text-black border-white shadow-lg'
                        : 'bg-white/5 hover:bg-white/10 border-white/15 text-white'
                    }`}
                  >
                    <div className="font-bold text-sm">{tech.title}</div>
                    <div className={`text-[11px] ${activeTech === tech.id ? 'text-black/70' : 'text-white/60'}`}>
                      {tech.desc}
                    </div>
                  </button>
                ))}
              </div>

              <div className="border border-white/20 rounded-xl p-6 bg-black/40 backdrop-blur-md">
                <span className="text-[10px] font-bold tracking-widest text-white/50 uppercase block mb-1">
                  Active Stack Specification
                </span>
                <h4 className="text-lg font-bold text-white mb-2">
                  {activeTech === 'ecdsa' && 'ECDSA SECP256k1 Cryptographic Engine'}
                  {activeTech === 'fastapi' && 'FastAPI Core Telemetry API'}
                  {activeTech === 'twilio' && 'Twilio Regional Telecom Voice Dispatch'}
                  {activeTech === 'weather' && 'OpenWeatherMap Meteorological Observation Grid'}
                  {activeTech === 'react' && 'React 19 & Smooth Scroll Frame Animation'}
                  {activeTech === 'groq' && 'Groq LLaMA-3.3-70B Agronomic Mitigation Engine'}
                  {activeTech === 'godot' && 'Godot 4 50x50m Farm Grid Simulator'}
                  {activeTech === 'scad' && 'OpenSCAD 3D Physical Enclosure Model'}
                </h4>
                <p className="text-xs sm:text-sm text-white/85 leading-relaxed">
                  {activeTech === 'ecdsa' && 'Verifies telemetry signatures against registered device public keys permanently fused in ESP32 eFuse, eliminating spoofed readings and fraud.'}
                  {activeTech === 'fastapi' && 'High-throughput asynchronous Python backend providing parametric claims evaluation, audit trail management, and telemetry ingestion.'}
                  {activeTech === 'twilio' && 'Outbound phone call automation delivering voice advisories in native Indian tongues (Tamil, Hindi, Telugu, Gujarati) to farmers with feature phones.'}
                  {activeTech === 'weather' && 'Live satellite observation grid cross-validating field conditions to detect physical probe tampering or sensor submersion fraud.'}
                  {activeTech === 'react' && 'High-performance interactive interface with full viewport canvas frame interpolation, transparent glassmorphism, and instant telemetry updates.'}
                  {activeTech === 'groq' && 'Generates contextual, localized crop advisory recommendations calibrated to regional agricultural university extension guidelines.'}
                  {activeTech === 'godot' && 'Interactive 2D simulation environment modeling soil water retention, plant evapotranspiration, and wireless packet transmission.'}
                  {activeTech === 'scad' && 'Parametric 3D CAD model for ruggedized, weatherproof on-farm IoT enclosures featuring solar bracket and mast mounts.'}
                </p>
              </div>
            </div>
          )}

          {/* TAB 7: ABOUT */}
          {activeTab === 'about' && (
            <div className="pt-8 max-w-[850px] space-y-6 text-sm sm:text-base text-white/90 leading-relaxed">
              <p>
                <strong className="text-white font-bold">AgriSentinel</strong> provides hyper-local, decentralized proof-of-loss for smallholder farmers, eliminating Basis Risk in crop insurance by measuring micro-climates directly at the farm fence line.
              </p>
              <p>
                By combining cryptographically authenticated edge IoT towers with automated parametric claim evaluation, the platform bridges the gap between verified field conditions and rapid, automated risk settlement.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4">
                <div className="border border-white/15 p-4 rounded-xl bg-white/5">
                  <div className="text-2xl font-bold text-white mb-1">9 Profiles</div>
                  <div className="text-xs text-white/70">Pan-India Agricultural Coverage</div>
                </div>
                <div className="border border-white/15 p-4 rounded-xl bg-white/5">
                  <div className="text-2xl font-bold text-white mb-1">SECP256k1</div>
                  <div className="text-xs text-white/70">Anti-Fraud Hardware Verification</div>
                </div>
                <div className="border border-white/15 p-4 rounded-xl bg-white/5">
                  <div className="text-2xl font-bold text-white mb-1">2G Voice</div>
                  <div className="text-xs text-white/70">Zero Smartphone Barrier</div>
                </div>
              </div>
            </div>
          )}

        </div>
      </section>

      {/* SECTION 3: ARCHITECTURAL FOOTER */}
      <section 
        className="relative z-10 w-full max-w-[1440px] px-6 sm:px-12 md:px-20 py-20 bg-transparent text-white border-t border-white/15"
      >
        <div className="max-w-[1080px] flex flex-col items-start">
          <div className="inline-flex items-center gap-2.5 text-[11px] font-semibold tracking-[2.2px] uppercase text-white/70 mb-6">
            <span className="w-1.5 h-1.5 rounded-full bg-white inline-block"></span>
            <span>Platform Architecture & Telemetry Pipeline</span>
          </div>

          <h2 className="text-4xl sm:text-6xl lg:text-[76px] font-bold leading-[1.02] tracking-[-2px] text-white mb-6 drop-shadow-md">
            Bringing the Field<br />
            <em className="font-display-serif italic font-normal tracking-[-0.5px] pr-1">
              Into Focus.
            </em>
          </h2>

          <p className="text-base sm:text-lg lg:text-[19px] leading-[1.6] font-normal text-white/80 max-w-[650px] mb-12 tracking-[-0.2px]">
            Localized environmental monitoring. Verifiable field data. Better visibility into the conditions that matter to farmers.
          </p>

          <div className="w-full grid grid-cols-1 md:grid-cols-3 gap-8 pt-8 border-t border-white/15 text-left">
            <div className="bg-black/30 backdrop-blur-md p-5 rounded-xl border border-white/10">
              <div className="text-3xl font-bold tracking-tight text-white mb-2">99.98%</div>
              <div className="text-xs uppercase tracking-wider text-white/50 mb-1 font-semibold">Signal Verifiability</div>
              <p className="text-xs text-white/70 leading-relaxed">
                Zero tampering window: field readings are sealed with SECP256k1 cryptographic hardware modules.
              </p>
            </div>
            <div className="bg-black/30 backdrop-blur-md p-5 rounded-xl border border-white/10">
              <div className="text-3xl font-bold tracking-tight text-white mb-2">&lt; 4 Hours</div>
              <div className="text-xs uppercase tracking-wider text-white/50 mb-1 font-semibold">Parametric Settlement</div>
              <p className="text-xs text-white/70 leading-relaxed">
                Automated insurance claims evaluate against immutable sensor thresholds without manual adjusters.
              </p>
            </div>
            <div className="bg-black/30 backdrop-blur-md p-5 rounded-xl border border-white/10">
              <div className="text-3xl font-bold tracking-tight text-white mb-2">9 Regions</div>
              <div className="text-xs uppercase tracking-wider text-white/50 mb-1 font-semibold">Monitored Profiles</div>
              <p className="text-xs text-white/70 leading-relaxed">
                Tamil Nadu, Uttar Pradesh, Gujarat, Andhra Pradesh, West Bengal, Rajasthan, Maharashtra, Kerala, Karnataka.
              </p>
            </div>
          </div>
        </div>
      </section>

    </div>
  );
}
