from django.db import models
import uuid

# Create your models here.

class ActivationKey(models.Model):
    key = models.CharField(max_length=36, unique=True, default=uuid.uuid4)
    owner = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    device_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.key} - {'Active' if self.is_active else 'Inactive'}"
