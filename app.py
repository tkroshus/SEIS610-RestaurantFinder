# http://127.0.0.1:5000

# from flask import Flask, request, jsonify
# import random

# app = Flask(__name__)

# # -----------------------------
# # Mock Data (Replace with DB later)
# # -----------------------------
# restaurants = [
#     {"name": "Sushi Place", "rating": 4.5, "price": "$$", "distance": 2},
#     {"name": "Burger Town", "rating": 4.0, "price": "$", "distance": 1},
#     {"name": "Fancy Steakhouse", "rating": 5.0, "price": "$$$", "distance": 4},
#     {"name": "Taco Spot", "rating": 3.5, "price": "$", "distance": 3},
#     {"name": "Pasta Paradise", "rating": 4.2, "price": "$$", "distance": 2},
#     {"name": "Curry Corner", "rating": 4.7, "price": "$$", "distance": 5},
#     {"name": "Vegan Vibes", "rating": 4.3, "price": "$$", "distance": 1},
#     {"name": "Pizza Palace", "rating": 3.9, "price": "$", "distance": 3},
#     {"name": "Mediterranean Grill", "rating": 4.6, "price": "$$", "distance": 4},
#     {"name": "Noodle Haven", "rating": 4.1, "price": "$", "distance": 2}
# ]

# promotions = [
#     "20% off at Sushi Place today!",
#     "Happy Hour at Taco Spot — 3pm to 6pm!",
#     "Free dessert at Fancy Steakhouse tonight!",
#     "Buy one entrée, get one half off at Pasta Paradise!",
#     "Curry Corner’s Spice Night — free drink with any combo!",
#     "Vegan Vibes offers 15% off all bowls today only!"
# ]

# # -----------------------------
# # Routes
# # -----------------------------

# last_random = None

# @app.route("/")
# def home():
#     return app.send_static_file("index.html")

# @app.route("/api/restaurants")
# def get_restaurants():
#     """Return restaurants filtered by quality, budget, and distance."""
#     # quality = float(request.args.get("quality", 0))
#     quality_raw = request.args.get("quality", "")
#     quality = float(quality_raw) if quality_raw else 0
#     budget = request.args.get("budget", "")
#     # distance = float(request.args.get("distance", 9999))
#     distance_raw = request.args.get("distance", "")
#     distance = float(distance_raw) if distance_raw else 9999

#     filtered = [
#         r for r in restaurants
#         if r["rating"] >= quality
#         and (budget == "" or r["price"] == budget)
#         and r["distance"] <= distance
#     ]

#     return jsonify(filtered)


# @app.route("/api/explore")
# def explore():
#     """Return a random restaurant."""
#     # return jsonify(random.choice(restaurants))
#     global last_random

#     # Filter out the last restaurant
#     choices = [r for r in restaurants if r != last_random]

#     # If all restaurants have been shown, reset
#     if not choices:
#         choices = restaurants.copy()

#     pick = random.choice(choices)
#     last_random = pick

#     return jsonify(pick)

# @app.route("/api/promotions")
# def get_promotions():
#     """Return a random promotion."""
#     return jsonify({"promotion": random.choice(promotions)})


# # -----------------------------
# # Run the server
# # -----------------------------
# if __name__ == "__main__":
#     app.run(debug=True)



#-------------------------updated below w API-----------

from flask import Flask, request, jsonify
import requests
import random

app = Flask(__name__)

YELP_API_KEY = "44rLSZFxLCGwmbm4tZpH61WzzBVkfDBZ7GrJg61Rc_pFdPejlBGZtJxfSMdJgINsXM2gjrz4yN_p5Lb4ybpvwbReW-NtNKb_4bnZcyIy92waqL6e23z2FSJDJLDyaXYx"
YELP_ENDPOINT = "https://api.yelp.com/v3/businesses/search"

# Minneapolis center point
MINNEAPOLIS_LAT = 44.9778
MINNEAPOLIS_LON = -93.2650

# Track last random pick
last_random = None


def miles_to_meters(miles):
    return int(float(miles) * 1609.34)


@app.route("/")
def home():
    return app.send_static_file("index.html")


@app.route("/api/restaurants")
def get_restaurants():
    quality_raw = request.args.get("quality", "")
    budget_raw = request.args.get("budget", "")
    distance_raw = request.args.get("distance", "")

    # Convert filters
    min_rating = float(quality_raw) if quality_raw else 0
    max_distance_miles = float(distance_raw) if distance_raw else 20
    max_distance_miles = min(max_distance_miles, 20)  # enforce 30-mile limit
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


@app.route("/api/promotions")
def get_promotions():
    promotions = [
        "20% off at select Minneapolis restaurants today!",
        "Happy Hour deals across Uptown and North Loop!",
        "Free dessert at participating restaurants tonight!"
    ]
    return jsonify({"promotion": random.choice(promotions)})


if __name__ == "__main__":
    app.run(debug=True)
