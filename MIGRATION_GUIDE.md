# Migration Guide: JSON to Django ORM

This document explains the migration from JSON-based storage to Django ORM with PostgreSQL.

## What Changed

### 1. Database Structure

**Before**: Questions and answers stored in `ciscoapp/diccionario.json` (~252KB)
```json
{
  "1. What is a switch?": [1, "A network device"],
  "2. Select all protocols": ["1, 3", "TCP. UDP"]
}
```

**After**: Questions stored in PostgreSQL with proper relational models:
- `Examen` - Exam container
- `Pregunta` - Individual questions
- `Respuesta` - Correct answers for normal questions
- `ParUnir` - Matching pairs for drag/drop questions

### 2. New Models (ciscoapp/models.py)

```python
class Examen(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    url_fuente = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Pregunta(models.Model):
    examen = models.ForeignKey(Examen, on_delete=models.CASCADE)
    numero = models.IntegerField()
    texto = models.TextField()
    tipo = models.CharField(choices=[
        ('opcion_simple', 'Opción Simple'),
        ('opcion_multiple', 'Opción Múltiple'),
        ('unir', 'Unir/Arrastrar')
    ])
    es_manual = models.BooleanField(default=False)

class Respuesta(models.Model):
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
    texto = models.TextField()
    indice = models.IntegerField()  # 1-based position

class ParUnir(models.Model):
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
    elemento_izquierdo = models.CharField(max_length=500)
    elemento_derecho = models.CharField(max_length=500)
```

### 3. Scraping Process

**Before** (`ciscoapp/scraper.py`):
- Selenium extracts questions
- Generates Python dictionary
- Saves to `diccionario.json`

**After** (`ciscoapp/scraper_orm.py`):
- Same Selenium extraction logic
- Saves directly to PostgreSQL
- Function: `scrapear_examen(url, nombre_examen, preguntas_a_ignorar, espera_inicial)`

Example usage:
```python
from ciscoapp.scraper_orm import scrapear_examen

scrapear_examen(
    url="https://examenredes.com/modulos-1-4-...",
    nombre_examen="Módulos 1-4",
    preguntas_a_ignorar={46, 40, 33},  # Questions to skip
    espera_inicial=15
)
```

### 4. API Changes (ciscoapp/cheatmain.py)

**Before**:
```python
# Load JSON at startup
with open(json_path, encoding='utf-8') as f:
    DICCIONARIO = json.load(f)

# Search in dictionary
if pregunta in DICCIONARIO:
    respuesta = DICCIONARIO[pregunta]
return JsonResponse({'respuesta': respuesta})  # Missing 'found' field!
```

**After**:
```python
# No JSON loading needed
# Search with ORM
pregunta_obj = Pregunta.objects.filter(texto__iexact=texto).first()
if not pregunta_obj:
    pregunta_obj = Pregunta.objects.filter(texto__icontains=texto).first()

# Format response based on question type
if pregunta_obj.tipo == 'unir':
    return JsonResponse({
        'respuesta': {'tipo': 'unir', 'pares': [...]},
        'found': True
    })
elif pregunta_obj.tipo == 'opcion_simple':
    return JsonResponse({
        'respuesta': [indice, texto],
        'found': True
    })
# ... etc
```

**Important**: Added the `found` field to ALL responses (was missing before).

### 5. Admin Interface (ciscoapp/admin.py)

New admin panels with Unfold UI:

- **ExamenAdmin**: List exams with question counts
- **PreguntaAdmin**: List questions with inline editors for:
  - `RespuestaInline`: Add/edit correct answers
  - `ParUnirInline`: Add/edit matching pairs for drag/drop questions

This makes it easy to manually add questions that can't be scraped automatically.

### 6. Chrome Extension Updates

**background.js** (NEW):
- Handles Alt+. keyboard shortcut
- Screen capture functionality

**content.js** (NEW, with aesthetic improvements):
- Improved formatting for matching questions (unir):
  - **Bold** left elements
  - Arrow separators (→)
  - All pairs visible at once
- Stealth design (opacity 0.3 → 1.0 on click)
- Dark/light mode adaptation
- Added `found` field handling

## Migration Steps

1. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

2. **Scrape data** (or migrate from JSON if needed):
   ```bash
   python ciscoapp/scraper_orm.py
   ```

3. **Manually add drag/drop questions** via Django admin:
   - Navigate to admin panel
   - Add `Pregunta` with `tipo='unir'` and `es_manual=True`
   - Add `ParUnir` entries via inline editor

4. **Update Chrome extension**:
   - Replace old JS files with new `background.js` and `content.js`
   - Update manifest to include both scripts

## Backward Compatibility

The JSON file (`diccionario.json`) is **NOT** deleted but **NOT** used in the code anymore. It's kept as a backup.

Response format remains compatible with the old JSON format for `opcion_simple` and `opcion_multiple` questions.

## Testing

Comprehensive test suite added (`ciscoapp/tests.py`):
- 9 tests covering all model types
- API endpoint testing for all question types
- All tests passing ✅

Run tests:
```bash
DJANGO_SETTINGS_MODULE=cheater.test_settings python manage.py test ciscoapp
```

## Benefits

1. **Scalability**: Database scales better than JSON file
2. **Query Performance**: Indexed database queries vs. full JSON scan
3. **Data Integrity**: Foreign keys, unique constraints
4. **Easy Management**: Django admin interface
5. **Flexibility**: Support for complex question types (matching/drag)
6. **Better UX**: Improved frontend with type-specific formatting
