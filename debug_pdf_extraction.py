import os
from pdf2image import convert_from_path
from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
POPPLER_PATH = os.path.join(os.getcwd(), 'poppler-25.07.0', 'Library', 'bin')

def test_pdf_extraction(pdf_path):
    print(f"\n{'='*60}")
    print(f"Testing PDF Extraction: {pdf_path}")
    print(f"{'='*60}\n")
    
    if not os.path.exists(pdf_path):
        print(f"ERROR: File not found at {pdf_path}")
        return
    
    print(f"✓ File exists ({os.path.getsize(pdf_path)} bytes)")
    
    try:
        print(f"\nStep 1: Converting PDF to images...")
        print(f"Using Poppler at: {POPPLER_PATH}")
        
        pages = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
        print(f"✓ Successfully converted PDF to {len(pages)} page(s)")
        
        print(f"\nStep 2: Saving first page as image for inspection...")
        first_page = pages[0]
        first_page.save("debug_page.jpg", "JPEG")
        print(f"✓ Saved as 'debug_page.jpg' (size: {first_page.size})")
        
        print(f"\nStep 3: Running OCR on first page...")
        text = pytesseract.image_to_string(first_page)
        
        print(f"\n{'='*60}")
        print(f"EXTRACTION RESULTS:")
        print(f"{'='*60}")
        print(f"Characters extracted: {len(text)}")
        print(f"Words extracted: {len(text.split())}")
        print(f"Lines extracted: {len(text.splitlines())}")
        
        if text.strip():
            print(f"\n--- First 500 characters ---")
            print(text[:500])
            print(f"\n--- Last 200 characters ---")
            print(text[-200:])
            print(f"\n✓ SUCCESS: Text extracted successfully!")
        else:
            print(f"\n⚠ WARNING: No text was extracted!")
            print(f"Possible reasons:")
            print(f"  1. PDF contains only images without text layer")
            print(f"  2. Image quality is too low")
            print(f"  3. Document is rotated or skewed")
            
    except Exception as e:
        print(f"\n❌ ERROR during extraction:")
        print(f"{type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdfs = [
        "aadhar card.pdf",
        "pan card.pdf",
        "static/uploads/aadhar card.pdf"
    ]
    
    for pdf in test_pdfs:
        if os.path.exists(pdf):
            test_pdf_extraction(pdf)
        else:
            print(f"Skipping {pdf} (not found)")
    
    print(f"\n{'='*60}")
    print("Testing complete!")
    print(f"{'='*60}")
