from django.contrib import admin, messages
from unfold.admin import ModelAdmin, TabularInline

from .models import ActivationKey, Answer, Exam, Question
from .scraper_service import scrape_exam



# ──────────────────────────────────────────────
# ActivationKey
# ──────────────────────────────────────────────
@admin.action(description="Generar nuevas claves de activación")
def generate_keys(modeladmin, request, queryset):
    count = 0
    for _ in range(int(request.POST.get("_selected_action_count", 1))):
        ActivationKey.objects.create()
        count += 1

    msg = (
        f"Se generó 1 nueva clave de activación"
        if count == 1
        else f"Se generaron {count} nuevas claves de activación"
    )
    messages.success(request, msg)


@admin.register(ActivationKey)
class ActivationKeyAdmin(ModelAdmin):
    list_display = ("owner", "key", "is_active", "created_at", "last_used", "device_id")
    list_filter = ("is_active",)
    search_fields = ("key", "device_id")
    readonly_fields = ("created_at",)
    actions = [generate_keys]


# ──────────────────────────────────────────────
# Answer inline (TabularInline de django-unfold)
# ──────────────────────────────────────────────
class AnswerInline(TabularInline):
    model = Answer
    extra = 1
    fields = ("text", "match_pair", "is_correct")


# ──────────────────────────────────────────────
# Question
# ──────────────────────────────────────────────
@admin.register(Question)
class QuestionAdmin(ModelAdmin):
    list_display = ("question_number", "short_text", "question_type", "exam")
    list_filter = ("question_type", "exam")
    search_fields = ("text", "question_number")
    inlines = [AnswerInline]

    @admin.display(description="Pregunta")
    def short_text(self, obj):
        return obj.text[:100] + ("…" if len(obj.text) > 100 else "")


# ──────────────────────────────────────────────
# Exam
# ──────────────────────────────────────────────
@admin.action(description="Scrapear examen seleccionado")
def scrape_exam_action(modeladmin, request, queryset):
    for exam in queryset:
        try:
            scrape_exam(exam.url)
            messages.success(request, f"✓ Examen '{exam.title}' scrapeado exitosamente")
        except Exception as e:
            messages.error(request, f"✗ Error scrapeando '{exam.title}': {str(e)}")

@admin.register(Exam)
class ExamAdmin(ModelAdmin):
    list_display = ("title", "url", "question_count", "created_at")
    search_fields = ("title", "url")
    readonly_fields = ("created_at",)
    actions = [scrape_exam_action]


    @admin.display(description="Preguntas")
    def question_count(self, obj):
        return obj.questions.count()


# ──────────────────────────────────────────────
# Answer (standalone, por si se necesita)
# ──────────────────────────────────────────────
@admin.register(Answer)
class AnswerAdmin(ModelAdmin):
    list_display = ("short_text", "match_pair", "is_correct", "question")
    list_filter = ("is_correct",)
    search_fields = ("text", "match_pair")

    @admin.display(description="Respuesta")
    def short_text(self, obj):
        return obj.text[:80] + ("…" if len(obj.text) > 80 else "")
