<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/Django-4.x-green?style=for-the-badge&logo=django" />
  <img src="https://img.shields.io/badge/JavaScript-injected-yellow?style=for-the-badge&logo=javascript" />
</p>

<h1 align="center">🕵️‍♂️ cisco-cheater</h1>

**cisco-cheater** es una herramienta diseñada para ayudarte a obtener respuestas de forma automatizada en los exámenes en línea de Cisco. Funciona inyectando un script JavaScript directamente en la página del examen, el cual se comunica con un servidor Django que devuelve las respuestas correspondientes en una pequeña ventana flotante. Además, incluye un scraper que recopila preguntas y respuestas de manera automatizada para alimentar la base de datos del sistema.

> ⚠️ Este proyecto tiene fines educativos. No se recomienda ni aprueba el uso indebido de esta herramienta. Úsala bajo tu propia responsabilidad.

---

## Características

* ✅ Inyección de script personalizada para la página del examen de Cisco.
* ✅ Backend en Django para servir respuestas.
* ✅ Scraper incluido para recolectar preguntas/respuestas automáticamente.
* ✅ Interfaz flotante simple con respuestas al instante.
* ✅ Compatible con Python 3.10.

---

## Requisitos

* Python 3.10
* pip
* navegador web (para usar el script JavaScript)
* sistema operativo Linux o Windows

---

## Instalación y uso

### 1. Clona el repositorio

```bash
git clone https://github.com/reeenatmc/cisco-cheater.git
cd cisco-cheater
```

### 2. Crea y activa el entorno virtual

```bash
python3.10 -m venv venv
source venv/bin/activate  # En Windows usa: venv\Scripts\activate
```

### 3. Instala dependencias

```bash
pip install -r requirements.txt
```

### 4. Corre las migraciones (si las hay)

```bash
python manage.py migrate
```

### 5. Levanta el servidor de Django

```bash
python manage.py runserver
```

Una vez iniciado, el servidor estará corriendo en:
👉 [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## Cómo usar el cheater en el examen de Cisco

1. Abre la página del examen en el navegador.
2. Copia el contenido del archivo `cheater-js/cheater.js`.
3. Abre la consola del navegador (usualmente con `F12`).
4. Pega y ejecuta el código JavaScript allí.
5. Aparecerá una pequeña ventana flotante con las respuestas a las preguntas detectadas. Es decr, para que te salga la respuesta debes seleccionar la pregunta.

> Asegúrate de que el servidor Django esté corriendo **antes** de inyectar el script.

---

## Scraper

Este proyecto incluye un scraper que te permite recolectar nuevas preguntas y respuestas desde exámenes de Cisco y agregarlas automáticamente al sistema.

Para usarlo:

```bash
python manage.py runscript scraper
```

Asegúrate de tener configurada la fuente desde la cual se extraerán los datos.

---

## 🤝 Colaboración

¡Las contribuciones son bienvenidas!

Si deseas mejorar este proyecto, seguir estos pasos:

1. **Haz un fork** del repositorio.

2. Crea una nueva rama con tu mejora:

   ```bash
   git checkout -b mejora-nueva
   ```

3. Realiza tus cambios y haz commit:

   ```bash
   git commit -m "Agrega nueva funcionalidad"
   ```

4. Sube tus cambios a tu fork:

   ```bash
   git push origin mejora-nueva
   ```

5. Abre un **Pull Request** explicando detalladamente tu contribución.

> Asegúrate de que tu código siga una estructura clara, esté comentado y probado.
> También puedes reportar bugs o sugerir mejoras en la sección de *Issues*.

---

## Nota legal

Este software es solo para fines educativos y de demostración técnica. El uso de esta herramienta en contextos reales puede violar las políticas de uso de plataformas educativas y conllevar consecuencias legales o académicas. **El autor no se responsabiliza por el mal uso de este software.**

---
