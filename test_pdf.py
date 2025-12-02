import os
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

POPPLER_PATH = os.path.join(os.getcwd(), 'poppler-25.07.0', 'Library', 'bin')
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

def test_pdf_extraction():
    print(f"Checking Poppler path: {POPPLER_PATH}")
    if not os.path.exists(POPPLER_PATH):
        print("ERROR: Poppler path does not exist!")
        return

    upload_folder = os.path.join('static', 'uploads')
    pdf_files = [f for f in os.listdir(upload_folder) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("No PDF files found in static/uploads to test.")
        return

    test_file = os.path.join(upload_folder, pdf_files[0])
    print(f"Testing extraction on: {test_file}")

    try:
        pages = convert_from_path(test_file, poppler_path=POPPLER_PATH)
        print(f"Successfully converted PDF to {len(pages)} images.")
        
        text = ""
        for i, page in enumerate(pages):
            print(f"OCR processing page {i+1}...")
            page_text = pytesseract.image_to_string(page)
            text += page_text
            print(f"Page {i+1} extracted {len(page_text)} characters.")
            
        print("\n--- Total Extracted Text Preview ---")
        print(text[:500])
        print("------------------------------------")
        
        
    except Exception as e:
        print(f"ERROR during extraction: {e}")

def test_embedding():
    import ollama
    print("\nTesting Ollama embedding...")
    try:
        res = ollama.embeddings(model='qwen:1.8b', prompt='hello world')
        print("Ollama embedding successful!")
        print(f"Vector length: {len(res['embedding'])}")
    except Exception as e:
        print(f"ERROR connecting to Ollama: {e}")

if __name__ == "__main__":
    test_pdf_extraction()
    test_embedding()
