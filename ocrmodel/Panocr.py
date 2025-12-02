from PIL import Image
import re
import pytesseract

pan_card_image = Image.open('HardikPan.jpg')

extracted_text = pytesseract.image_to_string(pan_card_image)

print(extracted_text)

pan_keywords = [
    'PERMANENT ACCOUNT NUMBER',
    'INCOME TAX DEPARTMENT',
    'GOVT. OF INDIA',
    'NAME',
    'FATHER\'S NAME',
    'DATE OF BIRTH',
    'PAN'
]

pan_pattern = r'[A-Z]{5}[0-9]{4}[A-Z]{1}'

found_indicators = {
    'keywords_found': [],
    'pan_number_found': None
}

extracted_text_upper = extracted_text.upper()

for keyword in pan_keywords:
    if keyword in extracted_text_upper:
        found_indicators['keywords_found'].append(keyword)

pan_match = re.search(pan_pattern, extracted_text)
if pan_match:
    found_indicators['pan_number_found'] = pan_match.group(0)

num_keywords_found = len(found_indicators['keywords_found'])
num_pan_number_found = 1 if found_indicators['pan_number_found'] else 0
total_indicators_found = num_keywords_found + num_pan_number_found

print(f"Keywords found: {found_indicators['keywords_found']}")
print(f"Total indicators found: {total_indicators_found}")

pan_pattern = r'[A-Z]{5}[0-9]{4}[A-Z]{1}'

pan_match = re.search(pan_pattern, extracted_text)

extracted_pan_number = None
if pan_match:
    extracted_pan_number = pan_match.group(0)

name_pattern = r'(?:NAME|TH / NAME)\s*\n\s*([A-Z ]+)'

name_match = re.search(name_pattern, extracted_text_upper)

extracted_account_holder_name = None
if name_match:
    extracted_account_holder_name = name_match.group(1).strip()

dob_pattern = r'(?:DATE OF BIRTH|DOB).*?(\d{2}/\d{2}/\d{4})'

dob_match = re.search(dob_pattern, extracted_text_upper, re.DOTALL)

extracted_date_of_birth = None
if dob_match:
    extracted_date_of_birth = dob_match.group(1).strip()

print(f"Extracted PAN Number: {extracted_pan_number}")
print(f"Extracted Account Holder's Name: {extracted_account_holder_name}")
print(f"Extracted Date of Birth: {extracted_date_of_birth}")
