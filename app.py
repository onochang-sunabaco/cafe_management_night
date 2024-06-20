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

@app.route('/product_list')
def product_list():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM Products')
    products = cur.fetchall()
    conn.close()
    return render_template('product_list.html', products=products)

# 入出庫の登録
@app.route('/add_inventory', methods=['GET', 'POST'])
def add_inventory():
    if request.method == 'POST':
        product_id = request.form['product_id']
        user_id = request.form['user_id']
        quantity = request.form['quantity']
        note = request.form['note']

        print(product_id)
        print(user_id)
        print(quantity)
        print(note)

        if not product_id or not user_id or not quantity:
            flash('All fields are required!')
            return redirect(url_for('add_inventory'))

        conn = get_db()
        cur = conn.cursor()
        try:
            cur.execute('''
                INSERT INTO Inventory (product_id, user_id, quantity, received_date, note)
                VALUES (?, ?, ?, datetime('now'), ?)
            ''', (product_id, user_id, int(quantity), note))
            cur.execute('''
                UPDATE Products SET quantity = quantity + ?
                WHERE id = ?
            ''', (int(quantity), product_id))
            conn.commit()
            flash('Inventory updated successfully!')
        except Exception as e:
            flash(f'Error: {e}')
        finally:
            conn.close()
        
        return redirect(url_for('add_inventory'))

    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM Products')
    products = cur.fetchall()
    print("-------")
    print(products)
    cur.execute('SELECT * FROM Users')
    users = cur.fetchall()
    print(users)
    conn.close()
    return render_template('add_inventory.html', products=products, users=users)


# 入出庫履歴の表示
@app.route('/inventory_list')
def inventory_list():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        SELECT Inventory.id, Products.name as product_name, Users.display_name as user_name, 
               Inventory.quantity, Inventory.received_date, Inventory.note
        FROM Inventory
        JOIN Products ON Inventory.product_id = Products.id
        JOIN Users ON Inventory.user_id = Users.id
        ORDER BY Inventory.received_date DESC
    ''')
    inventory = cur.fetchall()
    conn.close()
    return render_template('inventory_list.html', inventory=inventory)



if __name__ == '__main__':
    app.run(debug=True)
