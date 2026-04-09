"""Envío de instrucciones de activación por email con adjunto .zip."""

import logging
import os

from django.conf import settings
from django.core.mail import EmailMessage
from django.template import Template, Context

logger = logging.getLogger(__name__)

INSTRUCTIONS_PATH = os.path.join(settings.BASE_DIR, "instructions.md")
EXTENSION_ZIP_PATH = os.path.join(settings.BASE_DIR, "extension.zip")


def send_instructions_email(to_email: str, owner: str, activation_key: str) -> None:
    # Render instructions template
    with open(INSTRUCTIONS_PATH, encoding="utf-8") as f:
        template = Template(f.read())

    body = template.render(Context({"nombre": owner, "clave": activation_key}))

    email = EmailMessage(
        subject="Tu herramienta de estudio CCNA - Instrucciones",
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )

    # Attach extension .zip if it exists
    if os.path.exists(EXTENSION_ZIP_PATH):
        with open(EXTENSION_ZIP_PATH, "rb") as f:
            email.attach("ccna-study-tool.zip", f.read(), "application/zip")
    else:
        logger.warning(
            "extension.zip not found at %s — sending email without attachment",
            EXTENSION_ZIP_PATH,
        )

    email.send(fail_silently=False)
    logger.info("Instructions email sent to %s", to_email)
