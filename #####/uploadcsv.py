#1. uploadcsv.py

from flask import Flask, render_template, request, redirect, flash
import qrcode
from io import BytesIO
import base64
import mysql.connector
from datetime import datetime
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Database connection setup
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Advitha@11',
    'database': 'students',
    'port': 3306,
}

# Function to create a database connection
def create_db_connection():
    return mysql.connector.connect(**db_config)

# Define routes and functions
students = []

# -----------------------------Route 1----------------------------------------
# Route to student interface
@app.route('/')
def student_interface():
    return render_template('uploadstudentdata.html')

# -----------------------------Route 2----------------------------------------
# Route for uploading Excel files
@app.route('/upload_excel', methods=['POST'])
def upload_excel():
    if 'excel_file' in request.files:
        excel_file = request.files['excel_file']
        if excel_file.filename != '':
            students.clear()  # Clear the students list when a new file is uploaded
            try:
                if excel_file.filename.endswith(('.xls', '.xlsx')):
                    # For Excel files using pandas
                    excel_data = pd.read_excel(excel_file)
                    csv_reader = excel_data.to_dict(orient='records')
                else:
                    flash("Unsupported file format")
                    return redirect('/')

                for row in csv_reader:
                    # Ensure consistent field names with the Student model
                    student_data = {
                        'name': row['name'],
                        'class_name': row['class'],
                        'prnnumber': row['prnnumber'],
                        'contact': row['contact'],
                        'address': row['address'],
                        'dob': row['dob'].strftime('%d-%m-%Y'),
                    }
                    students.append(student_data)
                flash(f"Successfully uploaded: {excel_file.filename}")
            except Exception as e:
                flash(f"Error processing the file: {str(e)}")
    return redirect('/')

# -----------------------------Route 3----------------------------------------
# Route to generate ID cards with QR codes for uploaded students
@app.route('/generate_id_cards', methods=['POST'])
def generate_id_cards():
    qr_codes_and_id_cards = []

    if not students:
        return "No students to generate QR codes for"  # Handle the case when no students are available

    for student in students:
        # Generate student details with HTML formatting
        student_details = ", ".join([f"{key}: {value}" for key, value in student.items()])

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(student_details)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        qr_img.save(buffered, "PNG")
        qr_code_base64 = base64.b64encode(buffered.getvalue()).decode()

        # Render the libcard.html template with student data
        libcard_html = render_template('libcard.html', student=student, qr_code=qr_code_base64)
        qr_codes_and_id_cards.append(libcard_html)

    if qr_codes_and_id_cards:
        # Render the view_qrcodes.html template with the library cards
        return render_template('viewqrcodes.html', qr_codes_and_id_cards=qr_codes_and_id_cards)
    else:
        return "No QR Codes Generated"  # Handle the case when no QR codes are generated

# -----------------------------Route 4----------------------------------------
# Route to generate QR codes for registered students
@app.route('/generate_qr_codes', methods=['POST'])
def generate_qr_codes():
    cards = []  # Create an empty list to store card data

    for student in students:
        # Generate student details with HTML formatting
        student_details = ", ".join([f"{key}: {value}" for key, value in student.items()])

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(student_details)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        qr_img.save(buffered, "PNG")
        qr_code_base64 = base64.b64encode(buffered.getvalue()).decode()

        # Create a dictionary with student data and QR code
        card_data = {
            'student': student,
            'qr_code': qr_code_base64,
        }

        cards.append(card_data)  # Append the card data to the list

    if cards:
        # Render the libcard.html template with the list of cards
        return render_template('libcard.html', cards=cards)
    else:
        return "No QR Codes Generated"  # Handle the case when no QR codes are generated

# -----------------------------Route 5----------------------------------------
# Function to insert student data into the database
def insert_student_data(student):
    try:
        with create_db_connection() as conn:
            cursor = conn.cursor()
            dob_str = student['dob']
            dob_datetime = datetime.strptime(dob_str, '%d-%m-%Y')
            dob_formatted = dob_datetime.strftime('%Y-%m-%d')
            
            # Check if a record with the same PRN number already exists
            query = "SELECT * FROM degreestudents WHERE prnnumber = %s"
            cursor.execute(query, (student['prnnumber'],))
            existing_student = cursor.fetchone()

            if existing_student:
                # Update the existing record with the new data
                update_query = "UPDATE degreestudents SET name = %s, class = %s, contact = %s, address = %s, dob = %s WHERE prnnumber = %s"
                update_values = (student['name'], student['class_name'], student['contact'], student['address'], dob_formatted, student['prnnumber'])
                cursor.execute(update_query, update_values)
            else:
                # Insert a new record if no matching PRN number is found
                insert_query = "INSERT INTO degreestudents (name, class, prnnumber, contact, address, dob) VALUES (%s, %s, %s, %s, %s, %s)"
                insert_values = (student['name'], student['class_name'], student['prnnumber'], student['contact'], student['address'], dob_formatted)
                cursor.execute(insert_query, insert_values)

            conn.commit()
            print(f"Successfully uploaded {student['name']}'s data to the database.")
            return True
    except Exception as e:
        print(f"Failed to upload {student['name']}'s data to the database: {e}")
        return False

# -----------------------------Route 6----------------------------------------
# Route for uploading data to the database
@app.route('/upload_to_database', methods=['POST'])
def upload_to_database():
    if students:
        success_count = 0  # Initialize a count for successfully uploaded students
        for student in students:
            result = insert_student_data(student)
            if result:
                success_count += 1  # Increment the count for each successful upload

        if success_count > 0:
            flash(f"Successfully uploaded {success_count} student{'s' if success_count > 1 else ''} manually to the database.")

        # Clear the students list after uploading
        students.clear()

    return redirect('/')


#-----------------------Route 7 -----------------------

@app.route('/registered_students')
def registered_students():
    try:
        with create_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM degreestudents"
            cursor.execute(query)
            students = cursor.fetchall()

            # Format the date of birth in the desired format (day-month-year)
            for student in students:
                student['dob'] = student['dob'].strftime('%d-%m-%Y')

            return render_template('student_table.html', students=students)
    except Exception as e:
        print(f"Failed to fetch registered students: {e}")
        return "Error fetching registered students."

# Main entry point of the application
if __name__ == '__main__':
    app.run(debug=True)
