import os
import numpy as np
import faiss
import pickle
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import re
import json
from datetime import datetime

POPPLER_PATH = os.path.join(os.getcwd(), 'poppler-25.07.0', 'Library', 'bin')
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

AUTHENTIC_DOCS_INDEX = "authentic_docs.faiss"
AUTHENTIC_DOCS_METADATA = "authentic_docs_metadata.pkl"
VECTOR_DIMENSION = 100

class DocumentAuthenticityDetector:
    def __init__(self):
        self.index = None
        self.metadata_store = {}
        self.load_or_create_index()
    
    def load_or_create_index(self):
        if os.path.exists(AUTHENTIC_DOCS_INDEX) and os.path.exists(AUTHENTIC_DOCS_METADATA):
            print("Loading existing authenticity index...")
            self.index = faiss.read_index(AUTHENTIC_DOCS_INDEX)
            with open(AUTHENTIC_DOCS_METADATA, "rb") as f:
                self.metadata_store = pickle.load(f)
        else:
            print("Creating new authenticity index...")
            self.index = faiss.IndexFlatL2(VECTOR_DIMENSION)
            self.metadata_store = {}
    
    def extract_text_from_file(self, filepath):
        from PIL import ImageEnhance
        
        text = ""
        try:
            if filepath.lower().endswith('.pdf'):
                pages = convert_from_path(filepath, poppler_path=POPPLER_PATH, dpi=300)
                print(f"  Converted PDF to {len(pages)} page(s)")
                
                for i, page in enumerate(pages):
                    page = page.convert('L')
                    
                    enhancer = ImageEnhance.Contrast(page)
                    page = enhancer.enhance(2.0)
                    
                    enhancer = ImageEnhance.Sharpness(page)
                    page = enhancer.enhance(1.5)
                    
                    page_text = pytesseract.image_to_string(page, config='--psm 6 --oem 3')
                    text += page_text + "\n"
                    print(f"  Page {i+1}: Extracted {len(page_text)} characters")
            else:
                image = Image.open(filepath)
                image = image.convert('L')
                
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(2.0)
                
                enhancer = ImageEnhance.Sharpness(image)
                image = enhancer.enhance(1.5)
                
                text = pytesseract.image_to_string(image, config='--psm 6 --oem 3')
        except Exception as e:
            print(f"Error extracting text from {filepath}: {e}")
            import traceback
            traceback.print_exc()
            return None
        
        if text and len(text) > 10:
            print(f"  ✓ Successfully extracted {len(text)} characters, {len(text.split())} words")
        else:
            print(f"  ⚠ Warning: Only {len(text)} characters extracted")
        
        return text.strip()
    
    def extract_features(self, text, doc_type):
        features = []
        
        if doc_type == "PAN":
            pan_pattern = r'[A-Z]{5}[0-9]{4}[A-Z]{1}'
            pan_match = re.search(pan_pattern, text)
            features.append(1.0 if pan_match else 0.0)
            
            keywords = ['PERMANENT ACCOUNT NUMBER', 'INCOME TAX DEPARTMENT', 'GOVT. OF INDIA']
            for keyword in keywords:
                features.append(1.0 if keyword in text.upper() else 0.0)
            
            dob_pattern = r'\d{2}/\d{2}/\d{4}'
            features.append(1.0 if re.search(dob_pattern, text) else 0.0)
            
            name_pattern = r'[A-Z][a-z]+ [A-Z][a-z]+'
            features.append(1.0 if re.search(name_pattern, text) else 0.0)
            
        elif doc_type == "AADHAAR":
            aadhaar_pattern = r'\d{4}\s\d{4}\s\d{4}'
            features.append(1.0 if re.search(aadhaar_pattern, text) else 0.0)
            
            keywords = ['UIDAI', 'UNIQUE IDENTIFICATION', 'AADHAAR']
            for keyword in keywords:
                features.append(1.0 if keyword in text.upper() else 0.0)
            
            dob_pattern = r'\d{2}/\d{2}/\d{4}'
            features.append(1.0 if re.search(dob_pattern, text) else 0.0)
            
            address_indicators = ['S/O', 'D/O', 'W/O', 'C/O']
            features.append(1.0 if any(ind in text.upper() for ind in address_indicators) else 0.0)
        
        text_length = len(text)
        features.append(min(text_length / 1000.0, 1.0))
        
        word_count = len(text.split())
        features.append(min(word_count / 100.0, 1.0))
        
        uppercase_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        features.append(uppercase_ratio)
        
        digit_ratio = sum(1 for c in text if c.isdigit()) / max(len(text), 1)
        features.append(digit_ratio)
        
        while len(features) < VECTOR_DIMENSION:
            features.append(0.0)
        
        return np.array(features[:VECTOR_DIMENSION], dtype=np.float32)
    
    def train_on_authentic_document(self, filepath, doc_type):
        print(f"\nTraining on authentic {doc_type} document: {filepath}")
        
        text = self.extract_text_from_file(filepath)
        if not text:
            print("Failed to extract text")
            return False
        
        print(f"Extracted {len(text)} characters")
        
        features = self.extract_features(text, doc_type)
        features_2d = features.reshape(1, -1)
        
        vector_id = self.index.ntotal
        self.index.add(features_2d)
        
        self.metadata_store[vector_id] = {
            "filepath": filepath,
            "doc_type": doc_type,
            "text_length": len(text),
            "word_count": len(text.split()),
            "trained_at": datetime.now().isoformat()
        }
        
        self.save_index()
        print(f"Successfully trained! Document ID: {vector_id}")
        return True
    
    def verify_document(self, filepath, doc_type):
        print(f"\nVerifying {doc_type} document: {filepath}")
        
        text = self.extract_text_from_file(filepath)
        if not text:
            return {
                "is_authentic": False,
                "confidence": 0.0,
                "reason": "Failed to extract text from document"
            }
        
        features = self.extract_features(text, doc_type)
        features_2d = features.reshape(1, -1)
        
        if self.index.ntotal == 0:
            return {
                "is_authentic": False,
                "confidence": 0.0,
                "reason": "No authentic documents in database. Please train the model first."
            }
        
        k = min(3, self.index.ntotal)
        distances, indices = self.index.search(features_2d, k)
        
        avg_distance = np.mean(distances[0])
        similarity_score = 1 / (1 + avg_distance)
        
        threshold = 0.6
        is_authentic = similarity_score >= threshold
        
        matched_docs = []
        for idx in indices[0]:
            if idx != -1 and idx in self.metadata_store:
                matched_docs.append(self.metadata_store[idx])
        
        return {
            "is_authentic": is_authentic,
            "confidence": float(similarity_score),
            "avg_distance": float(avg_distance),
            "threshold": threshold,
            "matched_documents": matched_docs,
            "reason": "Document appears authentic" if is_authentic else "Document shows signs of being fake or altered"
        }
    
    def save_index(self):
        faiss.write_index(self.index, AUTHENTIC_DOCS_INDEX)
        with open(AUTHENTIC_DOCS_METADATA, "wb") as f:
            pickle.dump(self.metadata_store, f)
        print("Index saved successfully")

def main():
    detector = DocumentAuthenticityDetector()
    
    print("=" * 60)
    print("DOCUMENT AUTHENTICITY DETECTION SYSTEM")
    print("=" * 60)
    
    authentic_docs = [
        ("pan card.pdf", "PAN"),
        ("aadhar card.pdf", "AADHAAR")
    ]
    
    print("\n[TRAINING PHASE]")
    for filepath, doc_type in authentic_docs:
        if os.path.exists(filepath):
            detector.train_on_authentic_document(filepath, doc_type)
        else:
            print(f"Warning: {filepath} not found!")
    
    print("\n" + "=" * 60)
    print("Training complete!")
    print(f"Total authentic documents in database: {detector.index.ntotal}")
    print("=" * 60)
    
    print("\n[TESTING PHASE]")
    test_docs = [
        ("static/uploads/AALAE0983J.jpg", "PAN"),
        ("static/uploads/aadhar card.pdf", "AADHAAR")
    ]
    
    for filepath, doc_type in test_docs:
        if os.path.exists(filepath):
            result = detector.verify_document(filepath, doc_type)
            print(f"\nVerification Result:")
            print(json.dumps(result, indent=2))
        else:
            print(f"Test file not found: {filepath}")

if __name__ == "__main__":
    main()
