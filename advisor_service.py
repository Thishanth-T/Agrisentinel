import os
import json
import datetime
from typing import Dict, Any, List
from groq import AsyncGroq

# Pre-computed multi-language agronomic action database for all crops across regions
DEFAULT_AGRONOMIC_ACTIONS = {
    "Soybean": {
        "en": [
            "Apply broad-bed furrow irrigation to direct restricted water directly to the root zones.",
            "Apply organic bio-mulch to protect nodulation bacteria from hyper-thermal soil decay.",
            "Foliar spray with 2% urea solution to sustain nitrogen fixation under moisture stress."
        ],
        "hi": [
            "जड़ों तक सीमित पानी पहुंचाने के लिए चौड़ी क्यारी और नाली विधि से सिंचाई करें।",
            "मिट्टी की नमी और बैक्टीरिया की सुरक्षा के लिए जैविक बायो-मल्च का प्रयोग करें।",
            "नमी के तनाव में नाइट्रोजन पोषण बनाए रखने के लिए 2% यूरिया घोल का छिड़काव करें।"
        ],
        "ta": [
            "பாத்தி அமைத்து வேர்ப்பகுதிக்கு மட்டும் நேரடியாக பாசனம் செய்யவும்.",
            "மண் பாக்டீரியாக்களை பாதுகாக்க இயற்கை மூடாக்கு இடவும்.",
            "வறட்சியை தாங்க 2% யூரியா கரைசலை இலைகளில் தெளிக்கவும்."
        ],
        "te": [
            "వేరు మండలాలకు మాత్రమే నేరుగా నీటిని అందించడానికి సాళ్ళు మరియు బోదెల విధానంలో నీరు పెట్టండి.",
            "నేలలోని తేమను కాపాడటానికి సేంద్రీయ వ్యర్థాలతో నేలను కప్పండి (మల్చింగ్).",
            "తేమ కొరతను తట్టుకోవడానికి పైరుపై 2% యూరియా ద్రావణాన్ని పిచికారీ చేయండి."
        ],
        "gu": [
            "મર્યાદિત પાણી સીધું મૂળ સુધી પહોંચાડવા માટે પહોળા પાળા અને નીકની પદ્ધતિથી પિયત આપો.",
            "જમીનમાં ભેજ જાળવી રાખવા માટે કુદરતી કચરાનું આવરણ (મલ્ચિંગ) કરો.",
            "ભેજની અછતમાં પાકને ટકાવી રાખવા માટે 2% યુરિયાના દ્રાવણનો છંટકાવ કરો."
        ],
        "audio_phonetic": {
            "hi": "Jadon tak paani pahunchane ke liye naali vidhi se sinchai karein. Nami bachane ke liye bio mulch dalein. 2 pratishat urea ka chhidkaav karein.",
            "ta": "Verppagudhiku neradiyaaga paasanam seiyavum. Iyarkai moodakku idavum. 2 percent urea thelikkavum."
        }
    },
    "Wheat": {
        "en": [
            "Initiate supplemental micro-drip irrigation immediately during low-evaporative evening hours.",
            "Apply straw mulch across root beds to suppress evaporation and maintain residual soil moisture.",
            "Postpone nitrogen top-dressing to prevent hyper-transpiration stress under acute soil dryness."
        ],
        "hi": [
            "वाष्पीकरण कम करने के लिए शाम के समय हल्की ड्रिप या फव्वारा सिंचाई तुरंत शुरू करें।",
            "मिट्टी की नमी बनाए रखने के लिए जड़ों के पास पुआल या भूसे की मल्चिंग करें।",
            "अत्यधिक सूखे में पौधों के तनाव को रोकने के लिए नाइट्रोजन खाद का छिड़काव टालें।"
        ],
        "ta": [
            "ஆவியாதலை குறைக்க மாலை நேரங்களில் அவசர சொட்டு நீர் பாசனத்தை உடனே தொடங்கவும்.",
            "மண்ணின் ஈரப்பதத்தை பாதுகாக்க வேர்ப்பகுதியில் வைக்கோல் மூடாக்கு இடவும்.",
            "பயிரின் நீர் இழப்பை தடுக்க தழைச்சத்து உரமிடுவதை தற்காலிகமாக தவிர்க்கவும்."
        ],
        "audio_phonetic": {
            "hi": "Shaam ke samay halki sinchai karein. Puaal ki mulching karein. Nitrogen khad abhi na dalein.",
            "ta": "Maalai nerangalil sottu neer paasanathai thodangavum. Vaikkol moodakku idavum."
        }
    },
    "Cotton": {
        "en": [
            "Activate skip-furrow irrigation to maximize water delivery to boll-bearing root branches.",
            "Apply 2% DAP spray to arrest stress-induced square and boll shedding.",
            "Erect shade netting or reflective mulching to mitigate canopy scorch."
        ],
        "hi": [
            "कपास के पौधों को पानी बचाने के लिए एक नाली छोड़कर एक नाली में सिंचाई करें।",
            "फूल और गूलर को गिरने से रोकने के लिए 2% डीएपी घोल का छिड़काव करें।",
            "अत्यधिक धूप और झुलसन से बचाव के लिए परावर्तक मल्चिंग का उपयोग करें।"
        ],
        "gu": [
            "કપાસમાં પાણી બચાવવા માટે એક નાળ છોડીને એક નાળ પદ્ધતિથી પિયત આપો.",
            "ઝીંડવા ખરી પડતા અટકાવવા માટે 2% ડીએપી દ્રાવણનો છંટકાવ કરો.",
            "પાકને લૂ થી બચાવવા માટે પ્લાસ્ટિક અથવા કચરાનું મલ્ચિંગ કરો."
        ],
        "ta": [
            "பருத்தி செடிகளுக்கு ஒரு சால் விட்டு ஒரு சால் நீர் பாய்ச்சவும்.",
            "காய் உதிர்வதை தடுக்க 2% டிஏபி கரைசலை தெளிக்கவும்.",
            "அதிக வெப்பத்தை தணிக்க மூடாக்கு அல்லது நிழல் வலைகளை பயன்படுத்தவும்."
        ],
        "audio_phonetic": {
            "hi": "Ek naali chhodkar sinchai karein. 2 pratishat DAP ghol chhidkein.",
            "gu": "Ek naal chhodi ne piyat aapo. 2 percent DAP chhanto."
        }
    },
    "Rice": {
        "en": [
            "Implement Alternate Wetting and Drying (AWD) cycle to conserve critical water head.",
            "Seal bund micro-fissures with clay to arrest peripheral seepage loss across paddy plots.",
            "Spray 1% potassium chloride (KCl) solution as anti-transpirant to preserve leaf turgidity."
        ],
        "hi": [
            "पानी बचाने के लिए बारी-बारी से खेत को गीला और सूखा रखने की तकनीक (AWD) अपनाएं।",
            "मेड़ों से पानी के रिसाव को रोकने के लिए चिकनी मिट्टी से दरारें बंद करें।",
            "पत्तियों की नमी बरकरार रखने के लिए 1% पोटैशियम क्लोराइड का छिड़काव करें।"
        ],
        "ta": [
            "நீரை சேமிக்க முறைப்படி சுழற்சி முறையில் பாசனம் செய்யவும்.",
            "வரப்புகளில் நீர் கசிவதை தடுக்க களிமண் கொண்டு விரிசல்களை மூடவும்.",
            "இலைகளின் ஈரப்பதத்தை பாதுகாக்க பொட்டாசியம் குளோரைடு கரைசலை தெளிக்கவும்."
        ],
        "audio_phonetic": {
            "hi": "Paani bachane ke liye AWD vidhi apnayein. Medon ki daraarein band karein.",
            "ta": "Suzharchi muraiyil paasanam seiyavum. Varappu neer kasivai thadukkavum."
        }
    },
    "Maize": {
        "en": [
            "Apply pulse irrigation to the root zones during critical silking and grain-filling stages.",
            "Spread dry leaves or grass mulch to lower soil temperature by 3-5 degrees Celsius.",
            "Apply foliar zinc and boron micro-nutrients to sustain grain development under drought."
        ],
        "hi": [
            "मक्के के दाने भरने की अवस्था में जड़ों के पास हल्की और बार-बार सिंचाई करें।",
            "मिट्टी का तापमान कम रखने के लिए सूखे पत्तों या घास की मल्चिंग करें।",
            "सूखे के तनाव में दाने के विकास के लिए जिंक और बोरॉन सूक्ष्म पोषक तत्वों का छिड़काव करें।"
        ],
        "te": [
            "కంకి పాలు పోసుకునే దశలో మొక్కల వేర్లకు తక్కువ మోతాదులో తరచూ నీరు అందించండి.",
            "నేల ఉష్ణోగ్రతను తగ్గించడానికి ఎండిన ఆకులతో మల్చింగ్ ఏర్పాటు చేయండి.",
            "కరువు సమయంలో గింజ బరువు తగ్గకుండా జింక్ మరియు బోరాన్ పిచિકారీ చేయండి."
        ],
        "audio_phonetic": {
            "hi": "Makkai me daane bharte samay halki sinchai karein. Ghaas ki mulching dalein.",
            "te": "Kanki dasha lo takkuva neeru ivvandi. Dry leaves tho mulching cheyandi."
        }
    }
}

