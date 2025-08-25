from flask import Blueprint, request, jsonify

customer_bp = Blueprint('customer', __name__)
mysql = None

@customer_bp.route('/customer', methods=['GET'])
def api_get_customers():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM customer ORDER BY customer_id DESC")
    return jsonify(cur.fetchall())

@customer_bp.route('/customer/<int:cid>', methods=['GET'])
def api_get_customer(cid):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM customer WHERE customer_id=%s", (cid,))
    row = cur.fetchone()
    if not row:
        return jsonify({'message':'Not found'}), 404
    return jsonify(row)

@customer_bp.route('/customer', methods=['POST'])
def api_create_customer():
    data = request.json or {}
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO customer (name, email, phone, address) VALUES (%s,%s,%s,%s)",
        (data.get('name'), data.get('email'), data.get('phone'), data.get('address'))
    )
    mysql.connection.commit()
    return jsonify({'message':'created','customer_id':cur.lastrowid}), 201

@customer_bp.route('/customer/<int:cid>', methods=['PUT'])
def api_update_customer(cid):
    data = request.json or {}
    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE customer SET name=%s, email=%s, phone=%s, address=%s WHERE customer_id=%s",
        (data.get('name'), data.get('email'), data.get('phone'), data.get('address'), cid)
    )
    mysql.connection.commit()
    return jsonify({'message':'updated'})

@customer_bp.route('/customer/<int:cid>', methods=['DELETE'])
def api_delete_customer(cid):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM customer WHERE customer_id=%s", (cid,))
    mysql.connection.commit()
    return jsonify({'message':'deleted'})