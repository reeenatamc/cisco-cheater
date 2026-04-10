from django.contrib import admin
from django.db.models import Sum
from decimal import Decimal
from django.contrib import messages
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.shortcuts import redirect
from django.utils.html import format_html

from unfold.admin import ModelAdmin, TabularInline
from .models import ActivationKey, Exam, Question, Answer, HardwareChangeRequest


# ══════════════════════════════════════════════════════════════
# HardwareChangeRequest
# ══════════════════════════════════════════════════════════════

@admin.register(HardwareChangeRequest)
class HardwareChangeRequestAdmin(ModelAdmin):
    list_display = (
        "activation_key",
        "created_at",
        "is_processed",
        "reason_short",
    )
    list_filter = ("is_processed", "created_at")
    search_fields = ("activation_key__key", "reason")
    list_editable = ("is_processed",)
    readonly_fields = ("created_at", "activation_key", "reason", "old_device_id")

    @admin.display(description="Motivo")
    def reason_short(self, obj):
        return obj.reason[:100] + "…" if len(obj.reason) > 100 else obj.reason


# ══════════════════════════════════════════════════════════════
# ActivationKey
# ══════════════════════════════════════════════════════════════

@admin.action(description="Generar nuevas claves de activación")
def generate_keys(modeladmin, request, queryset):
    count = 0
    for _ in range(int(request.POST.get('_selected_action_count', 1))):
        ActivationKey.objects.create()
        count += 1
    messages.success(
        request,
        f"Se generó {count} nueva(s) clave(s) de activación" if count else "—",
    )


@admin.register(ActivationKey)
class ActivationKeyAdmin(ModelAdmin):
    list_display = (
        "owner",
        "key",
        "is_active",
        "phone_number",
        "enviar_whatsapp_link",
        "price_paid",
        "created_at",
        "expires_at",
        "last_used",
        "device_id",
    )
    list_display_links = ("key",)
    list_filter = ("is_active",)
    search_fields = ("key", "device_id", "owner")
    readonly_fields = ("created_at",)
    list_editable = ("is_active", "price_paid", "expires_at", "owner")

    list_before_template = "admin/ciscoapp/activationkey/dashboard.html"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        # Calculate totals for Dashboard
        total_keys = ActivationKey.objects.count()
        total_revenue = ActivationKey.objects.aggregate(total=Sum('price_paid'))['total'] or Decimal('0.00')
        active_keys = ActivationKey.objects.filter(is_active=True).count()
        
        extra_context['dashboard_revenue'] = total_revenue
        extra_context['dashboard_total_keys'] = total_keys
        extra_context['dashboard_active_keys'] = active_keys
        
        return super().changelist_view(request, extra_context=extra_context)

    actions = [generate_keys]

    @admin.display(description="WhatsApp")
    def enviar_whatsapp_link(self, obj):
        if not obj.phone_number:
            return "—"
        
        from django.conf import settings
        import urllib.parse
        import os
        
        nombre = obj.owner or "Estudiante"
        domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "localhost:8000")
        prefix = "https://" if "localhost" not in domain else "http://"
        download_url = f"{prefix}{domain}/download/{obj.key}/"
        
        mensaje = (
            f"¡Hola {nombre}! Aquí tienes tu acceso a la herramienta de estudio CCNA.\n\n"
            f"🔑 Tu clave de activación es: {obj.key}\n\n"
            f"📥 Puedes descargar la extensión y leer las instrucciones aquí:\n"
            f"{download_url}"
        )
        
        encoded_message = urllib.parse.quote(mensaje)
        wa_url = f"https://wa.me/{obj.phone_number}?text={encoded_message}"
        
        return format_html(
            '<a href="{}" target="_blank" style="background-color: #25D366; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none; font-weight: bold; font-size: 12px; display: inline-block;">Enviar WA</a>',
            wa_url
        )


# ══════════════════════════════════════════════════════════════
# Answer inline
# ══════════════════════════════════════════════════════════════

class AnswerInline(TabularInline):
    model = Answer
    extra = 1
    fields = ("text", "match_pair", "is_correct", "variant_number")


# ══════════════════════════════════════════════════════════════
# Question
# ══════════════════════════════════════════════════════════════

@admin.register(Question)
class QuestionAdmin(ModelAdmin):
    list_display = ("question_number", "text_short", "question_type", "exam")
    list_filter = ("question_type", "exam")
    search_fields = ("text",)
    readonly_fields = ("exam",)
    inlines = [AnswerInline]
    fieldsets = (
        (None, {
            "fields": ("exam", "question_number", "question_type"),
        }),
        ("Contenido", {
            "fields": ("text",),
        }),
    )

    @admin.display(description="Pregunta")
    def text_short(self, obj):
        return obj.text[:100] + "…" if len(obj.text) > 100 else obj.text



# ══════════════════════════════════════════════════════════════
# Answer  –  standalone (for adding MATCH/drag-drop manually)
# ══════════════════════════════════════════════════════════════

@admin.register(Answer)
class AnswerAdmin(ModelAdmin):
    list_display = ("question", "text_short", "match_pair", "is_correct", "variant_number")
    list_filter = ("is_correct", "question__question_type", "question__exam")
    search_fields = ("text", "question__text")
    raw_id_fields = ("question",)

    @admin.display(description="Respuesta")
    def text_short(self, obj):
        return obj.text[:80] + "…" if len(obj.text) > 80 else obj.text


# ══════════════════════════════════════════════════════════════
# Exam  –  with scraping action
# ══════════════════════════════════════════════════════════════

@admin.register(Exam)
class ExamAdmin(ModelAdmin):
    list_display = ("title", "url", "question_count", "created_at")
    search_fields = ("title", "url")
    readonly_fields = ("created_at",)

    @admin.display(description="Preguntas")
    def question_count(self, obj):
        return obj.questions.count()

    # ── Custom URL for scrape action ──────────────────────────
    def get_urls(self):
        custom = [
            path(
                "scrape/",
                self.admin_site.admin_view(self.scrape_view),
                name="ciscoapp_exam_scrape",
            ),
        ]
        return custom + super().get_urls()

    def scrape_view(self, request):
        """Form-based view to trigger a scrape from the admin."""
        if request.method == "POST":
            url = request.POST.get("url", "").strip()
            if not url:
                messages.error(request, "URL es requerida.")
                return redirect(reverse("admin:ciscoapp_exam_changelist"))

            try:
                from .scraper_service import scrape_exam

                stats = scrape_exam(url)
                messages.success(
                    request,
                    f"Scraping completado: {stats['exam_title']} - "
                    f"{stats['created']} nuevas, {stats['skipped']} duplicadas, "
                    f"{stats['image_only']} solo imagen.",
                )
            except Exception as exc:
                messages.error(request, f"Error: {exc}")

            return redirect(reverse("admin:ciscoapp_exam_changelist"))

        # GET → show a simple form
        context = {
            **self.admin_site.each_context(request),
            "title": "Scrapear Examen",
            "opts": self.model._meta,
        }
        return TemplateResponse(
            request, "admin/ciscoapp/exam/scrape_form.html", context
        )
