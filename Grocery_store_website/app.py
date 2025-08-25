from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
from db_config import init_db
from routes.product_routes import product_bp
from routes.customer_routes import customer_bp
from routes.order_routes import order_bp
import routes.product_routes as product_module
import routes.customer_routes as customer_module
import routes.order_routes as order_module

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

# DB
mysql = init_db(app)
product_module.mysql = mysql
customer_module.mysql = mysql
order_module.mysql = mysql

# Blueprints (JSON APIs)
app.register_blueprint(product_bp)
app.register_blueprint(customer_bp)
app.register_blueprint(order_bp)

# Uploads
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------- PAGES ----------
@app.route('/home')
def home():
 
    return render_template('home.html')

# PRODUCTS
@app.route('/products')
def product_page():
    cur = mysql.connection.cursor()
    cur.execute("SELECT product_id, name, category, price, discount, image_url FROM product ORDER BY product_id DESC")
    products = cur.fetchall()
    return render_template('product.html', products=products)

@app.route('/add-product', methods=['GET','POST'])
def add_product():
    if request.method == 'POST':
        # handle both `product_name` and `name`
        name = request.form.get('product_name') or request.form.get('name')
        category = request.form.get('category')
        price = request.form.get('price', type=float)
        discount = request.form.get('discount', type=float, default=0.0)
        image = request.files.get('image')
        image_url = None
        if image and allowed_file(image.filename):
            fname = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
            image_url = fname
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO product (name, category, price, discount, image_url) VALUES (%s,%s,%s,%s,%s)",
            (name, category, price, discount, image_url)
        )
        mysql.connection.commit()
        flash('Product added', 'success')
        return redirect(url_for('product_page'))
    return render_template('add_product.html')

@app.route('/update-product/<int:product_id>', methods=['GET','POST'])
def update_product(product_id):
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        name = request.form.get('name') or request.form.get('product_name')
        category = request.form.get('category')
        price = request.form.get('price', type=float)
        discount = request.form.get('discount', type=float, default=0.0)
        image = request.files.get('image')
        if image and allowed_file(image.filename):
            fname = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
            cur.execute(
                "UPDATE product SET name=%s, category=%s, price=%s, discount=%s, image_url=%s WHERE product_id=%s",
                (name, category, price, discount, fname, product_id)
            )
        else:
            cur.execute(
                "UPDATE product SET name=%s, category=%s, price=%s, discount=%s WHERE product_id=%s",
                (name, category, price, discount, product_id)
            )
        mysql.connection.commit()
        flash('Product updated', 'success')
        return redirect(url_for('product_page'))
    # GET
    cur.execute("SELECT * FROM product WHERE product_id=%s", (product_id,))
    product = cur.fetchone()
    if not product:
        flash('Product not found', 'danger')
        return redirect(url_for('product_page'))
    return render_template('update_product.html', product=product)

@app.route('/delete-product/<int:product_id>', methods=['POST'])
def delete_product_page(product_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM product WHERE product_id=%s", (product_id,))
    mysql.connection.commit()
    flash('Product deleted', 'success')
    return redirect(url_for('product_page'))

# CUSTOMERS
@app.route('/customers')
def customers():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM customer ORDER BY customer_id DESC")
    customers = cur.fetchall()
    return render_template('customers.html', customers=customers)

@app.route('/customers/add', methods=['GET','POST'])
def add_customer():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        address = request.form.get('address')
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO customer (name,email,phone,password,address) VALUES (%s,%s,%s,%s,%s)", (name,email,phone,password,address))
        mysql.connection.commit()
        flash('Customer added', 'success')
        return redirect(url_for('customers'))
    return render_template('add_customer.html')

@app.route('/customers/edit/<int:customer_id>', methods=['GET','POST'])
def edit_customer(customer_id):
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        cur.execute("UPDATE customer SET name=%s,email=%s,phone=%s,address=%s WHERE customer_id=%s",
                    (name,email,phone,address,customer_id))
        mysql.connection.commit()
        flash('Customer updated', 'success')
        return redirect(url_for('customers'))
    cur.execute("SELECT * FROM customer WHERE customer_id=%s", (customer_id,))
    row = cur.fetchone()
    if not row:
        flash('Customer not found', 'danger')
        return redirect(url_for('customers'))
    return render_template('update_customer.html', customer=row)

@app.route('/customers/delete/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM customer WHERE customer_id=%s", (customer_id,))
    mysql.connection.commit()
    flash('Customer deleted', 'success')
    return redirect(url_for('customers'))

# ORDERS
@app.route('/orders')
def orders_page():
    cur = mysql.connection.cursor()
    cur.execute(
        '''
        SELECT o.order_id, o.customer_id, c.name AS customer_name, o.total_price, o.order_date
        FROM orders o JOIN customer c ON o.customer_id = c.customer_id
        ORDER BY o.order_id DESC
        '''
    )
    orders = cur.fetchall()
    # render to 'order.html' to reuse your filename
    return render_template('order.html', orders=orders)

@app.route('/orders/create', methods=['GET','POST'])
def create_order_page():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        customer_id = request.form.get('customer_id', type=int)
        product_ids = request.form.getlist('product_id')
        quantities = request.form.getlist('quantity')
        cur.execute("INSERT INTO orders (customer_id, total_price) VALUES (%s, 0)", (customer_id,))
        order_id = cur.lastrowid
        total = 0.0
        for pid, qty in zip(product_ids, quantities):
            qty = int(qty or 0)
            if qty <= 0:
                continue
            cur.execute("SELECT price FROM product WHERE product_id=%s", (pid,))
            price = cur.fetchone()['price']
            total += float(price) * qty
            cur.execute("INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s,%s,%s,%s)",
                        (order_id, pid, qty, price))
        cur.execute("UPDATE orders SET total_price=%s WHERE order_id=%s", (total, order_id))
        mysql.connection.commit()
        flash('Order created', 'success')
        return redirect(url_for('orders_page'))
    # GET
    cur.execute("SELECT customer_id, name FROM customer ORDER BY name")
    customers = cur.fetchall()
    cur.execute("SELECT product_id, name, price FROM product ORDER BY name")
    products = cur.fetchall()
    return render_template('create_order.html', customers=customers, products=products)

@app.route('/orders/<int:order_id>')
def order_detail(order_id):
    cur = mysql.connection.cursor()
    cur.execute(
        '''
        SELECT o.order_id, o.order_date, o.total_price, c.customer_id, c.name, c.email, c.phone
        FROM orders o JOIN customer c ON o.customer_id=c.customer_id WHERE o.order_id=%s
        ''', (order_id,)
    )
    order = cur.fetchone()
    if not order:
        flash('Order not found', 'danger')
        return redirect(url_for('orders_page'))
    cur.execute(
        '''
        SELECT oi.order_item_id, p.name, oi.quantity, oi.price, (oi.quantity*oi.price) AS total
        FROM order_items oi JOIN product p ON oi.product_id=p.product_id
        WHERE oi.order_id=%s
        ''', (order_id,)
    )
    items = cur.fetchall()
    return render_template('order_detail.html', order=order, items=items)

@app.route('/orders/delete/<int:order_id>', methods=['POST'])
def delete_order_page(order_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM order_items WHERE order_id=%s", (order_id,))
    cur.execute("DELETE FROM orders WHERE order_id=%s", (order_id,))
    mysql.connection.commit()
    flash('Order deleted', 'success')
    return redirect(url_for('orders_page'))

if __name__ == '__main__':
    app.run(debug=True)