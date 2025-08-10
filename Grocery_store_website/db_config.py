from flask_mysqldb import MySQL
import MySQLdb.cursors

def init_db(app):
    app.config['MYSQL_HOST'] = '127.0.0.1'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'tharushi@2001'
    app.config['MYSQL_DB'] = 'grocery_store'
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'  

    return MySQL(app)
