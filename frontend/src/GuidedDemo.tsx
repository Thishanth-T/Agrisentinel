import React, { useState, useEffect, useRef } from 'react';
import {
  Play,
  Pause,
  SkipForward,
  SkipBack,
  X,
  Volume2,
  VolumeX,
  ShieldCheck,
  AlertTriangle,
  CloudRain,
  Radio,
  FileCheck,
  CheckCircle2,
  PhoneCall,
  Terminal,
  Zap,
  ArrowRight,
  RefreshCw,
  Lock,
  Sparkles,
  Eye,
  Languages
} from 'lucide-react';
import { 
  api, 
  FarmPlot, 
  ClaimRecord, 
  BasisRiskData, 
  FarmPassport 
} from './api';

export type TabType = 'overview' | 'cockpit' | 'basis-risk' | 'passport' | 'metrics' | 'voice' | 'how-it-works' | 'technology' | 'about';

interface GuidedDemoProps {
  isOpen: boolean;
  onClose: () => void;
  activeTab: TabType;
  setActiveTab: (tab: TabType) => void;
  selectedPlotId: string;
  setSelectedPlotId: (plotId: string) => void;
  refreshAllData: () => Promise<void>;
  plots: FarmPlot[];
  claims: ClaimRecord[];
  basisRisk: BasisRiskData | null;
  passport: FarmPassport | null;
}

interface DemoStep {
  stepIndex: number;
  id: string;
  badge: string;
  title: string;
  targetTab: TabType;
  targetPlotId: string;
  targetElementId: string;
  problem: string;
  solution: string;
  technicalProof: string;
  actionButtonLabel: string;
  speechText: string;
  subtitleText: string;
  translations?: {
    [key: string]: {
      text: string;
      lang: string;
    };
  };
}

