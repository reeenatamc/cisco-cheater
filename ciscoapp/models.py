from django.db import models
from django.contrib.postgres.indexes import GinIndex
import uuid


# ─── Activation ──────────────────────────────────────────────


class ActivationKey(models.Model):
    key = models.CharField("Clave", max_length=36, unique=True, default=uuid.uuid4)
    owner = models.CharField("Propietario", max_length=256, null=True, blank=True)
    is_active = models.BooleanField("Activa", default=True)
    created_at = models.DateTimeField("Fecha de creación", auto_now_add=True)
    last_used = models.DateTimeField("Último uso", null=True, blank=True)
    device_id = models.CharField("ID de dispositivo", max_length=255, null=True, blank=True)
    gemini_api_key = models.CharField(
        "Gemini API Key", max_length=512, null=True, blank=True
    )
    phone_number = models.CharField(
        "Teléfono (WhatsApp)", max_length=32, null=True, blank=True,
        help_text="Ej. 593999999999 (Código de país sin el '+' seguido del número)"
    )
    expires_at = models.DateTimeField(
        "Fecha de expiración", null=True, blank=True,
        help_text="Dejar vacío para que no expire nunca.",
    )

    class Meta:
        verbose_name = "Clave de activación"
        verbose_name_plural = "Claves de activación"
        indexes = [
            models.Index(fields=["device_id"], name="ak_device_id_idx"),
        ]

    def __str__(self):
        return f"{self.key} - {'Activa' if self.is_active else 'Inactiva'}"


# ─── Exam / Question / Answer ────────────────────────────────


class Exam(models.Model):
    url = models.URLField("URL", max_length=512, unique=True, db_index=True)
    title = models.CharField("Título", max_length=512, blank=True, default="")
    created_at = models.DateTimeField("Fecha de creación", auto_now_add=True)

    class Meta:
        verbose_name = "Examen"
        verbose_name_plural = "Exámenes"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title or self.url


class Question(models.Model):
    class Type(models.TextChoices):
        SINGLE = "SINGLE", "Respuesta única"
        MULTI = "MULTI", "Respuesta múltiple"
        MATCH = "MATCH", "Emparejamiento"

    exam = models.ForeignKey(
        Exam, on_delete=models.CASCADE, related_name="questions",
        verbose_name="Examen",
    )
    question_number = models.CharField(
        "Nº Pregunta", max_length=10, blank=True, default=""
    )
    text = models.TextField("Texto de la pregunta")
    question_type = models.CharField(
        "Tipo", max_length=10, choices=Type.choices, default=Type.SINGLE
    )

    class Meta:
        verbose_name = "Pregunta"
        verbose_name_plural = "Preguntas"
        ordering = ["exam", "question_number"]
        indexes = [
            GinIndex(
                fields=["text"],
                name="question_text_trgm_idx",
                opclasses=["gin_trgm_ops"],
            ),
        ]

    def __str__(self):
        prefix = f"P{self.question_number}" if self.question_number else "P?"
        return f"[{prefix}] {self.text[:80]}"


class Answer(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="answers",
        verbose_name="Pregunta",
    )
    text = models.TextField("Respuesta / Columna Izq")
    match_pair = models.TextField(
        "Columna Der (MATCH)", blank=True, default=""
    )
    is_correct = models.BooleanField("¿Correcta?", default=False)
    variant_number = models.IntegerField(
        "Nº Variante (para 'Otro caso:')", default=1
    )

    class Meta:
        verbose_name = "Respuesta"
        verbose_name_plural = "Respuestas"
        ordering = ["variant_number", "id"]

    def __str__(self):
        mark = "[v]" if self.is_correct else "[x]"
        return f"{mark} {self.text[:60]}"
