from flask import Flask, render_template, request, redirect, url_for, jsonify
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import os

import re

# ---------- CONFIGURATION ----------
# UPDATE THIS PATH TO YOUR TESSERACT EXECUTABLE
# Example: r'C:\Program Files\Tesseract-OCR\tesseract.exe'
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Set the tesseract path
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


app = Flask(__name__)

# ---------- DEFAULT (Landing) PAGE ----------
@app.route('/')
def default():
    return render_template('default.html')

# ---------- LOGIN PAGE ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Simulate login process (you can add authentication logic here)
        return redirect(url_for('index'))
    return render_template('login.html')

# ---------- HOME PAGE ----------
@app.route('/home')
def home():
    return render_template('home.html')

# ---------- INDEX PAGE (after login) ----------
@app.route('/index')
def index():
    return render_template('index.html')

# ---------- CHATBOT PAGE ----------
@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')


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
                # Define Poppler path
                poppler_path = os.path.join(os.getcwd(), 'poppler-25.07.0', 'Library', 'bin')
                pages = convert_from_path(filepath, poppler_path=poppler_path)
                for page in pages:
                    text += pytesseract.image_to_string(page)
            else:
                image = Image.open(filepath)
                text = pytesseract.image_to_string(image)

            # Convert backslashes to forward slashes for web URL
            web_image_path = filepath.replace('\\', '/')
            
            # Verify PAN Card
            verification_result = verify_pan_card(text)
            
            results.append({
                'image_path': web_image_path,
                'extracted_text': text.strip(),
                'verification': verification_result
            })

    return render_template('result.html', results=results)

def verify_pan_card(ocr_text):
    """
    Verifies if the extracted text contains a valid PAN card number.
    PAN Format: 5 letters, 4 numbers, 1 letter (e.g., ABCDE1234F)
    """
    if not ocr_text:
        return {'status': 'Invalid', 'pan_number': None, 'message': 'No text extracted'}
    
    # Regex pattern for PAN card
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

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
