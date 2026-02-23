"""
API views for cisco-cheater.

Endpoints:
    /              → home (landing page)
    /buscar/       → TrigramSimilarity search in DB
    /activate/     → activate device key
    /verify_activation/ → verify device activation
    /consultar_gemini/  → text question → Gemini
    /consultar_gemini_imagen/ → image → OCR → DB search → fallback Gemini
"""

import json
import re
import os
import base64
import shutil
import logging
from io import BytesIO
from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.postgres.search import TrigramSimilarity

from .models import ActivationKey, Question, Answer
from .whatsapp_service import send_instructions_pdf_whatsapp

from google import genai
from PIL import Image
import pytesseract

logger = logging.getLogger(__name__)

# ── Tesseract path detection ─────────────────────────────────

if not shutil.which("tesseract"):
    for p in [
        "/usr/bin/tesseract",
        "/usr/local/bin/tesseract",
        "/opt/homebrew/bin/tesseract",
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    ]:
        if os.path.exists(p):
            pytesseract.pytesseract.tesseract_cmd = p
            break


# ── Helpers ───────────────────────────────────────────────────

def _verify_device(device_id: str):
    """Return the ActivationKey or None. Updates last_used on success."""
    if not device_id:
        return None
    try:
        ak = ActivationKey.objects.get(device_id=device_id, is_active=True)
        ak.last_used = datetime.now()
        ak.save(update_fields=["last_used"])
        return ak
    except ActivationKey.DoesNotExist:
        return None


def _json_body(request):
    return json.loads(request.body)


def _format_question_result(question: Question) -> dict:
    """Serialize a Question + its Answers to the API response format.

    Answers are grouped by variant_number so the frontend can display
    'Otro caso' sections when a question has multiple answer sets.
    """
    answers_qs = question.answers.filter(is_correct=True).order_by(
        "variant_number", "id"
    )

    # Group answers by variant
    from itertools import groupby
    from operator import attrgetter

    variants = []
    for variant_num, group in groupby(answers_qs, key=attrgetter("variant_number")):
        answers_in_variant = list(group)

        if question.question_type == "MATCH":
            variant_answers = [
                {
                    "text": a.text,
                    "match_pair": a.match_pair,
                    "is_correct": True,
                }
                for a in answers_in_variant
            ]
        else:
            variant_answers = [
                {"text": a.text, "is_correct": True}
                for a in answers_in_variant
            ]

        variants.append({
            "variant": variant_num,
            "answers": variant_answers,
        })

    # If there's only one variant, return flat answers for backwards compat
    if len(variants) == 1:
        return {
            "question": question.text,
            "type": question.question_type,
            "answers": variants[0]["answers"],
        }

    # Multiple variants — include variants array
    return {
        "question": question.text,
        "type": question.question_type,
        "answers": variants[0]["answers"],  # default (variant 1)
        "variants": variants,
    }


# ── Search helpers ────────────────────────────────────────────

TRIGRAM_THRESHOLD = 0.3


def _search_db(text: str, limit: int = 5):
    """
    Search by TrigramSimilarity on Question.text.
    Returns list of (Question, similarity) tuples.
    """
    qs = (
        Question.objects.annotate(
            similarity=TrigramSimilarity("text", text),
        )
        .filter(similarity__gt=TRIGRAM_THRESHOLD)
        .select_related("exam")
        .prefetch_related("answers")
        .order_by("-similarity")[:limit]
    )
    return [(q, q.similarity) for q in qs]


# Keyword extraction for OCR fallback search
_STOP_WORDS = frozenset(
    "el la los las un una unos unas de del al a en con por para y o que es "
    "son se su como más pero sus le ya lo esto esta este".split()
)


def _extract_keywords(text: str) -> set[str]:
    words = re.findall(r"\b[a-záéíóúñü]+\b", text.lower())
    return {w for w in words if w not in _STOP_WORDS and len(w) > 2}


