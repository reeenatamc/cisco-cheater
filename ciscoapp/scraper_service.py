"""
Scraper for examenredes.com.

Extracts complete questions (with context included in the text)
and their correct answers. Detects SINGLE/MULTI/MATCH types.
Designed to be invoked from Django Admin or management command.
"""

import re
import logging
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException,
    WebDriverException,
)

from .models import Exam, Question, Answer

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────

_NUM_RE = re.compile(r"^_?(\d+)\.\s")
_MATCH_SEPARATORS = re.compile(r"\s*(?://|->|→|──>|—>)\s*")
_OTRO_CASO_RE = re.compile(
    r"^(?:Otro\s+caso(?:\s+\d+)?)\s*:?\s*$", re.IGNORECASE
)


def _extract_question_number(text: str) -> int | None:
    """Return the leading question number or None."""
    m = _NUM_RE.match(text)
    return int(m.group(1)) if m else None


def _normalize_question_text(text: str) -> str:
    """Remove leading number prefix: '_1. ' or '1. ' → clean text."""
    text = re.sub(r"^_(\d+\.\s)", r"\1", text)
    text = re.sub(r"^\d+\.\s*", "", text)
    return text.strip()


def _is_image_only(element) -> bool:
    """True when the element contains images but no meaningful text."""
    try:
        imgs = element.find_elements(By.TAG_NAME, "img")
        txt = element.text.strip()
        if imgs and (not txt or len(txt) < 10):
            return True
        if imgs and not re.search(r"[a-zA-ZáéíóúñÁÉÍÓÚÑ]{10,}", txt):
            return True
    except Exception:
        pass
    return False


def _detect_match_type(li_texts: list[str]) -> bool:
    """Return True if the answers look like a matching question."""
    match_count = sum(1 for t in li_texts if _MATCH_SEPARATORS.search(t))
    return match_count >= 2


