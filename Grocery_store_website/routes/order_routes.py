from flask import Blueprint, request, jsonify

order_bp = Blueprint('order', __name__)
mysql = None

@order_bp.route('/order', methods=['GET'])
def api_get_orders():
    cur = mysql.connection.cursor()
    cur.execute(
        '''
        SELECT o.order_id, o.customer_id, c.name as customer_name, o.total_price, o.order_date
        FROM orders o JOIN customer c ON o.customer_id=c.customer_id
        ORDER BY o.order_id DESC
        '''
    )
    return jsonify(cur.fetchall())

@order_bp.route('/order/<int:oid>', methods=['GET'])
def api_get_order(oid):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM orders WHERE order_id=%s", (oid,))
    order = cur.fetchone()
    if not order:
        return jsonify({'message':'Not found'}), 404
    cur.execute(
        '''
        SELECT oi.order_item_id, oi.product_id, p.name, oi.quantity, oi.price
        FROM order_items oi JOIN product p ON oi.product_id=p.product_id
        WHERE oi.order_id=%s
        ''',
        (oid,)
    )
    items = cur.fetchall()
    return jsonify({'order': order, 'items': items})

@order_bp.route('/order', methods=['POST'])
def api_create_order():
    data = request.json or {}
    customer_id = data.get('customer_id')
    items = data.get('items', [])
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO orders (customer_id,total_price) VALUES (%s, 0)", (customer_id,))
    oid = cur.lastrowid
    total = 0.0
    for item in items:
        pid = int(item['product_id'])
        qty = int(item.get('quantity',1))
        cur.execute("SELECT price FROM product WHERE product_id=%s", (pid,))
        price = cur.fetchone()['price']
        total += float(price)*qty
        cur.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s,%s,%s,%s)",
            (oid, pid, qty, price)
        )
    cur.execute("UPDATE orders SET total_price=%s WHERE order_id=%s", (total, oid))
    mysql.connection.commit()
    return jsonify({'message':'created','order_id':oid}), 201

@order_bp.route('/order/<int:oid>', methods=['DELETE'])
def api_delete_order(oid):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM order_items WHERE order_id=%s", (oid,))
    cur.execute("DELETE FROM orders WHERE order_id=%s", (oid,))
    mysql.connection.commit()
    return jsonify({'message':'deleted'})