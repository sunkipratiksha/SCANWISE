# alldashboard.py
# pip install Flask
# pip install mysql-connector-python
# pip install pandas
# pip install qrcode
# pip install python-dateutil
# pip install logging
# pip install pillow
# pip install qrcode
# pip install opencv-python-headless
# pip install pyzbar






from flask import Flask, render_template, request, redirect, url_for, flash, session, get_flashed_messages
import mysql.connector
import pandas as pd
import qrcode
import base64
from dateutil import parser
from io import BytesIO
from base64 import b64encode
import logging
from mysql.connector import IntegrityError, connect
import os
import cv2
from pyzbar.pyzbar import decode
import time
from PIL import Image
import qrcode
from datetime import datetime, timedelta, date
import traceback
from datetime import datetime 
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database configuration
db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'Advitha@11',   #  'pratiksha@123',
    'database': 'scanwise',
    'port': 3306,
}



# Establish a connection to the database
db_connection = mysql.connector.connect(**db_config)
cursor = db_connection.cursor()

# Flag to check if a system admin already exists
system_admin_created = False

def get_db_cursor():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    return connection, cursor

def close_db_connection(connection, cursor):
    cursor.close()
    connection.close()

@app.route('/')
def landing_page():
    return render_template('systemtemplates/landingpage.html')

@app.route('/start')
def start():
    return render_template('systemtemplates/start.html')



# ...

@app.route('/create_main_account', methods=['GET', 'POST'])
def create_main_account():
    global system_admin_created
    error_message = None

    if request.method == 'POST':
        connection, cursor = get_db_cursor()

        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirmpassword']
        phone = request.form['phone']

        if password != confirm_password:
            error_message = "Password and confirm password do not match."
            close_db_connection(connection, cursor)
            return render_template('systemtemplates/createmainaccount.html', error_message=error_message)

        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'System Admin'")
        system_admin_count = cursor.fetchone()[0]

        if system_admin_count >= 1:
            flash('A system admin account already exists. Further registration is disabled.', 'danger')
            close_db_connection(connection, cursor)
            return render_template('systemtemplates/registration_disabled.html')

        role = 'System Admin'
        insert_query = "INSERT INTO users (username, passwd, phone, role) VALUES (%s, %s, %s, %s)"
        insert_data = (username, password, phone, role)  # Note: No password hashing here

        try:
            cursor.execute(insert_query, insert_data)
            connection.commit()

            system_admin_created = True

            flash('System admin account successfully created!', 'success')
            return render_template('systemtemplates/account_success.html')
        except IntegrityError as e:
            flash('Username or phone number already exists. Please choose different ones.', 'danger')
            error_message = 'Username or phone number already exists. Please choose different ones.'
        finally:
            close_db_connection(connection, cursor)

    return render_template('systemtemplates/createmainaccount.html', error_message=error_message)




@app.route('/login_al', methods=['GET', 'POST'])
def login_al():
    return render_template('systemtemplates/loginAL.html')

@app.route('/registration_disabled')
def registration_disabled():
    return render_template('systemtemplates/registration_disabled.html')

@app.route('/account_success')
def account_success():
    return render_template('systemtemplates/account_success.html')

@app.route('/superadmin_login', methods=['GET', 'POST'])
def superadmin_login():
    try:
        connection, cursor = get_db_cursor()

        if request.method == 'POST':
            entered_username = request.form.get('username')
            entered_password = request.form.get('password')

            cursor.execute("SELECT username, passwd, role FROM users WHERE username = %s LIMIT 1", (entered_username,))
            result = cursor.fetchone()

            if result:
                system_admin_username, stored_password, user_role = result

                if entered_password == stored_password and user_role == 'System Admin':
                    return redirect(url_for('SA_dashboard'))
                else:
                    flash('Login failed! Please check your username and password.', 'danger')
            else:
                flash('Login failed! Please check your username and password.', 'danger')

        return render_template('systemtemplates/SAlogin.html')

    except Exception as e:
        flash('An error occurred during login. Please try again.', 'danger')

    finally:
        close_db_connection(connection, cursor)

# ---------------------------------------------------------------------------------------------------------------


@app.route('/SA_dashboard', methods=['GET', 'POST'])
def SA_dashboard():
    try:
        connection, cursor = get_db_cursor()

        # Fetch counts based on roles excluding the first row
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'bookadmin' AND id != 1")
        book_admins_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'librarian' AND id != 1")
        librarians_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admissionstaff' AND id != 1")
        admission_staff_count = cursor.fetchone()[0]

        # Fetch total accounts count based on usernames excluding the first row
        cursor.execute("SELECT COUNT(*) FROM users WHERE id != 1")
        total_accounts_count = cursor.fetchone()[0]

        # Fetch count of courses and registered students (modify these queries based on your actual structure)
        cursor.execute("SELECT COUNT(*) FROM courses")
        courses_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM degreestudents")
        registered_students_count = cursor.fetchone()[0]

        return render_template('systemtemplates/SA_dashboardinfo.html',
                               book_admins_count=book_admins_count,
                               librarians_count=librarians_count,
                               admission_staff_count=admission_staff_count,
                               total_accounts_count=total_accounts_count,
                               courses_count=courses_count,
                               registered_students_count=registered_students_count)

    except Exception as e:
        print(f"Failed to fetch dashboard information: {e}")
        return "Error fetching dashboard information."

    finally:
        close_db_connection(connection, cursor)


#--------------------------------------------------------------------------



# ---------------------------------------------------------------------------------------------------------------


# Add the route for SA_dashboard_info
@app.route('/SA_dashboard_info')
def SA_dashboard_info():
    # Render the SA_dashboardinfo.html page
    return render_template('systemtemplates/SA_dashboardinfo.html')

# ---------------------------------------------------------------------------------------------------------------


# Route for SA profile page
@app.route('/SA_profile')
def SA_profile():
    return render_template('systemtemplates/SAprofile.html')

#---------------------------------------------------------------------------------------------

# Route for SA profile page
@app.route('/ASprofile')
def ASprofile():
    return render_template('systemtemplates/ASprofile.html')


# ---------------------------------------------------------------------------------------------------------------



# Initialize 'show_password_column' within a request context
@app.before_request
def before_request():
    if 'show_password_column' not in session:
        session['show_password_column'] = True  # Initial state is True



# Flask route for toggling password column
@app.route('/toggle_password_column', methods=['POST'])
def toggle_password_column():
    # Your logic to toggle the password column here
    session['show_password_column'] = not session.get('show_password_column', True)
    return redirect(url_for('manage_users'))

# ---------------------------------------------------------------------------------------------------------------
# Flask route to manage users
@app.route('/manage_users', methods=['GET', 'POST'])
def manage_users():
    try:
        # Ensure MySQL connection is established
        if not db_connection.is_connected():
            db_connection.connect()

        cursor = db_connection.cursor()

        # If the request is a POST (form submission)
        if request.method == 'POST':
            role_filter = request.form.get('RoleFilter')
            # Filter the query based on the selected role
            if role_filter == 'all':
                query = "SELECT username, created, role, passwd FROM users WHERE role != 'System Admin'"
            else:
                query = f"SELECT username, created, role, passwd FROM users WHERE role = '{role_filter}' AND role != 'System Admin'"
        else:
            # If it's a GET request, retrieve all users (excluding the system admin)
            query = "SELECT username, created, role, passwd FROM users WHERE role != 'System Admin'"

        # Execute the query
        cursor.execute(query)

        users = []
        for row in cursor.fetchall():
            username, created, role, password = row
            # Format date as dd/mm/yyyy
            formatted_date = created.strftime('%d/%m/%Y')
            # Format time as 12-hour time
            formatted_time = created.strftime('%I:%M %p')

            user_data = {'username': username, 'created_date': formatted_date, 'created_time': formatted_time, 'role': role, 'password': password}
            users.append(user_data)

        # Render the manage_users.html template and pass the user data and show_password_column variable
        return render_template('systemtemplates/manage_users.html', users=users, show_password_column=session['show_password_column'])

    except Exception as e:
        # Handle exceptions, print or log the error
        flash('Error retrieving user data. Please try again.', 'danger')

    finally:
        # Close the cursor and MySQL connection
        if 'cursor' in locals() and cursor:
            cursor.close()
        if db_connection.is_connected():
            db_connection.close()

    # If an exception occurs or the request method is not POST, render the manage_users.html template
    return render_template('systemtemplates/manage_users.html', users=[], show_password_column=session['show_password_column'])

# ---------------------------------------------------------------------------------------------------------------
# Flask route to delete users based on username
@app.route('/delete_user', methods=['POST'])
def delete_user():
    try:
        # Ensure MySQL connection is established
        if not db_connection.is_connected():
            db_connection.connect()

        # Open cursor
        cursor = db_connection.cursor()

        # Get the username from the form submission
        username_to_delete = request.form.get('username')

        # Perform the delete operation in the database
        delete_query = f"DELETE FROM users WHERE username = '{username_to_delete}'"
        cursor.execute(delete_query)
        db_connection.commit()

        # Redirect back to the manage_users page
        return redirect(url_for('manage_users'))

    except mysql.connector.Error as e:
        # Handle MySQL errors
        print(f"MySQL Error: {e}")
        if "MySQL server has gone away" in str(e):
            # Reconnect to the MySQL server
            db_connection.reconnect(attempts=3, delay=0)
            print("Reconnected to MySQL server")
        else:
            flash('Error deleting user. Please try again.', 'danger')

    finally:
        # Close the cursor and MySQL connection
        if 'cursor' in locals() and cursor:
            cursor.close()
        if db_connection.is_connected():
            db_connection.close()

    return redirect(url_for('SA_dashboard_info'))


