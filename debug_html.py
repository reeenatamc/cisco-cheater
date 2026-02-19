"""
Script para depurar una pregunta específica del scraper
"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# URL del examen
EXAM_URL = input("URL del examen: ")
PREGUNTA_NUM = input("Número de pregunta a inspeccionar: ")

opts = Options()
opts.add_argument("--start-maximized")
driver = webdriver.Chrome(options=opts)

try:
    print(f"\n🌐 Navegando a: {EXAM_URL}")
    driver.get(EXAM_URL)
    print(f"⏳ Esperando 15 segundos...")
    time.sleep(15)
    
    contenedor = driver.find_element(By.CLASS_NAME, "entry")
    elementos = contenedor.find_elements(By.XPATH, "./*")
    
    print(f"\n📦 Total elementos: {len(elementos)}")
    print(f"\nBuscando pregunta #{PREGUNTA_NUM}...\n")
    
    encontrada = False
    for idx, elemento in enumerate(elementos):
        tag = elemento.tag_name
        
        # Buscar pregunta con el número
        if tag == "p":
            strongs = elemento.find_elements(By.TAG_NAME, "strong")
            if strongs:
                texto = strongs[0].text.strip()
                if texto.startswith(f"{PREGUNTA_NUM}."):
                    encontrada = True
                    print(f"✓ PREGUNTA ENCONTRADA en índice {idx}")
                    print(f"  Tag: {tag}")
                    print(f"  Texto: {texto}")
                    print(f"\n  Siguientes 10 elementos:")
                    
                    for i in range(idx, min(idx + 10, len(elementos))):
                        elem = elementos[i]
                        print(f"\n    [{i - idx}] Tag: {elem.tag_name}")
                        if elem.tag_name == "ul":
                            lis = elem.find_elements(By.TAG_NAME, "li")
                            print(f"        Items <li>: {len(lis)}")
                            for j, li in enumerate(lis[:5]):  # Máximo 5
                                classes = li.get_attribute("class") or ""
                                is_correct = "correct_answer" in classes
                                texto_li = li.text.strip()[:80]
                                correcta = "✓ CORRECTA" if is_correct else ""
                                print(f"        [{j+1}] {correcta} Class: '{classes}'")
                                print(f"            Texto: {texto_li}")
                        elif elem.tag_name == "p":
                            texto_p = elem.text.strip()[:100]
                            print(f"        Texto: {texto_p}")
                        elif elem.tag_name == "div":
                            imgs = elem.find_elements(By.TAG_NAME, "img")
                            if imgs:
                                print(f"        Contiene {len(imgs)} imagen(es)")
                        else:
                            print(f"        Texto: {elem.text.strip()[:60]}")
                    
                    break
    
    if not encontrada:
        print(f"❌ Pregunta #{PREGUNTA_NUM} NO encontrada")
    
    input("\n\nPresiona Enter para cerrar el navegador...")
    
finally:
    driver.quit()
