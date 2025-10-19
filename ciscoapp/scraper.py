# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# import time
# import re
# import json
#
#
# chrome_options = Options()
# chrome_options.add_argument("--start-maximized")
#
# driver = webdriver.Chrome(options=chrome_options)
# driver.get("https://examenredes.com/modulos-8-10-examen-de-comunicacion-entre-redes-respuestas/#goog_rewarded")
# time.sleep(15)  # Ajusta según tu conexión y carga de la pagina. Yo lo pongo por el anuncio!
#
# contenedor = driver.find_element(By.CLASS_NAME, "entry")
# elementos = contenedor.find_elements(By.XPATH, "./*")
#
# preguntas_y_respuestas = []
# pregunta_actual = None
# preguntas_a_ignorar = {8, 17, 18, 19, 20, 24}
#
# def extraer_numero_pregunta(texto):
#     match = re.match(r'^(\d+)\.\s', texto)
#     if match:
#         return int(match.group(1))
#     return None
#
# for elemento in elementos:
#     if elemento.tag_name == "p":
#         strongs = elemento.find_elements(By.TAG_NAME, "strong")
#         if strongs:
#             texto_fuerte = strongs[0].text.strip()
#             numero_pregunta = extraer_numero_pregunta(texto_fuerte)
#
#             if pregunta_actual:
#                 if pregunta_actual["correctas"]:
#                     preguntas_y_respuestas.append(pregunta_actual)
#
#             if numero_pregunta is None or numero_pregunta in preguntas_a_ignorar:
#                 pregunta_actual = None
#             else:
#                 pregunta_actual = {
#                     "numero": numero_pregunta,
#                     "pregunta": texto_fuerte,
#                     "correctas": [],
#                     "correctas_idx": []
#                 }
#
#     elif elemento.tag_name == "ul" and pregunta_actual:
#         respuestas = elemento.find_elements(By.TAG_NAME, "li")
#         for idx, r in enumerate(respuestas, start=1):
#             if "correct_answer" in (r.get_attribute("class") or ""):
#                 texto = r.text.strip()
#                 pregunta_actual["correctas"].append(texto)
#                 pregunta_actual["correctas_idx"].append(idx)
#
# if pregunta_actual and pregunta_actual["correctas"]:
#     preguntas_y_respuestas.append(pregunta_actual)
#
# for q in preguntas_y_respuestas:
#     print(f"--- Pregunta {q['numero']} ---")
#     print("Pregunta:", q["pregunta"])
#     print("Respuestas correctas (números):", ', '.join(map(str, q["correctas_idx"])))
#     print("Respuestas correctas (texto):")
#     for c in q["correctas"]:
#         print(" *", c)
#     print()
#
# DICCIONARIO = {}
#
# for q in preguntas_y_respuestas:
#     pregunta_texto = q["pregunta"]
#     correctas_idx = q["correctas_idx"]
#     correctas_textos = q["correctas"]
#
#     if len(correctas_idx) == 1:
#         DICCIONARIO[pregunta_texto] = [correctas_idx[0], correctas_textos[0]]
#     else:
#         indices_str = ', '.join(map(str, correctas_idx))
#         texto_union = '. '.join(correctas_textos)
#         DICCIONARIO[pregunta_texto] = [indices_str, texto_union]
#
# import pprint
# print("\nDICCIONARIO = ")
# pprint.pprint(DICCIONARIO, width=120)
#
#
# with open('diccionario.json', 'w', encoding='utf-8') as f:
#     json.dump(DICCIONARIO, f, ensure_ascii=False, indent=2)
#
# driver.quit()

import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import re
import json
import pprint

chrome_options = Options()
chrome_options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=chrome_options)
driver.get("https://examenredes.com/modulos-1-4-examen-de-conceptos-de-conmutacion-vlan-y-enrutamiento-entre-vlan-respuestas/")
# driver.get("https://examenredes.com/examen-de-punto-de-control-direccionamiento-ip/")

time.sleep(15)  # Ajusta según tu conexión y carga de la pagina

contenedor = driver.find_element(By.CLASS_NAME, "entry")
elementos = contenedor.find_elements(By.XPATH, "./*")

preguntas_y_respuestas = []
pregunta_actual = None
preguntas_a_ignorar = {46, 40, 33}
# preguntas_a_ignorar = {1, 5, 11}


def extraer_numero_pregunta(texto):
    match = re.match(r'^(\d+)\.\s', texto)
    if match:
        return int(match.group(1))
    return None

# Extraer preguntas y respuestas
for elemento in elementos:
    if elemento.tag_name == "p":
        strongs = elemento.find_elements(By.TAG_NAME, "strong")
        if strongs:
            texto_fuerte = strongs[0].text.strip()
            numero_pregunta = extraer_numero_pregunta(texto_fuerte)

            if pregunta_actual:
                if pregunta_actual["correctas"]:
                    preguntas_y_respuestas.append(pregunta_actual)

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

if pregunta_actual and pregunta_actual["correctas"]:
    preguntas_y_respuestas.append(pregunta_actual)

# --- Cargar JSON existente (si existe) ---
diccionario_path = 'diccionario.json'
if os.path.exists(diccionario_path):
    with open(diccionario_path, 'r', encoding='utf-8') as f:
        DICCIONARIO = json.load(f)
else:
    DICCIONARIO = {}

# --- Función para comparar preguntas y respuestas correctas ---
def pregunta_ya_existe(pregunta, correctas_idx, correctas_textos):
    if pregunta not in DICCIONARIO:
        return False
    valor = DICCIONARIO[pregunta]
    if len(correctas_idx) == 1:
        # caso de una sola respuesta correcta
        return valor == [correctas_idx[0], correctas_textos[0]]
    else:
        indices_str = ', '.join(map(str, correctas_idx))
        texto_union = '. '.join(correctas_textos)
        return valor == [indices_str, texto_union]

# --- Añadir preguntas nuevas solo si no existen ---
for q in preguntas_y_respuestas:
    pregunta_texto = q["pregunta"]
    correctas_idx = q["correctas_idx"]
    correctas_textos = q["correctas"]

    if not pregunta_ya_existe(pregunta_texto, correctas_idx, correctas_textos):
        if len(correctas_idx) == 1:
            DICCIONARIO[pregunta_texto] = [correctas_idx[0], correctas_textos[0]]
        else:
            indices_str = ', '.join(map(str, correctas_idx))
            texto_union = '. '.join(correctas_textos)
            DICCIONARIO[pregunta_texto] = [indices_str, texto_union]

print("\nDICCIONARIO ACTUALIZADO = ")
pprint.pprint(DICCIONARIO, width=120)

with open(diccionario_path, 'w', encoding='utf-8') as f:
    json.dump(DICCIONARIO, f, ensure_ascii=False, indent=2)

driver.quit()