# ---------------------------------------------------------------------------------------------------------------


# Route for creating a user (rendering the form)
@app.route('/create_user')
def create_user_page():
    return render_template('systemtemplates/create_user.html')


# ---------------------------------------------------------------------------------------------------------------
@app.route('/create_user', methods=['POST'])
def create_user():
    if request.method == 'POST':
        role = request.form.get('role')
        username = request.form.get('username')
        password = request.form.get('password')

        connection, cursor = get_db_cursor()

        # Check for uniqueness of username and password
        if not is_unique(cursor, username, password):
            flash('Username or password already exists. Please choose different ones.', 'danger')
            close_db_connection(connection, cursor)
            return redirect(url_for('create_user_page'))

        # Insert the new user into the database with the current timestamp
        insert_query = "INSERT INTO users (role, username, passwd, created) VALUES (%s, %s, %s, %s)"
        insert_data = (role, username, password, datetime.now())

        try:
            cursor.execute(insert_query, insert_data)
            connection.commit()

            # Show success message using flash
            flash('Account successfully created!', 'success')
        except IntegrityError as e:
            # Show error message using flash
            flash('Error creating account. Please try again.', 'danger')
        finally:
            close_db_connection(connection, cursor)

    # Redirect to the create_user_page
    return redirect(url_for('create_user_page'))

def is_unique(cursor, username, password):
    # Check for uniqueness in your database
    query = "SELECT COUNT(*) FROM users WHERE username = %s OR passwd = %s"
    cursor.execute(query, (username, password))
    count = cursor.fetchone()[0]
    return count == 0

# ---------------------------------------------------------------------------------------------------------------
# Route for managing courses
@app.route('/manage_courses')
def manage_courses():
    try:
        # Ensure MySQL connection is established
        if not db_connection.is_connected():
            db_connection.connect()

        # Fetch courses from the database
        cursor.execute("SELECT course_name FROM courses")
        courses = [row[0] for row in cursor.fetchall()]

        # Debug: Print retrieved courses
       

        # Render the manage_courses.html template and pass the course data
        return render_template('systemtemplates/manage_course.html', courses=courses, flash_messages=get_flashed_messages())

    except Exception as e:
        # Handle exceptions, print or log the error
        
        flash('Error retrieving course data. Please try again.', 'danger')

    finally:
        # Close the MySQL connection
        if db_connection.is_connected():
            db_connection.close()

    # If an exception occurs, render the manage_courses.html template with the flash message
    return render_template('systemtemplates/manage_course.html', courses=[], flash_messages=[])


# Add route for adding courses
@app.route('/add_course', methods=['POST'])
def add_course():
    try:
        if not db_connection.is_connected():
            db_connection.connect()

        cursor = db_connection.cursor()

        if request.method == 'POST':
            course_name = request.form.get('courseName')

            # Insert the new course into the database
            insert_query = "INSERT INTO courses (course_name) VALUES (%s)"
            insert_data = (course_name,)

            cursor.execute(insert_query, insert_data)
            db_connection.commit()

            # Redirect to the manage_courses route after adding the course
            flash('Course added successfully.', 'success')
            return redirect(url_for('manage_courses'))

    except Exception as e:
       
        flash('Error adding course. Please try again.', 'danger')

    finally:
        if cursor:
            cursor.close()

    return redirect(url_for('manage_courses'))


# Flask route to delete courses
@app.route('/delete_course', methods=['POST'])
def delete_course():
    try:
        # Ensure MySQL connection is established
        if not db_connection.is_connected():
            db_connection.connect()

        # Open cursor
        cursor = db_connection.cursor()

        # Get the course name from the form submission
        course_to_delete = request.form.get('courseName')

        # Perform the delete operation in the database
        delete_query = "DELETE FROM courses WHERE course_name = %s"
        cursor.execute(delete_query, (course_to_delete,))
        db_connection.commit()

        # Redirect back to the manage_courses page
        flash('Course deleted successfully.', 'success')
        return redirect(url_for('manage_courses'))

    except mysql.connector.Error as e:
        # Handle MySQL errors
        
        flash(f'Error deleting course. Please try again. ({e})', 'danger')

    finally:
        # Close the cursor
        if cursor:
            cursor.close()

    return redirect(url_for('manage_courses'))


@app.route('/edit_course', methods=['POST'])
def edit_course():
    try:
        if not db_connection.is_connected():
            db_connection.connect()

        cursor = db_connection.cursor()

        if request.method == 'POST':
            current_course_name = request.form.get('currentCourseName')
            edited_course_name = request.form.get('editedCourseName')

            update_query = "UPDATE courses SET course_name = %s WHERE course_name = %s"
            update_data = (edited_course_name, current_course_name)

            cursor.execute(update_query, update_data)
            db_connection.commit()

            flash('Course edited successfully.', 'success')
            return redirect(url_for('manage_courses'))

    except Exception as e:
        print(f"Error in edit_course: {e}")
        flash('Error editing course. Please try again.', 'danger')

    finally:
        if cursor:
            cursor.close()

    return redirect(url_for('manage_courses'))



# ---------------------------------------------------------------------------------------------------------------


# Function to create a MySQL connection and cursor
def get_cursor():
    db_connection = mysql.connector.connect(**db_config)
    return db_connection, db_connection.cursor()


# Route for Superadmin login
@app.route('/SA_creates', methods=['POST'])
def SA_creates():
    if request.method == 'POST':
        entered_role = request.form.get('role')
        entered_username = request.form.get('username')
        entered_password = request.form.get('password')

        # Get the cursor
        db_connection, cursor = get_cursor()

        try:
            # Inside the if request.method == 'POST': block
            app.logger.info(f"Entered Credentials: {entered_role}, {entered_username}, {entered_password}")


            # Query the database for the entered credentials with case-insensitive role and username
            query = "SELECT username, passwd, role FROM users WHERE LOWER(role) = LOWER(%s) AND LOWER(username) = LOWER(%s) AND passwd = %s LIMIT 1"
            cursor.execute(query, (entered_role, entered_username, entered_password))
            result = cursor.fetchone()
            app.logger.info(f"Result from Database: {result!r}")


            if result:
                # Extract the role from the result and convert to lowercase
                db_role = result[2].lower()

                if db_role == "bookadmin":
                    
                    logging.info("Redirecting to BA_dashboard_info")
                    app.logger.info("Redirecting to BA_dashboard_info")
                    return redirect(url_for('BA_dashboard'))
                elif db_role == "librarian":
                    logging.info("Redirecting to L_dashboard")
                    app.logger.info("Redirecting to L_dashboard")
                    return redirect(url_for('L_dashboard'))
                elif db_role == "admissionstaff":
                    logging.info("Redirecting to AS_dashboard")
                    app.logger.info("Redirecting to AS_dashboard")
                    return redirect(url_for('AS_dashboard'))
                else:
                    print("Redirecting to start")
                    return redirect(url_for('start'))

            # Flash an error message if login fails
            flash('Incorrect login credentials. Please try again.', 'danger')
            print("Login failed. Flashing error message.")

        finally:
            # Close the cursor and connection
            cursor.close()
            db_connection.close()

    # Render the loginLA.html page (assuming you have a loginLA.html template)
    return render_template('systemtemplates/loginAL.html')



# ---------------------------------------------------------------------------------------------------------------


# Route for rendering the admission staff dashboard template
@app.route('/AS_dashboard', methods=['GET', 'POST'])
def AS_dashboard():
    try:
        connection, cursor = get_db_cursor()
        
        # Fetch total students count
        cursor.execute("SELECT COUNT(*) FROM degreestudents")
        total_students_count = cursor.fetchone()[0]
        app.logger.info(f"Total students count: {total_students_count}")  # Log the total students count
        
        # Fetch class-wise counts
        cursor.execute("SELECT class, COUNT(*) FROM degreestudents GROUP BY class")
        class_counts = dict(cursor.fetchall())
        app.logger.info(f"Class-wise counts: {class_counts}")  # Log the class-wise counts
        
        return render_template('systemtemplates/AS_dashboardinfo.html', total_students_count=total_students_count, class_counts=class_counts)

    except Exception as e:
        # Log the exception with traceback
        logging.exception("An error occurred in AS_dashboard route")
        return "An error occurred. Please check the logs for more information."

    finally:
        close_db_connection(connection, cursor)


# ---------------------------------------------------------------------------------------------------------------
# Route for rendering the book admin dashboard template
@app.route('/BA_dashboard', methods=['GET', 'POST'])
def BA_dashboard():
    try:
        connection, cursor = get_db_cursor()

        if request.method == 'POST':
            # Handle the form submission logic here
            return redirect(url_for('BA_dashboard'))

        # Fetch count of courses
        cursor.execute("SELECT COUNT(*) FROM courses")
        courses_count = cursor.fetchone()[0]

        # Your logic for rendering the BA_dashboardinfo template for GET requests
        return render_template('systemtemplates/BA_dashboardinfo.html', courses_count=courses_count)

    except Exception as e:
        print(f"Error fetching data for BA dashboard: {e}")
        flash(f"Error fetching data for BA dashboard: {e}", 'error')
        return render_template('systemtemplates/BA_dashboardinfo.html', courses_count=None)

    finally:
        close_db_connection(connection, cursor)

