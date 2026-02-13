import json
from datetime import datetime
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import ActivationKey, Pregunta


def home(request):
    return render(request, 'you_never_gonna_catch_me.html')

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

        pregunta_texto = data.get('pregunta', '').strip()
        
        # Búsqueda: primero exacta (case-insensitive), luego parcial
        pregunta_obj = Pregunta.objects.filter(texto__iexact=pregunta_texto).first()
        if not pregunta_obj:
            pregunta_obj = Pregunta.objects.filter(texto__icontains=pregunta_texto).first()
        
        if not pregunta_obj:
            return JsonResponse({
                'respuesta': '❌ Pregunta no encontrada.',
                'found': False
            })
        
        # Formatear respuesta según el tipo de pregunta
        if pregunta_obj.tipo == 'unir':
            # Preguntas de tipo unir: devolver pares
            pares = []
            for par in pregunta_obj.pares.all():
                pares.append({
                    'izquierda': par.elemento_izquierdo,
                    'derecha': par.elemento_derecho
                })
            
            return JsonResponse({
                'respuesta': {
                    'tipo': 'unir',
                    'pregunta_numero': pregunta_obj.numero,
                    'pares': pares
                },
                'found': True
            })
        
        elif pregunta_obj.tipo == 'opcion_simple':
            # Una sola respuesta: formato [indice, texto]
            respuesta = pregunta_obj.respuestas.first()
            if respuesta:
                return JsonResponse({
                    'respuesta': [respuesta.indice, respuesta.texto],
                    'found': True
                })
        
        elif pregunta_obj.tipo == 'opcion_multiple':
            # Múltiples respuestas: formato ["idx1, idx2", "texto1. texto2"]
            respuestas = pregunta_obj.respuestas.all().order_by('indice')
            indices = [str(r.indice) for r in respuestas]
            textos = [r.texto for r in respuestas]
            
            indices_str = ', '.join(indices)
            textos_str = '. '.join(textos)
            
            return JsonResponse({
                'respuesta': [indices_str, textos_str],
                'found': True
            })
        
        # Fallback si no hay respuestas
        return JsonResponse({
            'respuesta': '❌ Pregunta no encontrada.',
            'found': False
        })

    return JsonResponse({'error': 'Método no permitido'}, status=405)