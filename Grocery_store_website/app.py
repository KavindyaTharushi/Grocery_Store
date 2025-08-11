from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
from db_config import init_db
import routes.product_routes as product_module
import routes.customer_routes as customer_module
import routes.order_routes as order_module

app = Flask(__name__)
mysql = init_db(app)

UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Inject the mysql instance into route modules
product_module.mysql = mysql
customer_module.mysql = mysql
order_module.mysql = mysql

# Register blueprints (API routes)
app.register_blueprint(product_module.product_bp)
app.register_blueprint(customer_module.customer_bp)
app.register_blueprint(order_module.order_bp)

products = []

@app.route('/add-product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        product_name = request.form['product_name']
        category = request.form['category']
        price = request.form['price']
        discount = request.form['discount']
        image = request.files['image']

        filename = None
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)

        # Save to MySQL
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO product (name, category, price, discount, image_url)
            VALUES (%s, %s, %s, %s, %s)
        """, (product_name, category, price, discount, filename))
        mysql.connection.commit()
        cur.close()

        # Redirect to product list page
        return redirect(url_for('product_page'))

    return render_template('add_product.html')

@app.route('/products')
def product_page():
    cur = mysql.connection.cursor()
    cur.execute("SELECT product_id, name, category, price, discount, image_url FROM product")
    products = cur.fetchall()
    cur.close()
    return render_template('product.html', products=products)


@app.route('/update-product/<int:product_id>', methods=['GET', 'POST'])
def update_product(product_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM product WHERE product_id = %s", (product_id,))
    product = cur.fetchone()

    if not product:
        
        return redirect(url_for('product_page'))

    if request.method == 'POST':
        product_name = request.form['name']
        category = request.form['category']
        price = request.form['price']
        discount = request.form['discount']
        image = request.files['image']

        filename = product['image_url']  
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)

        
        cur.execute("""
            UPDATE product
            SET name=%s, category=%s, price=%s, discount=%s, image_url=%s
            WHERE product_id=%s
        """, (product_name, category, price, discount, filename, product_id))
        mysql.connection.commit()
        cur.close()

        
        return redirect(url_for('product_page'))

    cur.close()
    return render_template('update_product.html', product=product)

@app.route('/register', methods=['GET', 'POST'])
def register():
      if request.method == 'POST':
        fullname = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        address = request.form['address']
      
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO customer (name, email, phone, password, address)
            VALUES (%s, %s, %s, %s, %s)
        """, (fullname, email, phone,password, address))
        mysql.connection.commit()
        cur.close()
        
        return redirect(url_for('register'))

      return render_template('register.html')



if __name__ == '__main__':
    app.run(debug=True)


