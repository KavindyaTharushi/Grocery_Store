from flask_mysqldb import MySQL

def init_db(app):
    app.config['MYSQL_HOST'] = '127.0.0.1'
    app.config['MYSQL_PASSWORD'] ='tharushi@2001'
    app.config['MYSQL_USER'] = 'root' 
    app.config['MYSQL_DB'] = 'grocery_store'

    return MySQL(app)