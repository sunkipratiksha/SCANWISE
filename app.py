from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)

app.debug = True
admins ={}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Retrieve the form data
        username = request.form['username']
        password = request.form['password']
        
        # Perform necessary login validation and database operations
        # Replace this with your own logic
        if username in admins and admins[username] == password:
            return 'Login successful!'
        else:
            return 'Invalid username or password'
    
    return render_template('admin_login.html')

@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        # Retrieve the form data
        username = request.form['username']
        password = request.form['password']
        admins[username] = password
        
        # Perform necessary registration validation and database operations
        # Replace this with your own logic
        # Store the admin credentials in the database or any other storage
        
        return render_template('registration_success.html')
    
    return render_template('admin_register.html')

if __name__ == '__main__':
    app.run()
