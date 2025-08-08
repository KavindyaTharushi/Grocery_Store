from flask import Flask, render_template
from db_config import init_db
import routes.product_routes as product_module
import routes.customer_routes as customer_module
import routes.order_routes as order_module

app = Flask(__name__)
mysql = init_db(app)

# Inject the mysql instance into route modules
product_module.mysql = mysql
customer_module.mysql = mysql
order_module.mysql = mysql

# Register blueprints (API routes)
app.register_blueprint(product_module.product_bp)
app.register_blueprint(customer_module.customer_bp)
app.register_blueprint(order_module.order_bp)

# New route to render HTML product page
@app.route('/products')
def product_page():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM product")
    rows = cur.fetchall()
    columns = [col[0] for col in cur.description]
    products = [dict(zip(columns, row)) for row in rows]
    return render_template('product.html', products=products)

if __name__ == '__main__':
    app.run(debug=True)
