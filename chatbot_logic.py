import os
import numpy as np
import faiss
import pickle
import ollama
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

TEXT_MODEL_NAME = 'qwen:1.8b'
EMBEDDING_MODEL_NAME = 'qwen:1.8b'
VECTOR_DIMENSION = 2048
INDEX_FILE = "chatbot_index.faiss"
METADATA_FILE = "chatbot_metadata.pkl"
POPPLER_PATH = os.path.join(os.getcwd(), 'poppler-25.07.0', 'Library', 'bin')
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

index = None
metadata_store = {}

def init_chatbot():
    global index, metadata_store
    
    if os.path.exists(INDEX_FILE) and os.path.exists(METADATA_FILE):
        print("Loading existing chatbot index...")
        index = faiss.read_index(INDEX_FILE)
        with open(METADATA_FILE, "rb") as f:
            metadata_store = pickle.load(f)
    else:
        print("Creating new chatbot index...")
        index = faiss.IndexFlatL2(VECTOR_DIMENSION)
        metadata_store = {}

def extract_text_from_file(filepath):
    from PIL import ImageEnhance
    
    text = ""
    try:
        if filepath.lower().endswith('.pdf'):
            pages = convert_from_path(filepath, poppler_path=POPPLER_PATH, dpi=300)
            for page in pages:
                page = page.convert('L')
                
                enhancer = ImageEnhance.Contrast(page)
                page = enhancer.enhance(2.0)
                
                enhancer = ImageEnhance.Sharpness(page)
                page = enhancer.enhance(1.5)
                
                page_text = pytesseract.image_to_string(page, config='--psm 6 --oem 3')
                text += page_text + "\n"
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
        return None
    
    print(f"--- Extracted Text from {filepath} ---")
    print(f"Length: {len(text)} characters")
    if text:
        print(text[:500])
    print("--------------------------------------")
    return text.strip()

def clear_knowledge_base():
    global index, metadata_store
    print("Clearing knowledge base...")
    index = faiss.IndexFlatL2(VECTOR_DIMENSION)
    metadata_store = {}
    save_knowledge_base()

def add_document_to_knowledge_base(filepath, filename):
    global index, metadata_store
    
    if index is None:
        init_chatbot()
        
    text = extract_text_from_file(filepath)
    if not text:
        return False, "Failed to extract text."

    chunk_size = 500
    overlap = 50
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        chunks.append(chunk)
    
    successful_chunks = 0
    last_error = None
    
    for chunk in chunks:
        try:
            result = ollama.embeddings(model=EMBEDDING_MODEL_NAME, prompt=chunk)
            vector = result['embedding']
            vector_np = np.array([vector]).astype('float32')
            
            vector_id = index.ntotal
            index.add(vector_np)
            
            metadata_store[vector_id] = {
                "filename": filename,
                "content": chunk,
                "full_text_snippet": text[:200] + "..."
            }
            successful_chunks += 1
        except Exception as e:
            print(f"Error embedding chunk: {e}")
            last_error = str(e)
            
    if successful_chunks > 0:
        save_knowledge_base()
        return True, f"Successfully learned {successful_chunks} chunks from {filename}."
    else:
        error_msg = f"Failed to learn content. Error: {last_error}" if last_error else "Failed to learn content."
        return False, error_msg

def save_knowledge_base():
    global index, metadata_store
    if index:
        faiss.write_index(index, INDEX_FILE)
        with open(METADATA_FILE, "wb") as f:
            pickle.dump(metadata_store, f)

def query_chatbot(user_query):
    global index, metadata_store
    
    if index is None:
        init_chatbot()
        
    if index.ntotal == 0:
        return "I haven't learned any documents yet. Please upload one first!"

    try:
        result = ollama.embeddings(model=EMBEDDING_MODEL_NAME, prompt=user_query)
        query_vector = np.array([result['embedding']]).astype('float32')
        
        k = 3
        distances, indices = index.search(query_vector, k)
        
        retrieved_context = ""
        for idx in indices[0]:
            if idx != -1 and idx in metadata_store:
                retrieved_context += metadata_store[idx]['content'] + "\n---\n"
        
        if not retrieved_context:
            return "I couldn't find any relevant information in the uploaded documents."

        prompt = f"""
You are an intelligent document analysis assistant. Your goal is to answer the user's question accurately using ONLY the provided context.
Pay close attention to specific details like account numbers, names, dates, and IDs.

Context:
{retrieved_context}

User Question: {user_query}

Instructions:
1. If the answer is explicitly in the context, provide it clearly.
2. If the user asks for a specific number (like account number, ID), look for patterns of digits.
3. If the answer is NOT in the context, say "I cannot find that information in the uploaded documents."
4. Do not make up information.

Answer:
"""
        response = ollama.generate(model=TEXT_MODEL_NAME, prompt=prompt)
        return response['response']

    except Exception as e:
        print(f"Error querying chatbot: {e}")
        return "Sorry, I encountered an error while processing your request."
