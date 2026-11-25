
from flask import render_template, request, jsonify, redirect
from app.database import db, Order
import json


def register_routes(app):

    menu_items = [
        {
            "id": 1,
            "name": "Classic Burger",
            "category": "Burger",
            "price": 159,
            "description": "Juicy burger with fresh vegetables.",
            "image": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": 2,
            "name": "Italian Pizza",
            "category": "Pizza",
            "price": 249,
            "description": "Fresh cheese, vegetables and delicious sauce.",
            "image": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": 3,
            "name": "Chicken Biryani",
            "category": "Biryani",
            "price": 220,
            "description": "Aromatic rice with flavourful chicken.",
            "image": "https://images.unsplash.com/photo-1563379091339-03246963d96c?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": 4,
            "name": "French Fries",
            "category": "Snacks",
            "price": 99,
            "description": "Crispy golden potato fries.",
            "image": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": 5,
            "name": "Pasta",
            "category": "Pasta",
            "price": 189,
            "description": "Creamy pasta with herbs and sauce.",
            "image": "https://images.unsplash.com/photo-1473093295043-cdd812d0e601?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": 6,
            "name": "Chocolate Brownie",
            "category": "Dessert",
            "price": 120,
            "description": "Rich chocolate brownie for dessert.",
            "image": "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?auto=format&fit=crop&w=600&q=80"
        }
    ]

    # HOME PAGE
    @app.route("/")
    def home():
        return render_template("index.html", menu_items=menu_items)


    # PLACE ORDER API
    @app.route("/place-order", methods=["POST"])
    def place_order():

        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid order data"}), 400

        name = data.get("name", "").strip()
        phone = data.get("phone", "").strip()
        address = data.get("address", "").strip()
        items = data.get("items", [])

        if not name or not phone or not address or not items:
            return jsonify({
                "error": "Please complete all order details"
            }), 400

        if not phone.isdigit() or len(phone) != 10:
            return jsonify({
                "error": "Enter a valid 10-digit phone number"
            }), 400

        menu_by_id = {item["id"]: item for item in menu_items}

        validated_items = []
        total = 0

        for cart_item in items:

            try:
                item_id = int(cart_item.get("id"))
                quantity = int(cart_item.get("quantity"))
            except (TypeError, ValueError):
                return jsonify({
                    "error": "Invalid item or quantity"
                }), 400

            product = menu_by_id.get(item_id)

            if not product or quantity <= 0 or quantity > 100:
                return jsonify({
                    "error": "Invalid cart item"
                }), 400

            subtotal = product["price"] * quantity
            total += subtotal

            validated_items.append({
                "name": product["name"],
                "price": product["price"],
                "quantity": quantity,
                "subtotal": subtotal
            })

        # SAVE ORDER TO DATABASE
        new_order = Order(
            customer_name=name,
            phone=phone,
            address=address,
            items=json.dumps(validated_items),
            total=total,
            status="Pending"
        )

        try:
            db.session.add(new_order)
            db.session.commit()

        except Exception:
            db.session.rollback()
            return jsonify({
                "error": "Unable to save order. Please try again."
            }), 500

        return jsonify({
            "message": "Order submitted successfully!",
            "order_id": new_order.id,
            "customer": name,
            "phone": phone,
            "address": address,
            "items": validated_items,
            "total": total,
            "status": new_order.status
        }), 200


    # ADMIN ORDERS PAGE
    @app.route("/admin/orders")
    def admin_orders():

        orders = Order.query.order_by(Order.id.desc()).all()

        for order in orders:
            order.items_list = json.loads(order.items)

        return render_template(
            "admin_orders.html",
            orders=orders
        )


    # UPDATE ORDER STATUS
    @app.route("/update-status/<int:order_id>", methods=["POST"])
    def update_status(order_id):

        order = Order.query.get_or_404(order_id)

        new_status = request.form.get("status")

        if new_status in ["Pending", "Preparing", "Delivered"]:
            order.status = new_status
            db.session.commit()

        return redirect("/admin/orders")


    # CUSTOMER ORDER TRACKING
    @app.route("/track-order", methods=["GET", "POST"])
    def track_order():

        order = None
        error = None

        if request.method == "POST":

            order_id = request.form.get("order_id", "").strip()
            phone = request.form.get("phone", "").strip()

            if order_id and phone:

                order = Order.query.filter_by(
                    id=order_id,
                    phone=phone
                ).first()

                if not order:
                    error = "Order not found. Please check your details."

                else:
                    # FIX: Convert saved JSON items into a Python list
                    order.items_list = json.loads(order.items)

            else:
                error = "Please enter Order ID and phone number."

        return render_template(
            "track_order.html",
            order=order,
            error=error
        )
