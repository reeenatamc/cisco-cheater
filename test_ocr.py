"""
Script para probar OCR localmente.
Uso: python test_ocr.py ruta/a/imagen.png
"""
import sys
import os
import shutil
import pytesseract
from PIL import Image

# Configurar la ruta de tesseract automáticamente si no está en PATH
if not shutil.which('tesseract'):
    possible_paths = [
        '/usr/bin/tesseract',
        '/usr/local/bin/tesseract',
        '/opt/homebrew/bin/tesseract',  # macOS
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',  # Windows
    ]
    for path in possible_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            break

def test_ocr(imagen_path):
    print(f"Abriendo imagen: {imagen_path}")
    imagen = Image.open(imagen_path)
    
    print("Extrayendo texto con OCR...")
    texto = pytesseract.image_to_string(imagen, lang='spa+eng')
    
    print("\n" + "="*50)
    print("TEXTO EXTRAÍDO:")
    print("="*50)
    print(texto)
    print("="*50)
    
    return texto

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python test_ocr.py ruta/a/imagen.png")
        print("\nPuedes tomar un screenshot de una pregunta y probarlo.")
        sys.exit(1)
    
    test_ocr(sys.argv[1])
