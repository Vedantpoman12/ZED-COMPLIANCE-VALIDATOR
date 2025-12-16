
# ZED AI Verification Assistant

![Status](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## 📄 Project Overview
**ZED AI Verification Assistant** is an intelligent web-based platform designed to automate the verification of identity and compliance documents (PAN, Aadhaar, GST). It leverages **OCR (Optical Character Recognition)**, **Machine Learning**, and **LLM-based RAG (Retrieval-Augmented Generation)** to provide a seamless, secure, and interactive verification experience.

This project was developed as a **Mini Project** to demonstrate the application of AI in minimizing manual bureaucratic work.

## ✨ Key Features
*   **Auto-Verification:** Automatically extracts text via Tesseract OCR and verifies ID formats (Regex-based).
*   **Fraud Detection:** Uses a ML similarity model (FAISS) to flag suspicious or altered documents.
*   **AI Chatbot:** "Chat" with your documents. Ask questions like *"What is the DOB?"* or *"Is this valid for Bronze Certification?"*.
*   **Knowledge Base:** Pre-trained on official manuals (Bronze Certification, General Instructions) to answer compliance queries.
*   **Secure & Local:** All processing happens locally (Local LLM via Ollama), ensuring data privacy.

## 🛠️ Tech Stack
*   **Backend:** Python, Flask
*   **Frontend:** HTML5, CSS3, JavaScript
*   **AI & ML:** 
    *   `LangChain` (Orchestration)
    *   `FAISS` (Vector Database)
    *   `Scikit-learn` & `Numpy` (ML Logic)
    *   `Ollama` (Local LLM Runner)
*   **OCR:** Tesseract 5.0, Poppler (PDF2Image)

## 🚀 Installation & Setup

### Prerequisites
*   Python 3.8 or higher
*   [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) installed.
*   [Poppler](http://blog.alivate.com.au/poppler-windows/) installed (for PDF support).

### Steps
1.  **Clone the Repo:**
    ```bash
    git clone https://github.com/Vedantpoman12/identity-ai.git
    cd identity-ai
    ```

2.  **Create Virtual Env:**
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the App:**
    ```bash
    python app.py
    ```

5.  **Access the Dashboard:**
    Open `http://127.0.0.1:5000` in your browser.

## 📂 Project Structure
```
ZED_FRONTEND/
├── app.py                  # Main Flask Server
├── chatbot_logic.py        # OCR & RAG Pipeline
├── train_authenticity_model.py # Fraud Detection Logic
├── static/                 # CSS, Images, Uploads
├── templates/              # HTML Frontend
├── authentic_docs.faiss    # ML Model Index
└── requirements.txt        # Dependencies
```

## 👥 Contributors
*   **Vedant Poman** - *Lead Developer*
*   [Add Teammate Name]
*   [Add Teammate Name]

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
