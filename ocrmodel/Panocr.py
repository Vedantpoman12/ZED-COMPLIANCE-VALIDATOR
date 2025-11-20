from PIL import Image
import re
import pytesseract
# Open the image file
pan_card_image = Image.open('HardikPan.jpg')



# Extract text from the image
extracted_text = pytesseract.image_to_string(pan_card_image)

# Print the extracted text
print(extracted_text)



# 1. Define a list of keywords and phrases indicative of a PAN card
pan_keywords = [
    'PERMANENT ACCOUNT NUMBER',
    'INCOME TAX DEPARTMENT',
    'GOVT. OF INDIA',
    'NAME',
    'FATHER\'S NAME',
    'DATE OF BIRTH',
    'PAN'
]

# 2. Define a regular expression pattern for a PAN card number
# (5 uppercase letters, followed by 4 digits, followed by 1 uppercase letter)
pan_pattern = r'[A-Z]{5}[0-9]{4}[A-Z]{1}'

# Initialize a dictionary to store found indicators
found_indicators = {
    'keywords_found': [],
    'pan_number_found': None
}

# Convert extracted_text to uppercase for case-insensitive matching
extracted_text_upper = extracted_text.upper()

# 3. Iterate through the extracted_text to check for keywords/phrases
for keyword in pan_keywords:
    if keyword in extracted_text_upper:
        found_indicators['keywords_found'].append(keyword)

# 4. Use the regular expression to search for a PAN card number
pan_match = re.search(pan_pattern, extracted_text)
if pan_match:
    found_indicators['pan_number_found'] = pan_match.group(0)

# 5. Count how many of these indicators are found
num_keywords_found = len(found_indicators['keywords_found'])
num_pan_number_found = 1 if found_indicators['pan_number_found'] else 0
total_indicators_found = num_keywords_found + num_pan_number_found

print(f"Keywords found: {found_indicators['keywords_found']}")
print(f"Total indicators found: {total_indicators_found}")



# Define a regular expression pattern for a PAN card number
# (5 uppercase letters, followed by 4 digits, followed by 1 uppercase letter)
pan_pattern = r'[A-Z]{5}[0-9]{4}[A-Z]{1}'

# Use the regular expression to search for a PAN card number in extracted_text
pan_match = re.search(pan_pattern, extracted_text)

# If a match is found, extract the matched string (the PAN number)
extracted_pan_number = None
if pan_match:
    extracted_pan_number = pan_match.group(0)



# Define a regular expression pattern to capture the name after 'Name' or 'TH / Name'
# It looks for 'NAME' (case-insensitive) followed by any characters until a newline
name_pattern = r'(?:NAME|TH / NAME)\s*\n\s*([A-Z ]+)'

# Search for the pattern in the extracted_text
name_match = re.search(name_pattern, extracted_text_upper)

extracted_account_holder_name = None
if name_match:
    # Get the captured group (the name)
    extracted_account_holder_name = name_match.group(1).strip()


# Define a regular expression pattern to capture the date of birth
# It looks for 'DATE OF BIRTH' (case-insensitive) followed by any characters until a date in DD/MM/YYYY format
dob_pattern = r'(?:DATE OF BIRTH|DOB).*?(\d{2}/\d{2}/\d{4})'

# Search for the pattern in the extracted_text_upper with re.DOTALL to match across newlines
dob_match = re.search(dob_pattern, extracted_text_upper, re.DOTALL)

extracted_date_of_birth = None
if dob_match:
    # Get the captured group (the date of birth)
    extracted_date_of_birth = dob_match.group(1).strip()

print(f"Extracted PAN Number: {extracted_pan_number}")
print(f"Extracted Account Holder's Name: {extracted_account_holder_name}")
print(f"Extracted Date of Birth: {extracted_date_of_birth}")
