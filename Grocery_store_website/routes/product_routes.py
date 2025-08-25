from flask import Blueprint, request, jsonify

product_bp = Blueprint('product', __name__)
mysql = None  # injected in app.py

@product_bp.route('/product', methods=['GET'])
def api_get_products():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM product ORDER BY product_id DESC")
    return jsonify(cur.fetchall())

@product_bp.route('/product/<int:pid>', methods=['GET'])
def api_get_product(pid):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM product WHERE product_id=%s", (pid,))
    row = cur.fetchone()
    if not row:
        return jsonify({'message':'Not found'}), 404
    return jsonify(row)

@product_bp.route('/product', methods=['POST'])
def api_create_product():
    data = request.json or {}
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO product (name, category, price, discount, image_url) VALUES (%s,%s,%s,%s,%s)",
        (data.get('name'), data.get('category'), data.get('price',0), data.get('discount',0), data.get('image_url'))
    )
    mysql.connection.commit()
    return jsonify({'message':'created','product_id':cur.lastrowid}), 201

@product_bp.route('/product/<int:pid>', methods=['PUT'])
def api_update_product(pid):
    data = request.json or {}
    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE product SET name=%s, category=%s, price=%s, discount=%s, image_url=%s WHERE product_id=%s",
        (data.get('name'), data.get('category'), data.get('price',0), data.get('discount',0), data.get('image_url'), pid)
    )
    mysql.connection.commit()
    return jsonify({'message':'updated'})

@product_bp.route('/product/<int:pid>', methods=['DELETE'])
def api_delete_product(pid):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM product WHERE product_id=%s", (pid,))
    mysql.connection.commit()
    return jsonify({'message':'deleted'})