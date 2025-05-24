import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

DICCIONARIO = {
    "Una PC puede tener acceso a los dispositivos en la misma red, pero no puede tener acceso a los dispositivos en otras redes. ¿Cuál es la causa probable de este problema?":
        [2, "La dirección de gateway predeterminado de la PC no es válida."],
    "¿Cuál de estas afirmaciones describe una característica del Protocolo IP?":
        [4, "IP utiliza los servicios de capa superior para manejar situaciones de paquetes faltantes o fuera de orden."],
    "¿Por qué no se necesita NAT en IPv6?":
        [1, "Cualquier host o usuario puede obtener una dirección de red IPv6 pública porque la cantidad de direcciones IPv6 disponibles es extremadamente grande."],
    "¿Cuál de estos parámetros utiliza el router para elegir la ruta hacia el destino cuando existen varias rutas disponibles?":
        [4, "El valor de métrica más bajo que se asocia a la red de destino."],
    "¿Cuáles de los siguientes son dos servicios que proporciona la capa de red OSI? Elija dos opciones.":
        [1,4,"Encapsulamiento de PDU de la capa de transporte", "Routing de paquetes hacia el destino"]
}

@csrf_exempt
def buscar(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        pregunta = data.get('pregunta', '').strip()
        respuesta = DICCIONARIO.get(pregunta, "❌ Pregunta no encontrada.")
        return JsonResponse({'respuesta': respuesta})
    return JsonResponse({'error': 'Método no permitido'}, status=405)