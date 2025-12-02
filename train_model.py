"""
DOCUMENT AUTHENTICITY TRAINING GUIDE
=====================================

This script trains your authenticity detection model with real documents.

HOW TO USE:
1. Make sure you have 'pan card.pdf' and 'aadhar card.pdf' in the main folder
2. Run this script: python train_authenticity_model.py
3. The script will create:
   - authentic_docs.faiss (Feature database)
   - authentic_docs_metadata.pkl (Document metadata)

Once trained, your chatbot will automatically detect fake documents!

WHAT IT CHECKS:
- Document format and structure
- Official keywords and patterns  
- Text consistency
- Security features
- Comparison with authentic documents

HOW IT WORKS:
✓ Green (AUTHENTIC): Document matches your trained real documents
✗ Red (FAKE/ALTERED): Document differs significantly from real ones

ACCURACY:
The more real documents you train on, the better the detection!
"""

import os
import sys

print(__doc__)

print("\n" + "="*60)
print("STARTING TRAINING...")
print("="*60 + "\n")

try:
    from train_authenticity_model import DocumentAuthenticityDetector
    
    detector = DocumentAuthenticityDetector()
    
    docs_to_train = [
        ("pan card.pdf", "PAN"),
        ("aadhar card.pdf", "AADHAAR")
    ]
    
    trained_count = 0
    for filepath, doc_type in docs_to_train:
        if os.path.exists(filepath):
            print(f"Training on: {filepath}")
            success = detector.train_on_authentic_document(filepath, doc_type)
            if success:
                trained_count += 1
        else:
            print(f"⚠ WARNING: {filepath} not found!")
    
    print("\n" + "="*60)
    if trained_count > 0:
        print(f"SUCCESS! Trained on {trained_count} authentic documents")
        print("Your system can now detect fake documents!")
    else:
        print("ERROR: No documents were trained.")
        print("Please check:")
        print("  1. Files exist in the main folder")
        print("  2. Tesseract is properly configured")
        print("  3. Poppler path is correct")
    print("="*60)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nMake sure:")
    print("  - Tesseract OCR is installed")
    print("  - Poppler is in the correct location")
    import traceback
    traceback.print_exc()