# ---------------------------------------------------------------------------------------------------------------


@app.route('/admin_profile')
def admin_profile():
    return render_template('systemtemplates/adminprofile.html')


#--------------------------------------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------------------------

cursor = db_connection.cursor()

# Function to get course names from the database
def get_courses_from_database():
    try:
        if not db_connection.is_connected():
            db_connection.connect()

        cursor.execute("SELECT course_name FROM courses")
        courses = [row[0] for row in cursor.fetchall()]
        return courses

    except Exception as e:
        print(f"Error in get_courses_from_database: {e}")
        flash('Error retrieving course data. Please try again.', 'danger')

    finally:
        if db_connection.is_connected():
            db_connection.close()

    return []


@app.route('/admin_create_book')
def admin_create_book():
   
    courses = get_courses_from_database()
    return render_template('systemtemplates/admin_createbook.html', courses=courses)




# Route for viewing books
@app.route('/view_books', methods=['GET', 'POST'])
def view_books():
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        # Fetch filters from the form
        selected_course = request.form.get('course')
        selected_year = request.form.get('year')
        selected_semester = request.form.get('semester')

        # Fetch courses from the "courses" table
        cursor.execute("SELECT course_name FROM courses")
        courses_data = cursor.fetchall()
        course_names = [course['course_name'] for course in courses_data]

        # Construct the base query to fetch books
        base_query = "SELECT * FROM books WHERE 1=1"

        # Add filters to the query based on user selections
        if selected_course:
            base_query += f" AND class = '{selected_course}'"

        if selected_year:
            # Use the selected_year directly without converting to uppercase
            base_query += f" AND year = '{selected_year}'"

        if selected_semester:
            base_query += f" AND semester = '{selected_semester}'"

        # Execute the final query
        cursor.execute(base_query)
        books_data = cursor.fetchall()

        # Pass courses and books to the template
        return render_template('systemtemplates/viewbooks.html', books=books_data, courses=course_names)

    except Exception as e:
        # Handle exceptions
        print(f"Error fetching data: {e}")
        return render_template('systemtemplates/viewbooks.html', books=None)

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()




# Route for viewing books
@app.route('/L_view_subjects', methods=['GET', 'POST'])
def L_view_subjects():
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        # Fetch filters from the form
        selected_course = request.form.get('course')
        selected_year = request.form.get('year')
        selected_semester = request.form.get('semester')

        # Fetch courses from the "courses" table
        cursor.execute("SELECT course_name FROM courses")
        courses_data = cursor.fetchall()
        course_names = [course['course_name'] for course in courses_data]

        # Construct the base query to fetch books
        base_query = "SELECT * FROM books WHERE 1=1"

        # Add filters to the query based on user selections
        if selected_course:
            base_query += f" AND class = '{selected_course}'"

        if selected_year:
            # Use the selected_year directly without converting to uppercase
            base_query += f" AND year = '{selected_year}'"

        if selected_semester:
            base_query += f" AND semester = '{selected_semester}'"

        # Execute the final query
        cursor.execute(base_query)
        books_data = cursor.fetchall()

        # Pass courses and books to the template
        return render_template('systemtemplates/L_viewbooks.html', books=books_data, courses=course_names)

    except Exception as e:
        # Handle exceptions
        print(f"Error fetching data: {e}")
        return render_template('systemtemplates/L_viewbooks.html', books=None)

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/edit_subject', methods=['POST'])
def edit_subject():
    if request.method == 'POST':
        current_subject_name = request.form['currentSubjectName']
        edited_subject_name = request.form['editedSubjectName']
        edited_subject_code = request.form['editedSubjectCode']
        
        # Establish a new connection and cursor
        connection, cursor = get_db_cursor()

        # Update the subject name and code in the database
        update_query = "UPDATE books SET subject = %s, subject_code = %s WHERE subject = %s"
        update_data = (edited_subject_name, edited_subject_code, current_subject_name)
        cursor.execute(update_query, update_data)
        connection.commit()

        # Close the connection and cursor
        close_db_connection(connection, cursor)

        return redirect(url_for('view_books'))



# Route for deleting books
@app.route('/delete_books', methods=['GET', 'POST'])
def delete_books():
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        # Fetch filters from the form
        selected_course = request.form.get('course')
        selected_year = request.form.get('year')
        selected_semester = request.form.get('semester')

        # Fetch courses from the "courses" table
        cursor.execute("SELECT course_name FROM courses")
        courses_data = cursor.fetchall()
        course_names = [course['course_name'] for course in courses_data]

        # Construct the base query
        base_query = 'SELECT * FROM books WHERE 1=1'

        # Add filters to the query based on user selections
        if selected_course:
            base_query += f" AND class = '{selected_course}'"

        if selected_year:
            # Use uppercase for consistency with the database values
            base_query += f" AND year = '{selected_year.upper()}'"

        if selected_semester:
            base_query += f" AND semester = '{selected_semester}'"

        # Execute the final query
        cursor.execute(base_query)
        books_data = cursor.fetchall()

        # Pass courses and books to the template
        return render_template('systemtemplates/deletebooks.html', books=books_data, courses=course_names,
                               selected_course=selected_course, selected_year=selected_year,
                               selected_semester=selected_semester)
    except Exception as e:
        # Handle exceptions
        print(f"Error fetching data: {e}")
        return render_template('systemtemplates/deletebooks.html', books=None)

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()

   
#------------------------------------------------------------------------------------   
# Route to handle the form submission for deleting selected books
@app.route('/delete_selected_books', methods=['POST'])
def delete_selected_books():
    if request.method == 'POST':
        selected_books = request.form.getlist('selectBook')
        
        if not selected_books:
            flash('No books selected for deletion.', 'error')
            return redirect(url_for('delete_books'))

        try:
            # Connect to the database
            connection, cursor = get_db_cursor()

            # Use the selected book IDs to perform deletion from the database
            for book_id in selected_books:
                delete_query = "DELETE FROM books WHERE id = %s"
                cursor.execute(delete_query, (book_id,))
                connection.commit()

            flash('Selected books deleted successfully!', 'success')
        except Exception as e:
            flash(f'Error deleting books: {e}', 'error')
        finally:
            close_db_connection(connection, cursor)

        return redirect(url_for('delete_books'))
    else:
        return redirect(url_for('delete_books'))


# ---------------------------------------------------------------------------------------------------------------



# Route for rendering the courses
@app.route('/view_courses', methods=['GET', 'POST'])
def view_courses():
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        # Construct the query to fetch courses
        courses_query = 'SELECT * FROM courses'

        # Execute the query
        cursor.execute(courses_query)
        courses_data = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        return render_template('systemtemplates/view_courses.html', courses=courses_data)

    except Exception as e:
        # Handle exceptions
        print(f"Error fetching courses data: {e}")
        return render_template('systemtemplates/view_courses.html', courses=None)

# Ensure to close the cursor and connection in case of exceptions
    finally:
      if cursor:
        cursor.close()
      if connection:
        connection.close()


# ---------------------------------------------------------------------------------------------------------------

@app.route('/logout')
def logout():
    # Add logic to handle logout if needed
    return render_template('systemtemplates/start.html')


# ---------------------------------------------------------------------------------------------------------------

@app.route('/store_book', methods=['POST'])
def store_book():
    db_connection = None
    cursor = None

    try:
        connection, cursor = get_db_cursor()

        # Get the values from the form
        class_value = request.form['class']
        year_value = request.form['year']
        semester_value = request.form['sem']
        num_subjects = int(request.form['numSubjects'])
        subjects = request.form.getlist('subjects[]')
        subject_codes = request.form.getlist('subjectCodes[]')

        # Validate input lengths
        if len(subjects) != num_subjects or len(subject_codes) != num_subjects:
            flash('Number of subjects and subject codes must match the entered number of subjects.', 'danger')
            return redirect(url_for('admin_create_book'))

        # Check if a similar entry already exists
        if book_exists(connection, cursor, {'class': class_value, 'year': year_value, 'semester': semester_value}):
            flash('Books for this combination already exist!', 'danger')
            return redirect(url_for('admin_create_book'))

        for i in range(num_subjects):
            # Store data in the 'books' table
            book_data = {
                'class': class_value,
                'year': year_value,
                'semester': semester_value,
                'subject': subjects[i].strip(),
                'subject_code': subject_codes[i].strip()
            }

            try:
                cursor.execute(
                    "INSERT INTO books (class, year, semester, subject, subject_code) VALUES (%(class)s, %(year)s, %(semester)s, %(subject)s, %(subject_code)s)",
                    book_data)
                connection.commit()
            except IntegrityError as e:
                # Handle duplicate entry error
                flash(f'Duplicate subject code: {subject_codes[i].strip()}. Please use a unique subject code.', 'danger')
                connection.rollback()
                return redirect(url_for('admin_create_book'))

        flash('Books added successfully!', 'success')

    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')

    finally:
        if cursor:
            cursor.close()
        if db_connection:
            db_connection.close()

    return redirect(url_for('admin_create_book'))


   
