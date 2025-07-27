from flask import Flask
from db_config import init_db
from routes.product_routes import product_bp
import routes.product_routes as product_module  # access the global `mysql` in routes
from routes.customer_routes import customer_bp
import routes.customer_routes as customer_module
from routes.order_routes import order_bp
import routes.order_routes as order_module


app = Flask(__name__)
mysql = init_db(app)

# Inject the mysql instance into the routes file
product_module.mysql = mysql
customer_module.mysql = mysql
order_module.mysql = mysql

# Register the blueprint
app.register_blueprint(product_bp)
app.register_blueprint(customer_bp)
app.register_blueprint(order_bp)

if __name__ == '__main__':
    app.run(debug=True)