def _parse_match_pair(text: str) -> tuple[str, str]:
    """Split 'left // right' into (left, right). Falls back to (text, '')."""
    parts = _MATCH_SEPARATORS.split(text, maxsplit=1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return text.strip(), ""


# ──────────────────────────────────────────────────────────────
# Main scraper
# ──────────────────────────────────────────────────────────────


def _build_driver() -> webdriver.Chrome:
    """Build a visible Chrome WebDriver."""
    opts = Options()
    opts.add_argument("--start-maximized")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
    return webdriver.Chrome(options=opts)


def scrape_exam(url: str, wait_seconds: int = 15) -> dict:
    """
    Scrape an exam page from examenredes.com and persist to DB.

    Strategy: grab the FULL text of each <p> that starts with a question
    number (e.g. "47. ..."). Everything in that <p> IS the question,
    including any scenario/context. Then grab the <ul> that follows
    for the answers.

    Returns dict with stats.
    """
    exam, _created = Exam.objects.get_or_create(
        url=url, defaults={"title": ""}
    )

    driver = _build_driver()
    stats = {
        "exam_id": exam.pk,
        "exam_title": "",
        "created": 0,
        "skipped": 0,
        "image_only": 0,
    }

    try:
        logger.info("Scraping %s …", url)
        driver.get(url)
        time.sleep(wait_seconds)

        # Grab page title
        try:
            page_title = driver.find_element(
                By.CSS_SELECTOR, "h1.entry-title, h1, .entry-title"
            ).text.strip()
        except NoSuchElementException:
            page_title = driver.title
        if page_title and not exam.title:
            exam.title = page_title[:512]
            exam.save(update_fields=["title"])
        stats["exam_title"] = exam.title

        # ── Walk child elements of .entry ─────────────────────
        container = driver.find_element(By.CLASS_NAME, "entry")
        children = container.find_elements(By.XPATH, "./*")

        current_question: dict | None = None
        current_variant: int = 1
        questions_buffer: list[dict] = []

        def _flush_question():
            nonlocal current_question, current_variant
            if current_question and current_question["answers"]:
                questions_buffer.append(current_question)
            current_question = None
            current_variant = 1

        for elem in children:
            tag = elem.tag_name

            # ── <p> or <strong> — check for question number ──
            if tag in ("p", "strong"):
                raw_text = elem.text.strip()
                if not raw_text:
                    continue

                # ── Detect "Otro caso:" / "Otro caso 2:" variant marker ──
                if _OTRO_CASO_RE.match(raw_text):
                    if current_question is not None:
                        current_variant += 1
                    continue

                # Try to find question number in <strong> child first
                num = None
                full_text = raw_text

                if tag == "p":
                    strongs = elem.find_elements(By.TAG_NAME, "strong")
                    if strongs:
                        strong_text = strongs[0].text.strip()
                        num = _extract_question_number(strong_text)

                if num is None:
                    num = _extract_question_number(raw_text)

                if num is not None:
                    # New question — use the FULL <p> text
                    _flush_question()

                    # Complete question text = full <p> minus leading number
                    clean_text = _normalize_question_text(full_text)

                    current_question = {
                        "number": str(num),
                        "text": clean_text,
                        "type": "SINGLE",
                        "answers": [],
                    }
                continue

            # ── <ul> — extract answers ────────────────────────
            if tag == "ul" and current_question is not None:
                if _is_image_only(elem):
                    current_question = None
                    continue

                items = elem.find_elements(By.TAG_NAME, "li")
                all_texts = []
                correct_items = []

                for li in items:
                    cls = li.get_attribute("class") or ""
                    li_text = li.text.strip()
                    if _is_image_only(li) or not li_text:
                        continue
                    is_correct = "correct_answer" in cls
                    all_texts.append(li_text)
                    if is_correct:
                        correct_items.append(li_text)

                # Detect question type
                is_match = _detect_match_type(all_texts)
                if is_match:
                    current_question["type"] = "MATCH"
                elif len(correct_items) > 1:
                    current_question["type"] = "MULTI"
                else:
                    current_question["type"] = "SINGLE"

                for li in items:
                    cls = li.get_attribute("class") or ""
                    li_text = li.text.strip()
                    if _is_image_only(li) or not li_text:
                        continue
                    is_correct = "correct_answer" in cls

                    if not is_correct:
                        continue

                    if is_match:
                        left, right = _parse_match_pair(li_text)
                        current_question["answers"].append({
                            "text": left,
                            "match_pair": right,
                            "is_correct": True,
                            "variant": current_variant,
                        })
                    else:
                        current_question["answers"].append({
                            "text": li_text,
                            "match_pair": "",
                            "is_correct": True,
                            "variant": current_variant,
                        })
                continue

        # Flush last question
        _flush_question()

        # ── Persist to DB ─────────────────────────────────────
        existing_texts = set(
            Question.objects.filter(exam=exam).values_list("text", flat=True)
        )

        for q in questions_buffer:
            norm = _normalize_question_text(q["text"])
            if norm in existing_texts:
                stats["skipped"] += 1
                continue

            question = Question.objects.create(
                exam=exam,
                question_number=q["number"],
                text=norm,
                question_type=q["type"],
            )

            for a in q["answers"]:
                Answer.objects.create(
                    question=question,
                    text=a["text"],
                    match_pair=a.get("match_pair", ""),
                    is_correct=a["is_correct"],
                    variant_number=a.get("variant", 1),
                )

            existing_texts.add(norm)
            stats["created"] += 1

    except WebDriverException as exc:
        logger.exception("Selenium error scraping %s", url)
        raise RuntimeError(f"Selenium error: {exc}") from exc
    finally:
        driver.quit()

    logger.info(
        "Scrape done: %d created, %d skipped, %d image-only",
        stats["created"],
        stats["skipped"],
        stats["image_only"],
    )
    return stats