def book_exists(connection, cursor, book_data):
    # Check if the combination of class, year, and semester already exists
    query = """
        SELECT COUNT(*) FROM books
        WHERE class = %(class)s AND year = %(year)s AND semester = %(semester)s
    """
    cursor.execute(query, book_data)
    return cursor.fetchone()[0] > 0




# ---------------------------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------------------
# Route for rendering the upload students data page
@app.route('/upload_students')
def upload_students():
    # Your logic for rendering the uploadstudentsdata.html template
    return render_template('systemtemplates/uploadstudentdata.html')


# --------------------------------------------------------------------------------------------------------------------
students = []



# Route for uploading Excel files
@app.route('/upload_excel', methods=['POST'])
def upload_excel():
    if 'excel_file' in request.files:
        excel_file = request.files['excel_file']
        if excel_file.filename != '':
            students.clear()  # Clear the students list when a new file is uploaded
            try:
                if excel_file.filename.endswith(('.xls', '.xlsx')):
                    # For Excel files using pandas, skip the first row
                    excel_data = pd.read_excel(excel_file, converters={'dob': str}, header=None, skiprows=1, index_col=None)

                    # Rename columns with desired names
                    excel_data.columns = ['prnnumber', 'name', 'class', 'contact', 'address', 'dob']

                    # Check if 'dob' column exists in the DataFrame
                    if 'dob' not in excel_data.columns:
                        flash(f"Error: 'dob' column not found in the Excel file. Please check your column names. Columns found: {list(excel_data.columns)}")
                        return redirect('/upload_students')

                    csv_reader = excel_data.to_dict(orient='records')
                else:
                    flash("Unsupported file format")
                    return redirect('/upload_students')

                for row in csv_reader:
                    # Ensure consistent field names with the Student model
                    dob_str = str(row['dob'])

                    student_data = {
                        'name': row.get('name', ''),
                        'class_name': row.get('class', ''),
                        'prnnumber': row.get('prnnumber', ''),
                        'contact': row.get('contact', ''),
                        'address': row.get('address', ''),
                        'dob': dob_str,
                    }
                    students.append(student_data)
                flash(f"Successfully uploaded: {excel_file.filename}")
            except Exception as e:
                flash(f"Error processing the file: {str(e)}")
    return redirect('/upload_students')


#------------------------------ROUTE 11---------------------------------
# Route to generate ID cards with QR codes for uploaded students
@app.route('/generate_id_cards', methods=['POST'])
def generate_id_cards():
    qr_codes_and_id_cards = []

    if not students:
        return "No students to generate QR codes for"  # Handle the case when no students are available

    for student in students:
        # Generate student details with HTML formatting
        student_details = ",\n\n".join([f"{key}: {value}" for key, value in student.items()])

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
        libcard_html = render_template('systemtemplates/libcard.html', student=student, qr_code=qr_code_base64)
        qr_codes_and_id_cards.append(libcard_html)

    if qr_codes_and_id_cards:
        # Render the viewqrcodes.html template with the library cards
        return render_template('systemtemplates/viewqrcodes.html', qr_codes_and_id_cards=qr_codes_and_id_cards)
    else:
        return "No QR Codes Generated"  # Handle the case when no QR codes are generated







from datetime import datetime

def format_scanned_data(student_data):
    # Format student data as per your requirement
    formatted_data = ""
    for key, value in student_data.items():
        formatted_data += f"{key}: {value},\n"
    return formatted_data





@app.route('/view_student_ids')
def view_student_ids():
    connection = None
    
    try:
        connection, cursor = get_db_cursor()
        
        fetch_students_query = "SELECT * FROM degreestudents"
        cursor.execute(fetch_students_query)
        students = cursor.fetchall()
        
        qr_codes_and_students = []

        if not students:
            return "No students available"

        for student in students:
            student_data = {
                'name': student[1],
                'class_name': student[2],
                'prnnumber': student[3],
                'contact': student[4],
                'address': student[5],
                'dob': student[6]
            }

            formatted_student_data = format_scanned_data(student_data)

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(formatted_student_data)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            buffered = BytesIO()
            qr_img.save(buffered, "PNG")
            qr_code_base64 = base64.b64encode(buffered.getvalue()).decode()

            qr_codes_and_students.append({'student': student_data, 'qr_code': qr_code_base64})

        if qr_codes_and_students:
            return render_template('systemtemplates/view_libcards.html', qr_codes_and_students=qr_codes_and_students)
        else:
            return "No QR Codes Generated"
    except Exception as e:
        print(f"Error fetching student IDs: {e}")
        return "Error fetching student IDs"
    finally:
        if connection is not None:
            close_db_connection(connection, cursor)
#--------------------------------------------------------------------------------------
import logging

# Configure logging
logging.basicConfig(filename='error.log', level=logging.ERROR)

# Function to insert student data into the database
def insert_student_data(student):
    connection = None  # Initialize connection to None
    try:
        connection, cursor = get_db_cursor()
        logging.info("Connected to the database successfully.")  # Log successful connection

        dob_str = student['dob']

        try:
            # Convert the date string to a datetime object using dateutil parser with fuzzy option
            dob_datetime = parser.parse(dob_str, fuzzy=True)
            dob_formatted = dob_datetime.strftime('%Y-%m-%d')
        except ValueError:
            flash(f"Error parsing date for: {student.get('name', 'Unknown')}. Please use a valid date format.")
            return False

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

        connection.commit()
        logging.info(f"Successfully uploaded {repr(student['name'])}'s data to the database.")
        return True
    except Exception as e:
        logging.error(f"Error details: {repr(e)}")  # Log error details
        logging.error(f"Failed to upload {repr(student['name'])}'s data to the database.")
        return False
    finally:
        if connection:
            close_db_connection(connection, cursor)

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

import logging

# Configure logging
logging.basicConfig(filename='error.log', level=logging.ERROR)
@app.route('/students_table', methods=['GET', 'POST'])
def students_table():
    try:
        connection, cursor = get_db_cursor()
        
        # Query to fetch courses from the course table
        course_query = "SELECT course_name FROM courses"
        cursor.execute(course_query)
        courses = [course[0] for course in cursor.fetchall()]  # Fetch course names

        # Fetch the count of students for each class/course
        count_query = "SELECT class, COUNT(*) as count FROM degreestudents GROUP BY class"
        cursor.execute(count_query)
        student_counts = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Fetch all students without any filtering
        student_query = "SELECT id, name, class, prnnumber, contact, address, DATE_FORMAT(dob, '%d-%m-%Y') as dob FROM degreestudents"
        cursor.execute(student_query)
        
        # Fetch the student data
        students = cursor.fetchall()

        # Log fetched student data
        logging.info("Fetched all student data.")

        return render_template('systemtemplates/student_table.html', students=students, courses=courses, student_counts=student_counts)

    except Exception as e:
        logging.error(f"Failed to fetch registered students: {e}")
        return redirect('/upload_students')
    finally:
        close_db_connection(connection, cursor)


# Route to view registered students with filter
@app.route('/registered_students', methods=['GET', 'POST'])
def registered_students():
    try:
        connection, cursor = get_db_cursor()

        # Fetch the list of courses from the courses table
        cursor.execute("SELECT course_name FROM courses")
        courses = [row[0] for row in cursor.fetchall()]

        if request.method == 'POST':
            course_filter = request.form.get('course')
            if course_filter:
                query = "SELECT name, class, prnnumber, contact, address, DATE_FORMAT(dob, '%d-%m-%Y') as dob FROM degreestudents WHERE class = %s"
                cursor.execute(query, (course_filter,))
            else:
                query = "SELECT name, class, prnnumber, contact, address, DATE_FORMAT(dob, '%d-%m-%Y') as dob FROM degreestudents"
                cursor.execute(query)
            students = cursor.fetchall()
        else:
            query = "SELECT name, class, prnnumber, contact, address, DATE_FORMAT(dob, '%d-%m-%Y') as dob FROM degreestudents"
            cursor.execute(query)
            students = cursor.fetchall()

        # Use logging to print fetched data to the console
        for student in students:
            logging.info(student)

        return render_template('systemtemplates/registered_students.html', students=students, courses=courses)

    except Exception as e:
        # Use logging for the exception message
        logging.error(f"Failed to fetch registered students: {e}")
        return redirect('/upload_students')

    finally:
        close_db_connection(connection, cursor)

    
#------------------------------ROUTE 16---------------------------------
@app.route('/registered_students_L')
def registered_students_L():
    try:
        connection, cursor = get_db_cursor()

        # Fetch the list of courses from the courses table
        cursor.execute("SELECT course_name FROM courses")
        courses = [row[0] for row in cursor.fetchall()]

        # Fetch all students without any filtering
        student_query = "SELECT id, name, class, prnnumber, contact, address, DATE_FORMAT(dob, '%d-%m-%Y') as dob FROM degreestudents"
        cursor.execute(student_query)
        students = cursor.fetchall()

        # Fetch the count of students for each class/course
        count_query = "SELECT class, COUNT(*) as count FROM degreestudents GROUP BY class"
        cursor.execute(count_query)
        student_counts = {row[0]: row[1] for row in cursor.fetchall()}

        # Use logging to print fetched data to the console
        for student in students:
            logging.info(student)

        return render_template('systemtemplates/registered_students_L.html', students=students, courses=courses, student_counts=student_counts)

    finally:
        close_db_connection(connection, cursor)





