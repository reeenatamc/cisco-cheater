"""
Scraper inteligente con Selenium (basado en scraper.py estable).

scrape_exam(url) → descarga un examen de examenredes.com,
detecta tipo SINGLE / MULTI / MATCH y almacena todo en la DB.
"""
import logging
import re
import time

from django.db import transaction
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from .models import Answer, Exam, Question, QuestionType

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Regex utilitarios
# ──────────────────────────────────────────────
_RE_QUESTION_NUM = re.compile(r"^(\d+)\.\s")
_RE_MATCH_ARROW = re.compile(r"\s*(?://|->|→|➜)\s*")


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────
def _build_driver() -> webdriver.Chrome:
    """Crea una instancia de Chrome visible (no headless)."""
    opts = Options()
    opts.add_argument("--start-maximized")
    return webdriver.Chrome(options=opts)


def _detect_match(text: str) -> tuple[bool, str, str]:
    """
    Detecta si una respuesta es de tipo MATCH.
    Retorna (es_match, col_a, col_b).
    """
    parts = _RE_MATCH_ARROW.split(text, maxsplit=1)
    if len(parts) == 2 and parts[0].strip() and parts[1].strip():
        return True, parts[0].strip(), parts[1].strip()
    return False, text.strip(), ""


def _extract_question_number(text: str) -> str | None:
    m = _RE_QUESTION_NUM.match(text)
    return m.group(1) if m else None


def _clean_question_text(text: str) -> str:
    """Remueve el número del inicio (ej: '1. Pregunta' → 'Pregunta')"""
    return _RE_QUESTION_NUM.sub("", text).strip()


