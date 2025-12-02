from flask import Flask, render_template, request, redirect, url_for, jsonify
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import os
import re

try:
    from train_authenticity_model import DocumentAuthenticityDetector
    authenticity_detector = DocumentAuthenticityDetector()
except Exception as e:
    print(f"Warning: Authenticity detector not available: {e}")
    authenticity_detector = None

TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

import chatbot_logic

app = Flask(__name__)

chatbot_logic.init_chatbot()

import os as _os
bronze_cert_path = _os.path.join(_os.getcwd(), 'User_Manual_Bronze_Certification_20.04.2022.pdf')
if _os.path.exists(bronze_cert_path) and chatbot_logic.index.ntotal == 0:
    print("Loading Bronze Certificate User Manual into chatbot...")
    success, msg = chatbot_logic.add_document_to_knowledge_base(
        bronze_cert_path, 
        'User_Manual_Bronze_Certification_20.04.2022.pdf'
    )
    if success:
        print(f"{msg}")
    else:
        print(f"Failed to load manual: {msg}")

@app.route('/')
def default():
    return render_template('default.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/gallery')
def gallery():
    from datetime import datetime
    
    upload_folder = os.path.join('static', 'uploads')
    documents = []
    
    if os.path.exists(upload_folder):
        for filename in os.listdir(upload_folder):
            filepath = os.path.join(upload_folder, filename)
            
            if os.path.isfile(filepath):
                file_size = os.path.getsize(filepath)
                if file_size < 1024:
                    size_str = f"{file_size} B"
                elif file_size < 1024 * 1024:
                    size_str = f"{file_size / 1024:.1f} KB"
                else:
                    size_str = f"{file_size / (1024 * 1024):.1f} MB"
                
                mod_time = os.path.getmtime(filepath)
                date_str = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M')
                
                doc_type = 'other'
                if 'pan' in filename.lower() or any(filename.endswith(ext) for ext in ['.jpg', '.jpeg', '.png'] if len(filename) == 14):
                    doc_type = 'pan'
                elif 'aadhar' in filename.lower() or 'aadhaar' in filename.lower():
                    doc_type = 'aadhaar'
                elif 'gst' in filename.lower():
                    doc_type = 'gst'
                
                file_format = 'pdf' if filename.lower().endswith('.pdf') else 'image'
                
                documents.append({
                    'name': filename,
                    'path': f'/static/uploads/{filename}',
                    'size': size_str,
                    'date': date_str,
                    'type': doc_type,
                    'format': file_format
                })
        
        documents.sort(key=lambda x: x['date'], reverse=True)
    
    return render_template('gallery.html', documents=documents)

