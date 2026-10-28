import os
from typing import Optional, Dict, Any
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather

VOICE_WEBHOOK_URLS: Dict[str, str] = {
    "en-IN": "https://webhook.site/4b2f6890-5186-4db4-826e-2320122dc53b",
    "ta-IN": "https://webhook.site/0c0c87aa-8393-45f9-935f-09bf151e590c",
    "hi-IN": "https://webhook.site/b0bf6f59-f791-47e0-8642-1199381a436f",
    "te-IN": "https://webhook.site/abfcebbe-80b5-4ecd-b67b-01461a0c8784",
    "bn-IN": "https://webhook.site/82651e60-4214-4ee6-8073-efd8e2dc0a2a",
    "gu-IN": "https://webhook.site/a335e210-cf58-4749-8bb4-c1b99a605512",
    "mr-IN": "https://webhook.site/d9354b42-20df-4073-9da1-b6f3706bdeed",
    "ml-IN": "https://webhook.site/0d99704b-28a4-443c-a4ae-ebe17341f7b3",
    "kn-IN": "https://webhook.site/f18de3ee-8ed8-4f93-87da-0e7dcc7fed9e",
}

class TelecomVoiceEngine:
    @staticmethod
    def get_twilio_client():
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        if account_sid and auth_token and not account_sid.startswith("mock"):
            return Client(account_sid, auth_token)
        return None

    @staticmethod
    def generate_breach_twiml(plot_id: str, moisture: float, payout_amount: float, language: str = "en-IN") -> str:
        response = VoiceResponse()
        response.say(
            f"Alert from AgriSentinel. Parametric drought threshold exceeded on Plot {plot_id}. Current soil moisture is {moisture:.1f} percent. Automated crop insurance payout of {payout_amount:.0f} rupees has been approved and disbursed.",
            voice="Polly.Aditi",
            language=language
        )
        gather = Gather(num_digits=1, action="/api/twilio/gather", method="POST")
        gather.say("Press 1 to confirm payout receipt. Press 2 to request immediate agronomist advisory dispatch.")
        response.append(gather)
        response.say("No input detected. AgriSentinel protection remains active. Goodbye.")
        return str(response)

    @staticmethod
    def generate_gather_response(digit: str) -> str:
        response = VoiceResponse()
        if digit == "1":
            response.say("Payout receipt confirmed. Funds have been routed to your registered account.")
        elif digit == "2":
            response.say("Agronomist advisory team notified. Emergency guidance sent to your mobile terminal.")
        else:
            response.say("Invalid entry received.")
        response.hangup()
        return str(response)

    @staticmethod
    async def dispatch_voice_alert(
        to_phone: str,
        plot_id: str,
        moisture: float,
        payout_amount: float,
        webhook_base_url: str,
        language_code: str = "en-IN",
        custom_url: Optional[str] = None,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        from_phone: Optional[str] = None
    ) -> Dict[str, Any]:
        account_sid = account_sid or os.getenv("TWILIO_ACCOUNT_SID", "AC7b5b6cc7e83c59d0edc54bcf59a4dee1")
        auth_token = auth_token or os.getenv("TWILIO_AUTH_TOKEN", "6af791ff2a26f1c8e69afe984fafcf17")
        from_phone = from_phone or os.getenv("TWILIO_PHONE_NUMBER", "+17372508034")

        if not (account_sid and auth_token and to_phone and not account_sid.startswith("mock")):
            return {
                "status": "simulated",
                "to": to_phone,
                "plot_id": plot_id,
                "amount": payout_amount,
                "language": language_code,
                "notes": "Safe simulation mode (Twilio credentials not configured in environment)"
            }

        try:
            import asyncio
            client = Client(account_sid, auth_token)
            voice_url = custom_url or os.getenv("TWILIO_VOICE_URL") or VOICE_WEBHOOK_URLS.get(language_code) or VOICE_WEBHOOK_URLS.get("en-IN")
            if not voice_url:
                if "127.0.0.1" in webhook_base_url or "localhost" in webhook_base_url:
                    voice_url = VOICE_WEBHOOK_URLS.get("ta-IN")
                else:
                    voice_url = f"{webhook_base_url}/api/twilio/voice?plot_id={plot_id}&moisture={moisture}&amount={payout_amount}"

            call = await asyncio.wait_for(
                asyncio.to_thread(
                    client.calls.create,
                    to=to_phone,
                    from_=from_phone,
                    url=voice_url
                ),
                timeout=3.0
            )
            return {
                "status": "queued",
                "call_sid": call.sid,
                "voice_url_used": voice_url,
                "language": language_code
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

generate_breach_twiml = TelecomVoiceEngine.generate_breach_twiml
generate_gather_response = TelecomVoiceEngine.generate_gather_response
dispatch_voice_alert = TelecomVoiceEngine.dispatch_voice_alert
get_twilio_client = TelecomVoiceEngine.get_twilio_client
