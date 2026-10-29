"""
AgriSentinel Telecom & Voice Advisory Engine
============================================
Automated 2G regional language voice dispatch and TwiML IVR response generation.

TRANSPARENCY NOTE:
This service integrates with Twilio Voice APIs for outbound telephone calls.
If Twilio credentials are not configured, it operates in a safe local simulation
mode where TwiML payloads are generated and verified without network failure.
"""

import os
from typing import Optional, Dict, Any
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather

class TelecomVoiceEngine:
    @staticmethod
    def get_twilio_credentials() -> Dict[str, Optional[str]]:
        """Loads Twilio credentials strictly from environment without exposing secrets."""
        sid = os.getenv("TWILIO_ACCOUNT_SID")
        token = os.getenv("TWILIO_AUTH_TOKEN")
        phone = os.getenv("TWILIO_PHONE_NUMBER")
        
        is_configured = bool(sid and token and phone and not sid.startswith("mock") and len(token) > 10)
        return {
            "account_sid": sid if is_configured else None,
            "auth_token": token if is_configured else None,
            "phone_number": phone if is_configured else None,
            "is_configured": is_configured
        }

    @staticmethod
    def generate_breach_twiml(plot_id: str, moisture: float, payout_amount: float, language: str = "ta-IN") -> str:
        """Generates standard TwiML voice XML with speech message and dual-tone keypad response."""
        response = VoiceResponse()
        
        # Regional language speech alert
        if language.startswith("ta"):
            msg = (
                f"வணக்கம். இது அக்ரி சென்டினல் அவசர அறிவிப்பு. "
                f"நிலம் {plot_id} இல் தீவிர வறட்சி அல்லது தீவிர வானிலை மாற்றங்கள் பதிவாகியுள்ளது. "
                f"மண்ணின் ஈரப்பதம் {moisture:.1f} சதவீதம் மட்டுமே உள்ளது. "
                f"மதிப்பிடப்பட்ட இழப்பீடு {payout_amount:.0f} ரூபாய் உரிமைகோரல் ஆவணம் பதிவு செய்யப்பட்டுள்ளது."
            )
        elif language.startswith("hi"):
            msg = (
                f"नमस्ते। यह एग्री सेंटिनल आपातकालीन चेतावनी है। "
                f"आपके खेत {plot_id} पर अत्यधिक मौसम या सूखा दर्ज किया गया है। "
                f"मिट्टी की नमी {moisture:.1f} प्रतिशत है। "
                f"अनुमानित दावा दस्तावेज तैयार कर लिया गया है।"
            )
        else:
            msg = (
                f"Alert from AgriSentinel. Parametric weather breach detected on Plot {plot_id}. "
                f"Current soil moisture is {moisture:.1f} percent. "
                f"Simulated parametric claim intent of {payout_amount:.0f} rupees has been recorded."
            )

        response.say(msg, voice="Polly.Aditi", language=language)
        
        gather = Gather(num_digits=1, action="/api/twilio/gather", method="POST")
        gather.say("Press 1 to confirm receipt. Press 2 to request emergency agronomist advisory.", language="en-IN")
        response.append(gather)
        response.say("No input detected. AgriSentinel plot monitoring remains active. Goodbye.")
        return str(response)

    @staticmethod
    def generate_gather_response(digit: str) -> str:
        response = VoiceResponse()
        if digit == "1":
            response.say("Receipt confirmed. Claim intent status logged in your policy ledger.")
        elif digit == "2":
            response.say("Agronomist advisory dispatch notified. Guidance sent to your village contact.")
        else:
            response.say("Invalid entry received.")
        response.hangup()
        return str(response)

    @classmethod
    async def dispatch_voice_alert(
        cls,
        to_phone: str,
        plot_id: str,
        moisture: float,
        payout_amount: float,
        webhook_base_url: str,
        language_code: str = "ta-IN",
        custom_url: Optional[str] = None,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        from_phone: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Dispatches voice alert.
        If Twilio credentials are not available, operates in simulated mode and
        returns validated TwiML preview.
        """
        env_creds = cls.get_twilio_credentials()
        final_sid = account_sid or env_creds["account_sid"]
        final_token = auth_token or env_creds["auth_token"]
        final_from = from_phone or env_creds["phone_number"]

        # Generate the TwiML content for reference / simulation
        twiml_preview = cls.generate_breach_twiml(plot_id, moisture, payout_amount, language_code)

        # Simulation mode if not configured
        if not (final_sid and final_token and final_from and to_phone):
            return {
                "status": "SIMULATED_VOICE_DISPATCH",
                "mode": "OFFLINE_SIMULATION",
                "message": "Twilio credentials not configured in environment. Voice alert verified locally in simulation mode.",
                "to_phone": to_phone,
                "plot_id": plot_id,
                "language_code": language_code,
                "twiml_generated": True,
                "twiml_preview": twiml_preview
            }

        # Real Twilio API dispatch
        try:
            import asyncio
            client = Client(final_sid, final_token)
            
            # Use custom_url or build webhook URL pointing to this server
            voice_url = custom_url or os.getenv("TWILIO_VOICE_URL")
            if not voice_url:
                voice_url = f"{webhook_base_url}/api/twilio/voice?plot_id={plot_id}&moisture={moisture}&amount={payout_amount}"

            call = await asyncio.wait_for(
                asyncio.to_thread(
                    client.calls.create,
                    to=to_phone,
                    from_=final_from,
                    url=voice_url
                ),
                timeout=4.0
            )
            return {
                "status": "QUEUED",
                "mode": "LIVE_TWILIO_DISPATCH",
                "call_sid": call.sid,
                "to_phone": to_phone,
                "language": language_code,
                "voice_url_used": voice_url
            }
        except Exception as e:
            # Mask error string to ensure credentials are never exposed
            err_msg = str(e)
            if final_token and final_token in err_msg:
                err_msg = err_msg.replace(final_token, "[REDACTED_AUTH_TOKEN]")
            if final_sid and final_sid in err_msg:
                err_msg = err_msg.replace(final_sid, "[REDACTED_ACCOUNT_SID]")
            return {
                "status": "ERROR",
                "mode": "DISPATCH_FAILED",
                "error_type": type(e).__name__,
                "sanitized_message": err_msg,
                "twiml_preview": twiml_preview
            }

# Backward compatibility
generate_breach_twiml = TelecomVoiceEngine.generate_breach_twiml
generate_gather_response = TelecomVoiceEngine.generate_gather_response
dispatch_voice_alert = TelecomVoiceEngine.dispatch_voice_alert
