"""
Quick Test - Check if your documents can be read now
"""
import os
from chatbot_logic import extract_text_from_file

print("="*70)
print("TESTING IMPROVED OCR")
print("="*70)

test_files = [
    "aadhar card.pdf",
    "pan card.pdf"
]

for filepath in test_files:
    if os.path.exists(filepath):
        print(f"\nTesting: {filepath}")
        print("-"*70)
        
        text = extract_text_from_file(filepath)
        
        if text and len(text) > 50:
            print(f"✓ SUCCESS! Extracted {len(text)} characters")
            print(f"First 200 characters:")
            print(text[:200])
        elif text:
            print(f"⚠ Extracted only {len(text)} characters (might be low quality)")
            print(f"Content: {text}")
        else:
            print("❌ FAILED - No text extracted")
    else:
        print(f"\n⚠ Skipping {filepath} - File not found")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
print("\nIf extraction failed:")
print("  1. Check if PDFs are image-based (scanned documents)")
print("  2. Verify Tesseract is working: tesseract --version")
print("  3. Try uploading JPG/PNG versions instead")
print("="*70)
