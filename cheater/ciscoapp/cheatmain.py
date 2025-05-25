import json
import os

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Ruta absoluta al archivo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Esto apunta a ciscoapp/
json_path = os.path.join(BASE_DIR, 'diccionario.json')

# Cargar el diccionario
with open(json_path, encoding='utf-8') as f:
    DICCIONARIO = json.load(f)

@csrf_exempt
def buscar(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        pregunta = data.get('pregunta', '').strip()
        respuesta = DICCIONARIO.get(pregunta, "❌ Pregunta no encontrada.")
        return JsonResponse({'respuesta': respuesta})
    return JsonResponse({'error': 'Método no permitido'}, status=405)