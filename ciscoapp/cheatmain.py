import json
import os
import base64
import shutil
from io import BytesIO
from datetime import datetime
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import ActivationKey
from google import genai
from google.genai import types
from PIL import Image
import pytesseract

# Configurar la ruta de tesseract automáticamente si no está en PATH
# Esto es necesario para entornos de producción como Railway
if not shutil.which('tesseract'):
    # Intentar rutas comunes de tesseract en Linux
    possible_paths = [
        '/usr/bin/tesseract',
        '/usr/local/bin/tesseract',
        '/opt/homebrew/bin/tesseract',  # macOS
    ]
    for path in possible_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            break


def home(request):
    return render(request, 'you_never_gonna_catch_me.html')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(BASE_DIR, 'diccionario.json')

with open(json_path, encoding='utf-8') as f:
    DICCIONARIO = json.load(f)

@csrf_exempt
def activate(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        key = data.get('key', '').strip()
        device_id = data.get('device_id', '').strip()

        if not key or not device_id:
            return JsonResponse({'error': 'Clave y ID de dispositivo son requeridos'}, status=400)

        try:
            activation_key = ActivationKey.objects.get(key=key, is_active=True)
            
            # Si la clave ya está en uso por otro dispositivo
            if activation_key.device_id and activation_key.device_id != device_id:
                return JsonResponse({'error': 'Esta clave ya está en uso en otro dispositivo'}, status=403)
            
            # Si es la primera vez que se usa o es el mismo dispositivo
            activation_key.device_id = device_id
            activation_key.last_used = datetime.now()
            activation_key.save()
            
            return JsonResponse({'message': 'Activación exitosa'})
            
        except ActivationKey.DoesNotExist:
            return JsonResponse({'error': 'Clave de activación inválida'}, status=404)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def verify_activation(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        device_id = data.get('device_id', '').strip()

        if not device_id:
            return JsonResponse({'error': 'ID de dispositivo requerido'}, status=400)

        try:
            activation_key = ActivationKey.objects.get(device_id=device_id, is_active=True)
            activation_key.last_used = datetime.now()
            activation_key.save()
            return JsonResponse({'is_activated': True})
        except ActivationKey.DoesNotExist:
            return JsonResponse({'is_activated': False})

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def buscar(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        device_id = data.get('device_id', '').strip()
        
        # Verificar activación
        try:
            activation_key = ActivationKey.objects.get(device_id=device_id, is_active=True)
            activation_key.last_used = datetime.now()
            activation_key.save()
        except ActivationKey.DoesNotExist:
            return JsonResponse({'error': 'Dispositivo no activado'}, status=403)

        pregunta = data.get('pregunta', '').strip().lower()
        if pregunta in (key.lower() for key in DICCIONARIO):
            clave_exacta = next(key for key in DICCIONARIO if key.lower() == pregunta)
            respuesta = DICCIONARIO[clave_exacta]
            return JsonResponse({'respuesta': respuesta, 'found': True})
        else:
            coincidencias = [DICCIONARIO[key] for key in DICCIONARIO if pregunta in key.lower()]
            if coincidencias:
                respuesta = coincidencias[0]
                return JsonResponse({'respuesta': respuesta, 'found': True})
            else:
                return JsonResponse({'respuesta': None, 'found': False})

    return JsonResponse({'error': 'Método no permitido'}, status=405)


@csrf_exempt
def consultar_gemini(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        device_id = data.get('device_id', '').strip()
        pregunta = data.get('pregunta', '').strip()
        api_key = data.get('api_key', '').strip()
        
        # Verificar activación
        try:
            activation_key = ActivationKey.objects.get(device_id=device_id, is_active=True)
            activation_key.last_used = datetime.now()
            activation_key.save()
        except ActivationKey.DoesNotExist:
            return JsonResponse({'error': 'Dispositivo no activado'}, status=403)
        
        if not api_key:
            return JsonResponse({'error': 'API key de Gemini requerida'}, status=400)
        
        if not pregunta:
            return JsonResponse({'error': 'Pregunta requerida'}, status=400)
        
        try:
            client = genai.Client(api_key=api_key)
            
            prompt = f"Eres un experto en redes y certificaciones Cisco CCNA. Responde de forma MUY breve y directa (máximo 2-3 líneas). Si es una pregunta de opción múltiple, indica solo el número de la opción correcta y una breve explicación. Pregunta: {pregunta}"
            
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=prompt
            )
            
            return JsonResponse({'respuesta': response.text, 'success': True})
            
        except Exception as e:
            return JsonResponse({'error': str(e), 'success': False}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)


def normalizar_texto(texto):
    """Normaliza texto para comparación: minúsculas, sin saltos de línea extra, espacios normalizados"""
    import re
    texto = texto.lower()
    texto = re.sub(r'\s+', ' ', texto)  # Múltiples espacios/saltos a un solo espacio
    texto = texto.strip()
    return texto


def extraer_palabras_clave(texto):
    """Extrae palabras significativas (ignora artículos, preposiciones, etc.)"""
    import re
    # Palabras a ignorar (stop words en español)
    stop_words = {'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'de', 'del', 'al', 
                  'a', 'en', 'con', 'por', 'para', 'y', 'o', 'que', 'es', 'son', 'se', 'su',
                  'como', 'más', 'pero', 'sus', 'le', 'ya', 'lo', 'esto', 'esta', 'este'}
    
    palabras = re.findall(r'\b[a-záéíóúñü]+\b', texto.lower())
    return [p for p in palabras if p not in stop_words and len(p) > 2]


def buscar_en_diccionario(texto):
    """Busca si el texto contiene alguna pregunta del diccionario (coincidencia flexible)"""
    texto_normalizado = normalizar_texto(texto)
    palabras_texto = set(extraer_palabras_clave(texto))
    
    mejor_coincidencia = None
    mejor_score = 0
    mejor_key = None
    
    for key in DICCIONARIO:
        key_normalizado = normalizar_texto(key)
        
        # Quitar el número de la pregunta (ej: "1. ¿Cuál..." -> "¿Cuál...")
        if '. ' in key_normalizado:
            pregunta_sin_numero = key_normalizado.split('. ', 1)[-1]
        else:
            pregunta_sin_numero = key_normalizado
        
        # MÉTODO 1: Coincidencia exacta (la pregunta está en el texto)
        if pregunta_sin_numero in texto_normalizado:
            if len(pregunta_sin_numero) > mejor_score:
                mejor_score = len(pregunta_sin_numero)
                mejor_coincidencia = DICCIONARIO[key]
                mejor_key = key
            continue
        
        # MÉTODO 2: Coincidencia por palabras clave (para cuando OCR omite palabras)
        palabras_pregunta = set(extraer_palabras_clave(pregunta_sin_numero))
        if len(palabras_pregunta) >= 3:
            # Calcular cuántas palabras coinciden
            coincidencias = palabras_texto & palabras_pregunta
            # Si coinciden al menos 70% de las palabras de la pregunta
            porcentaje = len(coincidencias) / len(palabras_pregunta)
            if porcentaje >= 0.7:
                score = len(coincidencias) * 10  # Dar peso a las coincidencias
                if score > mejor_score:
                    mejor_score = score
                    mejor_coincidencia = DICCIONARIO[key]
                    mejor_key = key
    
    return mejor_coincidencia, mejor_key


@csrf_exempt
def consultar_gemini_imagen(request):
    if request.method == 'POST':
        print("\n" + "="*60)
        print("📸 NUEVA SOLICITUD DE IMAGEN")
        print("="*60)
        
        data = json.loads(request.body)
        device_id = data.get('device_id', '').strip()
        imagen_base64 = data.get('imagen', '').strip()
        api_key = data.get('api_key', '').strip()
        
        print(f"🔑 Device ID: {device_id[:20]}...")
        
        # Verificar activación
        try:
            activation_key = ActivationKey.objects.get(device_id=device_id, is_active=True)
            activation_key.last_used = datetime.now()
            activation_key.save()
            print("✅ Dispositivo verificado")
        except ActivationKey.DoesNotExist:
            print("❌ Dispositivo NO activado")
            return JsonResponse({'error': 'Dispositivo no activado'}, status=403)
        
        if not api_key:
            print("❌ API key no proporcionada")
            return JsonResponse({'error': 'API key de Gemini requerida'}, status=400)
        
        if not imagen_base64:
            print("❌ Imagen no proporcionada")
            return JsonResponse({'error': 'Imagen requerida'}, status=400)
        
        try:
            # Remover el prefijo data:image/...;base64, si existe
            if ',' in imagen_base64:
                imagen_base64 = imagen_base64.split(',')[1]
            
            imagen_bytes = base64.b64decode(imagen_base64)
            print(f"📦 Imagen recibida: {len(imagen_bytes)} bytes")
            
            # OCR: extraer texto de la imagen
            print("🔍 Ejecutando OCR...")
            imagen = Image.open(BytesIO(imagen_bytes))
            print(f"📐 Dimensiones: {imagen.size[0]}x{imagen.size[1]} px")
            
            texto_extraido = pytesseract.image_to_string(imagen, lang='spa+eng')
            
            print("\n📝 TEXTO EXTRAÍDO:")
            print("-"*40)
            print(texto_extraido[:500] if len(texto_extraido) > 500 else texto_extraido)
            if len(texto_extraido) > 500:
                print(f"... ({len(texto_extraido)} caracteres totales)")
            print("-"*40)
            
            if not texto_extraido.strip():
                print("❌ No se extrajo texto de la imagen")
                return JsonResponse({'error': 'No se pudo extraer texto de la imagen', 'success': False}, status=400)
            
            # PRIMERO: Buscar en el diccionario
            print("📚 Buscando en diccionario...")
            respuesta_diccionario, pregunta_encontrada = buscar_en_diccionario(texto_extraido)
            
            if respuesta_diccionario:
                print("✅ ¡ENCONTRADO EN DICCIONARIO!")
                print(f"📌 Pregunta: {pregunta_encontrada[:80]}...")
                print(f"🎯 Respuesta: {respuesta_diccionario}")
                print("="*60 + "\n")
                
                # Formatear respuesta igual que en /buscar/
                if isinstance(respuesta_diccionario, list) and len(respuesta_diccionario) >= 2:
                    respuesta_texto = f"Opción {respuesta_diccionario[0]}: {respuesta_diccionario[1]}"
                else:
                    respuesta_texto = str(respuesta_diccionario)
                
                return JsonResponse({
                    'respuesta': f"📚 {respuesta_texto}",
                    'success': True,
                    'source': 'diccionario'
                })
            
            print("❌ No encontrado en diccionario, consultando Gemini...")
            
            # SEGUNDO: Si no está en diccionario, consultar Gemini
            print("🤖 Enviando a Gemini...")
            client = genai.Client(api_key=api_key)
            
            prompt = f"""Pregunta de examen Cisco CCNA extraída de una captura:

{texto_extraido}

Responde de forma MUY breve y directa (máximo 2-3 líneas).
- Si es opción múltiple: indica el número de la opción correcta.
- Si es de unir/emparejar: indica qué va con qué.
- Si es de arrastrar: indica el orden o la ubicación correcta.
Solo da la respuesta, sin explicaciones largas."""
            
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=prompt
            )
            
            print("\n🎯 RESPUESTA GEMINI:")
            print("-"*40)
            print(response.text)
            print("-"*40)
            print("✅ Solicitud completada exitosamente")
            print("="*60 + "\n")
            
            return JsonResponse({
                'respuesta': response.text,
                'success': True,
                'source': 'gemini'
            })
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            print("="*60 + "\n")
            return JsonResponse({'error': str(e), 'success': False}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)