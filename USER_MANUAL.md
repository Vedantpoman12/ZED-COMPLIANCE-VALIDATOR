
# ZED AI Verification Assistant - User Manual

## 1. Introduction
Welcome to the **ZED AI Verification Assistant**. This tool uses Artificial Intelligence to automate the verification of identity documents (PAN, Aadhaar, GST) and provides an interactive chatbot to answer questions about compliance and document content.

---

## 2. Getting Started

### 2.1 Prerequisites
Before running the application, ensure you have the following installed:
*   **Python 3.8+**
*   **Tesseract OCR** (For text extraction)
*   **Poppler** (For PDF processing)
*   **Modern Web Browser** (Chrome, Edge, Firefox)

### 2.2 Installation
1.  **Unzip the project folder**.
2.  Open a terminal/command prompt in the project folder `ZED_FRONTEND`.
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Run the application:
    ```bash
    python app.py
    ```
5.  Open your browser and navigate to: `http://127.0.0.1:5000`.

---

## 3. Using the Dashboard

### 3.1 Home Page
Upon launching, you will see the main dashboard.
*   **Status Overview:** Displays the system's operational status.
*   **Navigation:**
    *   **Chatbot:** Go here for document verification and Q&A.
    *   **Gallery:** View previously uploaded and processed documents.
    *   **Settings:** (Optional) Configure system preferences.

---

## 4. Document Verification (Chatbot)

This is the core feature of the application.

### 4.1 How to Verify a Document
1.  Navigate to the **Chatbot** page.
2.  Look for the input area at the bottom of the screen.
3.  Click the **"Upload Document"** button (Paperclip Icon).
4.  Select a file from your computer.
    *   *Supported Formats:* `.jpg`, `.png`, `.pdf`
    *   *Supported Types:* PAN Card, Aadhaar Card, GST Certificate.
5.  Wait for the **"Analyzing document..."** indicator to finish.

### 4.2 Understanding the Report
Once analyzed, the chatbot will generate a **Verification Card**:
*   **Summary:** A brief description of what the document is (e.g., "This appears to be a PAN Card").
*   **Status Badge:**
    *   <span style="color:green">**Verified:**</span> The document is authentic and valid.
    *   <span style="color:orange">**Minor Issues:**</span> Valid but has low quality or minor errors.
    *   <span style="color:red">**Suspicious/Review:**</span> Potential fraud or unrecognizable document.
*   **Key Findings:** A list of extracted details (Name, ID Number) and any anomalies found.

### 4.3 Asking Questions
After a document is uploaded, you can "chat" with it.
*   *Example 1:* "What is the date of birth on this card?"
*   *Example 2:* "Does the name match 'Vedant'?"
*   *Example 3:* "Is this document valid for Bronze Certification?"

---

## 5. Troubleshooting

**Q: The system says "No text found".**
*   **A:** The image might be too blurry or dark. Try re-uploading a clearer image or a high-quality PDF scan.

**Q: I get a "Tesseract Not Found" error.**
*   **A:** Ensure Tesseract OCR is installed and the path in `app.py` matches your installation location (e.g., `C:\Program Files\Tesseract-OCR\tesseract.exe`).

**Q: The chatbot is slow to respond.**
*   **A:** This is normal if running on a laptop CPU. The AI requires significant processing power. Be patient, it usually takes 5-10 seconds.

---

## 6. Support
For technical issues or bug reports, please contact the development team or check the GitHub repository logs.
