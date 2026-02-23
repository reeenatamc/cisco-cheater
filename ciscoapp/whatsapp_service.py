import os
import tempfile
from pathlib import Path

import requests
from django.conf import settings
from django.template import Context, Template


def _render_instructions_markdown(activation_key) -> str:
    md_path = Path(settings.BASE_DIR) / "instructions.md"
    with open(md_path, encoding="utf-8") as f:
        md_template = f.read()

    template = Template(md_template)
    return template.render(
        Context({"nombre": activation_key.owner or "Usuario", "clave": activation_key.key})
    )


def _markdown_to_document(markdown_text: str) -> str:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8")
    with tmp:
        tmp.write(markdown_text)
    return tmp.name


def send_instructions_pdf_whatsapp(activation_key):
    phone_number = (activation_key.phone_number or "").strip()
    if not phone_number:
        raise ValueError("La activation key no tiene phone_number configurado")

    access_token = os.environ.get("WHATSAPP_ACCESS_TOKEN", "").strip()
    phone_number_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID", "").strip()

    if not access_token or not phone_number_id:
        raise ValueError(
            "Faltan variables de entorno WHATSAPP_ACCESS_TOKEN o WHATSAPP_PHONE_NUMBER_ID"
        )

    document_body = _render_instructions_markdown(activation_key)
    doc_path = _markdown_to_document(document_body)

    upload_url = f"https://graph.facebook.com/v21.0/{phone_number_id}/media"
    send_url = f"https://graph.facebook.com/v21.0/{phone_number_id}/messages"
    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        with open(doc_path, "rb") as f:
            files = {
                "file": ("instrucciones.txt", f, "text/plain"),
                "messaging_product": (None, "whatsapp"),
                "type": (None, "text/plain"),
            }
            upload_resp = requests.post(upload_url, headers=headers, files=files, timeout=30)
            upload_resp.raise_for_status()
            media_id = upload_resp.json().get("id")

        if not media_id:
            raise ValueError("No se recibió media_id al subir el documento")

        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "document",
            "document": {
                "id": media_id,
                "filename": "instrucciones.txt",
                "caption": "Tus instrucciones personalizadas",
            },
        }
        send_resp = requests.post(
            send_url,
            headers={**headers, "Content-Type": "application/json"},
            json=payload,
            timeout=30,
        )
        send_resp.raise_for_status()
        return send_resp.json()
    finally:
        if os.path.exists(doc_path):
            os.remove(doc_path)
