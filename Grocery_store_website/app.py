from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
from db_config import init_db
import routes.product_routes as product_module
import routes.customer_routes as customer_module
import routes.order_routes as order_module

app = Flask(__name__)
mysql = init_db(app)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Inject the mysql instance into route modules
product_module.mysql = mysql
customer_module.mysql = mysql
order_module.mysql = mysql

# Register blueprints (API routes)
app.register_blueprint(product_module.product_bp)
app.register_blueprint(customer_module.customer_bp)
app.register_blueprint(order_module.order_bp)

@app.route('/add-product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        product_name = request.form['product_name']
        category = request.form['category']
        price = request.form['price']
        discount = request.form['discount']
        image = request.files['image']

        filename = None
        if image:
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

if __name__ == '__main__':
    app.run(debug=True)
