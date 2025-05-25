from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import re

chrome_options = Options()
chrome_options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=chrome_options)
driver.get("https://examenredes.com/modulos-8-10-examen-de-comunicacion-entre-redes-respuestas/#goog_rewarded")
time.sleep(15)  # Ajusta según tu conexión y carga de la página

contenedor = driver.find_element(By.CLASS_NAME, "entry")
elementos = contenedor.find_elements(By.XPATH, "./*")

preguntas_y_respuestas = []
pregunta_actual = None
preguntas_a_ignorar = {8, 17, 18, 19, 20, 24}

def extraer_numero_pregunta(texto):
    match = re.match(r'^(\d+)\.\s', texto)
    if match:
        return int(match.group(1))
    return None

for elemento in elementos:
    if elemento.tag_name == "p":
        strongs = elemento.find_elements(By.TAG_NAME, "strong")
        if strongs:
            texto_fuerte = strongs[0].text.strip()
            numero_pregunta = extraer_numero_pregunta(texto_fuerte)

            # Guardar pregunta anterior si es válida y existe
            if pregunta_actual:
                if pregunta_actual["correctas"]:  # Solo si tiene respuestas correctas
                    preguntas_y_respuestas.append(pregunta_actual)

            if numero_pregunta is None or numero_pregunta in preguntas_a_ignorar:
                pregunta_actual = None  # Saltamos esta pregunta
            else:
                pregunta_actual = {
                    "numero": numero_pregunta,
                    "pregunta": texto_fuerte,
                    "correctas": [],   # textos correctos
                    "correctas_idx": []  # índices correctos (1-based)
                }

    elif elemento.tag_name == "ul" and pregunta_actual:
        respuestas = elemento.find_elements(By.TAG_NAME, "li")
        for idx, r in enumerate(respuestas, start=1):
            if "correct_answer" in (r.get_attribute("class") or ""):
                texto = r.text.strip()
                pregunta_actual["correctas"].append(texto)
                pregunta_actual["correctas_idx"].append(idx)

# Guardar la última pregunta válida
if pregunta_actual and pregunta_actual["correctas"]:
    preguntas_y_respuestas.append(pregunta_actual)

# Mostrar resultados
for q in preguntas_y_respuestas:
    print(f"--- Pregunta {q['numero']} ---")
    print("Pregunta:", q["pregunta"])
    print("Respuestas correctas (números):", ', '.join(map(str, q["correctas_idx"])))
    print("Respuestas correctas (texto):")
    for c in q["correctas"]:
        print(" *", c)
    print()

# ... tu código original arriba sin cambios ...

# Al final, generamos el diccionario dinámico según el formato solicitado:

DICCIONARIO = {}

for q in preguntas_y_respuestas:
    pregunta_texto = q["pregunta"]
    correctas_idx = q["correctas_idx"]
    correctas_textos = q["correctas"]

    if len(correctas_idx) == 1:
        # Solo 1 respuesta correcta, valor es [número, texto]
        DICCIONARIO[pregunta_texto] = [correctas_idx[0], correctas_textos[0]]
    else:
        # Más de 1 correcta, valor es ["1, 4", "texto1 y texto2"]
        indices_str = ', '.join(map(str, correctas_idx))
        # Unimos los textos separados por punto y espacio para que se entienda mejor
        texto_union = '. '.join(correctas_textos)
        DICCIONARIO[pregunta_texto] = [indices_str, texto_union]

import pprint
print("\nDICCIONARIO = ")
pprint.pprint(DICCIONARIO, width=120)

import json

# Al final, luego de construir DICCIONARIO
with open('diccionario.json', 'w', encoding='utf-8') as f:
    json.dump(DICCIONARIO, f, ensure_ascii=False, indent=2)

driver.quit()



driver.quit()
