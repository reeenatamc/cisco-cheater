from django.db import models
import uuid

# Create your models here.

class ActivationKey(models.Model):
    key = models.CharField(max_length=36, unique=True, default=uuid.uuid4)
    owner = models.CharField(max_length=256, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    device_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.key} - {'Active' if self.is_active else 'Inactive'}"


class Examen(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    url_fuente = models.URLField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Examen"
        verbose_name_plural = "Exámenes"
        ordering = ['nombre']


class Pregunta(models.Model):
    TIPO_CHOICES = [
        ('opcion_simple', 'Opción Simple'),
        ('opcion_multiple', 'Opción Múltiple'),
        ('unir', 'Unir/Arrastrar'),
    ]

    examen = models.ForeignKey(Examen, on_delete=models.CASCADE, related_name='preguntas')
    numero = models.IntegerField()
    texto = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    es_manual = models.BooleanField(default=False, help_text="True para preguntas de unir/arrastrar agregadas manualmente")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.examen.nombre} - Q{self.numero}: {self.texto[:50]}..."

    class Meta:
        verbose_name = "Pregunta"
        verbose_name_plural = "Preguntas"
        unique_together = ['examen', 'numero']
        ordering = ['examen', 'numero']


class Respuesta(models.Model):
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE, related_name='respuestas')
    texto = models.TextField()
    indice = models.IntegerField(help_text="Posición 1-based en la lista original")

    def __str__(self):
        return f"Respuesta {self.indice}: {self.texto[:30]}..."

    class Meta:
        verbose_name = "Respuesta"
        verbose_name_plural = "Respuestas"
        ordering = ['indice']


class ParUnir(models.Model):
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE, related_name='pares')
    elemento_izquierdo = models.CharField(max_length=500)
    elemento_derecho = models.CharField(max_length=500)

    def __str__(self):
        return f"{self.elemento_izquierdo} → {self.elemento_derecho}"

    class Meta:
        verbose_name = "Par Unir"
        verbose_name_plural = "Pares Unir"
