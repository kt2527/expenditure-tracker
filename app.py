from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__, template_folder='templates')

# Dummy data for user and father login (can be replaced with real authentication)
users = {"user": "password"}  # Example: 'user' and 'password'
fathers = {"father": "fatherpassword"}  # Example: 'father' and 'fatherpassword'

@app.route('/')
def home():
    return render_template('base.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if it's a user login
        if username in users and users[username] == password:
            return redirect(url_for('dashboard'))

        # Check if it's a father login
        elif username in fathers and fathers[username] == password:
            return redirect(url_for('father_dashboard'))

        else:
            return render_template('login.html', error="Invalid credentials. Please try again.")

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/father_login', methods=['GET', 'POST'])
def father_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if it's a valid father login
        if username in fathers and fathers[username] == password:
            return redirect(url_for('father_dashboard'))

        else:
            return render_template('father_login.html', error="Invalid credentials. Please try again.")

    return render_template('father_login.html')

@app.route('/father_dashboard')
def father_dashboard():
    return render_template('father_dashboard.html')

@app.route('/history')
def history():
    return render_template('history.html')

if __name__ == '__main__':
    app.run(debug=True)
