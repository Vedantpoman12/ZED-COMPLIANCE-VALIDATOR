import os
from pdf2image import convert_from_path
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
POPPLER_PATH = os.path.join(os.getcwd(), 'poppler-25.07.0', 'Library', 'bin')

def preprocess_image(image):
    """
    Enhance image for better OCR results
    """
    image = image.convert('L')
    
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)
    
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(2.0)
    
    return image

def extract_text_with_preprocessing(filepath):
    """
    Extract text with image preprocessing for better accuracy
    """
    text = ""
    try:
        if filepath.lower().endswith('.pdf'):
            print(f"Converting PDF: {filepath}")
            pages = convert_from_path(filepath, poppler_path=POPPLER_PATH, dpi=300)
            print(f"Converted to {len(pages)} page(s)")
            
            for i, page in enumerate(pages):
                print(f"Processing page {i+1}...")
                
                processed_page = preprocess_image(page)
                
                page_text = pytesseract.image_to_string(
                    processed_page,
                    config='--psm 6 --oem 3'
                )
                
                text += page_text + "\n"
                print(f"  Extracted {len(page_text)} characters from page {i+1}")
        else:
            print(f"Processing image: {filepath}")
            image = Image.open(filepath)
            processed_image = preprocess_image(image)
            
            text = pytesseract.image_to_string(
                processed_image,
                config='--psm 6 --oem 3'
            )
    
    except Exception as e:
        print(f"ERROR: {e}")
        return None
    
    return text.strip()

def test_file(filepath):
    print(f"\n{'='*70}")
    print(f"Testing: {filepath}")
    print(f"{'='*70}")
    
    if not os.path.exists(filepath):
        print(f"File not found!")
        return
    
    print(f"File size: {os.path.getsize(filepath):,} bytes")
    
    text = extract_text_with_preprocessing(filepath)
    
    if text:
        print(f"\n✓ SUCCESS!")
        print(f"Total characters: {len(text)}")
        print(f"Total words: {len(text.split())}")
        print(f"\nFirst 300 characters:")
        print("-" * 70)
        print(text[:300])
        print("-" * 70)
    else:
        print(f"\n⚠ NO TEXT EXTRACTED")

if __name__ == "__main__":
    files_to_test = [
        "aadhar card.pdf",
        "pan card.pdf"
    ]
    
    for f in files_to_test:
        test_file(f)
    
    print(f"\n{'='*70}")
    print("Testing Complete")
    print(f"{'='*70}")
