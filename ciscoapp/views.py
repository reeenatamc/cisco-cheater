"""
API views para cisco-cheater.

Endpoints:
  POST /buscar/            → Búsqueda difusa (TrigramSimilarity)
  POST /activate/          → Activar clave
  POST /verify_activation/ → Verificar activación
  POST /consultar_gemini/  → Consultar Gemini con texto
  POST /consultar_gemini_imagen/ → Consultar Gemini con imagen + OCR
  GET  /                   → Home page
"""
import base64
import io
import json
import logging
from datetime import datetime

from django.contrib.postgres.search import TrigramSimilarity
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
try:
    import easyocr
    import numpy as np
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
from google import genai

from .models import ActivationKey, Answer, Exam, Question, QuestionType
from .scraper_service import scrape_exam

logger = logging.getLogger(__name__)

# Inicializar EasyOCR (se carga una sola vez)
ocr_reader = None

def get_ocr_reader():
    global ocr_reader
    if not EASYOCR_AVAILABLE:
        return None
    if ocr_reader is None:
        ocr_reader = easyocr.Reader(['es', 'en'], gpu=False)
    return ocr_reader

SIMILARITY_THRESHOLD = 0.3


# ──────────────────────────────────────────────
# Home
# ──────────────────────────────────────────────
def home(request):
    return render(request, "you_never_gonna_catch_me.html")


