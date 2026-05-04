# http://127.0.0.1:5000

from flask import Flask, request, jsonify, session, redirect
import requests
import random
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = "super_secret_demo_key_123"

YELP_API_KEY = "44rLSZFxLCGwmbm4tZpH61WzzBVkfDBZ7GrJg61Rc_pFdPejlBGZtJxfSMdJgINsXM2gjrz4yN_p5Lb4ybpvwbReW-NtNKb_4bnZcyIy92waqL6e23z2FSJDJLDyaXYx"
YELP_ENDPOINT = "https://api.yelp.com/v3/businesses/search"

# Minneapolis center point
MINNEAPOLIS_LAT = 44.9778
MINNEAPOLIS_LON = -93.2650

# Track last random pick
last_random = None

#Dummy login
DUMMY_EMAIL = "owner@example.com"
DUMMY_PASSWORD = "demo123"


def miles_to_meters(miles):
    return int(float(miles) * 1609.34)


@app.route("/")
def login_page():
    return app.send_static_file("login.html")


@app.route("/home")
def home():
    return app.send_static_file("home.html")


@app.route("/api/restaurants")
def get_restaurants():
    quality_raw = request.args.get("quality", "")
    budget_raw = request.args.get("budget", "")
    distance_raw = request.args.get("distance", "")

    # Convert filters
    min_rating = float(quality_raw) if quality_raw else 0
    max_distance_miles = float(distance_raw) if distance_raw else 20
    max_distance_miles = min(max_distance_miles, 20)  # enforce 20-mile limit
    radius = miles_to_meters(max_distance_miles)

    # Convert budget ($, $$, $$$) → Yelp price levels (1,2,3)
    price_map = {"$": "1", "$$": "2", "$$$": "3"}
    price = price_map.get(budget_raw, None)

    headers = {"Authorization": f"Bearer {YELP_API_KEY}"}

    params = {
        "term": "restaurants",
        "latitude": MINNEAPOLIS_LAT,
        "longitude": MINNEAPOLIS_LON,
        "radius": radius,
        "limit": 50,
        "sort_by": "rating"
    }

    if price:
        params["price"] = price

    response = requests.get(YELP_ENDPOINT, headers=headers, params=params)
    data = response.json().get("businesses", [])

    # Apply rating filter manually (Yelp doesn't support min rating)
    filtered = [
        {
            "name": r["name"],
            "rating": r.get("rating", 0),
            "price": r.get("price", "?"),
            "distance": round(r.get("distance", 0) / 1609.34, 2),  # meters → miles
            "address": " ".join(r["location"].get("display_address", [])),
            "image_url": r.get("image_url", "")
        }
        for r in data
        if r.get("rating", 0) >= min_rating
    ]

    return jsonify(filtered)


@app.route("/api/explore")
def explore():
    global last_random

    headers = {"Authorization": f"Bearer {YELP_API_KEY}"}

    params = {
        "term": "restaurants",
        "latitude": MINNEAPOLIS_LAT,
        "longitude": MINNEAPOLIS_LON,
        "radius": miles_to_meters(20),
        "limit": 50,
        "sort_by": "rating"
    }

    response = requests.get(YELP_ENDPOINT, headers=headers, params=params)
    data = response.json().get("businesses", [])

    # Convert Yelp format → your frontend format
    restaurants = [
        {
            "name": r["name"],
            "rating": r.get("rating", 0),
            "price": r.get("price", "?"),
            "distance": round(r.get("distance", 0) / 1609.34, 2),
            "address": " ".join(r["location"].get("display_address", [])),
            "image_url": r.get("image_url", "")
        }
        for r in data
    ]

    # Avoid repeating the last restaurant
    choices = [r for r in restaurants if r != last_random]
    if not choices:
        choices = restaurants.copy()

    pick = random.choice(choices)
    last_random = pick

    return jsonify(pick)


promotions_list = [
    "20% off at select Minneapolis restaurants today!",
    "Happy Hour deals across Uptown and North Loop!",
    "Free dessert at participating restaurants tonight!"
]


@app.route("/api/promotions")
def get_promotions():
     return jsonify({"promotion": random.choice(promotions_list)})


@app.route("/api/promotions/add", methods=["POST"])
def add_promotion():
    if not session.get("is_owner") and "owner_id" not in session:
        return jsonify({"error": "Unauthorized"}), 403


    data = request.json
    new_promo = data.get("promotion", "")

    if new_promo:
        promotions_list.append(new_promo)
        return jsonify({"status": "success"})

    return jsonify({"error": "No promotion text provided"}), 400


# For testing: view all promotions
@app.route("/api/promotions/all")
def get_all_promotions():
    return jsonify({"promotions": promotions_list})


# Registration
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    hashed = generate_password_hash(password)

    conn = sqlite3.connect("app.db")
    c = conn.cursor()

    try:
        c.execute("INSERT INTO owners (email, password) VALUES (?, ?)", (email, hashed))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already registered"}), 400

    return jsonify({"status": "registered"})


# Login
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    conn = sqlite3.connect("app.db")
    c = conn.cursor()
    c.execute("SELECT id, password FROM owners WHERE email = ?", (email,))
    row = c.fetchone()

    if email == DUMMY_EMAIL and password == DUMMY_PASSWORD:
        session["is_owner"] = True
        return jsonify({"status": "logged_in"})

    if row and check_password_hash(row[1], password):
        session["owner_id"] = row[0]
        return jsonify({"status": "logged_in"})

    return jsonify({"error": "Invalid credentials"}), 401


# Logout
@app.route("/logout")
def logout():
    session.clear()
    return jsonify({"status": "logged_out"})


# Check login
@app.route("/check_login")
def check_login():
     return jsonify({
        "is_owner": session.get("is_owner", False),
        "is_guest": session.get("is_guest", False)
    })


# Continue as guest
@app.route("/guest")
def guest():
    session.clear()
    session["is_guest"] = True
    session["is_owner"] = False
    return jsonify({"success": True})


@app.route("/dashboard")
def dashboard():
    if not session.get("is_owner") and "owner_id" not in session:
        return redirect("/")
    return app.send_static_file("owner_dashboard.html")



restaurant_info = {
    "name": "",
    "address": "",
    "hours": "",
    "image_url": "",
    "description": ""
}

@app.route("/api/restaurant")
def get_restaurant():
    return jsonify(restaurant_info)

@app.route("/api/restaurant/save", methods=["POST"])
def save_restaurant():
    if not session.get("is_owner") and "owner_id" not in session:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    restaurant_info.update(data)
    return jsonify({"status": "saved"})


dummy_restaurants = [
    {
        "id": 1,
        "name": "Sunset Grill",
        "promo_uses": 42,
        "traffic_increase": 18  # %
    },
    {
        "id": 2,
        "name": "Ocean Breeze Cafe",
        "promo_uses": 17,
        "traffic_increase": 9
    },
    {
        "id": 3,
        "name": "Mountain View Diner",
        "promo_uses": 8,
        "traffic_increase": 4
    }
]


@app.route("/api/owner/restaurants")
def owner_restaurants():
    if not session.get("is_owner") and "owner_id" not in session:
        return jsonify({"error": "Unauthorized"}), 403

    return jsonify({"restaurants": dummy_restaurants})



if __name__ == "__main__":
    app.run(debug=True)