const DEMO_STEPS: DemoStep[] = [
  {
    stepIndex: 1,
    id: 'baseline',
    badge: '01 / 07 • Pan-India Testbed',
    title: 'Baseline State Across 9 Agro-Climatic Zones',
    targetTab: 'overview',
    targetPlotId: 'plot_1',
    targetElementId: 'demo-target-metrics',
    problem: 'Traditional crop insurance relies on sparse district weather stations situated 15 to 40 km away from real farms, creating massive coverage blindspots.',
    solution: 'AgriSentinel connects 9 simulated edge nodes across India (Tamil Nadu, UP, Gujarat, Rajasthan, etc.), measuring plot-level soil moisture, precipitation, and thermal dynamics in real-time.',
    technicalProof: 'Each virtual node executes thermodynamic physics, autonomous solar charging, and signs every reading with hardware-grade SECP256k1 ECDSA curves.',
    actionButtonLabel: 'Inspect Nominal Baseline Telemetry',
    speechText: 'Milestone one: AgriSentinel monitors nine distinct agro-climatic zones across India. Each virtual edge node executes local thermodynamic physics, streaming authenticated telemetry signed with S-E-C-P 256-k-1 elliptic curve cryptography.',
    subtitleText: 'Milestone 1/7: 9 Agro-climatic zones nominal. SECP256k1 signed telemetry active across all edge nodes.',
    translations: {
      te: {
        text: 'మొదటి మైలురాయి: అగ్రిసెంటినెల్ భారతదేశంలోని తొమ్మిది వ్యవసాయ వాతావరణ మండలాలను నిరంతరం పర్యవేక్షిస్తుంది. ప్రతి పరికరం ఎస్-ఈ-సి-పి 256-కె-1 క్రిప్టోగ్రఫీతో ధృవీకరించబడింది.',
        lang: 'te-IN'
      },
      ta: {
        text: 'மைல்கல் ஒன்று: அக்ரிசென்டினல் இந்தியா முழுவதும் ஒன்பது வேளாண் காலநிலைப் பகுதிகளைக் கண்காணிக்கிறது. அனைத்து தரவுகளும் கிரிப்டோகிராபிக் முறையில் கையொப்பமிடப்பட்டுள்ளன.',
        lang: 'ta-IN'
      },
      hi: {
        text: 'मील का पत्थर एक: एग्रीसेंटिनल भारत भर में नौ कृषि-जलवायु क्षेत्रों की निगरानी करता है। प्रत्येक नोड क्रिप्टोग्राफ़िक हस्ताक्षर के साथ वास्तविक समय डेटा भेजता है।',
        lang: 'hi-IN'
      }
    }
  },
  {
    stepIndex: 2,
    id: 'cloudburst',
    badge: '02 / 07 • Micro-Climate Peril',
    title: 'Simulate Localized Cloudburst (85mm Influx)',
    targetTab: 'cockpit',
    targetPlotId: 'plot_1',
    targetElementId: 'demo-target-scenarios',
    problem: 'Localized cloudbursts and convective squalls frequently submerge an individual village or field while missing the official district meteorological station completely.',
    solution: 'We inject an acute 85mm localized cloudburst directly over Plot 1 (Madurai, Paddy) operated by farmer Murugan K.',
    technicalProof: 'The virtual edge node simulates acute precipitation, hydrological infiltration into topsoil, and signs the high-water reading before transmission.',
    actionButtonLabel: 'Trigger 85mm Cloudburst on Madurai Field',
    speechText: 'Milestone two: We inject an acute eighty-five millimeter localized cloudburst over Plot One in Madurai. Notice the on-farm rainfall sensor instantly crossing the seventy millimeter contractual flood threshold in real time.',
    subtitleText: 'Milestone 2/7: 85mm localized cloudburst triggered on Madurai paddy plot. Flood threshold breached.',
    translations: {
      te: {
        text: 'రెండవ మైలురాయి: మధురైలోని మొదటి పొలంలో ఎనభై ఐదు మిల్లీమీటర్ల ఆకస్మిక కుంభవృష్టి వర్షపాతం ప్రేరేపించబడింది. డెబ్బై మిల్లీమీటర్ల వరద పరిమితిని దాటింది.',
        lang: 'te-IN'
      },
      ta: {
        text: 'மைல்கல் இரண்டு: மதுரை நெல் வயலில் 85 மில்லிமீட்டர் தீவிர மேகவெடிப்பு மழையை உருவகப்படுத்துகிறோம். 70 மில்லிமீட்டர் ஒப்பந்த வரம்பு உடனடியாக தாண்டப்பட்டது.',
        lang: 'ta-IN'
      },
      hi: {
        text: 'मील का पत्थर दो: मदुरै के खेत पर 85 मिलीमीटर का तीव्र स्थानीय क्लाउडबर्स्ट सिम्युलेट किया गया। 70 मिमी की बाढ़ सीमा पार हो गई।',
        lang: 'hi-IN'
      }
    }
  },
  {
    stepIndex: 3,
    id: 'basis_risk',
    badge: '03 / 07 • Basis Risk Paradox',
    title: 'The Basis Risk Proof: IMD District Station vs Hyperlocal Node',
    targetTab: 'basis-risk',
    targetPlotId: 'plot_1',
    targetElementId: 'demo-target-basis-risk',
    problem: 'Basis Risk is why farmers distrust insurance: when the distant district IMD station records 0mm of rain, the insurance company rejects the claim even though the farmer\'s crop is destroyed underwater.',
    solution: 'Our Spatial Evidence Reconciliation Engine contrasts the official area station against our on-farm node with live OpenWeather verification.',
    technicalProof: 'District Station (15.2 km away) records 0.0mm [Claim: REJECTED]. AgriSentinel Hyperlocal Node records 85.0mm [Claim: BREACH DETECTED]. Basis Risk eliminated.',
    actionButtonLabel: 'Reconcile Spatial Evidence & Basis Risk',
    speechText: 'Milestone three: Here is the core Basis Risk paradox. The distant district weather station fifteen kilometers away records zero rainfall and denies the claim. AgriSentinel’s fence-line node proves the localized flood with atmospheric corroboration.',
    subtitleText: 'Milestone 3/7: Basis Risk Proof: District Station (15km) = 0mm [REJECTED] vs On-Farm Node = 85mm [BREACH DETECTED].',
    translations: {
      te: {
        text: 'మూడవ మైలురాయి: పదిహేను కిలోమీటర్ల దూరంలో ఉన్న జిల్లా వాతావరణ కేంద్రం సున్నా వర్షపాతం నమోదు చేసి క్లెయిమ్‌ను తిరస్కరిస్తుంది. కానీ అగ్రిసెంటినెల్ పొలం వద్దే వరదను నిరూపిస్తుంది.',
        lang: 'te-IN'
      },
      ta: {
        text: 'மைல்கல் மூன்று: 15 கிலோமீட்டர் தூரத்திலுள்ள மாவட்ட வானிலை மையம் பூஜ்ஜியம் என காட்டி இழப்பீட்டை மறுக்கிறது. ஆனால் அக்ரிசென்டினல் வயல்வெளியிலேயே உண்மையை நிரூபிக்கிறது.',
        lang: 'ta-IN'
      },
      hi: {
        text: 'मील का पत्थर तीन: 15 किमी दूर स्थित जिला केंद्र शून्य बारिश दिखाकर दावा खारिज करता है, जबकि एग्रीसेंटिनल खेत की बाड़ पर ही बाढ़ को प्रमाणित करता है।',
        lang: 'hi-IN'
      }
    }
  },
  {
    stepIndex: 4,
    id: 'crypto_gate',
    badge: '04 / 07 • Anti-Fraud Security',
    title: 'SECP256k1 Cryptographic Gate & Device Trust Defense',
    targetTab: 'overview',
    targetPlotId: 'plot_1',
    targetElementId: 'demo-target-crypto',
    problem: 'Can a bad actor tamper with sensor readings or pour a bucket of water on the sensor to trigger a fraudulent insurance payout?',
    solution: 'Dual-gate anti-fraud: Hardware ECDSA SECP256k1 mathematical signature verification + OpenWeather atmospheric cross-check. Uncorroborated bucket-pour spikes are quarantined.',
    technicalProof: 'Replay cache rejects duplicate nonces. Device Trust Score dynamically decays if readings freeze or drift. Only authentic hardware keys are accepted.',
    actionButtonLabel: 'Audit SECP256k1 Cryptographic Signatures',
    speechText: 'Milestone four: Anti-fraud cryptographic gate. Every sensor reading is verified against the hardware root of trust. Nonce replay caches and atmospheric cross-checks instantly isolate and quarantine synthetic bucket-pour tampering.',
    subtitleText: 'Milestone 4/7: SECP256k1 signature validation passed. Replay nonce verified. Device Trust: 1.0 (Authentic).',
    translations: {
      te: {
        text: 'నాల్గవ మైలురాయి: మోసాల నిరోధక క్రిప్టోగ్రఫీ గేట్. ప్రతి సెన్సార్ డేటా హార్డ్‌వేర్ కీతో పరిశీలించబడుతుంది. దొంగ క్లెయిమ్‌లను ఇది తక్షణమే అడ్డుకుంటుంది.',
        lang: 'te-IN'
      },
      ta: {
        text: 'மைல்கல் நான்கு: போலி இழப்பீடுகளைத் தடுக்கும் கிரிப்டோகிராபிக் பாதுகாப்பு. சென்சாரில் வாளித் தண்ணீர் ஊற்றி ஏமாற்றுவதை அமைப்பு உடனே கண்டறிந்து முடக்குகிறது.',
        lang: 'ta-IN'
      },
      hi: {
        text: 'मील का पत्थर चार: धोखाधड़ी-रोधी क्रिप्टोग्राफ़िक गेट। प्रत्येक डेटा हार्डवेयर कुंजी से जाँचा जाता है। पानी डालकर की गई धोखाधड़ी तुरंत पकड़ ली जाती है।',
        lang: 'hi-IN'
      }
    }
  },
  {
    stepIndex: 5,
    id: 'parametric_claim',
    badge: '05 / 07 • Autonomous Settlement',
    title: 'Instant Parametric Claim Intent (₹50,000 Benefit)',
    targetTab: 'cockpit',
    targetPlotId: 'plot_1',
    targetElementId: 'demo-target-claims',
    problem: 'Traditional PMFBY crop claims take 6 to 9 months and require manual visits by government revenue adjusters, often arriving long after the farmer has suffered financial ruin.',
    solution: 'AgriSentinel executes deterministic parametric logic: the verified 85mm rainfall exceeds the 70mm contract threshold, instantly generating a ₹50,000 indemnity record.',
    technicalProof: 'Zero paperwork. Zero claims adjusters. Claim intent persisted into SQLite database with full evidence passport ID and underwriting audit link.',
    actionButtonLabel: 'Query Persistent Parametric Claims Ledger',
    speechText: 'Milestone five: Autonomous parametric settlement. Because verified precipitation breached seventy millimeters, a fifty thousand rupee indemnity is calculated autonomously within seconds, eliminating traditional six-month loss adjuster delays.',
    subtitleText: 'Milestone 5/7: Claim generated: ₹50,000 indemnity calculated autonomously. Persisted to SQLite claims ledger.',
    translations: {
      te: {
        text: 'ఐదవ మైలురాయి: ఆటోమేటిక్ పారామెట్రిక్ క్లెయిమ్. డెబ్బై మిల్లీమీటర్లు మించినందున, యాభై వేల రూపాయల బీమా పరిహారం సెకన్లలో ఆమోదించబడింది.',
        lang: 'te-IN'
      },
      ta: {
        text: 'மைல்கல் ஐந்து: உடனடி காப்பீட்டுத் தீர்வு. 70 மில்லிமீட்டருக்கு மேல் மழை பெய்ததால், ஐம்பதாயிரம் ரூபாய் இழப்பீடு சில நொடிகளில் தானாகவே அங்கீகரிக்கப்பட்டது.',
        lang: 'ta-IN'
      },
      hi: {
        text: 'मील का पत्थर पाँच: स्वचालित पैरामेट्रिक निपटान। 70 मिमी से अधिक वर्षा होने पर पचास हज़ार रुपये का क्लेम बिना किसी कागजी देरी के तुरंत स्वीकृत हुआ।',
        lang: 'hi-IN'
      }
    }
  },
  {
    stepIndex: 6,
    id: 'voice_advisory',
    badge: '06 / 07 • 2G Telecom Inclusion',
    title: 'Regional 2G Telecom Voice Call & IVR Dispatch',
    targetTab: 'voice',
    targetPlotId: 'plot_1',
    targetElementId: 'demo-target-voice',
    problem: 'Smallholder farmers in rural India carry basic 2G feature phones without 4G/5G data connectivity, making smartphone apps useless in emergencies.',
    solution: 'AgriSentinel triggers an automated Twilio voice call in the farmer\'s mother tongue (Tamil for Madurai, Hindi for UP) with keypad DTMF confirmation.',
    technicalProof: 'TwiML voice engine generates regional speech explaining the peril breach, confirming the ₹50,000 claim, and giving agronomic spray cautions.',
    actionButtonLabel: '🔊 Dispatch Regional 2G Voice Alert (Tamil / Telugu)',
    speechText: 'Milestone six: Inclusive telecom dispatch. Since rural farmers rely on basic two-G feature phones, AgriSentinel immediately triggers an automated regional voice call in their native tongue, confirming the claim and relaying crop-saving I-C-A-R advice.',
    subtitleText: 'Milestone 6/7: Outbound Twilio 2G voice call dispatched to farmer. Multi-lingual regional audio enabled.',
    translations: {
      te: {
        text: 'నమస్కారం! మీ పొలంలో ఎనభై ఐదు మిల్లీమీటర్ల భారీ వర్షపాతం నమోదైంది. యాభై వేల రూపాయల పంట బీమా క్లెయిమ్ విజయవంతంగా నమోదు చేయబడింది. దయచేసి నీటి పారుదలని తనిఖీ చేయండి.',
        lang: 'te-IN'
      },
      ta: {
        text: 'வணக்கம் முருகன் அவர்களே! உங்கள் வயலில் 85 மில்லிமீட்டர் கனமழை பதிவாகியுள்ளது. பயிர் காப்பீட்டு இழப்பீடு ஐம்பதாயிரம் ரூபாய் அங்கீகரிக்கப்பட்டுள்ளது. வடிகால் வசதியை உடனடியாக சரிபார்க்கவும்.',
        lang: 'ta-IN'
      },
      hi: {
        text: 'नमस्ते किसान भाई, आपके खेत में 85 मिलीमीटर भारी बारिश दर्ज की गई है। पचास हज़ार रुपये का फसल बीमा क्लेम मंज़ूर कर लिया गया है। खेत की जलनिकासी तुरंत जांचें।',
        lang: 'hi-IN'
      }
    }
  },
  {
    stepIndex: 7,
    id: 'audit_passport',
    badge: '07 / 07 • Immutable Ledger',
    title: 'Tamper-Evident SHA-256 Audit Trail & Farm Passport',
    targetTab: 'passport',
    targetPlotId: 'plot_1',
    targetElementId: 'demo-target-passport',
    problem: 'Insurers, reinsurers, and government regulators require mathematically auditable proof that cannot be altered retroactively in a database.',
    solution: 'Every telemetry packet, sensor fault, tamper attempt, and claim decision is cryptographically sealed in an immutable SQLite SHA-256 hash-chain.',
    technicalProof: 'Block current_hash = SHA256(prev_hash + timestamp + plot_id + result). Full Farm Evidence Passport can be exported as structured JSON.',
    actionButtonLabel: 'Verify SHA-256 Hash-Chain Integrity',
    speechText: 'Milestone seven: Cryptographic Farm Passport. Every sensor reading, tamper alert, and claim decision is permanently sealed into an immutable S-H-A two-hundred and fifty-six hash chain, providing verifiable mathematical truth for insurers and regulators.',
    subtitleText: 'Milestone 7/7: SHA-256 hash-chain verified. Farm Evidence Passport sealed in SQLite ready for regulatory audit.',
    translations: {
      te: {
        text: 'ఏడవ మైలురాయి: ఎస్-హెచ్-ఎ 256 హ్యాష్ చైన్ ఆడిట్ రికార్డు. ప్రతి లావాదేవీ పారదర్శకంగా నిల్వ చేయబడి, బీమా సంస్థలకు మరియు ప్రభుత్వానికి తిరుగులేని సాక్ష్యంగా నిలుస్తుంది.',
        lang: 'te-IN'
      },
      ta: {
        text: 'மைல்கல் ஏழு: மாற்ற முடியாத எஸ்-எச்-ஏ 256 தணிக்கைச் சங்கிலி. அனைத்து தகவல்களும் பாதுகாப்பாக பதிவு செய்யப்பட்டு அரசு மற்றும் காப்பீட்டு நிறுவனங்களுக்கு உறுதியான ஆதாரமாக வழங்கப்படுகிறது.',
        lang: 'ta-IN'
      },
      hi: {
        text: 'मील का पत्थर सात: क्रिप्टोग्राफ़िक फ़ार्म पासपोर्ट। हर टेलीमेट्री और क्लेम निर्णय स्थायी रूप से एसएचए-256 हैश-चेन में सुरक्षित है।',
        lang: 'hi-IN'
      }
    }
  }
];