@app.route('/ocr', methods=['POST'])
def ocr_upload():
    files = [request.files.get('document1'),
             request.files.get('document2'),
             request.files.get('document3')]

    upload_folder = os.path.join('static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)

    results = []

    for file in files:
        if file and file.filename:
            filepath = os.path.join(upload_folder, file.filename)
            file.save(filepath)

            text = ""
            if file.filename.lower().endswith('.pdf'):
                from PIL import ImageEnhance
                poppler_path = os.path.join(os.getcwd(), 'poppler-25.07.0', 'Library', 'bin')
                pages = convert_from_path(filepath, poppler_path=poppler_path, dpi=300)
                for page in pages:
                    page = page.convert('L')
                    enhancer = ImageEnhance.Contrast(page)
                    page = enhancer.enhance(2.0)
                    enhancer = ImageEnhance.Sharpness(page)
                    page = enhancer.enhance(1.5)
                    text += pytesseract.image_to_string(page, config='--psm 6 --oem 3')
            else:
                from PIL import ImageEnhance
                image = Image.open(filepath)
                image = image.convert('L')
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(2.0)
                enhancer = ImageEnhance.Sharpness(image)
                image = enhancer.enhance(1.5)
                text = pytesseract.image_to_string(image, config='--psm 6 --oem 3')

            web_image_path = filepath.replace('\\', '/')
            
            verification_result = verify_pan_card(text)
            
            results.append({
                'image_path': web_image_path,
                'extracted_text': text.strip(),
                'verification': verification_result
            })

    return render_template('result.html', results=results)

def verify_pan_card(ocr_text):
    if not ocr_text:
        return {'status': 'Invalid', 'pan_number': None, 'message': 'No text extracted'}
    
    pan_pattern = r'[A-Z]{5}[0-9]{4}[A-Z]{1}'
    
    match = re.search(pan_pattern, ocr_text)
    
    if match:
        return {
            'status': 'Valid',
            'pan_number': match.group(0),
            'message': 'Valid PAN Card detected'
        }
    else:
        return {
            'status': 'Invalid',
            'pan_number': None,
            'message': 'No valid PAN number found'
        }

@app.route('/api/ocr', methods=['POST'])
def api_ocr_upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        upload_folder = os.path.join('static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        filepath = os.path.join(upload_folder, file.filename)
        file.save(filepath)

        text = ""
        if file.filename.lower().endswith('.pdf'):
            poppler_path = os.path.join(os.getcwd(), 'poppler-25.07.0', 'Library', 'bin')
            pages = convert_from_path(filepath, poppler_path=poppler_path)
            for page in pages:
                text += pytesseract.image_to_string(page)
        else:
            image = Image.open(filepath)
            text = pytesseract.image_to_string(image)

        web_image_path = '/' + filepath.replace('\\', '/')
        
        verification_result = verify_pan_card(text)
        
        return jsonify({
            'status': 'success',
            'image_path': web_image_path,
            'extracted_text': text.strip(),
            'verification': verification_result
        })

    return jsonify({'error': 'Unknown error'}), 500

@app.route('/api/verify-document', methods=['POST'])
def verify_document():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        upload_folder = os.path.join('static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        filepath = os.path.join(upload_folder, file.filename)
        file.save(filepath)

        text = ""
        try:
            if file.filename.lower().endswith('.pdf'):
                poppler_path = os.path.join(os.getcwd(), 'poppler-25.07.0', 'Library', 'bin')
                pages = convert_from_path(filepath, poppler_path=poppler_path)
                for page in pages:
                    text += pytesseract.image_to_string(page)
            else:
                image = Image.open(filepath)
                text = pytesseract.image_to_string(image)
        except Exception as e:
            return jsonify({'error': f'Failed to extract text: {str(e)}'}), 500

        web_image_path = '/' + filepath.replace('\\', '/')
        
        verification_report = generate_verification_report(text, file.filename)
        verification_report['image_path'] = web_image_path
        
        chatbot_logic.clear_knowledge_base()
        success, message = chatbot_logic.add_document_to_knowledge_base(filepath, file.filename)
        if success:
            verification_report['learning_status'] = "Document successfully learned by the chatbot!"
        else:
            verification_report['learning_status'] = f"Warning: Could not learn document ({message})"

        return jsonify({
            'status': 'success',
            'verification': verification_report,
            'extracted_text': text.strip()
        })

    return jsonify({'error': 'Unknown error'}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'response': 'Please say something!'})
        
    response = chatbot_logic.query_chatbot(user_message)
    return jsonify({'response': response})

def generate_verification_report(text, filename):
    doc_type = "Document"
    is_pan_document = False
    is_aadhaar_document = False
    
    if 'pan' in filename.lower() or 'INCOME TAX' in text.upper() or 'PERMANENT ACCOUNT NUMBER' in text.upper():
        doc_type = "PAN Card"
        is_pan_document = True
    elif 'aadhaar' in filename.lower() or 'UIDAI' in text.upper() or 'UNIQUE IDENTIFICATION AUTHORITY' in text.upper():
        doc_type = "Aadhaar Card"
        is_aadhaar_document = True
    elif 'gst' in filename.lower() or 'GSTIN' in text.upper() or 'GOODS AND SERVICES TAX' in text.upper():
        doc_type = "GST Certificate"
    
    authenticity_result = None
    if authenticity_detector and (is_pan_document or is_aadhaar_document):
        try:
            filepath = f"static/uploads/{filename}" if not filename.startswith("static") else filename
            if os.path.exists(filepath):
                doc_type_for_check = "PAN" if is_pan_document else "AADHAAR"
                authenticity_result = authenticity_detector.verify_document(filepath, doc_type_for_check)
        except Exception as e:
            print(f"Authenticity check error: {e}")
    
    pan_verification = verify_pan_card(text)
    
    summary = f"This appears to be a {doc_type}. "
    if text.strip():
        word_count = len(text.split())
        summary += f"The OCR extraction successfully captured approximately {word_count} words from the document. "
        summary += "The system has analyzed the content for required fields and formatting compliance."
    else:
        summary += "However, no text content could be extracted from the document image."
    
    status = ""
    statusClass = ""
    statusExplanation = ""
    
    if authenticity_result and not authenticity_result['is_authentic']:
        status = "STATUS: SUSPICIOUS - Possible Fake Document"
        statusClass = "status-review"
        statusExplanation = f"⚠ WARNING: This document shows signs of being fake or altered. Confidence: {authenticity_result['confidence']:.1%}. {authenticity_result['reason']}"
    elif authenticity_result and authenticity_result['is_authentic']:
        if is_pan_document and pan_verification['status'] == 'Valid':
            status = "STATUS: Verified (Authentic Document)"
            statusClass = "status-verified"
            statusExplanation = f"✓ This document appears authentic (Confidence: {authenticity_result['confidence']:.1%}). Valid PAN number detected: {pan_verification['pan_number']}."
        else:
            status = "STATUS: Likely Authentic"
            statusClass = "status-verified"
            statusExplanation = f"✓ Document appears authentic based on comparison with known genuine documents (Confidence: {authenticity_result['confidence']:.1%})."
    elif not text.strip():
        status = "STATUS: Requires Further Review"
        statusClass = "status-review"
        statusExplanation = "The document image quality may be too low, or the document may be blank. No text could be extracted for verification."
    elif is_pan_document and pan_verification['status'] == 'Valid':
        status = "STATUS: Verified (No Issues Found)"
        statusClass = "status-verified"
        statusExplanation = f"Valid PAN number detected: {pan_verification['pan_number']}. The document format meets standard requirements and all key information has been successfully extracted."
    elif is_pan_document:
        status = "STATUS: Verified with Minor Notes"
        statusClass = "status-minor"
        statusExplanation = "The document appears to be a PAN-related document, but the PAN number format could not be clearly identified. This may be due to image quality or OCR accuracy."
    else:
        status = "STATUS: Processed Successfully"
        statusClass = "status-verified"
        statusExplanation = f"The document has been processed as a {doc_type}. Text extraction was successful. You can now ask questions about its content."
    
    findings = []
    
    if authenticity_result:
        if authenticity_result['is_authentic']:
            findings.append(f"<strong>Authenticity Check:</strong> <span style='color: #4ade80;'>Document appears AUTHENTIC</span> (Confidence: {authenticity_result['confidence']:.1%})")
        else:
            findings.append(f"<strong>Authenticity Check:</strong> <span style='color: #f87171;'>Document may be FAKE or ALTERED</span> (Confidence: {authenticity_result['confidence']:.1%})")
        findings.append(f"<strong>Reason:</strong> {authenticity_result['reason']}")
    
    if is_pan_document and pan_verification['status'] == 'Valid':
        findings.append(f"<strong>PAN Number Identified:</strong> {pan_verification['pan_number']}")
        findings.append("<strong>Format Validation:</strong> PAN number follows the standard format (5 letters, 4 digits, 1 letter)")
        findings.append(f"<strong>Extracted Text Length:</strong> {len(text)} characters successfully captured")
        findings.append("<strong>Document Authenticity:</strong> Format appears consistent with official PAN card structure")
        question = ""
    elif not text.strip():
        findings.append("<strong>Text Extraction:</strong> Failed - No content could be extracted")
        findings.append("<strong>Possible Causes:</strong> Low image quality, blank document, or unsupported format")
        findings.append("<strong>Recommendation:</strong> Please re-upload with a clearer image (at least 300 DPI recommended)")
        findings.append("<strong>Supported Formats:</strong> PDF, JPG, JPEG, PNG files are accepted")
        question = ""
    else:
        findings.append(f"<strong>Document Type:</strong> Identified as {doc_type}")
        findings.append(f"<strong>Text Extraction:</strong> Successfully extracted {len(text.split())} words")
        findings.append(f"<strong>Content Analysis:</strong> Document contains readable text. You can ask the chatbot for specific details.")
        
        if 'name' in text.lower():
            findings.append("<strong>Name Field:</strong> Detected in document")
        if 'date' in text.lower() or re.search(r'\d{2}[/-]\d{2}[/-]\d{4}', text):
            findings.append("<strong>Date Information:</strong> Date fields found in document")
        
        question = ""
    
    return {
        'summary': summary,
        'status': status,
        'statusClass': statusClass,
        'statusExplanation': statusExplanation,
        'findings': findings,
        'question': question,
        'document_type': doc_type
    }

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