def _search_db_for_ocr(ocr_text: str, limit: int = 3):
    """
    Two-pass search for OCR text:
      1. TrigramSimilarity on the full OCR text (best matches).
      2. If nothing found, try keyword overlap fallback.
    """
    # Pass 1: trigram on a cleaned version of the OCR text (take first ~200 chars)
    clean = re.sub(r"\s+", " ", ocr_text).strip()[:300]
    results = _search_db(clean, limit=limit)
    if results:
        return results

    # Pass 2: keyword overlap (for noisy OCR)
    keywords = _extract_keywords(ocr_text)
    if len(keywords) < 3:
        return []

    best = None
    best_score = 0
    for q in Question.objects.prefetch_related("answers").iterator(chunk_size=200):
        q_keywords = _extract_keywords(q.text)
        if len(q_keywords) < 3:
            continue
        overlap = keywords & q_keywords
        score = len(overlap) / len(q_keywords)
        if score >= 0.7 and score > best_score:
            best_score = score
            best = q
    return [(best, best_score)] if best else []


# ══════════════════════════════════════════════════════════════
# Views
# ══════════════════════════════════════════════════════════════


def home(request):
    return render(request, "you_never_gonna_catch_me.html")


# ── /buscar/ ──────────────────────────────────────────────────

@csrf_exempt
def buscar(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data = _json_body(request)
    device_id = data.get("device_id", "").strip()

    if not _verify_device(device_id):
        return JsonResponse({"error": "Device not activated"}, status=403)

    pregunta = data.get("pregunta", "").strip()
    if not pregunta:
        return JsonResponse({"respuesta": None, "found": False})

    results = _search_db(pregunta, limit=3)

    if results:
        top_q, sim = results[0]
        return JsonResponse({
            "found": True,
            "similarity": round(sim, 3),
            "results": [_format_question_result(q) for q, _ in results],
        })

    return JsonResponse({"respuesta": None, "found": False})


# ── /activate/ ────────────────────────────────────────────────

@csrf_exempt
def activate(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data = _json_body(request)
    key = data.get("key", "").strip()
    device_id = data.get("device_id", "").strip()

    if not key or not device_id:
        return JsonResponse(
            {"error": "Key and device ID are required"}, status=400
        )

    try:
        ak = ActivationKey.objects.get(key=key, is_active=True)
        if ak.device_id and ak.device_id != device_id:
            return JsonResponse(
                {"error": "This key is already in use on another device"},
                status=403,
            )
        ak.device_id = device_id
        ak.last_used = datetime.now()
        ak.save()
        return JsonResponse({"message": "Activation successful"})
    except ActivationKey.DoesNotExist:
        return JsonResponse(
            {"error": "Invalid activation key"}, status=404
        )


# ── /verify_activation/ ──────────────────────────────────────

@csrf_exempt
def verify_activation(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data = _json_body(request)
    device_id = data.get("device_id", "").strip()

    if not device_id:
        return JsonResponse(
            {"error": "Device ID is required"}, status=400
        )

    ak = _verify_device(device_id)
    return JsonResponse({"is_activated": ak is not None})


@csrf_exempt
def send_instructions_whatsapp(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data = _json_body(request)
    key = data.get("key", "").strip()
    device_id = data.get("device_id", "").strip()

    if not key:
        return JsonResponse({"error": "Key is required"}, status=400)

    try:
        ak = ActivationKey.objects.get(key=key, is_active=True)
    except ActivationKey.DoesNotExist:
        return JsonResponse({"error": "Invalid activation key"}, status=404)

    if device_id and ak.device_id and ak.device_id != device_id:
        return JsonResponse(
            {"error": "This key is already in use on another device"},
            status=403,
        )

    try:
        result = send_instructions_pdf_whatsapp(ak)
        return JsonResponse({"success": True, "message": "Instructions sent", "result": result})
    except Exception as exc:
        logger.exception("WhatsApp send failed")
        return JsonResponse({"success": False, "error": str(exc)}, status=500)


# ── /consultar_gemini/ ────────────────────────────────────────

@csrf_exempt
def consultar_gemini(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data = _json_body(request)
    device_id = data.get("device_id", "").strip()
    pregunta = data.get("pregunta", "").strip()
    api_key = data.get("api_key", "").strip()

    if not _verify_device(device_id):
        return JsonResponse({"error": "Device not activated"}, status=403)
    if not api_key:
        return JsonResponse(
            {"error": "Gemini API key is required"}, status=400
        )
    if not pregunta:
        return JsonResponse({"error": "Question is required"}, status=400)

    try:
        client = genai.Client(api_key=api_key)
        prompt = (
            "Eres un experto en redes y certificaciones Cisco CCNA. "
            "Responde de forma MUY breve y directa (máximo 2-3 líneas). "
            "Si es una pregunta de opción múltiple, indica solo el número "
            "de la opción correcta y una breve explicación. "
            f"Pregunta: {pregunta}"
        )
        response = client.models.generate_content(
            model="gemini-3-flash-preview", contents=prompt
        )
        return JsonResponse({"respuesta": response.text, "success": True})
    except Exception as e:
        logger.exception("Gemini error")
        return JsonResponse({"error": str(e), "success": False}, status=500)


# ── /consultar_gemini_imagen/ ─────────────────────────────────

@csrf_exempt
def consultar_gemini_imagen(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data = _json_body(request)
    device_id = data.get("device_id", "").strip()
    imagen_base64 = data.get("imagen", "").strip()
    api_key = data.get("api_key", "").strip()

    if not _verify_device(device_id):
        return JsonResponse({"error": "Device not activated"}, status=403)
    if not api_key:
        return JsonResponse(
            {"error": "Gemini API key is required"}, status=400
        )
    if not imagen_base64:
        return JsonResponse({"error": "Image is required"}, status=400)

    try:
        # Strip data URI prefix
        if "," in imagen_base64:
            imagen_base64 = imagen_base64.split(",", 1)[1]

        imagen_bytes = base64.b64decode(imagen_base64)
        imagen = Image.open(BytesIO(imagen_bytes))
        texto_extraido = pytesseract.image_to_string(imagen, lang="spa+eng")

        logger.info("OCR extracted %d chars", len(texto_extraido))

        if not texto_extraido.strip():
            return JsonResponse(
                {"error": "Could not extract text from image", "success": False},
                status=400,
            )

        # ── Search DB with trigram ────────────────────────────
        results = _search_db_for_ocr(texto_extraido, limit=1)

        if results:
            top_q, _ = results[0]
            result_data = _format_question_result(top_q)
            # Build a short text summary for the popup
            if top_q.question_type == "MATCH":
                pairs = [
                    f"{a['text']} → {a['match_pair']}" for a in result_data["answers"]
                ]
                respuesta_texto = "[DB] " + " | ".join(pairs)
            else:
                correct_texts = [a["text"] for a in result_data["answers"]]
                respuesta_texto = "[DB] " + ". ".join(correct_texts)

            return JsonResponse(
                {
                    "respuesta": respuesta_texto,
                    "success": True,
                    "source": "diccionario",
                    "result": result_data,
                }
            )

        # ── Fallback to Gemini ────────────────────────────────
        logger.info("No DB match for OCR text, falling back to Gemini")
        client = genai.Client(api_key=api_key)
        prompt = (
            "Pregunta de examen Cisco CCNA extraída de una captura:\n\n"
            f"{texto_extraido}\n\n"
            "Responde de forma MUY breve y directa (máximo 2-3 líneas).\n"
            "- Si es opción múltiple: indica el número de la opción correcta.\n"
            "- Si es de unir/emparejar: indica qué va con qué.\n"
            "- Si es de arrastrar: indica el orden o la ubicación correcta.\n"
            "Solo da la respuesta, sin explicaciones largas."
        )
        response = client.models.generate_content(
            model="gemini-3-flash-preview", contents=prompt
        )
        return JsonResponse(
            {"respuesta": response.text, "success": True, "source": "gemini"}
        )

    except Exception as e:
        logger.exception("Error in consultar_gemini_imagen")
        return JsonResponse({"error": str(e), "success": False}, status=500)
