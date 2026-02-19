import uuid

from django.contrib.postgres.indexes import GinIndex
from django.db import models


# ---------------------------------------------------------------------------
# Activation Key (modelo original)
# ---------------------------------------------------------------------------
class ActivationKey(models.Model):
    key = models.CharField(max_length=36, unique=True, default=uuid.uuid4)
    owner = models.CharField(max_length=256, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    device_id = models.CharField(max_length=255, null=True, blank=True)
    gemini_api_key = models.CharField(max_length=512, null=True, blank=True, verbose_name="Gemini API Key")

    def __str__(self):
        return f"{self.key} - {'Active' if self.is_active else 'Inactive'}"


# ---------------------------------------------------------------------------
# Exam
# ---------------------------------------------------------------------------
class Exam(models.Model):
    url = models.URLField(max_length=512, unique=True, db_index=True)
    title = models.CharField(max_length=512, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Examen"
        verbose_name_plural = "Exámenes"

    def __str__(self):
        return self.title or self.url


# ---------------------------------------------------------------------------
# Question
# ---------------------------------------------------------------------------
class QuestionType(models.TextChoices):
    SINGLE = "SINGLE", "Respuesta única"
    MULTI = "MULTI", "Respuesta múltiple"
    MATCH = "MATCH", "Emparejamiento"


class Question(models.Model):
    exam = models.ForeignKey(
        Exam, on_delete=models.CASCADE, related_name="questions"
    )
    text = models.TextField(verbose_name="Texto de la pregunta")
    question_type = models.CharField(
        max_length=10,
        choices=QuestionType.choices,
        default=QuestionType.SINGLE,
    )
    question_number = models.CharField(
        max_length=10, blank=True, default="", verbose_name="Nº Pregunta"
    )

    class Meta:
        ordering = ["exam", "question_number"]
        verbose_name = "Pregunta"
        verbose_name_plural = "Preguntas"
        indexes = [
            GinIndex(
                name="question_text_trgm_idx",
                fields=["text"],
                opclasses=["gin_trgm_ops"],
            )
        ]

    def __str__(self):
        label = f"Q{self.question_number}" if self.question_number else f"#{self.pk}"
        return f"[{label}] {self.text[:80]}"


# ---------------------------------------------------------------------------
# Answer
# ---------------------------------------------------------------------------
class Answer(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="answers"
    )
    text = models.TextField(verbose_name="Respuesta / Columna Izq")
    match_pair = models.TextField(
        blank=True, default="", verbose_name="Columna Der (MATCH)"
    )
    is_correct = models.BooleanField(default=False, verbose_name="¿Correcta?")
    variant_number = models.IntegerField(
        default=1, verbose_name="Nº Variante (para 'Otro caso:')"
    )

    class Meta:
        verbose_name = "Respuesta"
        verbose_name_plural = "Respuestas"
        ordering = ["variant_number", "id"]

    def __str__(self):
        mark = "✓" if self.is_correct else "✗"
        variant = f" [V{self.variant_number}]" if self.variant_number > 1 else ""
        return f"{mark}{variant} {self.text[:60]}"
