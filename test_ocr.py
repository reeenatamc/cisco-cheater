"""
Script para probar OCR localmente.
Uso: python test_ocr.py ruta/a/imagen.png
"""
import sys
import pytesseract
from PIL import Image

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
