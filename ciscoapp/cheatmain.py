import json
import os
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ActivationKey

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
        else:
            coincidencias = [DICCIONARIO[key] for key in DICCIONARIO if pregunta in key.lower()]
            if coincidencias:
                respuesta = coincidencias[0]
            else:
                respuesta = "❌ Pregunta no encontrada."

        return JsonResponse({'respuesta': respuesta})

    return JsonResponse({'error': 'Método no permitido'}, status=405)