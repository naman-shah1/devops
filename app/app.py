from datetime import datetime, timezone
from flask import Flask, render_template, redirect, session, request, url_for
from supabase import create_client
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Supabase config
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

MAX_ORDER_HISTORY = 25

# In-memory demo user store for basic auth pages.
registered_users = {}


def _current_user():
    return session.get("user")


@app.context_processor
def inject_current_user():
    return {"current_user": _current_user()}


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    error = None
    username = ""

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not username:
            error = "Please enter a username."
        elif not password:
            error = "Please enter a password."
        elif password != confirm_password:
            error = "Passwords do not match."
        elif username in registered_users:
            error = "That username is already taken."

        if not error:
            registered_users[username] = password
            session["user"] = {"username": username}
            return redirect(url_for('home'))

    return render_template('signin.html', error=error, username=username)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    username = ""

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username:
            error = "Please enter a username."
        elif not password:
            error = "Please enter a password."
        elif username not in registered_users or registered_users[username] != password:
            error = "Invalid username or password."

        if not error:
            session["user"] = {"username": username}
            return redirect(url_for('home'))

    return render_template('login.html', error=error, username=username)


@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect(url_for('home'))


def _cart_line_items(cart):
    """Resolve session cart dict to product rows with quantity and subtotal."""
    items = []
    total = 0
    for pid, qty in (cart or {}).items():
        response = supabase.table("products").select("*").eq("id", int(pid)).execute()
        if not response.data:
            continue
        product = dict(response.data[0])
        product["quantity"] = qty
        product["subtotal"] = qty * product["price"]
        items.append(product)
        total += product["subtotal"]
    return items, total


# 🏠 Home
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/health')
def health():
    return {'status': 'ok'}, 200
    
# 🛍️ Products
@app.route('/products')
def show_products():
    response = supabase.table("products").select("*").execute()
    products = response.data or []
    return render_template('products.html', products=products)


# ➕ Add to Cart
@app.route('/add-to-cart/<int:product_id>')
def add_to_cart(product_id):
    if "cart" not in session:
        session["cart"] = {}

    cart = session["cart"]
    pid = str(product_id)

    if pid in cart:
        cart[pid] += 1
    else:
        cart[pid] = 1

    session["cart"] = cart
    session.modified = True

    return redirect('/cart')


# ➖ Decrease Quantity
@app.route('/decrease/<int:product_id>')
def decrease(product_id):
    cart = session.get("cart", {})
    pid = str(product_id)

    if pid in cart:
        cart[pid] -= 1
        if cart[pid] <= 0:
            del cart[pid]

    session["cart"] = cart
    session.modified = True

    return redirect('/cart')


# ❌ Remove Item
@app.route('/remove/<int:product_id>')
def remove(product_id):
    cart = session.get("cart", {})
    pid = str(product_id)

    if pid in cart:
        del cart[pid]

    session["cart"] = cart
    session.modified = True

    return redirect('/cart')


# 🛒 Cart Page
@app.route('/cart')
def view_cart():
    cart = session.get("cart", {})
    items, total = _cart_line_items(cart)
    return render_template('cart.html', items=items, total=total)


# ✅ Checkout
@app.route('/checkout')
def checkout():
    cart = session.get("cart", {})
    items, total = _cart_line_items(cart)

    if not items:
        return redirect('/cart')

    placed = datetime.now(timezone.utc)
    order = {
        "id": str(uuid.uuid4()),
        "placed_at": placed.isoformat(),
        "placed_at_label": placed.strftime("%d %b %Y, %H:%M UTC"),
        "items": [
            {
                "id": row["id"],
                "name": row["name"],
                "price": row["price"],
                "quantity": row["quantity"],
                "subtotal": row["subtotal"],
                "image_url": row.get("image_url"),
            }
            for row in items
        ],
        "total": total,
        "item_count": sum(row["quantity"] for row in items),
    }

    history = list(session.get("order_history", []))
    history.insert(0, order)
    session["order_history"] = history[:MAX_ORDER_HISTORY]
    session.pop("cart", None)
    session.modified = True

    return render_template('checkout.html')


# 📜 Order history
@app.route('/orders')
def order_history():
    orders = list(session.get("order_history", []))
    return render_template('orders.html', orders=orders)


# ❤️ Health Check
@app.route('/health')
def health():
    return {"status": "running"}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
