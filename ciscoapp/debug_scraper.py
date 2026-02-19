"""
Script de debug para ver la estructura de preguntas 1-14
Sin guardar nada, solo para inspeccionar
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re

# Configurar Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)

# URL de la página (misma que usa el scraper principal)
URL = "https://examenredes.com/ccna-1-examen-final-itnv7-preguntas-y-respuestas/"

print(f"Cargando: {URL}")
driver.get(URL)
time.sleep(15)  # Esperar a que cargue completamente

# Obtener todos los elementos relevantes (mismo selector que scraper.py)
contenedor = driver.find_element(By.CLASS_NAME, "entry")
elementos = contenedor.find_elements(By.XPATH, "./*")

print(f"\nTotal elementos: {len(elementos)}")
print("=" * 80)

# Simular el scraper con la nueva lógica para preguntas 12-15
print("\n--- SIMULACIÓN DEL SCRAPER CORREGIDO (preguntas 12-15) ---\n")

pregunta_actual = None
resultados = []

for i, elem in enumerate(elementos):
    tag = elem.tag_name
    texto = elem.text.strip() if elem.text else ""
    
    # NUEVO: Detectar <strong> directo
    if tag == "strong":
        match = re.match(r'^\_?(\d+)\.\s', texto)
        if match:
            num = int(match.group(1))
            if 12 <= num <= 15:
                if pregunta_actual:
                    resultados.append(pregunta_actual)
                pregunta_actual = {"num": num, "texto": texto[:80], "correctas": [], "elem": i}
                print(f"\n📌 PREGUNTA {num} detectada en <STRONG> (elem #{i})")
                print(f"   {texto[:70]}...")
        continue
    
    # Detectar <p> con pregunta
    if tag == "p":
        strongs = elem.find_elements(By.TAG_NAME, "strong")
        texto_strong = strongs[0].text.strip() if strongs else ""
        match = re.match(r'^\_?(\d+)\.\s', texto_strong) or re.match(r'^\_?(\d+)\.\s', texto)
        
        if match:
            num = int(match.group(1))
            if 12 <= num <= 15:
                if pregunta_actual:
                    resultados.append(pregunta_actual)
                pregunta_actual = {"num": num, "texto": texto[:80], "correctas": [], "elem": i}
                print(f"\n📌 PREGUNTA {num} detectada en <P> (elem #{i})")
                print(f"   {texto[:70]}...")
            elif num > 15:
                break
        continue
    
    # Procesar <ul> - SOLO si pregunta_actual no tiene respuestas aún
    if tag == "ul" and pregunta_actual and pregunta_actual["num"] <= 15:
        # FIX: Si ya tiene respuestas, ignorar este UL
        if pregunta_actual["correctas"]:
            print(f"   ⚠️  UL #{i} IGNORADO (pregunta {pregunta_actual['num']} ya tiene respuestas)")
            continue
        
        lis = elem.find_elements(By.TAG_NAME, "li")
        for li in lis:
            if "correct_answer" in (li.get_attribute("class") or ""):
                pregunta_actual["correctas"].append(li.text.strip()[:40])
        
        print(f"   📋 UL #{i}: {len(pregunta_actual['correctas'])} correctas asignadas a pregunta {pregunta_actual['num']}")

# Guardar última
if pregunta_actual:
    resultados.append(pregunta_actual)

print("\n" + "=" * 70)
print("RESUMEN:")
for r in resultados:
    print(f"  Pregunta {r['num']}: {len(r['correctas'])} respuestas correctas")
    for c in r['correctas']:
        print(f"    ✅ {c}...")

driver.quit()
