import os
import glob
import pickle
import numpy as np
import faiss
import json
import pytesseract
from pdf2image import convert_from_path
import ollama
import time

POPPLER_PATH = r"C:\Users\Hardik\OneDrive\Desktop\ZED_FRONTEND\poppler-25.07.0\Library\bin" 

TEXT_MODEL_NAME = 'qwen:1.8b'
EMBEDDING_MODEL_NAME = 'qwen:1.8b'

VECTOR_DIMENSION = 2048

index = faiss.IndexFlatL2(VECTOR_DIMENSION)

metadata_store = {}

EXTRACTION_PROMPT = """
You are an expert data extraction bot.
From the raw OCR text of a GST Registration Certificate provided below, extract
the following fields and return *only* a valid JSON object.

Fields to extract:
1. legal_name
2. registration_number (the GSTIN)
3. trade_name (if any, otherwise 'N/A')
4. address (the full principal place of business address)
5. date_of_liability
6. type_of_registration (Regular, Composition, etc.)
7. date_of_issue

OCR TEXT:
---
"""

def get_structured_data(file_path):
    print(f"  Extracting text from: {file_path}...")
    try:
        images = convert_from_path(file_path, poppler_path=POPPLER_PATH)
        
        raw_text = ""
        for img in images:
            raw_text += pytesseract.image_to_string(img) + "\n"
        
        if not raw_text.strip():
            print(f"    Warning: No text found in {file_path}. Skipping.")
            return None

        full_prompt = EXTRACTION_PROMPT + raw_text
        response = ollama.generate(
            model=TEXT_MODEL_NAME,
            prompt=full_prompt,
            format='json'
        )
        
        llm_response_text = response['response']
        extracted_data = json.loads(llm_response_text)
        
        extracted_data["source_file"] = file_path
        extracted_data["document_type"] = "GST Registration Certificate"

        print(f"    Successfully extracted data for: {extracted_data.get('legal_name')}")
        return extracted_data

    except Exception as e:
        print(f"    Error processing {file_path}: {e}")
        return None

print("--- Starting Document Processing Pipeline (using local Qwen model) ---")

UPLOAD_FOLDER_PATH = "static/uploads/*.pdf"
files_to_process = glob.glob(UPLOAD_FOLDER_PATH)

if not files_to_process:
    print(f"Error: No PDF files found at '{UPLOAD_FOLDER_PATH}'.")
    print("Please check the path.")
    exit()

print(f"Starting processing for {len(files_to_process)} files...")

for file_path in files_to_process:
    try:
        metadata = get_structured_data(file_path)

        if metadata is None:
            continue 
        
        content_to_embed = f"""
            GST Registration for {metadata.get('legal_name')}.
            GSTN: {metadata.get('registration_number')}.
            Address: {metadata.get('address')}.
            Registration Type: {metadata.get('type_of_registration')}.
        """

        result = ollama.embeddings(
            model=EMBEDDING_MODEL_NAME,
            prompt=content_to_embed
        )
        vector = result['embedding']
        
        vector_np = np.array([vector]).astype('float32')

        vector_id = index.ntotal
        index.add(vector_np)

        metadata_store[vector_id] = metadata

        print(f"Successfully processed and indexed ID {vector_id}: {metadata.get('legal_name')}")
        
    except Exception as e:
        print(f"FAILED to process {file_path}: {e}")

print("All files processed. Saving databases...")

faiss.write_index(index, "gst_index.faiss")

with open("gst_metadata.pkl", "wb") as f:
    pickle.dump(metadata_store, f)

print("Database build complete.")
print(f"Total documents indexed: {len(metadata_store)}")