STATE_TO_LANG_MAP = {
    "Uttar Pradesh": ("hi", "Hindi"),
    "Madhya Pradesh": ("hi", "Hindi"),
    "Rajasthan": ("hi", "Hindi"),
    "Bihar": ("hi", "Hindi"),
    "Haryana": ("hi", "Hindi"),
    "Tamil Nadu": ("ta", "Tamil"),
    "Andhra Pradesh": ("te", "Telugu"),
    "Telangana": ("te", "Telugu"),
    "Gujarat": ("gu", "Gujarati"),
    "Maharashtra": ("mr", "Marathi"),
    "West Bengal": ("bn", "Bengali"),
    "Kerala": ("ml", "Malayalam"),
    "Karnataka": ("kn", "Kannada"),
}

class GroqAdvisoryService:
    @classmethod
    async def get_agronomic_advisory(
        cls,
        plot_id: str,
        crop: str,
        moisture: float,
        temp: float,
        rainfall: float,
        state: str = "Tamil Nadu",
        language_code: str = "ta-IN",
        language_name: str = "Tamil",
        month: str = ""
    ) -> Dict[str, Any]:
        if not month:
            month = datetime.datetime.now().strftime("%B")

        lang_key, mapped_lang_name = STATE_TO_LANG_MAP.get(state, ("ta", "Tamil"))
        if language_name:
            mapped_lang_name = language_name

        crop_data = DEFAULT_AGRONOMIC_ACTIONS.get(crop, DEFAULT_AGRONOMIC_ACTIONS.get("Soybean"))
        regional_actions = crop_data.get(lang_key) or crop_data.get("hi") or crop_data.get("ta") or crop_data.get("en")
        phonetic_dict = crop_data.get("audio_phonetic", {})
        phonetic_script = phonetic_dict.get(lang_key) or phonetic_dict.get("hi") or phonetic_dict.get("ta") or "AgriSentinel Parametric Advisory Alert"

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key or api_key.startswith("mock"):
            return {
                "plot_id": plot_id,
                "crop": crop,
                "state": state,
                "language_name": mapped_lang_name,
                "month": month,
                "condition": "Critical Parametric Drought Breached",
                "actions_english": crop_data["en"],
                "actions_regional": regional_actions,
                "regional_audio_script": phonetic_script,
                "payout_status": "Approved for Automated Instant Indemnity Settlement",
                "source": "AgriSentinel Resilient Regional Rulebase"
            }

        try:
            client = AsyncGroq(api_key=api_key, timeout=4.0)
            prompt = (
                f"You are the AgriSentinel AI Agronomic Engine for Indian agriculture. "
                f"A parametric drought breach has triggered on Farm Plot {plot_id.upper()} in {state}. "
                f"Crop: {crop}. Current Month: {month}. Soil Moisture: {moisture:.1f}% (critical). "
                f"Ambient Temperature: {temp:.1f}C. 24h Rainfall: {rainfall:.1f}mm.\n"
                f"Target regional language: {mapped_lang_name}.\n"
                f"Task:\n"
                f"1. Provide 3 high-impact, immediate emergency agronomic actions for the farmer in English.\n"
                f"2. Provide the exact 3 corresponding actions translated into natural agricultural {mapped_lang_name} (in the native {mapped_lang_name} script).\n"
                f"Format as strict JSON with keys: 'actions_en' (list of 3 strings), 'actions_regional' (list of 3 strings)."
            )

            response = await client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are AgriSentinel's enterprise agricultural AI. Always respond with valid JSON containing 'actions_en' and 'actions_regional'."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"},
                max_tokens=600
            )

            raw_json = response.choices[0].message.content
            parsed = json.loads(raw_json)
            actions_en = parsed.get("actions_en", [])
            actions_reg = parsed.get("actions_regional", [])

            return {
                "plot_id": plot_id,
                "crop": crop,
                "state": state,
                "language_name": mapped_lang_name,
                "month": month,
                "condition": "Critical Parametric Drought Breached",
                "actions_english": actions_en if len(actions_en) >= 2 else crop_data["en"],
                "actions_regional": actions_reg if len(actions_reg) >= 2 else regional_actions,
                "regional_audio_script": phonetic_script,
                "payout_status": "Approved for Automated Instant Indemnity Settlement",
                "source": f"Groq LLaMA-3.3-70B Enterprise ({mapped_lang_name})"
            }
        except Exception:
            return {
                "plot_id": plot_id,
                "crop": crop,
                "state": state,
                "language_name": mapped_lang_name,
                "month": month,
                "condition": "Critical Parametric Drought Breached",
                "actions_english": crop_data["en"],
                "actions_regional": regional_actions,
                "regional_audio_script": phonetic_script,
                "payout_status": "Approved for Automated Instant Indemnity Settlement",
                "source": f"AgriSentinel Resilient Regional Rulebase ({mapped_lang_name})"
            }