# ──────────────────────────────────────────────
# Activación
# ──────────────────────────────────────────────
@csrf_exempt
def activate(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    data = json.loads(request.body)
    key = data.get("key", "").strip()
    device_id = data.get("device_id", "").strip()
    gemini_api_key = data.get("gemini_api_key", "").strip()

    if not key or not device_id:
        return JsonResponse(
            {"error": "Clave y ID de dispositivo son requeridos"}, status=400
        )

    try:
        activation_key = ActivationKey.objects.get(key=key, is_active=True)

        if activation_key.device_id and activation_key.device_id != device_id:
            return JsonResponse(
                {"error": "Esta clave ya está en uso en otro dispositivo"}, status=403
            )

        activation_key.device_id = device_id
        activation_key.last_used = datetime.now()
        
        # Guardar Gemini API key si se proporciona
        if gemini_api_key:
            activation_key.gemini_api_key = gemini_api_key
        
        activation_key.save()
        return JsonResponse({"message": "Activación exitosa"})

    except ActivationKey.DoesNotExist:
        return JsonResponse(
            {"error": "Clave de activación inválida"}, status=404
        )


@csrf_exempt
def verify_activation(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    data = json.loads(request.body)
    device_id = data.get("device_id", "").strip()

    if not device_id:
        return JsonResponse({"error": "ID de dispositivo requerido"}, status=400)

    try:
        activation_key = ActivationKey.objects.get(
            device_id=device_id, is_active=True
        )
        activation_key.last_used = datetime.now()
        activation_key.save()
        return JsonResponse({"is_activated": True})
    except ActivationKey.DoesNotExist:
        return JsonResponse({"is_activated": False})


# ──────────────────────────────────────────────
# Helper: formatear respuesta según tipo
# ──────────────────────────────────────────────
def _format_question_response(question: Question) -> dict:
    """
    Retorna un JSON serializable con soporte para variantes:
      {
        "type": "SINGLE" | "MULTI" | "MATCH",
        "question": "...",
        "has_variants": bool,
        "total_variants": int,
        "data": ... (para retrocompatibilidad, muestra variante 1)
        "answers": [  (nuevo formato con variantes)
            {"text": "...", "variant": 1, "match_pair": "..." (opcional)},
            ...
        ]
      }
    """
    correct_answers = question.answers.filter(is_correct=True).order_by("variant_number", "id")
    
    # Detectar si hay variantes
    variant_numbers = list(set(a.variant_number for a in correct_answers))
    has_variants = len(variant_numbers) > 1
    total_variants = max(variant_numbers) if variant_numbers else 1
    
    # Formato nuevo: todas las respuestas con variant_number
    answers_list = []
    for a in correct_answers:
        answer_dict = {
            "text": a.text,
            "variant": a.variant_number,
        }
        if question.question_type == QuestionType.MATCH:
            answer_dict["match_pair"] = a.match_pair
        answers_list.append(answer_dict)
    
    # Formato legacy (data): solo variante 1 para retrocompatibilidad
    variant_1_answers = [a for a in correct_answers if a.variant_number == 1]
    
    if question.question_type == QuestionType.MATCH:
        data = [
            {"col_a": a.text, "col_b": a.match_pair}
            for a in variant_1_answers
        ]
    elif question.question_type == QuestionType.MULTI:
        data = [a.text for a in variant_1_answers]
    else:  # SINGLE
        first = variant_1_answers[0] if variant_1_answers else None
        data = first.text if first else ""

    return {
        "type": question.question_type,
        "question": question.text,
        "question_number": question.question_number,
        "has_variants": has_variants,
        "total_variants": total_variants,
        "data": data,  # Legacy format (variant 1 only)
        "answers": answers_list,  # New format (all variants)
    }


# ──────────────────────────────────────────────
# Búsqueda difusa
# ──────────────────────────────────────────────
@csrf_exempt
def buscar(request):
    """
    POST /buscar/
    Body: { "device_id": "...", "pregunta": "...", "url": "..." (opcional) }

    Lazy Scraping: si se envía `url` y no existe, se scrapea al vuelo.
    Búsqueda: TrigramSimilarity sobre Question.text (umbral > SIMILARITY_THRESHOLD).
    """
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    data = json.loads(request.body)
    device_id = data.get("device_id", "").strip()

    # ── Verificar activación ──
    try:
        activation_key = ActivationKey.objects.get(
            device_id=device_id, is_active=True
        )
        activation_key.last_used = datetime.now()
        activation_key.save()
    except ActivationKey.DoesNotExist:
        return JsonResponse({"error": "Dispositivo no activado"}, status=403)

    pregunta = data.get("pregunta", "").strip()
    exam_url = data.get("url", "").strip()

    if not pregunta:
        return JsonResponse({"error": "Pregunta requerida"}, status=400)

    # ── Lazy Scraping ──
    if exam_url:
        if not Exam.objects.filter(url=exam_url).exists():
            try:
                scrape_exam(exam_url)
                logger.info("Lazy scrape completado: %s", exam_url)
            except Exception as exc:
                logger.error("Error en lazy scrape %s: %s", exam_url, exc)
                # Continuar con lo que haya en la DB

    # ── Búsqueda con TrigramSimilarity ──
    qs = (
        Question.objects
        .annotate(similarity=TrigramSimilarity("text", pregunta))
        .filter(similarity__gt=SIMILARITY_THRESHOLD)
        .order_by("-similarity")
    )

    # Si se proporcionó URL, filtrar por ese examen
    if exam_url:
        qs = qs.filter(exam__url=exam_url)

    best = qs.first()

    if best:
        response_data = _format_question_response(best)
        response_data["similarity"] = round(best.similarity, 3)
        return JsonResponse({"respuesta": response_data, "found": True})

    # ── Fallback: búsqueda por substring (case-insensitive) ──
    fallback_qs = Question.objects.filter(text__icontains=pregunta)
    if exam_url:
        fallback_qs = fallback_qs.filter(exam__url=exam_url)

    fallback = fallback_qs.first()
    if fallback:
        response_data = _format_question_response(fallback)
        response_data["similarity"] = 0.0
        return JsonResponse({"respuesta": response_data, "found": True})

    return JsonResponse({"respuesta": "❌ Pregunta no encontrada.", "found": False})


# ──────────────────────────────────────────────
# Consultar Gemini con texto
# ──────────────────────────────────────────────
@csrf_exempt
def consultar_gemini(request):
    """
    POST /consultar_gemini/
    Body: { "device_id": "...", "pregunta": "...", "api_key": "..." }
    
    Consulta a Gemini API para responder una pregunta de texto.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)
    
    data = json.loads(request.body)
    device_id = data.get("device_id", "").strip()
    pregunta = data.get("pregunta", "").strip()
    api_key = data.get("api_key", "").strip()
    
    # Verificar activación
    try:
        activation_key = ActivationKey.objects.get(
            device_id=device_id, is_active=True
        )
        activation_key.last_used = datetime.now()
        activation_key.save()
        
        # Si no se proporciona API key en request, usar la del ActivationKey
        if not api_key and activation_key.gemini_api_key:
            api_key = activation_key.gemini_api_key
            
    except ActivationKey.DoesNotExist:
        return JsonResponse({"error": "Dispositivo no activado"}, status=403)
    
    if not pregunta:
        return JsonResponse({"error": "Pregunta requerida"}, status=400)
    
    if not api_key:
        return JsonResponse({"error": "API key de Gemini no configurada"}, status=400)
    
    try:
        # Configurar Gemini
        client = genai.Client(api_key=api_key)
        
        # Generar respuesta
        prompt = f"Responde la siguiente pregunta de forma concisa y precisa:\n\n{pregunta}"
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt
        )
        
        respuesta_texto = response.text if hasattr(response, 'text') else str(response)
        
        return JsonResponse({
            "success": True,
            "respuesta": respuesta_texto
        })
        
    except Exception as e:
        logger.error(f"Error consultando Gemini: {e}")
        return JsonResponse({
            "success": False,
            "error": f"Error al consultar Gemini: {str(e)}"
        }, status=500)


# ──────────────────────────────────────────────
# Consultar Gemini con imagen + OCR
# ──────────────────────────────────────────────
@csrf_exempt
def consultar_gemini_imagen(request):
    """
    POST /consultar_gemini_imagen/
    Body: { "device_id": "...", "imagen": "data:image/png;base64,...", "api_key": "..." }
    
    1. Extrae texto de la imagen con OCR (pytesseract)
    2. Busca coincidencias en la base de datos
    3. Si no encuentra, consulta a Gemini API con la imagen
    """
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)
    
    data = json.loads(request.body)
    device_id = data.get("device_id", "").strip()
    imagen_base64 = data.get("imagen", "").strip()
    api_key = data.get("api_key", "").strip()
    
    # Verificar activación
    try:
        activation_key = ActivationKey.objects.get(
            device_id=device_id, is_active=True
        )
        activation_key.last_used = datetime.now()
        activation_key.save()
        
        # Si no se proporciona API key en request, usar la del ActivationKey
        if not api_key and activation_key.gemini_api_key:
            api_key = activation_key.gemini_api_key
            
    except ActivationKey.DoesNotExist:
        return JsonResponse({"error": "Dispositivo no activado"}, status=403)
    
    if not imagen_base64:
        return JsonResponse({"error": "Imagen requerida"}, status=400)
    
    try:
        # Decodificar imagen base64
        if "base64," in imagen_base64:
            imagen_base64 = imagen_base64.split("base64,")[1]
        
        image_bytes = base64.b64decode(imagen_base64)
        image = Image.open(io.BytesIO(image_bytes))
        
        texto_ocr = ""
        
        # Intentar OCR con EasyOCR si está disponible
        if EASYOCR_AVAILABLE:
            try:
                # Convertir a numpy array para EasyOCR
                image_np = np.array(image)
                
                # Extraer texto con EasyOCR
                reader = get_ocr_reader()
                result = reader.readtext(image_np)
                texto_ocr = ' '.join([text[1] for text in result])
                texto_ocr = texto_ocr.strip()
                logger.info(f"Texto extraído por EasyOCR: {texto_ocr[:200]}")
            except Exception as e:
                logger.warning(f"Error en EasyOCR, continuando sin OCR: {e}")
                texto_ocr = ""
        
        # Buscar en base de datos con el texto extraído
        if texto_ocr:
            qs = (
                Question.objects
                .annotate(similarity=TrigramSimilarity("text", texto_ocr))
                .filter(similarity__gt=SIMILARITY_THRESHOLD)
                .order_by("-similarity")
            )
            
            best = qs.first()
            
            if best and best.similarity > 0.5:  # Umbral más alto para OCR
                response_data = _format_question_response(best)
                response_data["similarity"] = round(best.similarity, 3)
                response_data["ocr_text"] = texto_ocr[:200]  # Primeros 200 chars
                
                # Formatear respuesta como texto simple para mostrar en popup
                if response_data["type"] == "SINGLE":
                    respuesta_texto = f"📝 Respuesta encontrada en BD:\n\n{response_data['data']}"
                elif response_data["type"] == "MULTI":
                    respuestas = "\n• ".join(response_data['data'])
                    respuesta_texto = f"📝 Respuestas encontradas en BD:\n\n• {respuestas}"
                elif response_data["type"] == "MATCH":
                    pares = "\n".join([f"• {p['col_a']} ➜ {p['col_b']}" for p in response_data['data']])
                    respuesta_texto = f"📝 Emparejamientos encontrados en BD:\n\n{pares}"
                else:
                    respuesta_texto = str(response_data['data'])
                
                return JsonResponse({
                    "success": True,
                    "respuesta": respuesta_texto,
                    "source": "database",
                    "similarity": response_data["similarity"]
                })
        
        # Si no se encuentra en BD o no hay API key, usar Gemini con la imagen
        if not api_key:
            return JsonResponse({
                "success": False,
                "error": "No se encontró en BD y no hay API key de Gemini configurada"
            }, status=400)
        
        # Consultar a Gemini con la imagen
        client = genai.Client(api_key=api_key)
        
        # Preparar imagen para Gemini
        image_part = genai.types.Part.from_bytes(
            data=base64.b64decode(imagen_base64),
            mime_type="image/png"
        )
        
        prompt = "Analiza esta imagen y responde la pregunta que se muestra. Si es una pregunta de opción múltiple, indica cuál(es) son la(s) respuesta(s) correcta(s). Sé conciso y preciso."
        
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=[prompt, image_part]
        )
        
        respuesta_texto = response.text if hasattr(response, 'text') else str(response)
        
        return JsonResponse({
            "success": True,
            "respuesta": respuesta_texto,
            "source": "gemini",
            "ocr_text": texto_ocr[:200] if texto_ocr else None
        })
        
    except Exception as e:
        logger.error(f"Error en consultar_gemini_imagen: {e}")
        return JsonResponse({
            "success": False,
            "error": f"Error: {str(e)}"
        }, status=500)
