<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/Django-4.x-green?style=for-the-badge&logo=django" />
  <img src="https://img.shields.io/badge/Chrome%20Extension-Ready-yellow?style=for-the-badge&logo=googlechrome" />
</p>

<h1 align="center">🕵️‍♂️ cisco-cheater</h1>

**cisco-cheater** es una herramienta diseñada para ayudarte a obtener respuestas automáticamente en los exámenes en línea de Cisco. Incluye una extensión de navegador que detecta las preguntas seleccionadas y consulta un servidor Django local para mostrar la respuesta en una pequeña ventana flotante. Además, incluye un scraper para alimentar la base de datos con preguntas y respuestas.

> ⚠️ Este proyecto tiene fines educativos. No se recomienda ni aprueba el uso indebido de esta herramienta. Úsala bajo tu propia responsabilidad.

---

## Características

* ✅ Extensión de Chrome que funciona automáticamente en los exámenes de Cisco.
* ✅ Backend en Django para servir respuestas.
* ✅ Scraper incluido para recolectar preguntas/respuestas automáticamente.
* ✅ Interfaz flotante simple con respuestas instantáneas.
* ✅ Compatible con Python 3.10.

---

## Requisitos

* Python 3.10
* pip
* Tesseract OCR (requerido para procesamiento de imágenes)
* Navegador Chrome (para usar la extensión)
* Sistema operativo Linux o Windows

### Instalación de Tesseract OCR

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-spa tesseract-ocr-eng
```

**Windows:**
1. Descarga el instalador desde: https://github.com/UB-Mannheim/tesseract/wiki
2. Instala Tesseract y agrega la ruta de instalación a tu PATH del sistema
3. Por defecto se instala en: `C:\Program Files\Tesseract-OCR\tesseract.exe`

**macOS:**
```bash
brew install tesseract tesseract-lang
```

---

## Instalación y uso del servidor Django

### 1. Clona el repositorio

```bash
git clone https://github.com/reeenatmc/cisco-cheater.git
cd cisco-cheater
````

### 2. Crea y activa el entorno virtual

```bash
python3.10 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instala dependencias de Python

```bash
pip install -r requirements.txt
```

> ⚠️ **Importante:** Asegúrate de tener Tesseract OCR instalado en tu sistema antes de continuar. Ver la sección de Requisitos arriba.

### 4. Aplica migraciones

```bash
python manage.py migrate
```

### 5. Inicia el servidor

```bash
python manage.py runserver
```

El servidor estará disponible en:
👉 [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## Cómo usar el cheater en Cisco NetAcad

Ya no necesitas inyectar código manualmente. Solo:

1. Instala la extensión desde este repositorio 👉 [cisco-cheater-extension](https://github.com/reeenatamc/cisco-cheater-extension).
2. Abre un examen en [netacad.com](https://www.netacad.com/).
3. Selecciona una pregunta con el mouse.
4. La respuesta aparecerá automáticamente en una pequeña ventana flotante.

> Asegúrate de tener el servidor Django corriendo **antes** de usar la extensión.

---

## Scraper

Incluye un scraper para recolectar preguntas y respuestas desde exámenes reales de Cisco:

```bash
python manage.py runscript scraper
```

Asegúrate de tener configurada la fuente de datos.

---

## 🤝 Colaboración

¡Contribuciones bienvenidas!

1. Haz un fork del repositorio.
2. Crea una rama nueva: `git checkout -b mejora-nueva`
3. Haz tus cambios y haz commit: `git commit -m "Agrega nueva funcionalidad"`
4. Sube los cambios: `git push origin mejora-nueva`
5. Abre un Pull Request.

---

## 📜 Nota legal

Este software es solo para fines educativos y de demostración técnica. El uso indebido de esta herramienta puede violar las políticas de uso de plataformas educativas. **El autor no se responsabiliza por el mal uso del software.**