# ──────────────────────────────────────────────
# Función principal
# ──────────────────────────────────────────────
@transaction.atomic
def scrape_exam(url: str) -> Exam:
    """
    Scrapea un examen completo desde *url* y lo almacena en la DB.
    Basado en scraper.py estable.
    """
    print(f"\n{'='*60}")
    print(f"[SCRAPER] Iniciando scrape de: {url}")
    print(f"{'='*60}\n")
    
    # Si ya existe Y tiene preguntas, retornarlo
    existing = Exam.objects.filter(url=url).first()
    if existing:
        question_count = existing.questions.count()
        if question_count > 0:
            print(f"⚠️  [SCRAPER] Exam ya existe en DB con {question_count} preguntas")
            print(f"    Título: {existing.title}")
            print(f"    ID: {existing.id}")
            print(f"    ℹ️  Usa otro examen o borra este para re-scrapear")
            logger.info("Exam ya existe en DB: %s", url)
            return existing
        else:
            print(f"⚠️  [SCRAPER] Exam existe pero tiene 0 preguntas. Re-scrapeando...")
            exam = existing
    else:
        print(f"✓ [SCRAPER] Examen no existe, procediendo a scrapear...")
        exam = None
    print(f"🌐 [SCRAPER] Abriendo Chrome...")
    
    driver = _build_driver()
    print(f"✓ [SCRAPER] Chrome abierto exitosamente")

    try:
        print(f"📡 [SCRAPER] Navegando a: {url}")
        driver.get(url)
        print(f"⏳ [SCRAPER] Esperando 15 segundos para que cargue...")
        time.sleep(15)
        print(f"✓ [SCRAPER] Página cargada")

        # Título
        try:
            title = driver.find_element(By.CSS_SELECTOR, "h1.entry-title, h1").text.strip()
            print(f"📝 [SCRAPER] Título detectado: {title}")
        except Exception as e:
            title = url
            print(f"⚠️  [SCRAPER] No se pudo obtener título, usando URL: {e}")

        if exam is None:
            exam = Exam.objects.create(url=url, title=title)
            print(f"✓ [SCRAPER] Examen creado en DB (ID: {exam.id})")
        else:
            exam.title = title
            exam.save()
            print(f"✓ [SCRAPER] Examen actualizado en DB (ID: {exam.id})")

        contenedor = driver.find_element(By.CLASS_NAME, "entry")
        elementos = contenedor.find_elements(By.XPATH, "./*")
        print(f"📦 [SCRAPER] Encontrados {len(elementos)} elementos HTML")

        pregunta_actual: dict | None = None
        preguntas_buffer: list[dict] = []
        variant_actual = 1  # Rastrear variante actual (para "Otro caso:")

        for idx, elemento in enumerate(elementos):
            tag = elemento.tag_name

            # ── Detectar nueva pregunta ──
            if tag == "p":
                strongs = elemento.find_elements(By.TAG_NAME, "strong")
                if strongs:
                    texto_fuerte = strongs[0].text.strip()
                    q_num = _extract_question_number(texto_fuerte)
                    texto_limpio = _clean_question_text(texto_fuerte)

                    # Solo crear nueva pregunta si tiene número válido
                    if q_num:
                        # Guardar la pregunta anterior si tenía respuestas
                        if pregunta_actual and pregunta_actual["answers"]:
                            print(f"  ➜ Pregunta {pregunta_actual['number']}: {len(pregunta_actual['answers'])} respuestas, {pregunta_actual.get('max_variant', 1)} variante(s)")
                            preguntas_buffer.append(pregunta_actual)
                        elif pregunta_actual:
                            # Pregunta sin respuestas - ADVERTENCIA
                            print(f"  ⚠️  Pregunta {pregunta_actual['number']} DESCARTADA (sin respuestas correctas)")

                        # Nueva pregunta - resetear variante
                        variant_actual = 1
                        print(f"\n🔹 [SCRAPER] Pregunta #{q_num}: {texto_limpio[:80]}...")
                        pregunta_actual = {
                            "text": texto_limpio,  # Texto sin el número
                            "number": q_num,
                            "answers": [],
                            "max_variant": 1,  # Rastrear cuántas variantes tiene
                        }
                else:
                    # <p> sin <strong> - podría ser "Otro caso:"
                    texto_p = elemento.text.strip().lower()
                    if "otro caso" in texto_p and pregunta_actual is not None:
                        variant_actual += 1
                        pregunta_actual["max_variant"] = variant_actual
                        print(f"    🔄 Detectada variante #{variant_actual}")

            # ── Extraer respuestas de <ul> ──
            elif tag == "ul" and pregunta_actual is not None:
                respuestas = elemento.find_elements(By.TAG_NAME, "li")
                respuestas_nuevas = 0
                for li in respuestas:
                    is_correct = "correct_answer" in (li.get_attribute("class") or "")
                    if is_correct:  # SOLO guardar las correctas
                        text = li.text.strip()
                        if text:
                            pregunta_actual["answers"].append(
                                {
                                    "text": text, 
                                    "is_correct": True,
                                    "variant_number": variant_actual,
                                }
                            )
                            print(f"    ✓ CORRECTA [V{variant_actual}]: {text[:60]}...")
                            respuestas_nuevas += 1
                
                # Log si encontramos respuestas en este <ul>
                if respuestas_nuevas > 0:
                    print(f"    📝 {respuestas_nuevas} respuesta(s) agregada(s) de este bloque <ul>")

        # Última pregunta pendiente
        if pregunta_actual:
            if pregunta_actual["answers"]:
                print(f"  ➜ Pregunta {pregunta_actual['number']}: {len(pregunta_actual['answers'])} respuestas, {pregunta_actual.get('max_variant', 1)} variante(s)")
                preguntas_buffer.append(pregunta_actual)
            else:
                print(f"  ⚠️  Pregunta {pregunta_actual['number']} DESCARTADA (sin respuestas correctas)")

        print(f"\n{'='*60}")
        print(f"📊 [SCRAPER] Total preguntas detectadas: {len(preguntas_buffer)}")
        print(f"{'='*60}\n")

        # ── Guardar en DB ──
        print(f"💾 [SCRAPER] Guardando en base de datos...")
        for pdata in preguntas_buffer:
            # Detectar tipo
            has_match = False
            correct_count = len(pdata["answers"])  # Todas son correctas ahora
            
            for a in pdata["answers"]:
                is_m, _, _ = _detect_match(a["text"])
                if is_m:
                    has_match = True
                    break

            if has_match:
                q_type = QuestionType.MATCH
            elif correct_count > 1:
                q_type = QuestionType.MULTI
            else:
                q_type = QuestionType.SINGLE

            question = Question.objects.create(
                exam=exam,
                text=pdata["text"],
                question_type=q_type,
                question_number=pdata["number"],
            )

            for a in pdata["answers"]:
                is_m, col_a, col_b = _detect_match(a["text"])
                Answer.objects.create(
                    question=question,
                    text=col_a,
                    match_pair=col_b if is_m else "",
                    is_correct=True,  # Todas son correctas porque ya filtramos
                    variant_number=a.get("variant_number", 1),
                )

        print(f"✅ [SCRAPER] ¡COMPLETADO! {len(preguntas_buffer)} preguntas guardadas")
        print(f"{'='*60}\n")
        
        logger.info(
            "Scrapeado: %s — %d preguntas guardadas", url, len(preguntas_buffer)
        )
        return exam

    finally:
        print(f"🚪 [SCRAPER] Cerrando Chrome...")
        driver.quit()
        print(f"✓ [SCRAPER] Chrome cerrado\n")
