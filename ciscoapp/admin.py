from django.contrib import admin
from django.contrib import messages

# Register your models here.

from unfold.admin import ModelAdmin, TabularInline
from .models import ActivationKey, Examen, Pregunta, Respuesta, ParUnir

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


@admin.register(Examen)
class ExamenAdmin(ModelAdmin):
    list_display = ('nombre', 'url_fuente', 'created_at', 'total_preguntas')
    search_fields = ('nombre',)
    readonly_fields = ('created_at',)

    def total_preguntas(self, obj):
        return obj.preguntas.count()
    total_preguntas.short_description = 'Total Preguntas'


class RespuestaInline(TabularInline):
    model = Respuesta
    extra = 1
    fields = ('indice', 'texto')


class ParUnirInline(TabularInline):
    model = ParUnir
    extra = 1
    fields = ('elemento_izquierdo', 'elemento_derecho')


@admin.register(Pregunta)
class PreguntaAdmin(ModelAdmin):
    list_display = ('numero', 'examen', 'texto_corto', 'tipo', 'es_manual', 'total_respuestas')
    list_filter = ('examen', 'tipo', 'es_manual')
    search_fields = ('texto', 'numero')
    readonly_fields = ('created_at',)
    inlines = [RespuestaInline, ParUnirInline]

    def texto_corto(self, obj):
        return obj.texto[:60] + '...' if len(obj.texto) > 60 else obj.texto
    texto_corto.short_description = 'Texto'

    def total_respuestas(self, obj):
        return obj.respuestas.count()
    total_respuestas.short_description = 'Respuestas'
