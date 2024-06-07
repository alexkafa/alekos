# BEGIN CODE HERE
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from pymongo import TEXT
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import os
# END CODE HERE


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://127.0.0.1:27017/pspi"
CORS(app)
mongo = PyMongo(app)
mongo.db.products.create_index([("name", TEXT)])


@app.route("/search", methods=["GET"])
def search():
    # BEGIN CODE HERE
    name = request.args.get('name')
    if not name:
        return jsonify([])

    products = list(mongo.db.products.find({"$text": {"$search": name}}))
    products.sort(key=lambda x: x['price'], reverse=True)

    results = [{"id": str(prod["_id"]), "name": prod["name"], "production_year": prod["production_year"],
                "price": prod["price"], "color": prod["color"], "size": prod["size"]} for prod in products]

    return jsonify(results)
    # END CODE HERE


@app.route("/add-product", methods=["POST"])
def add_product():
    # BEGIN CODE HERE
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400

    product = mongo.db.products.find_one({"name": data["name"]})
    if product:
        mongo.db.products.update_one(
            {"name": data["name"]},
            {"$set": {"production_year": data["production_year"],
                      "price": data["price"],
                      "color": data["color"],
                      "size": data["size"]}}
        )
    else:
        mongo.db.products.insert_one(data)

    return jsonify({"status": "success"}), 201
    # END CODE HERE


def cosine_similarity(v1, v2):
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    return dot_product / (norm_v1 * norm_v2)


@app.route("/content-based-filtering", methods=["POST"])
def content_based_filtering():
    # BEGIN CODE HERE
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400

    try:
        target_vector = np.array([data["price"], data["color"], data["size"]])
    except KeyError:
        return jsonify({"error": "Invalid input data format"}), 400

    products = list(mongo.db.products.find())

    similar_products = []
    for prod in products:
        try:
            prod_vector = np.array([prod["price"], prod["color"], prod["size"]])
            similarity = cosine_similarity(target_vector, prod_vector)
            if similarity > 0.7:
                similar_products.append(prod["name"])
        except KeyError:
            continue

    return jsonify(similar_products)
    # END CODE HERE


@app.route("/crawler", methods=["GET"])
def crawler():
    # BEGIN CODE HERE
    semester = request.args.get('semester')
    if not semester:
        return jsonify({"error": "Invalid input"}), 400

    url = f"https://qa.auth.gr/el/x/studyguide/600000438/current"
    options = Options()
    options.headless = True
    chrome_driver_path = os.getenv('CHROMEDRIVER_PATH', 'path_to_chromedriver')
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)

    courses = []
    try:
        elements = driver.find_elements(By.CSS_SELECTOR, f'div[data-semester="{semester}"] .course-title')
        for elem in elements:
            courses.append(elem.text)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        driver.quit()

    return jsonify(courses)
    # END CODE HERE


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
