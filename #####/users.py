# users.py

from flask import Flask, render_template, request, redirect, flash
import mysql.connector
from mysql.connector import IntegrityError

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Database connection setup
db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Advitha@11',
    database='students',
    port=3306
)

@app.route('/')  # Route for the main registration page
def home():
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'superadmin'")
    superadmin_count = cursor.fetchone()[0]
    cursor.close()

    # If the maximum superadmin limit is reached, disable registration
    if superadmin_count >= 3:
        return render_template('Accounts/registration_disabled.html')
    else:
        return render_template('Accounts/createmainaccount.html')

@app.route('/submit_main_account', methods=['POST'])
def submit_main_account():
    error_message = ""  # Initialize the error_message variable

    if request.method == 'POST':
        role = request.form.get('role')
        username = request.form.get('username')
        password = request.form.get('password')
        confirmpassword = request.form.get('confirmpassword')
        email = request.form.get('email')

        cursor = db.cursor()

        # Check if the role is superadmin and the maximum limit is reached
        if role == 'superadmin':
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'superadmin'")
            superadmin_count = cursor.fetchone()[0]

            if superadmin_count >= 3:
                flash('Maximum number of superadmin accounts reached. Registration is disabled.', 'danger')
                return render_template('Accounts/createmainaccount.html')

        if role in ['user', 'admin', 'superadmin']:
            if password == confirmpassword:
                try:
                    cursor.execute("INSERT INTO users (username, password, email, role) VALUES (%s, %s, %s, %s)", (username, password, email, role))
                    db.commit()
                    cursor.close()
                    flash(f'{role.capitalize()} account successfully created!', 'success')
                    flash(f'Account Created Successfully {username}', 'success')
                    return render_template('Accounts/accountsuccess.html')
                except IntegrityError as e:
                    flash('Username or email already exists. Please choose a different one.', 'danger')
                    error_message = 'Username or email already exists. Please choose a different one'
            else:
                flash('Password and Confirm Password do not match', 'danger')
                error_message = 'Password and Confirm Password do not match'
        else:
            flash('Invalid role selected', 'danger')
            error_message = 'Invalid role selected'

    return render_template('Accounts/createmainaccount.html', error_message=error_message)

@app.route('/login_superadmin')
def login_superadmin():
    # Add your code for the superadmin login page here
    return render_template('Accounts/loginsuperadmin.html')

if __name__ == "__main__":
    app.run(debug=True)