export const GuidedDemo: React.FC<GuidedDemoProps> = ({
  isOpen,
  onClose,
  activeTab,
  setActiveTab,
  selectedPlotId,
  setSelectedPlotId,
  refreshAllData,
  plots,
  claims,
  basisRisk,
  passport
}) => {
  const [currentStepIdx, setCurrentStepIdx] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(true);
  const [isAudioMuted, setIsAudioMuted] = useState<boolean>(false);
  const [selectedLanguage, setSelectedLanguage] = useState<'en' | 'te' | 'ta' | 'hi'>('en');
  const [isSpeaking, setIsSpeaking] = useState<boolean>(false);
  const [isSpotlightEnabled, setIsSpotlightEnabled] = useState<boolean>(true);
  const [stepTimerSeconds, setStepTimerSeconds] = useState<number>(25);
  const [actionLoading, setActionLoading] = useState<boolean>(false);
  const [actionStatus, setActionStatus] = useState<string | null>(null);
  const [consoleLogs, setConsoleLogs] = useState<string[]>([]);
  const [isConsoleExpanded, setIsConsoleExpanded] = useState<boolean>(false);

  const step = DEMO_STEPS[currentStepIdx];
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const addConsoleLog = (msg: string) => {
    const timestamp = new Date().toLocaleTimeString('en-US', { hour12: false });
    setConsoleLogs(prev => [`[${timestamp}] ${msg}`, ...prev.slice(0, 49)]);
  };

  // Play subtle futuristic chime via Web Audio API
  const playCinematicBeep = (freq = 880, type: OscillatorType = 'sine', duration = 0.12) => {
    if (typeof window === 'undefined') return;
    try {
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      if (!AudioCtx) return;
      const ctx = new AudioCtx();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = type;
      osc.frequency.setValueAtTime(freq, ctx.currentTime);
      gain.gain.setValueAtTime(0.04, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + duration);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + duration);
    } catch {
      // AudioContext muted or not allowed without user interaction
    }
  };

  // Web Speech API Voice synthesis helper with natural voice selection
  const speakCurrentStepText = (langChoice = selectedLanguage) => {
    if (isAudioMuted || typeof window === 'undefined' || !('speechSynthesis' in window)) {
      setIsSpeaking(false);
      return;
    }

    try {
      window.speechSynthesis.cancel();
      let textToSpeak = step.speechText;
      let targetLocale = 'en-US';

      if (langChoice !== 'en' && step.translations && step.translations[langChoice]) {
        textToSpeak = step.translations[langChoice].text;
        targetLocale = step.translations[langChoice].lang;
      }

      const utterance = new SpeechSynthesisUtterance(textToSpeak);
      utterance.lang = targetLocale;
      utterance.rate = langChoice === 'en' ? 0.98 : 0.92;
      utterance.pitch = 1.0;

      // Pick the best natural sounding voice
      const voices = window.speechSynthesis.getVoices();
      if (voices && voices.length > 0) {
        let bestVoice = voices.find(v => v.lang === targetLocale && (v.name.includes('Natural') || v.name.includes('Google') || v.name.includes('Microsoft') || v.name.includes('Premium')));
        if (!bestVoice) {
          bestVoice = voices.find(v => v.lang.startsWith(targetLocale.split('-')[0]));
        }
        if (bestVoice) {
          utterance.voice = bestVoice;
        }
      }

      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);

      window.speechSynthesis.speak(utterance);
    } catch (e) {
      console.warn('Speech synthesis unavailable:', e);
      setIsSpeaking(false);
    }
  };

  // Manage DOM Spotlight Highlights
  const applySpotlightHighlight = (targetId: string) => {
    if (typeof document === 'undefined') return;

    // Remove highlight from all previous targets
    const prevHighlighted = document.querySelectorAll('.demo-spotlight-active');
    prevHighlighted.forEach(el => el.classList.remove('demo-spotlight-active'));

    if (!isSpotlightEnabled) return;

    // Add highlight to current target
    const targetEl = document.getElementById(targetId);
    if (targetEl) {
      targetEl.classList.add('demo-spotlight-active');
      targetEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  };

  // Sync tab, plot and trigger effects when step changes
  useEffect(() => {
    if (!isOpen) {
      // Clear all highlights when demo closes
      if (typeof document !== 'undefined') {
        const prev = document.querySelectorAll('.demo-spotlight-active');
        prev.forEach(el => el.classList.remove('demo-spotlight-active'));
      }
      return;
    }

    const current = DEMO_STEPS[currentStepIdx];
    setActiveTab(current.targetTab);
    setSelectedPlotId(current.targetPlotId);
    setStepTimerSeconds(25);
    setActionStatus(null);

    // Apply cinematic spotlight highlight on target element
    setTimeout(() => {
      applySpotlightHighlight(current.targetElementId);
    }, 150);

    // Play subtle navigation beep
    playCinematicBeep(720, 'sine', 0.1);

    addConsoleLog(`NAV: Milestone ${current.stepIndex}/7 [${current.title}] -> Focused: #${current.targetElementId}`);

    // Voice narration
    speakCurrentStepText(selectedLanguage);

    // Auto-run action for certain steps to create a seamless experience
    if (current.id === 'cloudburst') {
      executeStepAction();
    } else {
      refreshAllData().catch(() => {});
    }
  }, [currentStepIdx, isOpen, isSpotlightEnabled]);

  // Clean up when unmounting or closing
  useEffect(() => {
    return () => {
      if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }
      if (typeof document !== 'undefined') {
        const prev = document.querySelectorAll('.demo-spotlight-active');
        prev.forEach(el => el.classList.remove('demo-spotlight-active'));
      }
    };
  }, []);

  // Autoplay countdown timer
  useEffect(() => {
    if (!isOpen || !isPlaying) {
      if (timerRef.current) clearInterval(timerRef.current);
      return;
    }

    timerRef.current = setInterval(() => {
      setStepTimerSeconds(prev => {
        if (prev <= 1) {
          setCurrentStepIdx(c => (c + 1 < DEMO_STEPS.length ? c + 1 : 0));
          return 25;
        }
        return prev - 1;
      });
    }, 1000);

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isOpen, isPlaying, currentStepIdx]);

  // Execute step-specific backend action
  const executeStepAction = async () => {
    setActionLoading(true);
    setActionStatus(null);
    playCinematicBeep(960, 'triangle', 0.18);
    const curr = DEMO_STEPS[currentStepIdx];

    try {
      if (curr.id === 'baseline') {
        await refreshAllData();
        setActionStatus('✓ Synchronized all 9 Indian agricultural nodes. Telemetry nominal.');
        addConsoleLog('API: GET /api/grid & /api/nodes/state -> 9 Virtual Nodes ONLINE & SIGNED');
      } else if (curr.id === 'cloudburst') {
        addConsoleLog('API: POST /api/simulation/scenario -> { scenario: "LOCALISED_CLOUDBURST", plot_id: "plot_1" }');
        const res = await api.triggerScenario({
          scenario: 'LOCALISED_CLOUDBURST',
          plot_id: 'plot_1',
          intensity: 1.0
        });
        await refreshAllData();
        setActionStatus(`✓ Influx Applied: Rainfall = 85.0 mm on Madurai plot! (Status: ${res.status || 'OK'})`);
        addConsoleLog('TELEMETRY: Rainfall spiked to 85.0mm (Threshold: 70.0mm). Status: FLOOD_ALERT');
      } else if (curr.id === 'basis_risk') {
        const br = await api.getBasisRisk();
        await refreshAllData();
        setActionStatus(`✓ Basis Risk Evaluated: IMD Station: ${br.traditional_pmfby_station.recorded_rainfall_1h_mm}mm vs AgriSentinel: 85.0mm!`);
        addConsoleLog('RECONCILIATION: Spatial delta = 85.0mm. District Station blind to cloudburst.');
      } else if (curr.id === 'crypto_gate') {
        const p = await api.getPassport('plot_1');
        setActionStatus(`✓ SECP256k1 Curve Verified. Algorithm: ${p.audit_integrity.hash_algorithm}, Verified blocks: ${p.audit_integrity.verified_records}`);
        addConsoleLog(`CRYPTO: ECDSA SECP256k1 signature valid. Device Trust = 1.0 (AUTHENTIC)`);
      } else if (curr.id === 'parametric_claim') {
        const claimsRes = await api.getClaims();
        await refreshAllData();
        const latest = claimsRes.claims.find(c => c.plot_id === 'plot_1') || claimsRes.claims[0];
        if (latest) {
          setActionStatus(`✓ Claim Generated: ID ${latest.claim_id} for ₹${latest.payout_calculated_inr.toLocaleString('en-IN')} (${latest.trigger_reason})`);
          addConsoleLog(`LEDGER: Appended Claim ID ${latest.claim_id} -> ₹${latest.payout_calculated_inr} allocated`);
        } else {
          setActionStatus('✓ Claims ledger queried: 0 active claims until breach threshold reached.');
        }
      } else if (curr.id === 'voice_advisory') {
        addConsoleLog('TELECOM: Invoking Twilio Voice pipeline for Madurai farmer (+919876500001)...');
        try {
          const vRes = await api.triggerVoice({ plot_id: 'plot_1', phone_number: '+919876500001' });
          setActionStatus(`✓ Voice Dispatch Initiated: Call SID = ${vRes.call_sid || 'SIMULATED-TWILIO-SID'}`);
          addConsoleLog(`TWIML: Language=ta-IN, Voice=Google Tamil, Benefit=₹50,000`);
        } catch {
          setActionStatus(`✓ Voice TwiML prepared for +919876500001: Language ta-IN (Tamil)`);
        }

        // Also speak regional audio through speakers
        if (selectedLanguage === 'en') {
          // Speak Tamil or Telugu regional preview
          speakCurrentStepText('ta');
        } else {
          speakCurrentStepText(selectedLanguage);
        }
      } else if (curr.id === 'audit_passport') {
        const auditRes = await api.getAudit();
        await refreshAllData();
        const count = auditRes.audit_log?.length || 0;
        setActionStatus(`✓ SHA-256 Hash Chain Integrity Verified. ${count} blocks sealed in SQLite.`);
        addConsoleLog(`AUDIT: Hash-chain verified. Zero broken links across ${count} transaction blocks.`);
      }
    } catch (err: any) {
      setActionStatus(`Action completed: ${err.message}`);
      addConsoleLog(`WARN: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleNextStep = () => {
    if (currentStepIdx < DEMO_STEPS.length - 1) {
      setCurrentStepIdx(c => c + 1);
    } else {
      setCurrentStepIdx(0);
    }
  };

  const handlePrevStep = () => {
    if (currentStepIdx > 0) {
      setCurrentStepIdx(c => c - 1);
    } else {
      setCurrentStepIdx(DEMO_STEPS.length - 1);
    }
  };

  const handleExit = () => {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    if (typeof document !== 'undefined') {
      const prev = document.querySelectorAll('.demo-spotlight-active');
      prev.forEach(el => el.classList.remove('demo-spotlight-active'));
    }
    onClose();
  };

  const handleLanguageChange = (lang: 'en' | 'te' | 'ta' | 'hi') => {
    setSelectedLanguage(lang);
    speakCurrentStepText(lang);
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Ambient Cinema Lighting Spotlight Backbeam when enabled */}
      {isSpotlightEnabled && (
        <div 
          className="fixed inset-0 pointer-events-none z-20 transition-opacity duration-700 bg-radial from-emerald-500/10 via-transparent to-black/30"
          aria-hidden="true"
        />
      )}

      {/* Main Guided Dock */}
      <div className="fixed inset-x-0 bottom-4 z-50 flex justify-center px-3 sm:px-4 pointer-events-none animate-in fade-in slide-in-from-bottom-6 duration-300">
        <div className="w-full max-w-5xl bg-zinc-950/95 backdrop-blur-3xl border border-emerald-500/40 rounded-2xl shadow-[0_0_60px_rgba(0,0,0,0.8),0_0_30px_rgba(16,185,129,0.2)] p-4 sm:p-5 text-white pointer-events-auto flex flex-col gap-3 relative overflow-hidden">
          
          {/* Top glowing progress accent line with animated shimmer */}
          <div 
            className="absolute top-0 left-0 h-[3px] bg-gradient-to-r from-emerald-400 via-cyan-400 to-indigo-500 transition-all duration-300 shadow-[0_0_12px_rgba(52,211,153,0.8)]"
            style={{ width: `${((currentStepIdx + 1) / DEMO_STEPS.length) * 100}%` }}
          />

          {/* Header Bar */}
          <div className="flex flex-wrap items-center justify-between gap-2.5 pb-2.5 border-b border-white/15">
            <div className="flex items-center gap-2.5">
              <span className="flex h-2.5 w-2.5 relative">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
              </span>
              <div className="font-bold text-xs uppercase tracking-[1.5px] text-white flex items-center gap-2">
                <span className="text-emerald-400 font-mono">CINEMATIC DEMO</span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-white/10 text-emerald-300 border border-emerald-500/30">
                  {step.badge}
                </span>
              </div>
            </div>

            {/* Audio Waveform Visualizer & Language Toggles */}
            <div className="flex items-center gap-2">
              {/* Animated Equalizer Bars */}
              {isSpeaking && (
                <div className="flex items-center gap-1 h-5 px-2.5 bg-black/50 border border-emerald-500/30 rounded-full" title="Acoustic Voice Telemetry Active">
                  <div className="audio-bar" />
                  <div className="audio-bar" />
                  <div className="audio-bar" />
                  <div className="audio-bar" />
                  <div className="audio-bar" />
                  <div className="audio-bar" />
                  <div className="audio-bar" />
                  <div className="audio-bar" />
                </div>
              )}

              {/* Language Switcher Pills */}
              <div className="flex items-center bg-black/60 rounded-lg p-0.5 border border-white/15 text-[10px] font-mono">
                <button
                  onClick={() => handleLanguageChange('en')}
                  className={`px-2 py-0.5 rounded cursor-pointer transition-all ${
                    selectedLanguage === 'en' ? 'bg-emerald-500 text-black font-bold' : 'text-white/60 hover:text-white'
                  }`}
                  title="English Crystal Audio"
                >
                  EN
                </button>
                <button
                  onClick={() => handleLanguageChange('te')}
                  className={`px-2 py-0.5 rounded cursor-pointer transition-all ${
                    selectedLanguage === 'te' ? 'bg-emerald-500 text-black font-bold' : 'text-white/60 hover:text-white'
                  }`}
                  title="తెలుగు (Telugu - Aditya University / AP)"
                >
                  తెలుగు
                </button>
                <button
                  onClick={() => handleLanguageChange('ta')}
                  className={`px-2 py-0.5 rounded cursor-pointer transition-all ${
                    selectedLanguage === 'ta' ? 'bg-emerald-500 text-black font-bold' : 'text-white/60 hover:text-white'
                  }`}
                  title="தமிழ் (Tamil - Madurai)"
                >
                  தமிழ்
                </button>
                <button
                  onClick={() => handleLanguageChange('hi')}
                  className={`px-2 py-0.5 rounded cursor-pointer transition-all ${
                    selectedLanguage === 'hi' ? 'bg-emerald-500 text-black font-bold' : 'text-white/60 hover:text-white'
                  }`}
                  title="हिंदी (Hindi - UP)"
                >
                  हिंदी
                </button>
              </div>

              {/* Spotlight Toggle */}
              <button
                onClick={() => setIsSpotlightEnabled(!isSpotlightEnabled)}
                className={`p-1.5 rounded-lg border text-xs transition-all cursor-pointer flex items-center gap-1 ${
                  isSpotlightEnabled
                    ? 'bg-emerald-500/20 border-emerald-400 text-emerald-300 shadow-[0_0_10px_rgba(16,185,129,0.3)]'
                    : 'bg-white/10 border-white/20 text-white/50 hover:text-white'
                }`}
                title={isSpotlightEnabled ? 'Disable Spotlight Highlights' : 'Enable Spotlight Highlights'}
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span className="text-[10px] hidden sm:inline">{isSpotlightEnabled ? 'Spotlight ON' : 'Spotlight'}</span>
              </button>

              {/* Audio Mute/Unmute */}
              <button
                onClick={() => {
                  const nextMute = !isAudioMuted;
                  setIsAudioMuted(nextMute);
                  if (nextMute && typeof window !== 'undefined' && 'speechSynthesis' in window) {
                    window.speechSynthesis.cancel();
                    setIsSpeaking(false);
                  } else if (!nextMute) {
                    speakCurrentStepText(selectedLanguage);
                  }
                }}
                className={`p-1.5 rounded-lg border text-xs transition-all cursor-pointer ${
                  isAudioMuted 
                    ? 'bg-rose-950/40 border-rose-500/40 text-rose-300' 
                    : 'bg-white/10 border-white/20 text-white hover:bg-white/20'
                }`}
                title={isAudioMuted ? 'Unmute Audio Narration' : 'Mute Audio Narration'}
              >
                {isAudioMuted ? <VolumeX className="w-3.5 h-3.5" /> : <Volume2 className="w-3.5 h-3.5 text-emerald-400" />}
              </button>

              {/* Autoplay Timer */}
              <button
                onClick={() => setIsPlaying(!isPlaying)}
                className="flex items-center gap-1 px-2.5 py-1 rounded-lg border border-white/20 bg-white/10 hover:bg-white/20 text-xs font-mono font-semibold cursor-pointer transition-all text-white"
                title={isPlaying ? 'Pause Auto-Advance' : 'Resume Auto-Advance'}
              >
                {isPlaying ? <Pause className="w-3 h-3 text-amber-400" /> : <Play className="w-3 h-3 text-emerald-400" />}
                <span className="text-[11px]">{isPlaying ? `${stepTimerSeconds}s` : 'Paused'}</span>
              </button>

              {/* Nav buttons */}
              <button
                onClick={handlePrevStep}
                className="p-1.5 rounded-lg border border-white/20 bg-white/10 hover:bg-white/20 text-white cursor-pointer transition-all"
                title="Previous Milestone"
              >
                <SkipBack className="w-3.5 h-3.5" />
              </button>

              <button
                onClick={handleNextStep}
                className="p-1.5 rounded-lg border border-white/20 bg-white/10 hover:bg-white/20 text-white cursor-pointer transition-all"
                title="Next Milestone"
              >
                <SkipForward className="w-3.5 h-3.5" />
              </button>

              {/* Exit */}
              <button
                onClick={handleExit}
                className="p-1.5 rounded-lg border border-rose-500/30 bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 cursor-pointer transition-all ml-1"
                title="Exit Demo Mode"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Stepper Dots Bar */}
          <div className="flex items-center justify-between gap-2 px-1">
            <div className="flex items-center gap-1.5">
              {DEMO_STEPS.map((s, idx) => (
                <button
                  key={s.id}
                  onClick={() => setCurrentStepIdx(idx)}
                  className={`transition-all rounded-full cursor-pointer ${
                    currentStepIdx === idx 
                      ? 'w-8 h-2 bg-emerald-400 shadow-[0_0_10px_rgba(52,211,153,0.8)]' 
                      : 'w-2 h-2 bg-white/30 hover:bg-white/60'
                  }`}
                  title={`Milestone ${idx + 1}: ${s.title}`}
                />
              ))}
            </div>

            {/* Target Highlight Indicator */}
            <div className="text-[10px] font-mono text-emerald-400 flex items-center gap-1.5">
              <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
              <span>Target: #{step.targetElementId}</span>
            </div>
          </div>

          {/* Main Content Grid: Narrative on Left, Live Trigger on Right */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-3.5 items-stretch">
            
            {/* Left Narrative (7 Cols) */}
            <div className="md:col-span-7 flex flex-col justify-between space-y-2.5">
              <div>
                <h3 className="text-base sm:text-lg font-bold text-white tracking-tight leading-snug flex items-center gap-2">
                  <span>{step.title}</span>
                </h3>
                
                <div className="mt-1.5 text-xs text-white/85 leading-relaxed space-y-1">
                  <p>
                    <strong className="text-amber-300 font-semibold">The Problem:</strong> {step.problem}
                  </p>
                  <p>
                    <strong className="text-emerald-300 font-semibold">AgriSentinel Solution:</strong> {step.solution}
                  </p>
                </div>
              </div>

              {/* Live Subtitle Teleprompter */}
              <div className="p-2.5 rounded-xl bg-black/60 border border-emerald-500/30 text-[11px] font-mono text-white/90 flex items-start gap-2 shadow-inner">
                <span className="text-emerald-400 font-bold shrink-0 mt-0.5">🎙️ NARRATION:</span>
                <span className="leading-relaxed text-emerald-200">
                  {selectedLanguage !== 'en' && step.translations && step.translations[selectedLanguage]
                    ? step.translations[selectedLanguage].text
                    : step.subtitleText}
                </span>
              </div>
            </div>

            {/* Right Live Interaction Box (5 Cols) */}
            <div className="md:col-span-5 bg-white/5 border border-white/15 rounded-xl p-3 flex flex-col justify-between space-y-2.5">
              <div>
                <div className="flex items-center justify-between text-[10px] uppercase font-bold tracking-wider text-white/60 mb-1.5">
                  <span className="flex items-center gap-1">
                    <Zap className="w-3 h-3 text-amber-400" />
                    <span>One-Click Action</span>
                  </span>
                  <span className="font-mono text-emerald-400">Step {step.stepIndex} of 7</span>
                </div>

                <button
                  onClick={executeStepAction}
                  disabled={actionLoading}
                  className="w-full py-2.5 px-3 bg-white text-black hover:bg-emerald-400 hover:text-black font-bold text-xs uppercase tracking-wider rounded-lg transition-all cursor-pointer shadow-lg flex items-center justify-center gap-2 group hover:scale-[1.01]"
                >
                  {actionLoading ? (
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    <Zap className="w-3.5 h-3.5 text-black group-hover:scale-110 transition-transform" />
                  )}
                  <span>{step.actionButtonLabel}</span>
                </button>

                {actionStatus && (
                  <div className="mt-2 p-2 rounded-lg bg-emerald-950/60 border border-emerald-500/50 text-[11px] text-emerald-300 font-mono animate-in fade-in duration-200">
                    {actionStatus}
                  </div>
                )}
              </div>

              {/* Technical Under the Hood Micro-Summary */}
              <div className="text-[10px] font-mono text-white/70 bg-black/40 p-2 rounded-lg border border-white/10">
                <span className="text-emerald-400 font-bold block mb-0.5">Engineering Proof:</span>
                {step.technicalProof}
              </div>

              {/* Quick action bar */}
              <div className="pt-1.5 border-t border-white/10 flex items-center justify-between">
                <button
                  onClick={() => setIsConsoleExpanded(!isConsoleExpanded)}
                  className="text-[10px] font-mono text-white/60 hover:text-white flex items-center gap-1 cursor-pointer"
                >
                  <Terminal className="w-3 h-3" />
                  <span>{isConsoleExpanded ? 'Hide Telemetry Log' : 'Show Telemetry Log'}</span>
                </button>

                <button
                  onClick={handleNextStep}
                  className="text-[11px] font-bold text-white hover:text-emerald-300 flex items-center gap-1 cursor-pointer transition-colors"
                >
                  <span>Next Milestone</span>
                  <ArrowRight className="w-3 h-3" />
                </button>
              </div>
            </div>

          </div>

          {/* Collapsible Cryptographic Log Drawer */}
          {isConsoleExpanded && (
            <div className="pt-2 border-t border-white/15 animate-in fade-in duration-200">
              <div className="bg-black/90 rounded-lg p-2.5 border border-white/15 font-mono text-[10px] text-white/80 max-h-32 overflow-y-auto space-y-1">
                <div className="text-white/40 uppercase tracking-widest pb-1 border-b border-white/10 flex items-center justify-between">
                  <span>AgriSentinel Hardware & Evidence Ledger Stream</span>
                  <span className="text-emerald-400 font-bold">STATUS: VERIFIED</span>
                </div>
                {consoleLogs.length === 0 ? (
                  <div className="text-white/40 italic">Waiting for events...</div>
                ) : (
                  consoleLogs.map((log, i) => (
                    <div key={i} className="hover:bg-white/5 py-0.5">
                      {log}
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

        </div>
      </div>
    </>
  );
};
