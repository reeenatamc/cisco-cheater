import requests
from django.conf import settings

def send_whatsapp_message(phone_number, message):
    """
    Envía un mensaje de WhatsApp usando una API externa.
    phone_number: str, en formato internacional (ej: +521234567890)
    message: str, texto a enviar
    """
    # Configura aquí tu endpoint y token de la API de WhatsApp
    api_url = getattr(settings, "WHATSAPP_API_URL", None)
    api_token = getattr(settings, "WHATSAPP_API_TOKEN", None)
    if not api_url or not api_token:
        raise Exception("No está configurada la API de WhatsApp en settings.")
    headers = {"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"}
    data = {
        "to": phone_number,
        "message": message,
    }
    response = requests.post(api_url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()
