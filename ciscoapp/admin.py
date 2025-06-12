from django.contrib import admin

# Register your models here.

from unfold.admin import ModelAdmin
from .models import ActivationKey

@admin.register(ActivationKey)
class ActivationKeyAdmin(ModelAdmin):
    list_display = ('key', 'is_active', 'created_at', 'last_used', 'device_id')
    list_filter = ('is_active',)
    search_fields = ('key', 'device_id')
    readonly_fields = ('created_at',)
