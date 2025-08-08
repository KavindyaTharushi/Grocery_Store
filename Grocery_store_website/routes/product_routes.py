from flask import Blueprint, request, jsonify

product_bp = Blueprint('product', __name__)
mysql = None  # Will be set from app.py

@product_bp.route('/product', methods=['GET'])
def get_all_products():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM product")
    rows = cur.fetchall()
    columns = [col[0] for col in cur.description]
    results = [dict(zip(columns, row)) for row in rows]
    return jsonify(results)

@product_bp.route('/product/<int:id>', methods=['GET'])
def get_product(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM product WHERE product_id = %s", (id,))
    row = cur.fetchone()
    if row:
        columns = [col[0] for col in cur.description]
        return jsonify(dict(zip(columns, row)))
    return jsonify({"message": "Product not found"}), 404

@product_bp.route('/product', methods=['POST'])
def create_product():
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO product (name, category, price, discount, image_url)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        data['name'], data['category'], data['price'], data['discount'], data['image_url']
    ))
    mysql.connection.commit()
    return jsonify({"message": "Product added successfully"}), 201

@product_bp.route('/product/<int:id>', methods=['PUT'])
def update_product(id):
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE product SET name=%s, category=%s, price=%s, discount=%s, image_url=%s
        WHERE product_id = %s
    """, (
        data['name'], data['category'], data['price'], data['discount'], data['image_url'], id
    ))
    mysql.connection.commit()
    return jsonify({"message": "Product updated successfully"})

@product_bp.route('/product/<int:id>', methods=['DELETE'])
def delete_product(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM product WHERE product_id = %s", (id,))
    mysql.connection.commit()
    return jsonify({"message": "Product deleted successfully"})
