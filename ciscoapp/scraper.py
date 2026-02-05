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

# import os
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# import time
# import re
# import json
# import pprint
#
# chrome_options = Options()
# chrome_options.add_argument("--start-maximized")
#
# driver = webdriver.Chrome(options=chrome_options)
# driver.get("https://examenredes.com/ccna-2-v7-examen-final-de-srwe-preguntas-y-respuestas/")
# # driver.get("https://examenredes.com/examen-de-punto-de-control-direccionamiento-ip/")
#
# time.sleep(15)  # Ajusta según tu conexión y carga de la pagina
#
# contenedor = driver.find_element(By.CLASS_NAME, "entry")
# elementos = contenedor.find_elements(By.XPATH, "./*")
#
# preguntas_y_respuestas = []
# pregunta_actual = None
# preguntas_a_ignorar = {3, 19, 26, 54, 56, 59, 126, }
# # preguntas_a_ignorar = {1, 5, 11}
#
#
# def extraer_numero_pregunta(texto):
#     match = re.match(r'^(\d+)\.\s', texto)
#     if match:
#         return int(match.group(1))
#     return None
#
# # Extraer preguntas y respuestas
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
# # --- Cargar JSON existente (si existe) ---
# diccionario_path = 'diccionario.json'
# if os.path.exists(diccionario_path):
#     with open(diccionario_path, 'r', encoding='utf-8') as f:
#         DICCIONARIO = json.load(f)
# else:
#     DICCIONARIO = {}
#
# # --- Función para comparar preguntas y respuestas correctas ---
# def pregunta_ya_existe(pregunta, correctas_idx, correctas_textos):
#     if pregunta not in DICCIONARIO:
#         return False
#     valor = DICCIONARIO[pregunta]
#     if len(correctas_idx) == 1:
#         # caso de una sola respuesta correcta
#         return valor == [correctas_idx[0], correctas_textos[0]]
#     else:
#         indices_str = ', '.join(map(str, correctas_idx))
#         texto_union = '. '.join(correctas_textos)
#         return valor == [indices_str, texto_union]
#
# # --- Añadir preguntas nuevas solo si no existen ---
# for q in preguntas_y_respuestas:
#     pregunta_texto = q["pregunta"]
#     correctas_idx = q["correctas_idx"]
#     correctas_textos = q["correctas"]
#
#     if not pregunta_ya_existe(pregunta_texto, correctas_idx, correctas_textos):
#         if len(correctas_idx) == 1:
#             DICCIONARIO[pregunta_texto] = [correctas_idx[0], correctas_textos[0]]
#         else:
#             indices_str = ', '.join(map(str, correctas_idx))
#             texto_union = '. '.join(correctas_textos)
#             DICCIONARIO[pregunta_texto] = [indices_str, texto_union]
#
# print("\nDICCIONARIO ACTUALIZADO = ")
# pprint.pprint(DICCIONARIO, width=120)
#
# with open(diccionario_path, 'w', encoding='utf-8') as f:
#     json.dump(DICCIONARIO, f, ensure_ascii=False, indent=2)
#
# driver.quit()

import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import re
import json
import pprint

chrome_options = Options()
chrome_options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=chrome_options)
driver.get("https://examenredes.com/ccna-1-examen-final-itnv7-preguntas-y-respuestas/")

time.sleep(15)  # Ajusta según tu conexión y carga de la página

contenedor = driver.find_element(By.CLASS_NAME, "entry")
elementos = contenedor.find_elements(By.XPATH, "./*")

preguntas_y_respuestas = []
pregunta_actual = None
preguntas_a_ignorar = set()  # Se determinarán dinámicamente basándose en si solo tienen imágenes
preguntas_solo_imagenes = []  # Lista para almacenar preguntas que solo tienen imágenes


def extraer_numero_pregunta(texto):
    """Extrae el número de pregunta, manejando casos con guion bajo"""
    match = re.match(r'^\_?(\d+)\.\s', texto)
    if match:
        return int(match.group(1))
    return None


