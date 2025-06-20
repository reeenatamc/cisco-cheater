from django.contrib import admin
from django.contrib import messages

# Register your models here.

from unfold.admin import ModelAdmin
from .models import ActivationKey

@admin.action(description="Generar nuevas claves de activación")
def generate_keys(ModelAdmin, request, queryset):
    count = 0
    for _ in range(request.POST.get('_selected_action_count', 1)):
        key = ActivationKey.objects.create()
        count += 1
    
    if count == 1:
        messages.success(request, f'Se generó 1 nueva clave de activación')
    else:
        messages.success(request, f'Se generaron {count} nuevas claves de activación')

@admin.register(ActivationKey)
class ActivationKeyAdmin(ModelAdmin):
    list_display = ('owner', 'key', 'is_active', 'created_at', 'last_used', 'device_id')
    list_filter = ('is_active',)
    search_fields = ('key', 'device_id')
    readonly_fields = ('created_at',)
    actions = [generate_keys]