# Route for My Profile
@app.route('/libprofile')
def libprofile():
    return render_template('systemtemplates/libprofile.html')







# Route for Register Books
@app.route('/L_book_register')
def L_book_register():
    return render_template('systemtemplates/L_book_register.html')



# Route for Sent Messages
@app.route('/sentmessages')
def sentmessages():
    return render_template('systemtemplates/sentmessages.html')

# Route for Fine Collected
@app.route('/fine')
def fine():
    return render_template('systemtemplates/fine.html')

# Route for View Courses
@app.route('/L_view_courses')
def L_view_courses():
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        # Construct the query to fetch courses
        courses_query = 'SELECT * FROM courses'

        # Execute the query
        cursor.execute(courses_query)
        courses_data = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        return render_template('systemtemplates/L_view_courses.html', courses=courses_data)

    except Exception as e:
        # Handle exceptions
        print(f"Error fetching courses data: {e}")
        return render_template('systemtemplates/L_view_courses.html')

# Ensure to close the cursor and connection in case of exceptions
    finally:
      if cursor:
        cursor.close()
      if connection:
        connection.close()





#-------------------------------------------------------------------------------------------------------------
def fetch_book_details_from_database(book_id):
    try:
        # Establish a connection to the database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Fetch details for the given book ID
        query = """
            SELECT libbooks.class, libbooks.year, libbooks.semester, books.subject, libbooks.subject_code, libbooks.author, libbooks.publication
            FROM libbooks
            JOIN books ON libbooks.books_id = books.id
            WHERE libbooks.books_id = %s
            LIMIT 1
        """
        print("Executing query:", query)
        print("Query parameter:", book_id)
        cursor.execute(query, (book_id,))
        result = cursor.fetchone()

        print("Query result:", result)  # Add this line for debugging

        if result:
            # Construct a dictionary with the fetched details
            class_value, year_value, semester_value, subject, subject_code, author, publication = result
            details = {
                'Class': class_value,
                'Year': year_value,
                'Semester': semester_value,
                'Title': subject,  # Assuming 'subject' holds the title
                'Author': author,
                'Publication': publication,
                'Subject Code': subject_code  # Corrected key name
            }
            return details
        else:
            # Return an empty dictionary if no details are found
            return {}

    except mysql.connector.Error as error:
        print(f"Error fetching book details from the database: {error}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()



@app.route('/flash_message')
def flash_message():
    return render_template('systemtemplates/flash_message.html', flashed_messages=get_flashed_messages())

def generate_book_ids(subject_code, quantity, author, publication, class_value, year_value, semester_value, title, count_start=1):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    try:
        # Check if there are existing entries for the same book details
        query = """
            SELECT COUNT(*)
            FROM qrcodetable
            WHERE class = %s
              AND year = %s
              AND semester = %s
              AND title = %s
              AND subject_code = %s
        """
        cursor.execute(query, (class_value, year_value, semester_value, title, subject_code))
        count = cursor.fetchone()[0]

        # If there are existing entries, get the maximum count and add the new quantity
        if count > 0:
            query_max_count = """
                SELECT MAX(CAST(SUBSTRING(book_id, -5) AS UNSIGNED))
                FROM qrcodetable
                WHERE class = %s
                  AND year = %s
                  AND semester = %s
                  AND title = %s
                  AND subject_code = %s
            """
            cursor.execute(query_max_count, (class_value, year_value, semester_value, title, subject_code))
            max_count = cursor.fetchone()[0] or 0
            count_start = max_count + 1

        # Start generating book IDs from the specified starting value
        book_ids = [f"{subject_code}{str(count_start + i - 1).zfill(5)}" for i in range(1, quantity + 1)]
        details = {
            'Class': class_value,
            'Year': year_value,
            'Semester': semester_value,
            'Title': title,
            'Author': author,
            'Publication': publication,
            'Subject Code': subject_code
        }
        return book_ids, details

    except Exception as e:
        print(f"Error generating book IDs: {e}")
        return [], {}

    finally:
        cursor.close()
        connection.close()




@app.route('/generate_qr_codes', methods=['GET', 'POST'])
def generate_qr_codes():
    if request.method == 'POST':
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()

            cursor.execute("SELECT book_id, class, year, semester, title, subject_code, author, publication FROM qrcodetable ORDER BY id DESC")
            qr_code_data = []
            for result in cursor.fetchall():
                book_data = {
                    'details': {
                        'Book ID': result[0],
                        'Class': result[1],
                        'Year': result[2],
                        'Semester': result[3],
                        'Title': result[4],
                        'Subject Code': result[5],
                        'Author': result[6],
                        'Publication': result[7]
                    }
                }
                # Generate QR code image and add it to the book data
                book_data['qr_image'] = generate_qr_code(str(book_data['details']))
                qr_code_data.append(book_data)
            
            cursor.close()
            connection.close()

            return render_template('systemtemplates/book_qrcode.html', qr_code_data=qr_code_data)
        except mysql.connector.Error as error:
            flash(f'Error fetching data from database: {error}', 'error')
            return redirect(url_for('flash_message'))
    else:
        # This block will execute when the route is accessed via GET method
        # You can include the QR code generation logic here directly
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()

            cursor.execute("SELECT book_id, class, year, semester, title, subject_code, author, publication FROM qrcodetable ORDER BY id DESC")
            qr_code_data = []
            for result in cursor.fetchall():
                book_data = {
                    'details': {
                        'Book ID': result[0],
                        'Class': result[1],
                        'Year': result[2],
                        'Semester': result[3],
                        'Title': result[4],
                        'Subject Code': result[5],
                        'Author': result[6],
                        'Publication': result[7]
                    }
                }
                # Generate QR code image and add it to the book data
                book_data['qr_image'] = generate_qr_code(str(book_data['details']))
                qr_code_data.append(book_data)
            
            cursor.close()
            connection.close()

            return render_template('systemtemplates/book_qrcode.html', qr_code_data=qr_code_data)
        except mysql.connector.Error as error:
            flash(f'Error fetching data from database: {error}', 'error')
            return redirect(url_for('flash_message'))




# Function to generate QR code image as base64 string
def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    img_buffer = BytesIO()
    img.save(img_buffer, "PNG")
    img_str = base64.b64encode(img_buffer.getvalue()).decode()

    return img_str

@app.route('/librarian_book_registration', methods=['GET', 'POST'])
def librarian_book_registration():
    subjects_dict = {}  # Initialize an empty dictionary
    class_value = ""
    year_value = ""
    semester_value = ""
    selected_subject_code = ""
    quantity = ""
    author = ""
    publication = ""
    title = ""  # Define the title variable

    if request.method == 'POST':
        subject_code = request.form.get('subjectCode')
        quantity = request.form.get('quantity')
        author = request.form.get('author')
        publication = request.form.get('publication')
        class_value = request.form.get('class')  # Add this line to retrieve class_value
        year_value = request.form.get('year')    # Add this line to retrieve year_value
        semester_value = request.form.get('semester')  # Add this line to retrieve semester_value
        title = request.form.get('title')        # Add this line to retrieve title

        # Fetch details from the database based on the subject code
        connection, cursor = get_db_cursor()
        try:
            query = """
                SELECT class, year, semester, subject, subject_code
                FROM books
                WHERE subject_code = %s
                LIMIT 1
            """
            cursor.execute(query, (subject_code,))
            result = cursor.fetchone()

            if result:
                class_value, year_value, semester_value, title, selected_subject_code = result
                subjects_dict[selected_subject_code] = {
                    'title': title,
                    'class': class_value,
                    'year': year_value,
                    'semester': semester_value
                }

        except Exception as e:
            print(f"Error executing query to fetch book details: {e}")
        finally:
            close_db_connection(connection, cursor)

        if 'registerBooksButton' in request.form:
            connection, cursor = get_db_cursor()
            try:
                if all([quantity, author, publication, title]):
                    insert_query = """
                        INSERT INTO libbooks (class, year, semester, title, subject_code, quantity, author, publication)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    subject_codes = ','.join(subjects_dict.keys())
                    cursor.execute(insert_query, (class_value, year_value, semester_value, title, subject_code, quantity, author, publication))
                    connection.commit()
                    flash('Data inserted into libbooks table successfully.', 'success')
                else:
                    flash('Not all required fields are provided.', 'error')

            except Exception as insert_error:
                flash(f'Error inserting data into libbooks table: {insert_error}', 'error')

            finally:
                close_db_connection(connection, cursor)

        elif 'generateBookIDsButton' in request.form:
            quantity_str = request.form.get('quantity')
            try:
                if quantity_str and quantity_str.isdigit() and subject_code:
                    quantity = int(quantity_str)
                    if quantity > 0:
                        # Call generate_book_ids with author and publication parameters
                        book_ids, details = generate_book_ids(subject_code, quantity, author, publication, class_value, year_value, semester_value, title, count_start=1)
                        book_details = {book_id: details for book_id in book_ids}  # Create a dictionary of book details
                        flash('Book IDs generated successfully.', 'success')
                        return render_template('systemtemplates/generated_ids.html', book_ids=book_ids, book_details=book_details)
                    else:
                        flash('Quantity must be greater than 0.', 'error')
                else:
                    flash('Invalid quantity value or subject code.', 'error')
            except ValueError:
                flash('Invalid quantity value. Please enter a valid positive integer.', 'error')

    return render_template('systemtemplates/L_book_register.html',
                           subjects_dict=subjects_dict,
                           class_value=class_value,
                           year_value=year_value,
                           semester_value=semester_value,
                           selected_subject_code=selected_subject_code,
                           quantity=quantity,
                           author=author,
                           publication=publication,
                           title=title)



#=======================================================================================================
@app.route('/upload_qr_code_details', methods=['POST'])
def upload_qr_code_details():
    # Retrieve data from the POST request
    book_ids = request.form.getlist('book_id[]')

    # Validate the received data
    if not book_ids:
        flash('Missing data in the request', 'error')
        return redirect(url_for('flash_message'))

    try:
        # Store the data in the qrcodetable table
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Insert data into the qrcodetable
        query = "INSERT INTO qrcodetable (book_id, class, year, semester, title, subject_code, author, publication) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        
        for book_id in book_ids:
            # Retrieve data for the current book ID from the form data
            class_value = request.form.get(f"class[{book_id}]")
            year_value = request.form.get(f"year[{book_id}]")
            semester_value = request.form.get(f"semester[{book_id}]")
            title = request.form.get(f"title[{book_id}]")
            subject_code = request.form.get(f"subject_code[{book_id}]")
            author = request.form.get(f"author[{book_id}]")
            publication = request.form.get(f"publication[{book_id}]")

            # Execute the insertion query with the retrieved data
            cursor.execute(query, (book_id, class_value, year_value, semester_value, title, subject_code, author, publication))
        
        # Commit the changes to the database
        connection.commit()

        flash('QR code details uploaded successfully', 'success')
        return redirect(url_for('flash_message'))

    except mysql.connector.Error as error:
        flash(f"Error inserting QR code details into database: {error}", 'error')
        return redirect(url_for('flash_message'))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()



import cv2
from pyzbar.pyzbar import decode



def read_qrcode_from_camera(first_scan=True):
    try:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Use DirectShow backend
        qr_data = None

        while qr_data is None:
            ret, frame = cap.read()  # Read a frame
            if not ret:
                break

            text = "" if first_scan else "Scan Book QR code"

            cv2.putText(frame, text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)  # Display text
            decoded_objects = decode(frame)  # Decode QR codes in the frame
            for obj in decoded_objects:
                qr_data = obj.data.decode("utf-8")
                #print("QR Code data:", qr_data)

            cv2.imshow("QR Code Reader", frame)  # Display the frame

            if cv2.waitKey(1) & 0xFF == ord("q"):  # Press 'q' to exit
                break

            if first_scan and qr_data is not None:
                first_scan = False  # Update first_scan to False after the first scan

        cap.release()
        cv2.destroyAllWindows()

        return qr_data

    except OSError as e:
        #print("Error:", e)
        return None


import json

def parse_data(qr_data):
    data = {}

    # Check if qr_data is already in dictionary format
    if isinstance(qr_data, dict):
        return qr_data

    try:
        # Try parsing the QR code data as JSON
        data = json.loads(qr_data.replace("'", "\""))
    except json.JSONDecodeError:
        # If parsing as JSON fails, assume it's in string format and split by ','
        fields = qr_data.split(',')
        for field in fields:
            if ':' in field:
                key, value = field.split(':', 1)
                data[key.strip()] = value.strip()

    # Clean up empty or missing fields
    cleaned_data = {}
    for key, value in data.items():
        if value.strip():  # Check if the value is not empty
            cleaned_data[key.strip()] = value.strip()

    return cleaned_data

import traceback
from flask import redirect, url_for

def insert_scanned_data(book_id, book_data, student_data):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    try:
        # Check if book_id exists in qrcodetable
        cursor.execute("SELECT book_id FROM qrcodetable WHERE book_id = %s", (book_id,))
        book_exists = cursor.fetchone()

        # Check if the student exists in degreestudents
        cursor.execute("SELECT prnnumber FROM degreestudents WHERE prnnumber = %s", (student_data.get('prnnumber'),))
        student_exists = cursor.fetchone()

        # Check if the book is already issued to the student
        cursor.execute("SELECT book_id FROM scanned WHERE book_id = %s AND student_prnnumber = %s", (book_id, student_data.get('prnnumber')))
        already_issued = cursor.fetchone()

        if not book_exists or not student_exists:
            # Flash an error message indicating that the book or student is not found
            flash("Book or student not found", "error")
            return redirect(url_for('error', error_msg='Book or student not found'))

        elif already_issued:
            # Flash an error message indicating that the book is already issued
            flash("Book is already issued to the student", "error")
            return redirect(url_for('error', error_msg='Book is already issued to the student'))

        else:
            # Use current time as issued date
            issued_date = datetime.now()

            # Calculate due date (7 days from the issued date)
            due_date = issued_date + timedelta(days=7)

            # Construct the SQL query
            sql_query = """
                INSERT INTO scanned (
                    book_id, book_name, book_class, book_year, book_semester, 
                    book_title, book_subject_code, book_author, book_publication,
                    student_id, student_name, student_class, student_prnnumber,
                    student_contact,
                    issued_date, due_date, status
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            # Define the parameter values
            parameter_values = (
                book_id, 
                book_data.get('Title') if book_data else None,
                book_data.get('Class') if book_data else None, 
                book_data.get('Year') if book_data else None, 
                book_data.get('Semester') if book_data else None, 
                book_data.get('Title') if book_data else None, 
                book_data.get('Subject Code') if book_data else None, 
                book_data.get('Author') if book_data else None, 
                book_data.get('Publication') if book_data else None,
                student_data.get('prnnumber'), 
                student_data.get('name', None), 
                student_data.get('class_name', None), 
                student_data.get('prnnumber', None), 
                student_data.get('contact', None), 
                issued_date,  # Use current time as issued date
                due_date,     # Use calculated due date
                7  # Assuming a default status value
            )

            # Execute the SQL query with parameterized values
            cursor.execute(sql_query, parameter_values)

            # Commit the transaction
            connection.commit()

            # Redirect to display_scanned_data route after successful insertion
            return redirect(url_for('display_scanned_data'))

    except mysql.connector.IntegrityError as e:
        if e.errno == 1062:  # MySQL error number for duplicate entry
            # Flash a custom message for duplicate entry
            flash("Book is already issued and the student can't take more than one book", "error")
            return redirect(url_for('error', error_msg="Book is already issued and the student can't take more than one book"))
        else:
            # Flash a generic error message for other integrity errors
            flash("Error inserting data into database: {}".format(e), "error")
            return redirect(url_for('error', error_msg="Error inserting data into database"))

    except Exception as e:
        traceback.print_exc()  # Print out the stack trace
        flash("Error inserting data into database: {}".format(e), "error")  # Flash error message
        return redirect(url_for('error', error_msg="Error inserting data into database"))

    finally:
        cursor.close()
        connection.close()




@app.route('/error')
def error():
    error_msg = request.args.get('error_msg', 'An error occurred.')
    return render_template('systemtemplates/error.html', error_msg=error_msg)

# Main function to scan QR codes
def scan_qr_codes():
    student_data = read_qrcode_from_camera()
    book_data = read_qrcode_from_camera()

    # Parse student data
    if student_data:
        parsed_student_data = parse_data(student_data)
    else:
        parsed_student_data = {}

    # Parse book data
    if book_data:
        parsed_book_data = parse_data(book_data)
    else:
        parsed_book_data = {}

    # Store book data and student data in session
    session['book_data'] = parsed_book_data
    session['student_data'] = parsed_student_data

    # Insert scanned data into database
    if parsed_book_data:
        book_id = parsed_book_data.get('Book ID')
        if book_id:
            insert_scanned_data(book_id, parsed_book_data, parsed_student_data)

# Route to scan IDs
@app.route('/scan_ids', methods=['GET', 'POST'])
def scan_ids():
    if request.method == 'POST':
        # Scan QR codes
        scan_qr_codes()
        
        # Check if any error messages are flashed
        error_messages = get_flashed_messages(with_categories=True)
        
        # If there are no error messages, redirect to display_scanned_data
        if not error_messages:
            return redirect(url_for('display_scanned_data'))
        
        # If there are error messages, redirect to error route
        return redirect(url_for('error', error_msg=error_messages[0][1]))
        
    return render_template('systemtemplates/scan_ids.html')



# Route to display scanned data
@app.route('/display_scanned_data')
def display_scanned_data():
    # Retrieve book_data and student_data from the session
    book_data = session.get('book_data')
    student_data = session.get('student_data')

    # Convert book details to dictionary format
    book_details_dict = {key: value for key, value in (book_data.items() if book_data else {})}

    # Check if student data is empty
    if not student_data:
        student_data = {
            'PRN Number': '',
            'Name': '',
            'Contact': '',
            'Address': '',
            'Date of Birth': ''
        }

    # Retrieve flashed error messages
    error_messages = get_flashed_messages(with_categories=True)

    return render_template('systemtemplates/display_scanned.html', book_details=book_details_dict, student_data=student_data, error_messages=error_messages)



# Route to view issued books
@app.route('/viewissuedbooks', methods=['GET', 'POST'])
def view_issued_books():
    try:
        if request.method == 'POST':
            # Extract filter criteria from the form data
            student_id = request.form.get('student_id')
            student_name = request.form.get('student_name')
            book_id = request.form.get('book_id')
            
            # Fetch issued books data from the database based on filter criteria
            issued_books = fetch_issued_books_from_database(student_id, student_name, book_id)
        else:
            # If no filter criteria provided, fetch all issued books
            issued_books = fetch_issued_books_from_database()

        return render_template('systemtemplates/viewissuedbooks.html', issued_books=issued_books)

    except Exception as e:
        traceback.print_exc()  # Print out the stack trace
        logging.error(f"Error fetching issued books from database: {e}")
        flash("Error fetching issued books from database.", "error")
        return render_template('systemtemplates/viewissuedbooks.html', issued_books=[])

def fetch_issued_books_from_database(student_id=None, student_name=None, book_id=None):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    try:
        # Define the base SQL query to fetch issued books data
        sql_query = """
            SELECT book_id, book_name, student_id, student_name, student_contact, issued_date, due_date, status
            FROM scanned
        """

        # Append filter conditions based on provided criteria
        conditions = []
        parameters = []

        if student_id:
            conditions.append("student_id = %s")
            parameters.append(student_id)
        if student_name:
            conditions.append("LOWER(student_name) LIKE LOWER(%s)")
            parameters.append(f"%{student_name}%")
        if book_id:
            conditions.append("book_id = %s")
            parameters.append(book_id)

        if conditions:
            sql_query += " WHERE " + " AND ".join(conditions)

        # Execute the SQL query with parameters
        cursor.execute(sql_query, parameters)

        # Fetch all rows of data
        issued_books = cursor.fetchall()

        return issued_books

    except Exception as e:
        traceback.print_exc()  # Print out the stack trace
        flash("Error fetching issued books from database: {}".format(e), "error")
        return []

    finally:
        cursor.close()
        connection.close()



def validate_date(date_string):
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

import mysql.connector
from mysql.connector import errorcode

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except mysql.connector.Error as err:
        if err.errno == errorcode.CR_SERVER_LOST:
            logging.error("Lost connection to MySQL server. Reconnecting...")
            connection = mysql.connector.connect(**db_config)
            return connection
        else:
            logging.error(f"MySQL error: {err}")
            raise



@app.route('/return_book', methods=['POST'])
def return_book():
    try:
        # Get the book ID from the request
        book_id = request.form['book_id']

        # Connect to the database
        connection = get_db_connection()
        cursor = connection.cursor()

        # Fetch the scanned book details from the database
        cursor.execute("SELECT * FROM scanned WHERE book_id = %s", (book_id,))
        book_details = cursor.fetchone()

        if book_details:
            # Convert issued date to datetime object
            issued_date = datetime.strptime(str(book_details[15]), '%Y-%m-%d %H:%M:%S')  # Issued date is at index 15

            # Calculate due date (7 days from the issued date)
            due_date = issued_date + timedelta(days=7)

            # Set returned date as current date and time
            returned_date = datetime.now()

            # Calculate the fine
            fine = calculate_fine(issued_date, returned_date)

            # Insert record into records table
            cursor.execute("""
                INSERT INTO records (
                    book_id, book_name, book_class, book_year, book_semester,
                    book_title, book_subject_code, book_author, book_publication,
                    student_id, student_name, student_class, student_prnnumber,
                    student_contact, issued_date, due_date, returned_date, fine
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                book_details[1], book_details[2], book_details[3], book_details[4],
                book_details[5], book_details[6], book_details[7], book_details[8],
                book_details[9], book_details[10], book_details[11], book_details[12],
                book_details[13], book_details[14], issued_date.strftime('%Y-%m-%d %H:%M:%S'),
                due_date.strftime('%Y-%m-%d %H:%M:%S'), returned_date.strftime('%Y-%m-%d %H:%M:%S'), fine
            ))

            # Delete the scanned book details from the scanned table
            cursor.execute("DELETE FROM scanned WHERE book_id = %s", (book_id,))

            # Commit the transaction
            connection.commit()

            # Redirect back to the page displaying issued books
            return redirect(url_for('view_issued_books'))
        else:
            flash('Book not found in scanned table', 'error')
            return redirect(url_for('view_issued_books'))
    except Exception as e:
        logging.error(f"Error returning book: {e}")
        flash('An error occurred while returning the book', 'error')
        return redirect(url_for('view_issued_books'))
    finally:
        cursor.close()
        connection.close()


def calculate_fine(issued_date, return_date):
    # Calculate the difference in minutes
    minutes_difference = (return_date - issued_date).total_seconds() / 60

    # If returned within 1 minute after issuance time, no fine
    if minutes_difference <= 1:
        return 0
    else:
        # Increment fine by 1 for each minute late after the first minute
        fine = int(minutes_difference) - 1
        return fine


# Route to view issued history based on applied filters
@app.route('/issued_history', methods=['GET', 'POST'])
def issued_history():
    try:
        if request.method == 'POST':
            # Retrieve filter values from the form submission
            student_name_filter = request.form.get('student_name', '').strip()
            book_id_filter = request.form.get('book_id', '').strip()

            # Connect to the database
            connection, cursor = get_db_cursor()

            # Construct the SQL query based on the filters
            app.logger.info(f"Filters - Student Name: {student_name_filter}, Book ID: {book_id_filter}")
            query = """
                SELECT book_id, book_name, student_id, student_name, 
                       DATE_FORMAT(issued_date, '%Y-%m-%d %H:%i:%s') as issued_date, 
                       DATE_FORMAT(returned_date, '%Y-%m-%d %H:%i:%s') as returned_date, 
                       due_date, fine
                FROM records
                WHERE 1=1
            """
            conditions = []
            if student_name_filter:
                conditions.append(f"student_name LIKE '%{student_name_filter}%'")
            if book_id_filter:
                conditions.append(f"book_id LIKE '%{book_id_filter}%'")

            if conditions:
                query += " AND " + " AND ".join(conditions)

            app.logger.info(f"Generated SQL query: {query}")

            # Execute the query
            cursor.execute(query)
            records = cursor.fetchall()

            # Format the dates for display
            formatted_records = []
            for record in records:
                formatted_record = list(record)
                formatted_records.append(formatted_record)

            # Log the fetched records
            logging.info(f"Fetched {len(records)} records from database: {records}")

            # Close the database connection
            close_db_connection(connection, cursor)

            # Render the history.html template with the formatted records data
            return render_template('systemtemplates/history.html', records=formatted_records)

        else:
            # If no filters applied, fetch all records
            # Connect to the database
            connection, cursor = get_db_cursor()

            # Fetch specific columns from the records table
            cursor.execute("""
                SELECT book_id, book_name, student_id, student_name, 
                       DATE_FORMAT(issued_date, '%Y-%m-%d %H:%i:%s') as issued_date, 
                       DATE_FORMAT(returned_date, '%Y-%m-%d %H:%i:%s') as returned_date, 
                       due_date, fine
                FROM records
            """)

            records = cursor.fetchall()

            # Format the dates for display
            formatted_records = []
            for record in records:
                formatted_record = list(record)
                formatted_records.append(formatted_record)

            # Log the fetched records
            logging.info(f"Fetched {len(records)} records from database: {records}")

            # Close the database connection
            close_db_connection(connection, cursor)

            # Render the history.html template with the formatted records data
            return render_template('systemtemplates/history.html', records=formatted_records)

    except Exception as e:
        logging.error(f"Error fetching records from database: {e}")
        flash("Error fetching records from database.", "error")
        return render_template('systemtemplates/history.html', records=[])



@app.route("/L_view_generated_ids")
def L_view_generated_ids():
    connection, cursor = get_db_cursor()

    # Query to retrieve book details from qrcodetable
    query = "SELECT book_id, class, year, semester, title, subject_code, author, publication FROM qrcodetable"
    cursor.execute(query)
    books = cursor.fetchall()

    # Prepare data in the format required by the template
    book_details = {}
    for book in books:
        book_id = book[0]  # Use integer index to access the book ID
        book_details[book_id] = {
            'Class': book[1],
            'Year': book[2],
            'Semester': book[3],
            'Title': book[4],
            'Subject Code': book[5],
            'Author': book[6],
            'Publication': book[7]
        }

    close_db_connection(connection, cursor)

    return render_template("systemtemplates/view_generated_ids.html", book_details=book_details)

@app.route('/L_dashboard')
def L_dashboard():
    try:
        # Get the database cursor
        db_connection, cursor = get_db_cursor()

        # Fetch total number of books from qrcodetable
        cursor.execute("SELECT COUNT(*) FROM qrcodetable")
        total_books = cursor.fetchone()[0]

        # Fetch number of books issued from scanned table
        cursor.execute("SELECT COUNT(*) FROM scanned")
        books_issued = cursor.fetchone()[0]

        # Calculate total number of books after issued
        total_books_after_issued = total_books - books_issued

        # Fetch total fine collected
        cursor.execute("SELECT SUM(fine) FROM records")
        total_fine = cursor.fetchone()[0] or 0

        # Calculate total number of books issued
        cursor.execute("SELECT COUNT(*) FROM scanned")
        total_books_issued = cursor.fetchone()[0]

        # Close the cursor and database connection
        close_db_connection(db_connection, cursor)

        return render_template('systemtemplates/L_dashboard.html', total_books=total_books, 
                               books_issued=books_issued, total_fine=total_fine,
                               total_books_after_issued=total_books_after_issued,
                               total_books_issued=total_books_issued)
    except Exception as e:
        print(f"Error fetching dashboard data: {e}")
        return render_template( error_message="An error occurred while fetching dashboard data.")


# Function to fetch all fields from the libbooks table
def get_registered_books_from_database():
    try:
        # Establish database connection
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        # Execute SQL query to fetch all fields from libbooks
        query = "SELECT * FROM libbooks"
        cursor.execute(query)
        registered_books = cursor.fetchall()

        return registered_books
    except Exception as e:
        logging.error(f'Error fetching registered books: {e}')
        return []

# Function to update book details in the database
def update_book_details(book_id, author, publication):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        update_query = """
            UPDATE libbooks
            SET author = %s, publication = %s
            WHERE id = %s
        """
        cursor.execute(update_query, (author, publication, book_id))
        connection.commit()
        flash('Book details updated successfully.', 'success')
    except Exception as e:
        flash(f'Error updating book details: {e}', 'error')
    finally:
        cursor.close()
        connection.close()

# Route to handle viewing and updating registered books
@app.route('/viewregisteredbooks', methods=['GET', 'POST'])
def viewregisteredbooks():
    if request.method == 'POST':
        book_id = request.form.get('book_id')
        author = request.form.get('author')
        publication = request.form.get('publication')

        # Update book details in the database
        update_book_details(book_id, author, publication)

        # Redirect back to the same page after updating
        return redirect('/viewregisteredbooks')

    # Fetch registered books from the database
    registered_books = get_registered_books_from_database()

    # Render the template for viewing registered books
    return render_template('systemtemplates/viewregisteredbooks.html', registered_books=registered_books)





# Function to delete entries from qrcodetable based on libbooks id
def delete_entries_from_qrcodetable(libbooks_id):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        delete_query = "DELETE FROM qrcodetable WHERE book_id LIKE %s"
        cursor.execute(delete_query, (f"{libbooks_id}%",))  # Deleting all entries starting with libbooks_id
        connection.commit()
    except Exception as e:
        logging.error(f'Error deleting entries from qrcodetable: {e}')
    finally:
        cursor.close()
        connection.close()

# Route to delete a registered book
@app.route('/delete_registered_book', methods=['POST'])
def delete_registered_book():
    if request.method == 'POST':
        logging.info("Delete form submitted successfully!")
        book_id = request.form.get('id')  # Get the ID of the book to delete
        logging.info(f"Book ID to delete: {book_id}")

        try:
            # Establish database connection
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()

            # Fetch the libbooks_id of the book to be deleted
            fetch_query = "SELECT subject_code FROM libbooks WHERE id = %s"
            cursor.execute(fetch_query, (book_id,))
            libbooks_id = cursor.fetchone()[0]

            # Delete the book from libbooks
            delete_query = "DELETE FROM libbooks WHERE id = %s"
            cursor.execute(delete_query, (book_id,))
            connection.commit()

            if cursor.rowcount > 0:
                # Delete corresponding entries from qrcodetable
                delete_entries_from_qrcodetable(libbooks_id)

                flash('Book deleted successfully.', 'success')
                logging.info("Book deleted successfully.")
            else:
                flash('No book found with ID: ' + book_id, 'error')
                logging.warning(f"No book found with ID: {book_id}")
        except Exception as e:
            flash(f'Error deleting book: {e}', 'error')
            logging.error(f'Error deleting book: {e}')
        finally:
            cursor.close()
            connection.close()

        return redirect(url_for('viewregisteredbooks'))




@app.route('/update_book/<int:book_id>', methods=['POST'])
def update_book(book_id):
    if request.method == 'POST':
        author = request.form.get('author')
        publication = request.form.get('publication')
        quantity = request.form.get('quantity')

        # Perform database update using the retrieved book ID
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()

            update_query = """
                UPDATE libbooks
                SET author = %s, publication = %s, quantity = %s
                WHERE id = %s
            """
            cursor.execute(update_query, (author, publication, quantity, book_id))
            connection.commit()
            flash('Book details updated successfully.', 'success')
        except Exception as e:
            flash(f'Error updating book details: {e}', 'error')
        finally:
            cursor.close()
            connection.close()

        return redirect('/viewregisteredbooks')



# Function to fetch all fields from the qrcodetable
def get_all_books_from_qrcodetable():
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM qrcodetable"
        cursor.execute(query)
        all_books = cursor.fetchall()

        return all_books
    except Exception as e:
        logging.error(f'Error fetching all books: {e}')
        return []


# Route to view all books based on applied filters
@app.route('/view_all_books', methods=['GET', 'POST'])
def view_all_books():
    try:
        if request.method == 'POST':
            # Retrieve filter values from the form submission
            bookIdFilter = request.form.get('bookIdFilter', '')
            subjectCodeFilter = request.form.get('subjectCodeFilter', '')
            classFilter = request.form.get('classFilter', '')
            authorFilter = request.form.get('authorFilter', '')
            publicationFilter = request.form.get('publicationFilter', '')

            # Establish database connection
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)

            # Construct the SQL query based on the filters
            conditions = []
            if bookIdFilter:
                conditions.append(f"LOWER(book_id) LIKE '%{bookIdFilter.lower()}%'")
            if subjectCodeFilter:
                conditions.append(f"LOWER(subject_code) LIKE '%{subjectCodeFilter.lower()}%'")
            if classFilter:
                conditions.append(f"LOWER(class) LIKE '%{classFilter.lower()}%'")
            if authorFilter:
                conditions.append(f"LOWER(author) LIKE '%{authorFilter.lower()}%'")
            if publicationFilter:
                conditions.append(f"LOWER(publication) LIKE '%{publicationFilter.lower()}%'")

            where_clause = " AND ".join(conditions) if conditions else ""

            query = f"SELECT * FROM qrcodetable"
            if where_clause:
                query += f" WHERE TRUE AND {where_clause}"

            print("Generated SQL query:", query)  # Print the generated SQL query

            # Execute the query
            cursor.execute(query)
            all_books = cursor.fetchall()

            # Close database connection
            cursor.close()
            connection.close()

            return render_template('systemtemplates/view_all_books.html', all_books=all_books)

        else:
            # If no filters applied, retrieve all books
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM qrcodetable")
            all_books = cursor.fetchall()
            cursor.close()
            connection.close()

            return render_template('systemtemplates/view_all_books.html', all_books=all_books)

    except Exception as e:
        return f'Error occurred: {str(e)}'




# @app.route('/delete_all_books', methods=['GET', 'POST'])
# def delete_all_books():
#     # Handle filters if submitted in the form
#     if request.method == 'POST':
#         filters = {'book_id': request.form.get('bookIdFilter'),
#                    'subject_code': request.form.get('subjectCodeFilter'),
#                    'class': request.form.get('classFilter'),
#                    'author': request.form.get('authorFilter'),
#                    'publication': request.form.get('publicationFilter')}

#         # Build WHERE clause based on submitted filters
#         where_conditions = [f"{key} = %({key})s" for key, value in filters.items() if value]
#         where_clause = ' AND '.join(where_conditions)

#     # Connect to the database
#     connection, cursor = get_db_cursor()

#     try:
#         # Delete entries from qrcodetable based on filters
#         delete_qrcode_query = f"DELETE FROM qrcodetable"
#         if where_clause:
#             delete_qrcode_query += f" WHERE {where_clause}"
#         cursor.execute(delete_qrcode_query, filters)

#         if cursor.rowcount > 0:
#             flash(f"Successfully deleted {cursor.rowcount} entries from qrcodetable.", 'success')

#             # Update libbooks quantity accordingly, ensuring proper filtering based on the same criteria
#             update_libbooks_query = f"""
#                 UPDATE libbooks L
#                 SET L.quantity = L.quantity - (
#                     SELECT COUNT(*)
#                     FROM qrcodetable Q
#                     WHERE Q.books_id = L.books_id
#                     {where_clause}
#                 )
#             """
#             if where_clause:
#                 update_libbooks_query += f" WHERE {where_clause}"
#             cursor.execute(update_libbooks_query, filters)

#             if cursor.rowcount > 0:
#                 flash(f"Successfully updated quantity in {cursor.rowcount} libbooks entries.", 'success')
#         else:
#             flash("No books were found with the specified filters.", 'info')

#         connection.commit()  # Commit changes to the database
#     except mysql.connector.Error as err:
#         print(f"Error deleting books: {err}")
#         flash("An error occurred while deleting books. Please try again later.", 'error')
#     finally:
#         close_db_connection(connection, cursor)

#     return redirect(url_for('view_all_books'))





@app.route('/librarian_dashboard')
def librarian_dashboard():
    # Fetch total number of books
    cursor.execute("SELECT COUNT(*) FROM qrcodetable")
    total_books = cursor.fetchone()[0]

    # Fetch number of books issued
    cursor.execute("SELECT COUNT(*) FROM scanned WHERE status = 1")
    books_issued = cursor.fetchone()[0]

    # Fetch total fine collected
    cursor.execute("SELECT SUM(fine) FROM records")
    total_fine = cursor.fetchone()[0] or 0

    return render_template('systemtemplates/L_dashboard.html', total_books=total_books, books_issued=books_issued, total_fine=total_fine)


if __name__ == '__main__':
    app.run(debug=True)
