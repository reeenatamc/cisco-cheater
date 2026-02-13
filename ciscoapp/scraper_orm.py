"""
Scraper ORM - Guarda preguntas directamente en la base de datos usando modelos Django.
Sigue EXACTAMENTE la misma lógica de extracción que scraper.py.
"""

import os
import sys
import django
import re
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cheater.settings')
django.setup()

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from ciscoapp.models import Examen, Pregunta, Respuesta


def extraer_numero_pregunta(texto):
    """Extrae el número de pregunta usando regex r'^(\d+)\.\s'"""
    match = re.match(r'^(\d+)\.\s', texto)
    if match:
        return int(match.group(1))
    return None


def scrapear_examen(url, nombre_examen, preguntas_a_ignorar=None, espera_inicial=15):
    """
    Scrapea un examen de examenredes.com y guarda directamente en BD.
    
    Args:
        url: URL del examen a scrapear
        nombre_examen: Nombre descriptivo del examen (ej: "Módulos 8-10")
        preguntas_a_ignorar: Set de números de preguntas a ignorar (las de unir/arrastrar)
        espera_inicial: Segundos de espera inicial después de cargar la página
    """
    if preguntas_a_ignorar is None:
        preguntas_a_ignorar = set()
    
    # Crear o recuperar el Examen
    examen, created = Examen.objects.get_or_create(
        nombre=nombre_examen,
        defaults={'url_fuente': url}
    )
    if created:
        print(f"✓ Examen creado: {nombre_examen}")
    else:
        print(f"✓ Examen existente: {nombre_examen}")
    
    # Configurar Selenium
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Navegar y esperar
        print(f"Navegando a {url}...")
        driver.get(url)
        print(f"Esperando {espera_inicial} segundos...")
        time.sleep(espera_inicial)
        
        # Buscar contenedor entry
        contenedor = driver.find_element(By.CLASS_NAME, "entry")
        elementos = contenedor.find_elements(By.XPATH, "./*")
        
        preguntas_y_respuestas = []
        pregunta_actual = None
        
        # Extraer preguntas y respuestas (misma lógica que scraper.py)
        for elemento in elementos:
            if elemento.tag_name == "p":
                strongs = elemento.find_elements(By.TAG_NAME, "strong")
                if strongs:
                    texto_fuerte = strongs[0].text.strip()
                    numero_pregunta = extraer_numero_pregunta(texto_fuerte)
                    
                    # Guardar pregunta anterior si existe
                    if pregunta_actual:
                        if pregunta_actual["correctas"]:
                            preguntas_y_respuestas.append(pregunta_actual)
                    
                    # Ignorar preguntas en la lista (las de unir/arrastrar)
                    if numero_pregunta is None or numero_pregunta in preguntas_a_ignorar:
                        pregunta_actual = None
                    else:
                        pregunta_actual = {
                            "numero": numero_pregunta,
                            "pregunta": texto_fuerte,
                            "correctas": [],
                            "correctas_idx": []
                        }
            
            elif elemento.tag_name == "ul" and pregunta_actual:
                respuestas = elemento.find_elements(By.TAG_NAME, "li")
                for idx, r in enumerate(respuestas, start=1):
                    if "correct_answer" in (r.get_attribute("class") or ""):
                        texto = r.text.strip()
                        pregunta_actual["correctas"].append(texto)
                        pregunta_actual["correctas_idx"].append(idx)
        
        # No olvidar la última pregunta
        if pregunta_actual and pregunta_actual["correctas"]:
            preguntas_y_respuestas.append(pregunta_actual)
        
        print(f"\n✓ Scraping completado. Total preguntas encontradas: {len(preguntas_y_respuestas)}")
        
        # Guardar en la base de datos
        for q in preguntas_y_respuestas:
            numero = q["numero"]
            texto = q["pregunta"]
            correctas_idx = q["correctas_idx"]
            correctas_textos = q["correctas"]
            
            # Determinar tipo
            if len(correctas_idx) == 1:
                tipo = 'opcion_simple'
            else:
                tipo = 'opcion_multiple'
            
            # Crear o actualizar pregunta
            pregunta_obj, created = Pregunta.objects.update_or_create(
                examen=examen,
                numero=numero,
                defaults={
                    'texto': texto,
                    'tipo': tipo,
                    'es_manual': False
                }
            )
            
            # Borrar respuestas anteriores y crear nuevas
            pregunta_obj.respuestas.all().delete()
            
            for idx, texto_resp in zip(correctas_idx, correctas_textos):
                Respuesta.objects.create(
                    pregunta=pregunta_obj,
                    texto=texto_resp,
                    indice=idx
                )
            
            action = "creada" if created else "actualizada"
            print(f"  Pregunta {numero} {action}: {tipo} con {len(correctas_idx)} respuesta(s)")
        
        print(f"\n✓✓ Proceso completado exitosamente! ✓✓")
        
    finally:
        driver.quit()


# Ejemplo de uso
if __name__ == "__main__":
    # Ejemplo: scrapear módulos 1-4
    scrapear_examen(
        url="https://examenredes.com/modulos-1-4-examen-de-conceptos-de-conmutacion-vlan-y-enrutamiento-entre-vlan-respuestas/",
        nombre_examen="Módulos 1-4",
        preguntas_a_ignorar={46, 40, 33},  # Preguntas de unir/arrastrar
        espera_inicial=15
    )
