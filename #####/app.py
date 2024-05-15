
#app.py

from flask import Flask, render_template, request, redirect, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'generate_a_random_secret_key_here'

# Database connection setup
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Advitha@11',
    'database': 'students',
    'port': 3306,
}

def create_db_connection():
    return mysql.connector.connect(**db_config)

# Define routes and functions
students = []

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/manage_accounts')
def manage_accounts():
    return render_template('Accounts/createmainaccount.html')

@app.route('/registered_students')
def registered_students():
    try:
        with create_db_connection() as db:
            cursor = db.cursor(dictionary=True)
            query = "SELECT * FROM degreestudents"
            cursor.execute(query)
            students = cursor.fetchall()

            # Format the date of birth in the desired format (day-month-year)
            for student in students:
                student['dob'] = student['dob'].strftime('%d-%m-%Y')

        return render_template('registered_students.html', students=students)

    except Exception as e:
        # Log the error or display an error message to the user
        print(f"Error: {e}")
        flash("An error occurred while fetching student data.")
        return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)