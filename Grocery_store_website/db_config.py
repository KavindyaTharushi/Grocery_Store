from flask_mysqldb import MySQL
import os

def init_db(app):
    app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', '127.0.0.1')
    app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
    app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'tharushi@2001')
    app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'grocery_store')
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
    return MySQL(app)