def normalizar_texto_pregunta(texto):
    """Normaliza el texto de la pregunta removiendo el guion bajo antes del número"""
    # Remover guion bajo antes del número si existe
    texto_normalizado = re.sub(r'^_(\d+\.\s)', r'\1', texto)
    return texto_normalizado


def tiene_solo_imagenes(elemento):
    """Verifica si un elemento contiene solo imágenes sin texto significativo"""
    try:
        # Buscar todas las imágenes en el elemento
        imagenes = elemento.find_elements(By.TAG_NAME, "img")
        texto = elemento.text.strip()
        
        # Si tiene imágenes y el texto está vacío o es muy corto, probablemente es solo imagen
        if imagenes and (not texto or len(texto) < 10):
            return True
        
        # Verificar si el HTML contiene solo imágenes
        html = elemento.get_attribute("outerHTML")
        # Si tiene imágenes pero no tiene texto con contenido, es solo imagen
        if imagenes and not re.search(r'[a-zA-ZáéíóúñÁÉÍÓÚÑ]{10,}', texto):
            return True
            
        return False
    except:
        return False


def extraer_respuestas_correctas(lista_elemento, pregunta_texto):
    """Extrae las respuestas correctas de una lista, verificando que tengan texto"""
    respuestas_correctas = []
    respuestas_idx = []
    
    try:
        items = lista_elemento.find_elements(By.TAG_NAME, "li")
        for idx, item in enumerate(items, start=1):
            if "correct_answer" in (item.get_attribute("class") or ""):
                texto = item.text.strip()
                
                # Verificar si la respuesta tiene solo imagen
                if tiene_solo_imagenes(item):
                    # Si todas las respuestas son solo imágenes, ignorar la pregunta completa
                    # Pero si solo algunas son imágenes, mantener las que tienen texto
                    continue
                
                if texto:  # Solo agregar si tiene texto
                    respuestas_correctas.append(texto)
                    respuestas_idx.append(idx)
    except:
        pass
    
    return respuestas_correctas, respuestas_idx


def es_caso_multiple(texto):
    """Verifica si el texto indica un caso múltiple (Caso 2, Caso 3, Otro caso 2, etc.)"""
    # Detecta: "Caso 2", "Caso 3", "Otro caso 2", "Otro Caso 3", etc.
    return re.match(r'^(Otro\s+)?Caso\s+\d+', texto, re.IGNORECASE) is not None


