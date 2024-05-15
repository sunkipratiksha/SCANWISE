# test.py

from flask import Flask, render_template, request, redirect, flash, session , make_response, url_for
from werkzeug.security import generate_password_hash, check_password_hash

import qrcode
from io import BytesIO
import base64
import mysql.connector
from mysql.connector.errors import IntegrityError

from datetime import datetime
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Database connection setup
db_config = {
    'host': '192.168.0.109',
    'user': 'pratiksha',
    'password': 'pratiksha@123',
    'database': 'students',
    'port': 3306,
}

def create_db_connection():
    return mysql.connector.connect(**db_config)

students = []

# Default route to redirect to the dashboard
@app.route('/')
def home():
    return redirect('/dashboard')


#------------------------------ROUTE 1---------------------------------
# Route for the dashboard
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

#------------------------------ROUTE 2---------------------------------

# Route to manage accounts
@app.route('/manage_accounts')
def manage_accounts():
    return render_template('Accounts/createmainaccount.html')

#------------------------------ROUTE 3---------------------------------


# Route for registered students dashboard
@app.route('/registered_students_dashboard', methods=['GET', 'POST'])
def registered_students_dashboard():
    selected_class = None
    try:
        with create_db_connection() as db:
            cursor = db.cursor(dictionary=True)

            # Handle form submission
            if request.method == 'POST':
                selected_class = request.form.get('classFilter')
                if selected_class and selected_class.lower() != 'all':
                    query = "SELECT * FROM degreestudents WHERE LOWER(class) = LOWER(%s)"
                    cursor.execute(query, (selected_class,))
                else:
                    query = "SELECT * FROM degreestudents"
                    cursor.execute(query)
            else:
                query = "SELECT * FROM degreestudents"
                cursor.execute(query)

            students = cursor.fetchall()

            # Format the date of birth in the desired format (day-month-year)
            for student in students:
                student['dob'] = student['dob'].strftime('%d-%m-%Y')

        return render_template('registered_students.html', students=students, selected_class=selected_class)

    except Exception as e:
        # Log the error or display an error message to the user
        print(f"Error: {e}")
        flash("An error occurred while fetching student data.")
        return redirect('/')

#------------------------------ROUTE 4---------------------------------

@app.route('/upload')
def uploaddata():
    return render_template('uploadstudentdata.html')

#------------------------------ROUTE 5---------------------------------

# Route to submit main account
@app.route('/submit_main_account', methods=['POST'])
def submit_main_account():
    error_message = ""  # Initialize the error_message variable

    if request.method == 'POST':
        # Call the create_db_connection function to get the database connection
        with create_db_connection() as db:
            cursor = db.cursor()

            role = 'superadmin'  # Fixed role as superadmin for this form
            username = request.form.get('username')
            password = request.form.get('password')
            confirmpassword = request.form.get('confirmpassword')
            email = request.form.get('email')

            # Check if the maximum limit of superadmin accounts is reached
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'superadmin'")
            superadmin_count = cursor.fetchone()[0]

            if superadmin_count >= 1:
                flash('A superadmin account already exists. Further registration is disabled.', 'danger')
                return render_template('Accounts/registration_disabled.html')

            if password == confirmpassword:
                try:
                    cursor.execute("INSERT INTO users (username, password, email, role) VALUES (%s, %s, %s, %s)", (username, password, email, role))
                    db.commit()
                    cursor.close()
                    flash('Superadmin account successfully created!', 'success')
                    flash(f'Account Created Successfully {username}', 'success')
                    return render_template('ACCOUNTS/accountsuccess.html')
                except IntegrityError as e:
                    flash('Username or email already exists. Please choose a different one.', 'danger')
                    error_message = 'Username or email already exists. Please choose a different one'
            else:
                flash('Password and Confirm Password do not match', 'danger')
                error_message = 'Password and Confirm Password do not match'

    return render_template('Accounts/createmainaccount.html', error_message=error_message)

#------------------------------ROUTE 6---------------------------------
@app.route('/process_superadmin_login', methods=['POST'])
def process_superadmin_login():
    error_message = ""

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        print(f"Entered username: {username}, entered password: {password}")  # Add this line for debugging

        try:
            # Call the create_db_connection function to get the database connection
            with create_db_connection() as db:
                cursor = db.cursor(dictionary=True)

                # Check if the entered credentials match a superadmin account
                cursor.execute("SELECT * FROM users WHERE username = %s AND role = 'superadmin'", (username,))
                superadmin = cursor.fetchone()

                if superadmin and check_password_hash(superadmin['password'], password):
                    # Successful login, store user information in session
                    session['user_id'] = superadmin['id']
                    flash('Login successful!', 'success')
                    print("Redirecting to SUPERADMIN.html")  # Add this line for debugging
                    return redirect(url_for('superadmin_dashboard'))  # Update this line to redirect to the superadmin_dashboard route
                else:
                    # Invalid credentials, show error message
                    flash('Invalid username or password for superadmin.', 'danger')
                    error_message = 'Invalid username or password'
        except Exception as e:
            flash(f"An error occurred during login: {str(e)}", 'danger')
            return render_template('Accounts/loginsuperadmin.html', error_message="An error occurred during login.")

    print("Login failed")  # Add this line for debugging
    return render_template('Accounts/loginsuperadmin.html', error_message=error_message)



#------------------------------ROUTE 7---------------------------------
# Route for superadmin login
@app.route('/login_superadmin')
def login_superadmin():
    return render_template('Accounts/loginsuperadmin.html')


#------------------------------ROUTE 8---------------------------------

@app.route('/set_cookie')
def set_cookie():
    response = make_response('Cookie set!')
    response.set_cookie('myCookie', 'myValue', secure=True)
    return response

#-------------------------------------ROUTE 9----------------------------------------------------------

# Route for student interface
@app.route('/student_interface')
def student_interface():
    return render_template('uploadstudentdata.html')


#------------------------------ROUTE 10---------------------------------

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
    return redirect('/upload')


#------------------------------ROUTE 11---------------------------------


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
        # Render the viewqrcodes.html template with the library cards
        return render_template('viewqrcodes.html', qr_codes_and_id_cards=qr_codes_and_id_cards)
    else:
        return "No QR Codes Generated"  # Handle the case when no QR codes are generated

#------------------------------ROUTE 12---------------------------------

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

#------------------------------ROUTE 13--------------------------------
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


#------------------------------ROUTE 14---------------------------------

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

    return redirect('/upload_students')

#------------------------------ROUTE 15---------------------------------


# Route to view registered students
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
        return redirect('/upload')
    
#------------------------------ROUTE 16---------------------------------


# Route to go to the dashboard
@app.route('/go_to_dashboard')
def go_to_dashboard():
    return redirect('/dashboard')


@app.route('/sacreates')
def sacreates():
    # Your view logic here
    return render_template('SAcreates.html')



if __name__ == '__main__':
    app.run(debug=True)



