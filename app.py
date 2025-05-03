from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# ---------- DATABASE SETUP ----------
def init_db():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                role TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                amount REAL,
                type TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Add default users if not present
        cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('user', 'userpass', 'user')")
        cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('father', 'fatherpass', 'father')")

init_db()

# ---------- ROUTES ----------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username, password = request.form['username'], request.form['password']
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
            result = cursor.fetchone()
            if result:
                session['username'] = username
                session['role'] = result[0]
                if result[0] == 'user':
                    return redirect(url_for('user_dashboard'))
                else:
                    return redirect(url_for('father_dashboard'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/user', methods=['GET', 'POST'])
def user_dashboard():
    if 'username' not in session or session['role'] != 'user':
        return redirect(url_for('login'))

    username = session['username']
    if request.method == 'POST':
        amount = float(request.form['amount'])
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO transactions (username, amount, type) VALUES (?, ?, ?)", (username, amount, 'debit'))
    transactions, balance = get_user_data(username)
    return render_template('user_dashboard.html', username=username, balance=balance, transactions=transactions)

@app.route('/father', methods=['GET', 'POST'])
def father_dashboard():
    if 'username' not in session or session['role'] != 'father':
        return redirect(url_for('login'))

    if request.method == 'POST':
        amount = float(request.form['amount'])
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO transactions (username, amount, type) VALUES (?, ?, ?)", ('user', amount, 'credit'))

    transactions, balance = get_user_data('user')
    return render_template('father_dashboard.html', username='user', balance=balance, transactions=transactions)

def get_user_data(username):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT amount, type, timestamp FROM transactions WHERE username=? ORDER BY timestamp DESC", (username,))
        transactions = cursor.fetchall()
        balance = 0
        for amt, ttype, _ in transactions:
            balance += amt if ttype == 'credit' else -amt
        return transactions, balance

if __name__ == '__main__':
    app.run(debug=True)
