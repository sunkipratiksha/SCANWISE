# readcsvfile.py

import csv
from jinja2 import Template
from io import BytesIO
import base64
import qrcode

# Load the HTML template from the "generated_cards.html" file
with open(r'H:\My Drive\PythonPro\templates\generated_cards.html', 'r') as template_file:
    template_content = template_file.read()
    template = Template(template_content)

# Read student information from the CSV file and create library cards
cards = []

with open(r'H:\My Drive\PythonPro\templates\data.csv', 'r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    
    for row in csv_reader:
        # Check if any required fields have null values
        if row['full_name'] and row['class_name'] and row['roll_no'] and row['prn_number'] and row['contact_no'] and row['address']:
            student = {
                'full_name': row['full_name'],
                'class_name': row['class_name'],
                'roll_no': row['roll_no'],
                'prn_number': row['prn_number'],
                'contact_no': row['contact_no'],
                'address': row['address']
            }
            
            # Generate QR code
            student_details = f"Name: {student['full_name']}\nClass: {student['class_name']}\nRoll No: {student['roll_no']}\nPRN Number: {student['prn_number']}\nContact No: {student['contact_no']}\nAddress: {student['address']}"
            qr_code_img = qrcode.make(student_details)
            buffered = BytesIO()
            qr_code_img.save(buffered, "PNG")
            qr_code_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            # Add student data and QR code to the card list
            cards.append({'student': student, 'qr_code': qr_code_base64})

# Render the template with the card data and QR codes
html_output = template.render(cards=cards)

# Save the generated HTML content to a file
with open('generated_cards.html', 'w') as output_file:
    output_file.write(html_output)
