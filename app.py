from flask import Flask, render_template, redirect, url_for, request, jsonify
import sqlite3

app = Flask(__name__)

PRESENTATION_MODE = True

cart = {}

products = [
    {"name": "Cleanser", "price": 299, "img": "cleanser.webp", "rating": 4.5},
    {"name": "Serum", "price": 499, "img": "serum.webp", "rating": 4.7},
    {"name": "Sunscreen", "price": 399, "img": "sunscreen.webp", "rating": 4.6},
    {"name": "BodyWash", "price": 249, "img": "bodywash.webp", "rating": 4.4},
    {"name": "Moisturizer", "price": 349, "img": "moisturizer.webp", "rating": 4.6},
    {"name": "Night Cream", "price": 599, "img": "nightcream.webp", "rating": 4.7},
    {"name": "Lip Balm", "price": 149, "img": "lipbalm.webp", "rating": 4.3},
    {"name": "Toner", "price": 279, "img": "toner.webp", "rating": 4.5},
    {"name": "Sheet Mask", "price": 99, "img": "sheetmask.webp", "rating": 4.2},
    {"name": "Eye Cream", "price": 699, "img": "eyecream.webp", "rating": 4.6},
    {"name": "Face Scrub", "price": 199, "img": "facescrub.webp", "rating": 4.3},
    {"name": "Hair Oil", "price": 299, "img": "hairoil.webp", "rating": 4.5}
]

# INIT DB
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            address TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT,
            quantity INTEGER,
            total_price INTEGER
        )
    ''')

    conn.commit()
    conn.close()

# HOME
@app.route('/')
def home():
    return render_template("index.html", products=products)

# ADD TO CART
@app.route('/add/<name>')
def add(name):
    if name in cart:
        cart[name]["qty"] += 1
    else:
        for p in products:
            if p["name"] == name:
                cart[name] = {"data": p, "qty": 1}
    return redirect(url_for('home'))

# CART
@app.route('/cart')
def view_cart():
    total = sum(item["data"]["price"] * item["qty"] for item in cart.values())
    return render_template("cart.html", cart=cart, total=total)

# CHECKOUT
@app.route('/checkout')
def checkout():
    total = sum(item["data"]["price"] * item["qty"] for item in cart.values())
    return render_template("checkout.html", total=total)

# ORDER
@app.route('/place_order', methods=['POST'])
def place_order():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    for item in cart.values():
        name = item["data"]["name"]
        qty = item["qty"]
        total = item["data"]["price"] * qty

        c.execute(
            "INSERT INTO orders (product_name, quantity, total_price) VALUES (?, ?, ?)",
            (name, qty, total)
        )

    conn.commit()
    conn.close()

    cart.clear()
    return redirect(url_for('success'))

# SUCCESS
@app.route('/success')
def success():
    return render_template("success.html")

# ACCOUNT
@app.route('/account')
def account():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("SELECT * FROM users ORDER BY id DESC LIMIT 1")
    data = c.fetchone()

    conn.close()

    if PRESENTATION_MODE:
        user = {"name": "", "phone": "", "address": ""}
    else:
        if data:
            user = {"name": data[1], "phone": data[2], "address": data[3]}
        else:
            user = {"name": "", "phone": "", "address": ""}

    return render_template("account.html", user=user)

# SAVE ACCOUNT
@app.route('/save_account', methods=['POST'])
def save_account():
    name = request.form.get("name")
    phone = request.form.get("phone")
    address = request.form.get("address")

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("DELETE FROM users")
    c.execute("INSERT INTO users (name, phone, address) VALUES (?, ?, ?)",
              (name, phone, address))

    conn.commit()
    conn.close()

    return redirect(url_for('account'))

# ANALYZER
@app.route('/analyzer')
def analyzer():
    return render_template("analyzer.html")

@app.route('/analyze', methods=['POST'])
def analyze():
    import random

    skin_types = ["Oily Skin", "Dry Skin", "Combination Skin", "Acne Prone Skin"]

    advice = {
        "Oily Skin": "Use oil-free cleanser + gel moisturizer",
        "Dry Skin": "Use hydrating cream + gentle face wash",
        "Combination Skin": "Balance T-zone skincare",
        "Acne Prone Skin": "Use salicylic acid & avoid heavy creams"
    }

    result = random.choice(skin_types)

    return jsonify({
        "result": result,
        "advice": advice[result]
    })

# RUN (RENDER READY)
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=10000)