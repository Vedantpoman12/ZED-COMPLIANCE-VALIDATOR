import os
import glob
import pickle
import numpy as np
import faiss
import json
import pytesseract
from pdf2image import convert_from_path
import ollama  # <-- NEW: Import ollama
import time

# --- 1. ALL CONFIGURATION ---

# --- IMPORTANT: PATHS ---
# Add the path to your Poppler 'bin' folder
POPPLER_PATH = r"C:\Users\Hardik\OneDrive\Desktop\ZED_FRONTEND\poppler-25.07.0\Library\bin" 

# If you are on Windows, tell pytesseract where to find the .exe
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# --- NEW: MODEL DEFINITIONS ---
# We use the same model for both tasks
TEXT_MODEL_NAME = 'qwen:1.8b'
EMBEDDING_MODEL_NAME = 'qwen:1.8b'

# --- CRITICAL: NEW DIMENSION ---
# Qwen-1.8B creates vectors of this size.
VECTOR_DIMENSION = 2048  # <-- CRITICAL CHANGE

# --- DATABASE INITIALIZATION ---
# Initialize FAISS with the NEW dimension
index = faiss.IndexFlatL2(VECTOR_DIMENSION)

# Initialize our metadata store
metadata_store = {}

# --- PROMPT DEFINITION ---
# This is the prompt that instructs the LLM
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

# --- 2. DATA EXTRACTION FUNCTION (UPDATED) ---

def get_structured_data(file_path):
    print(f"  Extracting text from: {file_path}...")
    try:
        # 1. Convert PDF to images
        images = convert_from_path(file_path, poppler_path=POPPLER_PATH)
        
        # 2. Run OCR on all images and combine the text
        raw_text = ""
        for img in images:
            raw_text += pytesseract.image_to_string(img) + "\n"
        
        if not raw_text.strip():
            print(f"    Warning: No text found in {file_path}. Skipping.")
            return None

        # --- 3. FIX: Use Ollama to generate text ---
        full_prompt = EXTRACTION_PROMPT + raw_text
        response = ollama.generate(
            model=TEXT_MODEL_NAME,
            prompt=full_prompt,
            format='json'  # Ask Ollama for JSON directly
        )
        
        # 4. Parse the JSON response
        llm_response_text = response['response'] # Get the text
        extracted_data = json.loads(llm_response_text)
        
        # 5. Add our own metadata
        extracted_data["source_file"] = file_path
        extracted_data["document_type"] = "GST Registration Certificate"

        print(f"    Successfully extracted data for: {extracted_data.get('legal_name')}")
        return extracted_data

    except Exception as e:
        print(f"    Error processing {file_path}: {e}")
        return None # Skip this file on error

# --- 3. THE MAIN PROCESSING LOOP (UPDATED) ---

print("--- Starting Document Processing Pipeline (using local Qwen model) ---")

# Point this to your actual uploads folder
UPLOAD_FOLDER_PATH = "static/uploads/*.pdf"
files_to_process = glob.glob(UPLOAD_FOLDER_PATH)

if not files_to_process:
    print(f"Error: No PDF files found at '{UPLOAD_FOLDER_PATH}'.")
    print("Please check the path.")
    exit() # Exit the script if no files

print(f"Starting processing for {len(files_to_process)} files...")

for file_path in files_to_process:
    try:
        # --- EXTRACT & TRANSFORM ---
        metadata = get_structured_data(file_path)

        if metadata is None:
            continue 
        
        # Create the 'content_to_embed' string from the metadata
        content_to_embed = f"""
            GST Registration for {metadata.get('legal_name')}.
            GSTN: {metadata.get('registration_number')}.
            Address: {metadata.get('address')}.
            Registration Type: {metadata.get('type_of_registration')}.
        """

        # --- LOAD ---
        
        # --- 1. FIX: Use Ollama to create embeddings ---
        result = ollama.embeddings(
            model=EMBEDDING_MODEL_NAME,
            prompt=content_to_embed
        )
        vector = result['embedding']
        
        # FAISS requires a 2D NumPy array, so we reshape
        vector_np = np.array([vector]).astype('float32')

        # 2. Add to FAISS Index
        vector_id = index.ntotal
        index.add(vector_np)

        # 3. Add to Metadata Store
        metadata_store[vector_id] = metadata

        print(f"Successfully processed and indexed ID {vector_id}: {metadata.get('legal_name')}")
        
    except Exception as e:
        print(f"FAILED to process {file_path}: {e}")

# --- 4. SAVE (PERSIST) YOUR DATABASES ---
print("All files processed. Saving databases...")

# Save the FAISS index to disk
faiss.write_index(index, "gst_index.faiss")

# Save the metadata mapping to disk
with open("gst_metadata.pkl", "wb") as f:
    pickle.dump(metadata_store, f)

print("Database build complete.")
print(f"Total documents indexed: {len(metadata_store)}")