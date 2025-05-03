from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenditure.db'
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Replace with a secure key
db = SQLAlchemy(app)

# Models
class Expenditure(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(100), default=datetime.utcnow)

class Father(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(100), nullable=False)

# Routes
@app.route('/')
def home():
    return redirect(url_for('dashboard'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    expenditures = Expenditure.query.all()
    current_balance = sum([exp.amount for exp in expenditures])

    if request.method == 'POST':
        amount = request.form['amount']
        description = request.form['description']
        if amount and description:
            new_exp = Expenditure(amount=-float(amount), description=description, date=datetime.utcnow())
            db.session.add(new_exp)
            db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('dashboard.html', expenditures=expenditures, current_balance=current_balance)

@app.route('/father_login', methods=['GET', 'POST'])
def father_login():
    if request.method == 'POST':
        password = request.form['password']
        father = Father.query.first()
        if father and password == father.password:
            session['father_logged_in'] = True
            return redirect(url_for('father_dashboard'))
        return 'Invalid credentials, try again.'
    return render_template('father_login.html')

@app.route('/father_dashboard', methods=['GET', 'POST'])
def father_dashboard():
    if 'father_logged_in' not in session:
        return redirect(url_for('father_login'))

    expenditures = Expenditure.query.all()
    current_balance = sum([exp.amount for exp in expenditures])

    if request.method == 'POST':
        add_money = request.form['add_money']
        if add_money:
            new_exp = Expenditure(amount=float(add_money), description="Money added by Father", date=datetime.utcnow())
            db.session.add(new_exp)
            db.session.commit()
        return redirect(url_for('father_dashboard'))

    return render_template('father_dashboard.html', expenditures=expenditures, current_balance=current_balance)

@app.route('/father_logout')
def father_logout():
    session.pop('father_logged_in', None)
    return redirect(url_for('father_login'))

# Initialize the database
with app.app_context():
    db.create_all()
    # Create a default father password if not exists
    if not Father.query.first():
        default_father = Father(password='father123')  # Change this password as needed
        db.session.add(default_father)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
