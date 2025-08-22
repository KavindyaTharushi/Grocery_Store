from flask import Blueprint, request, jsonify

order_bp = Blueprint('order', __name__)
mysql = None  # will be injected from app.py

# GET all orders

@order_bp.route('/order', methods=['GET'])
def get_orders():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM orders")
    orders = cur.fetchall()
    columns = [col[0] for col in cur.description]
    result = [dict(zip(columns, row)) for row in orders]
    return jsonify(result)

# GET a specific order with items
@order_bp.route('/order/<int:order_id>', methods=['GET'])
def get_order(order_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM orders WHERE order_id = %s", (order_id,))
    order = cur.fetchone()
    if not order:
        return jsonify({"message": "Order not found"}), 404

    columns = [col[0] for col in cur.description]
    order_data = dict(zip(columns, order))

    cur.execute("""
        SELECT oi.order_item_id, oi.product_id, p.name AS product_name, oi.quantity, oi.price
        FROM order_items oi
        JOIN product p ON oi.product_id = p.product_id
        WHERE oi.order_id = %s
    """, (order_id,))
    items = cur.fetchall()
    item_columns = [col[0] for col in cur.description]
    order_data['items'] = [dict(zip(item_columns, row)) for row in items]

    return jsonify(order_data)

# POST create new order
@order_bp.route('/order', methods=['POST'])
def create_order():
    data = request.json
    customer_id = data['customer_id']
    status = data.get('status', 'Pending')
    items = data['items']  # list of {product_id, quantity, price}

    total_price = sum(item['quantity'] * item['price'] for item in items)

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO orders (customer_id, status, total_price) VALUES (%s, %s, %s)",
                (customer_id, status, total_price))
    order_id = cur.lastrowid

    for item in items:
        cur.execute("""
            INSERT INTO order_items (order_id, product_id, quantity, price)
            VALUES (%s, %s, %s, %s)
        """, (order_id, item['product_id'], item['quantity'], item['price']))

    mysql.connection.commit()
    return jsonify({"message": "Order created successfully", "order_id": order_id}), 201

# PUT update order status or items
@order_bp.route('/order/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    data = request.json
    status = data.get('status')
    items = data.get('items', [])  # optional, if updating items

    cur = mysql.connection.cursor()

    if status:
        cur.execute("UPDATE orders SET status = %s WHERE order_id = %s", (status, order_id))

    if items:
        # Remove existing items
        cur.execute("DELETE FROM order_items WHERE order_id = %s", (order_id,))
        # Re-insert updated items
        total_price = sum(item['quantity'] * item['price'] for item in items)
        for item in items:
            cur.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, price)
                VALUES (%s, %s, %s, %s)
            """, (order_id, item['product_id'], item['quantity'], item['price']))
        # Update order price
        cur.execute("UPDATE orders SET total_price = %s WHERE order_id = %s", (total_price, order_id))

    mysql.connection.commit()
    return jsonify({"message": "Order updated successfully"})

# DELETE order and its items
@order_bp.route('/order/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM order_items WHERE order_id = %s", (order_id,))
    cur.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))
    mysql.connection.commit()
    return jsonify({"message": "Order deleted successfully"})
