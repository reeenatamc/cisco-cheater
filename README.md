# cisco-cheater

A Django service that reads a question off the screen and answers it, plus the
browser extension that puts the answer where you are looking.

> **About this project.** I built it in my own free time to practise scraping,
> OCR and LLM integration on top of Django. It is published as a portfolio
> piece.
>
> How anyone chooses to use it is their own responsibility, and so are the
> consequences, including any academic integrity policy they may be bound by.
> I do not endorse using it to gain an unfair advantage in an examination.
>
> No exam content is distributed here. See [NOTICE](NOTICE).

## How it works

```
selection in the browser  ->  extension  ->  Django  ->  answer in a popup
                                               |
                                        local OCR (Tesseract)
                                               |
                                          Gemini, only if
                                        the lookup misses
```

Three pieces:

**The scraper.** Selenium walks question banks and fills the database, so the
common case is a lookup rather than a model call.

**Local OCR.** Questions that arrive as images go through Tesseract on the
server before anything else. This exists to cut cost: sending an image to Gemini
burns far more tokens than sending the text Tesseract already extracted.

**Gemini, last.** Only questions that miss both the database and OCR reach the
model.

## Stack

Django · PostgreSQL · Selenium · pytesseract · google-genai · Gunicorn and
WhiteNoise, deployed on Railway. Rate limited with django-ratelimit.

## Running it

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Needs PostgreSQL, a Gemini API key, and Tesseract installed on the system. The
extension lives in
[cisco-cheater-extension](https://github.com/reeenatamc/cisco-cheater-extension)
and expects the server on localhost.

## Licence

MIT for the code. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
