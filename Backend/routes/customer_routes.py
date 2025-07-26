from flask import Blueprint,request,jsonify

customer_bp = Blueprint('customer',__name__)
mysql = None

@customer_bp.route('/customer',methods=['GET'])
def get_all_customers():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM customer" )
    rows = cur.fetchall()
    columns = [col[0] for col in cur.description]
    results = [dict(zip(columns, row)) for row in rows]
    return jsonify(results)

@customer_bp.route('/customer/<int:id>',methods=['GET'])
def get_customers(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM customer WHERE customer_id = %s ",(id,))
    row = cur.fetchone()
    if row:
      columns = [col[0] for col in cur.description]
      return jsonify(dict(zip(columns, row)))
    return jsonify({"message":"customer not found "}),404

@customer_bp.route('/customer',methods=['POST'])
def create_customers():
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("""INSERT INTO customer (name,email,phone,password,address) 
                VALUES (%s,%s,%s,%s,%s)""",(
        data['name'], data['email'], data['phone'],data['password'],data['address']
    ))
    mysql.connection.commit()
    return jsonify({"message": "customer added successfully"}), 201


@customer_bp.route('/customer/<int:id>', methods=['PUT'])
def update_customer(id):
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("""
    UPDATE customer SET name=%s, email=%s, phone=%s, password=%s, address=%s
    WHERE customer_id = %s
    """, (
        data['name'], data['email'], data['phone'],data['password'],data['address'], id
    ))
    mysql.connection.commit()
    return jsonify({"message": "customer updated successfully"})

@customer_bp.route('/customer/<int:id>', methods=['DELETE'])
def delete_customer(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM customer WHERE customer_id = %s", (id,))
    mysql.connection.commit()
    return jsonify({"message": "customer deleted successfully"})