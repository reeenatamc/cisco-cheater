import json
import os

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(BASE_DIR, 'diccionario.json')

with open(json_path, encoding='utf-8') as f:
    DICCIONARIO = json.load(f)

@csrf_exempt
def buscar(request):
    if request.method == 'POST':
        data = json.loads(request.body)
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