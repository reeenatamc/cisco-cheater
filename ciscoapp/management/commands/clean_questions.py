from django.core.management.base import BaseCommand
import json
import os

class Command(BaseCommand):
    help = 'Limpia el archivo diccionario.json reemplazando el primer elemento de cada respuesta con un espacio'

    def handle(self, *args, **options):
        # Ruta al archivo diccionario.json
        diccionario_path = os.path.join(os.path.dirname(__file__), '..', '..', 'diccionario.json')
        
        try:
            # Cargar el diccionario desde el archivo JSON
            with open(diccionario_path, 'r', encoding='utf-8') as f:
                preguntas = json.load(f)
            
            self.stdout.write(f'Cargado diccionario con {len(preguntas)} preguntas')
            
            # Modificar el primer elemento de cada respuesta para que sea un espacio
            for key in preguntas:
                preguntas[key][0] = " "
            
            # Guardar el diccionario modificado de vuelta al archivo
            with open(diccionario_path, 'w', encoding='utf-8') as f:
                json.dump(preguntas, f, ensure_ascii=False, indent=2)
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Diccionario limpiado exitosamente. {len(preguntas)} preguntas procesadas.')
            )
            
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR('❌ No se encontró el archivo diccionario.json')
            )
        except json.JSONDecodeError:
            self.stdout.write(
                self.style.ERROR('❌ Error al decodificar el archivo JSON')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error inesperado: {str(e)}')
            )