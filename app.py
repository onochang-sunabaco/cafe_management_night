from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'supersecretkey'

DATABASE = 'cafe_management.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return 'Welcome to Cafe Management System'

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        price = request.form['price']
        quantity = request.form['quantity']

        if not name or not category or not price or not quantity:
            flash('All fields are required!')
            return redirect(url_for('add_product'))

        conn = get_db()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO Products (name, category, price, quantity)
            VALUES (?, ?, ?, ?)
        ''', (name, category, float(price), int(quantity)))
        conn.commit()
        conn.close()
        flash('Product added successfully!')
        return redirect(url_for('add_product'))

    return render_template('add_product.html')

if __name__ == '__main__':
    app.run(debug=True)
