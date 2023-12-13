from flask import Flask, request, jsonify
import random
import string

app = Flask(__name__)

# In-memory storage for cart and orders
carts = {}
orders = []

# Discount configuration
discount_frequency = 5
discount_percentage = 10

# Admin access key (you should use a more secure method in production)
admin_key = "admin123"

@app.route('/')
def index():
    return "Hello Admin, Kindly go to postman and try out the APIs discussed below."

# API to add items to the cart
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    user_id = data.get('user_id')
    item_id = data.get('item_id')
    quantity = data.get('quantity')

    # Add the item to the cart
    if user_id not in carts:
        carts[user_id] = {}
    if item_id not in carts[user_id]:
        carts[user_id][item_id] = 0
    carts[user_id][item_id] += quantity

    return jsonify({"message": "Item added to cart successfully"})

# API to checkout and apply discount if eligible
@app.route('/checkout', methods=['POST'])
def checkout():
    data = request.get_json()
    user_id = data.get('user_id')
    cart = carts.get(user_id, {})

    total_amount = sum(cart.values())

    # Check if the order is eligible for a discount
    if len(orders) % discount_frequency == 0:
        # Generate a discount code
        discount_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        discount_amount = (total_amount * discount_percentage) / 100

        # Add discount details to the orders
        orders.append({
            "user_id": user_id,
            "total_amount": total_amount,
            "discount_code": discount_code,
            "discount_amount": discount_amount
        })

        return jsonify({
            "message": "Order placed successfully with a discount!",
            "discount_code": discount_code,
            "discount_amount": discount_amount
        })

    # No discount for this order
    orders.append({"user_id": user_id, "total_amount": total_amount})
    return jsonify({"message": "Order placed successfully"})

# Admin API to generate discount code
@app.route('/admin/generate_discount_code', methods=['POST'])
def generate_discount_code():
    admin_key_input = request.headers.get('admin-key')
    if admin_key_input != admin_key:
        return jsonify({"error": "Unauthorized"}), 401

    # Check if the condition for discount is satisfied
    if len(orders) % discount_frequency == 0:
        # Generate a discount code
        discount_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        return jsonify({"discount_code": discount_code})

    return jsonify({"message": "Discount code not generated. Condition not satisfied."})

# Admin API to get statistics
@app.route('/admin/statistics', methods=['GET'])
def get_statistics():
    admin_key_input = request.headers.get('admin-key')
    if admin_key_input != admin_key:
        return jsonify({"error": "Unauthorized"}), 401

    total_items_purchased = sum([sum(cart.values()) for cart in carts.values()])
    total_purchase_amount = sum([order["total_amount"] for order in orders])
    discount_codes = [order["discount_code"] for order in orders if "discount_code" in order]
    total_discount_amount = sum([order["discount_amount"] for order in orders if "discount_amount" in order])

    return jsonify({
        "total_items_purchased": total_items_purchased,
        "total_purchase_amount": total_purchase_amount,
        "discount_codes": discount_codes,
        "total_discount_amount": total_discount_amount
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
