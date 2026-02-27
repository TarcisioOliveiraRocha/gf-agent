import io, os, sys
print(f"Python: {sys.version}")
try:
    from pypdf import PdfReader
    print("OK pypdf")
except Exception as e:
    print(f"ERRO pypdf: {e}")
try:
    from PIL import Image
    print("OK Pillow")
except Exception as e:
    print(f"ERRO Pillow: {e}")
try:
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    print(f"OK pytesseract - versao: {pytesseract.get_tesseract_version()}")
except Exception as e:
    print(f"ERRO pytesseract: {e}")
try:
    import subprocess
    from pathlib import Path
    result = subprocess.run([r"C:\poppler\poppler-25.12.0\Library\bin\pdftoppm.exe", "-h"], capture_output=True)
    print("OK Poppler")
except Exception as e:
    print(f"ERRO Poppler: {e}")
