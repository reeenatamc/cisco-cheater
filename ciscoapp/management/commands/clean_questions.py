from django.core.management.base import BaseCommand
import json
import os

class Command(BaseCommand):
    help = 'Clean diccionario.json by replacing the first element of each answer with a space'

    def handle(self, *args, **options):
        # Path to diccionario.json
        diccionario_path = os.path.join(os.path.dirname(__file__), '..', '..', 'diccionario.json')
        
        try:
            # Load dictionary from JSON file
            with open(diccionario_path, 'r', encoding='utf-8') as f:
                preguntas = json.load(f)
            
            self.stdout.write(f'Loaded dictionary with {len(preguntas)} questions')
            
            # Replace first element of each answer with a space
            for key in preguntas:
                preguntas[key][0] = " "
            
            # Save modified dictionary back to file
            with open(diccionario_path, 'w', encoding='utf-8') as f:
                json.dump(preguntas, f, ensure_ascii=False, indent=2)
            
            self.stdout.write(
                self.style.SUCCESS(f'Dictionary cleaned successfully. {len(preguntas)} questions processed.')
            )
            
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR('File diccionario.json not found')
            )
        except json.JSONDecodeError:
            self.stdout.write(
                self.style.ERROR('Error decoding JSON file')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Unexpected error: {str(e)}')
            )