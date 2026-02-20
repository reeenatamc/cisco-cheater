from django.contrib import admin
from django.contrib import messages
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.shortcuts import redirect
from django.utils.html import format_html

from unfold.admin import ModelAdmin, TabularInline
from .models import ActivationKey, Exam, Question, Answer


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
    list_display = ("owner", "key", "is_active", "created_at", "last_used", "device_id")
    list_filter = ("is_active",)
    search_fields = ("key", "device_id")
    readonly_fields = ("created_at",)
    actions = [generate_keys]


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