def extraer_numero_caso(texto):
    """Extrae el número del caso del texto"""
    match = re.search(r'(?:Otro\s+)?Caso\s+(\d+)', texto, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 1  # Si no encuentra, es el caso 1


# Procesar elementos
pregunta_base = None  # Para almacenar la pregunta base cuando hay casos múltiples

for i, elemento in enumerate(elementos):
    tag = elemento.tag_name
    
    # Manejar <strong> directo (algunas preguntas están en <strong> sin <p>)
    if tag == "strong":
        try:
            texto_pregunta = elemento.text.strip()
            numero_pregunta = extraer_numero_pregunta(texto_pregunta)
            
            if numero_pregunta is not None and texto_pregunta:
                # Si encontramos una nueva pregunta en <strong> directo
                # Guardar pregunta anterior si existe y tiene respuestas
                if pregunta_actual and pregunta_actual["correctas"]:
                    preguntas_y_respuestas.append(pregunta_actual)
                
                texto_pregunta_normalizado = normalizar_texto_pregunta(texto_pregunta)
                
                pregunta_actual = {
                    "numero": numero_pregunta,
                    "pregunta": texto_pregunta_normalizado,
                    "correctas": [],
                    "correctas_idx": [],
                    "caso": None
                }
                pregunta_base = {
                    "numero": numero_pregunta,
                    "pregunta": texto_pregunta_normalizado
                }
                print(f"[DEBUG] Pregunta {numero_pregunta} detectada en <strong> directo")
        except Exception as e:
            print(f"[DEBUG] Error procesando <strong>: {e}")
        continue
    
    if tag == "p":
        try:
            texto_pregunta = None
            numero_pregunta = None
            
            # Buscar texto fuerte (preguntas normales)
            strongs = elemento.find_elements(By.TAG_NAME, "strong")
            if strongs:
                texto_pregunta = strongs[0].text.strip()
                numero_pregunta = extraer_numero_pregunta(texto_pregunta)
            
            # Si no se encontró en <strong>, buscar directamente en el texto del párrafo
            # (para preguntas con guion bajo que pueden estar en <br> u otros elementos)
            if numero_pregunta is None:
                texto_elemento = elemento.text.strip()
                # Buscar si el texto completo del elemento contiene una pregunta
                numero_pregunta = extraer_numero_pregunta(texto_elemento)
                if numero_pregunta is not None:
                    # Extraer solo la parte que contiene la pregunta (antes del primer salto de línea o hasta el final)
                    lineas = texto_elemento.split('\n')
                    for linea in lineas:
                        num_temp = extraer_numero_pregunta(linea.strip())
                        if num_temp == numero_pregunta:
                            texto_pregunta = linea.strip()
                            break
                    # Si no se encontró en las líneas, usar todo el texto
                    if texto_pregunta is None:
                        texto_pregunta = texto_elemento
            
            # Si encontramos una pregunta (ya sea en <strong> o en el texto del elemento)
            if numero_pregunta is not None and texto_pregunta:
                # Verificar si es un caso múltiple (Caso 2, Caso 3, etc.)
                if es_caso_multiple(texto_pregunta):
                    # Si hay una pregunta actual con respuestas, guardarla antes de empezar un nuevo caso
                    if pregunta_actual and pregunta_actual["correctas"]:
                        preguntas_y_respuestas.append(pregunta_actual.copy())
                    
                    # Si hay una pregunta base guardada, crear una nueva entrada para este caso
                    if pregunta_base:
                        pregunta_actual = {
                            "numero": pregunta_base["numero"],
                            "pregunta": pregunta_base["pregunta"],  # Mantener la pregunta original
                            "correctas": [],
                            "correctas_idx": [],
                            "caso": texto_pregunta  # Guardar el identificador del caso
                        }
                    continue
                
                # Si encontramos una nueva pregunta
                # Guardar pregunta anterior si existe y tiene respuestas
                if pregunta_actual and pregunta_actual["correctas"]:
                    preguntas_y_respuestas.append(pregunta_actual)
                
                # Normalizar el texto de la pregunta (remover guion bajo)
                texto_pregunta_normalizado = normalizar_texto_pregunta(texto_pregunta)
                
                # Verificar si la pregunta tiene solo imágenes
                if tiene_solo_imagenes(elemento):
                    preguntas_a_ignorar.add(numero_pregunta)
                    print(f"[DEBUG] Pregunta {numero_pregunta} ignorada por solo imágenes")
                    # Guardar la información de la pregunta para mostrarla al final
                    preguntas_solo_imagenes.append({
                        "numero": numero_pregunta,
                        "pregunta": texto_pregunta_normalizado if texto_pregunta_normalizado else texto_pregunta
                    })
                    pregunta_actual = None
                    pregunta_base = None
                else:
                    pregunta_actual = {
                        "numero": numero_pregunta,
                        "pregunta": texto_pregunta_normalizado,  # Usar texto normalizado
                        "correctas": [],
                        "correctas_idx": [],
                        "caso": None
                    }
                    # Guardar como pregunta base en caso de que aparezcan casos múltiples después
                    pregunta_base = {
                        "numero": numero_pregunta,
                        "pregunta": texto_pregunta_normalizado  # Usar texto normalizado
                    }
            elif pregunta_actual is None:
                # Podría ser texto adicional de una pregunta anterior
                pass
                    
        except Exception as e:
            continue
    
    elif tag == "ul" and pregunta_actual:
        try:
            # Verificar si la lista tiene solo imágenes
            if tiene_solo_imagenes(elemento):
                # Si todas las respuestas son imágenes, ignorar
                pregunta_actual = None
                continue
            
            # Extraer respuestas correctas
            correctas, idxs = extraer_respuestas_correctas(elemento, pregunta_actual["pregunta"])
            
            if correctas:
                pregunta_actual["correctas"] = correctas
                pregunta_actual["correctas_idx"] = idxs
                
        except Exception as e:
            continue

# Guardar última pregunta si existe
if pregunta_actual and pregunta_actual["correctas"]:
    preguntas_y_respuestas.append(pregunta_actual)

# --- Cargar JSON existente ---
diccionario_path = 'diccionario.json'
if os.path.exists(diccionario_path):
    with open(diccionario_path, 'r', encoding='utf-8') as f:
        DICCIONARIO = json.load(f)
else:
    DICCIONARIO = {}


def pregunta_ya_existe(pregunta, correctas_textos):
    """Compara si una pregunta ya existe con las mismas respuestas"""
    # Normalizar pregunta antes de buscar
    pregunta_normalizada = normalizar_texto_pregunta(pregunta)
    
    # Buscar en todas las claves del diccionario normalizándolas
    pregunta_encontrada = None
    for clave in DICCIONARIO.keys():
        clave_normalizada = normalizar_texto_pregunta(clave)
        if clave_normalizada == pregunta_normalizada:
            pregunta_encontrada = clave
            break
    
    # Si no se encontró con normalización, buscar con las claves exactas
    if not pregunta_encontrada:
        claves_posibles = [pregunta_normalizada]
        if pregunta != pregunta_normalizada:
            claves_posibles.append(pregunta)
        
        for clave in claves_posibles:
            if clave in DICCIONARIO:
                pregunta_encontrada = clave
                break
    
    if not pregunta_encontrada:
        return False
    
    valor_existente = DICCIONARIO[pregunta_encontrada]
    
    # El formato en el diccionario es: [" ", "respuesta1. respuesta2"] o [" ", "respuesta"]
    # Puede ser también una lista con índice y respuesta: [indice, "respuesta"] o ["indices", "respuestas"]
    if not isinstance(valor_existente, list) or len(valor_existente) < 2:
        return False
    
    # Si el primer elemento es un espacio, es el formato nuevo
    if valor_existente[0] == " ":
        respuesta_existente = valor_existente[1]
    else:
        # Formato antiguo con índice
        respuesta_existente = valor_existente[1] if len(valor_existente) > 1 else ""
    
    # Formar la respuesta nueva en el mismo formato
    if len(correctas_textos) == 1:
        respuesta_nueva = correctas_textos[0]
    else:
        respuesta_nueva = '. '.join(correctas_textos)
    
    # Comparar respuestas (normalizar espacios)
    respuesta_existente = respuesta_existente.strip()
    respuesta_nueva = respuesta_nueva.strip()
    
    return respuesta_existente == respuesta_nueva


def formatear_para_diccionario(correctas_textos):
    """Formatea las respuestas correctas en el formato del diccionario"""
    if len(correctas_textos) == 1:
        return [" ", correctas_textos[0]]
    else:
        return [" ", '. '.join(correctas_textos)]


def formatear_casos_multiples(casos_respuestas):
    """Formatea múltiples casos en el formato: caso 1: respuestas. caso 2: respuestas"""
    partes = []
    for caso_num, respuestas in casos_respuestas:
        respuestas_str = '. '.join(respuestas)
        partes.append(f"{caso_num}: {respuestas_str}")
    return ' '.join(partes)


# --- Agrupar preguntas con casos múltiples ---
preguntas_agrupadas = {}
preguntas_normales = []
preguntas_por_numero = {}  # Para detectar si hay casos múltiples después

# Primera pasada: identificar preguntas que tienen casos múltiples
for q in preguntas_y_respuestas:
    numero = q["numero"]
    if q.get("caso"):
        preguntas_por_numero[numero] = True

# Segunda pasada: procesar y agrupar
for q in preguntas_y_respuestas:
    pregunta_texto = normalizar_texto_pregunta(q["pregunta"])  # Normalizar pregunta
    numero = q["numero"]
    
    # Ignorar si está en la lista de preguntas a ignorar
    if numero in preguntas_a_ignorar:
        continue
    
    if not q["correctas"]:
        continue
    
    # Si tiene un caso múltiple, agruparlo
    if q.get("caso"):
        if pregunta_texto not in preguntas_agrupadas:
            preguntas_agrupadas[pregunta_texto] = []
        preguntas_agrupadas[pregunta_texto].append((q["caso"], q["correctas"]))
    else:
        # Si este número tiene casos múltiples después, convertir esta pregunta normal a "Caso 1"
        if numero in preguntas_por_numero:
            if pregunta_texto not in preguntas_agrupadas:
                preguntas_agrupadas[pregunta_texto] = []
            preguntas_agrupadas[pregunta_texto].append(("Caso 1", q["correctas"]))
        else:
            # Pregunta normal (sin casos múltiples)
            # Actualizar pregunta con texto normalizado
            q["pregunta"] = pregunta_texto
            preguntas_normales.append(q)


# --- Procesar preguntas con casos múltiples ---
preguntas_agregadas = 0
preguntas_omitidas = []  # Lista para almacenar preguntas que se omiten

for pregunta_texto, casos_respuestas in preguntas_agrupadas.items():
    # Ordenar casos por número (Caso 1, Caso 2, etc.)
    def extraer_numero_caso(caso_str):
        match = re.search(r'(\d+)', caso_str)
        return int(match.group(1)) if match else 999
    
    casos_respuestas.sort(key=lambda x: extraer_numero_caso(x[0]))
    
    # Formatear todas las respuestas organizadas por caso
    respuesta_final = formatear_casos_multiples(casos_respuestas)
    
    # Normalizar pregunta antes de buscar/guardar
    pregunta_texto_normalizada = normalizar_texto_pregunta(pregunta_texto)
    
    # Buscar en el diccionario con normalización (buscar tanto la clave normalizada como variantes)
    clave_encontrada = None
    for clave in DICCIONARIO.keys():
        if normalizar_texto_pregunta(clave) == pregunta_texto_normalizada:
            clave_encontrada = clave
            break
    
    # Si no se encuentra, usar la clave normalizada
    if clave_encontrada is None:
        clave_encontrada = pregunta_texto_normalizada
    
    # Verificar si ya existe
    if clave_encontrada not in DICCIONARIO:
        # Guardar con clave normalizada
        DICCIONARIO[pregunta_texto_normalizada] = [" ", respuesta_final]
        preguntas_agregadas += 1
    else:
        # Verificar si el contenido es diferente
        valor_existente = DICCIONARIO[clave_encontrada]
        respuesta_existente = valor_existente[1] if len(valor_existente) > 1 else ""
        
        if respuesta_existente.strip() != respuesta_final.strip():
            # Si las claves son diferentes, mover de la clave antigua a la normalizada
            if clave_encontrada != pregunta_texto_normalizada:
                del DICCIONARIO[clave_encontrada]
            DICCIONARIO[pregunta_texto_normalizada] = [" ", respuesta_final]
            preguntas_agregadas += 1
        else:
            preguntas_omitidas.append({
                "tipo": "casos_multiples",
                "pregunta": pregunta_texto_normalizada,
                "razon": "ya existe con las mismas respuestas"
            })


# --- Procesar preguntas normales (sin casos múltiples) ---
for q in preguntas_normales:
    pregunta_texto = normalizar_texto_pregunta(q["pregunta"])  # Asegurar normalización
    correctas_textos = q["correctas"]

    clave_pregunta = pregunta_texto
    
    # Buscar en el diccionario con normalización
    clave_encontrada = None
    for clave in DICCIONARIO.keys():
        if normalizar_texto_pregunta(clave) == clave_pregunta:
            clave_encontrada = clave
            break
    
    # Si no se encuentra, usar la clave normalizada
    if clave_encontrada is None:
        clave_encontrada = clave_pregunta
    
    if clave_encontrada not in DICCIONARIO:
        # Guardar con clave normalizada
        DICCIONARIO[clave_pregunta] = formatear_para_diccionario(correctas_textos)
        preguntas_agregadas += 1
    elif not pregunta_ya_existe(clave_pregunta, correctas_textos):
        # Si las claves son diferentes, mover de la clave antigua a la normalizada
        if clave_encontrada != clave_pregunta:
            del DICCIONARIO[clave_encontrada]
        DICCIONARIO[clave_pregunta] = formatear_para_diccionario(correctas_textos)
        preguntas_agregadas += 1
    else:
        preguntas_omitidas.append({
            "tipo": "normal",
            "numero": q['numero'],
            "pregunta": clave_pregunta,
            "razon": "ya existe con las mismas respuestas"
        })

# Agregar preguntas ignoradas a la lista de omitidas (excepto las de solo imágenes que ya se guardaron)
preguntas_ignoradas_info = []
for q in preguntas_y_respuestas:
    numero = q.get("numero")
    if numero in preguntas_a_ignorar and numero not in [p["numero"] for p in preguntas_solo_imagenes]:
        # Ya se capturó en preguntas_solo_imagenes, no duplicar
        pass
    elif not q.get("correctas"):
        preguntas_ignoradas_info.append({
            "tipo": "ignorada",
            "numero": numero,
            "pregunta": q.get("pregunta", ""),
            "razon": "sin respuestas con texto"
        })

preguntas_omitidas.extend(preguntas_ignoradas_info)

# Mostrar preguntas omitidas (excepto las de solo imágenes)
if preguntas_omitidas:
    print(f"\n{'='*80}")
    print(f"PREGUNTAS OMITIDAS ({len(preguntas_omitidas)}):")
    print(f"{'='*80}")
    for i, omitida in enumerate(preguntas_omitidas, 1):
        if omitida["tipo"] == "casos_multiples":
            print(f"\n{i}. [Casos múltiples] - {omitida['razon']}")
            print(f"   {omitida['pregunta'][:120]}...")
        elif omitida["tipo"] == "normal":
            print(f"\n{i}. [Pregunta {omitida.get('numero', 'N/A')}] - {omitida['razon']}")
            print(f"   {omitida['pregunta'][:120]}...")
        elif omitida["tipo"] == "ignorada" and omitida.get('razon') != "solo contiene imágenes":
            numero_str = f"Pregunta {omitida.get('numero', 'N/A')}" if omitida.get('numero') else "Pregunta desconocida"
            print(f"\n{i}. [{numero_str}] - {omitida['razon']}")
            if omitida.get('pregunta'):
                print(f"   {omitida['pregunta'][:120]}...")
    print(f"\n{'='*80}")

# Mostrar preguntas ignoradas por solo imágenes
if preguntas_solo_imagenes:
    print(f"\n{'='*80}")
    print(f"PREGUNTAS OMITIDAS (Solo imágenes) ({len(preguntas_solo_imagenes)}):")
    print(f"{'='*80}")
    for i, img_pregunta in enumerate(preguntas_solo_imagenes, 1):
        print(f"\n{i}. [Pregunta {img_pregunta['numero']}] - Solo contiene imágenes")
        if img_pregunta.get('pregunta'):
            print(f"   {img_pregunta['pregunta']}")
        else:
            print(f"   (Sin texto - solo imagen)")
    print(f"\n{'='*80}")

# Guardar diccionario actualizado
with open(diccionario_path, 'w', encoding='utf-8') as f:
    json.dump(DICCIONARIO, f, ensure_ascii=False, indent=2)

driver.quit()

