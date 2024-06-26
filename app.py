from flask import Flask, render_template, request, redirect, url_for, flash, session
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
    return render_template("index.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        display_name = request.form['display_name']
        role = request.form['role']

        if not username or not password or not display_name or not role:
            flash('All fields are required!')
            return redirect(url_for('register'))

        password_hash = generate_password_hash(password)

        conn = get_db()
        cur = conn.cursor()
        try:
            cur.execute('''
                INSERT INTO Users (username, password_hash, display_name, role)
                VALUES (?, ?, ?, ?)
            ''', (username, password_hash, display_name, role))
            conn.commit()
            flash('User registered successfully!')
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            flash('Username already exists!')
        finally:
            conn.close()
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        cur = conn.cursor()
        cur.execute('SELECT * FROM Users WHERE username = ?', (username,))
        user = cur.fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['display_name'] = user['display_name']
            session['role'] = user['role']
            flash('Logged in successfully!')
            return redirect(url_for('inventory_list'))
        else:
            flash('Invalid username or password')
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!')
    return redirect(url_for('login'))

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

@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        price = request.form['price']
        quantity = request.form['quantity']

        if not name or not category or not price or not quantity:
            flash('All fields are required!')
            return redirect(url_for('edit_product', product_id=product_id))

        cur.execute('''
            UPDATE Products SET name = ?, category = ?, price = ?, quantity = ?
            WHERE id = ?
        ''', (name, category, float(price), int(quantity), product_id))
        conn.commit()
        conn.close()
        flash('Product updated successfully!')
        return redirect(url_for('product_list'))

    cur.execute('SELECT * FROM Products WHERE id = ?', (product_id,))
    product = cur.fetchone()
    conn.close()
    return render_template('edit_product.html', product=product)

@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM Products WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()
    flash('Product deleted successfully!')
    return redirect(url_for('product_list'))

@app.route('/add_inventory', methods=['GET', 'POST'])
def add_inventory():
    if request.method == 'POST':
        product_id = request.form['product_id']
        user_id = request.form['user_id']
        quantity = request.form['quantity']
        note = request.form['note']

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
    cur.execute('SELECT * FROM Users')
    users = cur.fetchall()
    conn.close()
    return render_template('add_inventory.html', products=products, users=users)

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

@app.route('/edit_inventory/<int:inventory_id>', methods=['GET', 'POST'])
def edit_inventory(inventory_id):
    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':
        product_id = request.form['product_id']
        user_id = request.form['user_id']
        quantity = request.form['quantity']
        note = request.form['note']

        if not product_id or not user_id or not quantity:
            flash('All fields are required!')
            return redirect(url_for('edit_inventory', inventory_id=inventory_id))

        cur.execute('''
            UPDATE Inventory SET product_id = ?, user_id = ?, quantity = ?, note = ?
            WHERE id = ?
        ''', (product_id, user_id, int(quantity), note, inventory_id))
        cur.execute('''
            UPDATE Products SET quantity = quantity + ?
            WHERE id = ?
        ''', (int(quantity), product_id))
        conn.commit()
        conn.close()
        flash('Inventory updated successfully!')
        return redirect(url_for('inventory_list'))

    cur.execute('SELECT * FROM Inventory WHERE id = ?', (inventory_id,))
    inventory = cur.fetchone()
    cur.execute('SELECT * FROM Products')
    products = cur.fetchall()
    cur.execute('SELECT * FROM Users')
    users = cur.fetchall()
    conn.close()
    return render_template('edit_inventory.html', inventory=inventory, products=products, users=users)

@app.route('/delete_inventory/<int:inventory_id>', methods=['POST'])
def delete_inventory(inventory_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM Inventory WHERE id = ?', (inventory_id,))
    conn.commit()
    conn.close()
    flash('Inventory deleted successfully!')
    return redirect(url_for('inventory_list'))

if __name__ == '__main__':
    app.run(debug=True)
