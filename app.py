from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify, send_from_directory, make_response, url_for
from flask_session import Session
from helpers import *
from prompt_helpers import *
import os
from openai import OpenAI
from queue import Queue
from threading import Thread
from werkzeug.security import check_password_hash, generate_password_hash

# Configure application
app = Flask(__name__)

image_queue = Queue()

building_description = ""
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

create_tables()
# Database for users
db = SQL("sqlite:///blueprintai.db")

# OpenAI API Client
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# I took this from the CS50 Finance project
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
def index():
    if session.get("user_id") is None:
        return redirect("/login")
    return render_template("index.html"), 200


@app.route('/submit_form', methods=['POST'])
def submit_form():
    # Get the form values into session object
    building_type = request.form.get("buildingType")
    num_stories = request.form.get("heightStories")
    color_finishes = request.form.get("colorFinishes")
    primary_materials = request.form.get("primaryMaterials")
    location_context = request.form.get("locationContext")
    landscape_type = request.form.get("landscapeType")
    architectural_style = request.form.get("architecturalStyle")
    quality_tier = request.form.get("qualityTier")
    additional_elements = request.form.get("additionalElements")
    if (num_stories):
        qualitative_height = building_height_description(num_stories)
    # Validate the form values
    if not building_type:
        return jsonify({"message": "You forgot to enter a Building Type"}), 400
    if not num_stories:
        return jsonify({"message": "You forgot to enter a Number of Stories"}), 400
    if not color_finishes:
        return jsonify({"message": "You forgot to enter a Color Scheme"}), 400
    if not primary_materials:
        return jsonify({"message": "You forgot to enter Primary Materials"}), 400
    if not location_context:
        return jsonify({"message": "You forgot to enter a Location Context"}), 400
    if not landscape_type:
        return jsonify({"message": "You forgot to enter a Landscape Type"}), 400
    if not  architectural_style:
        return jsonify({"message": "You forgot to enter an Architectural Style"}), 400
    if not quality_tier:
        return jsonify({"message": "You forgot to enter a Quality Tier"}), 400
    if not qualitative_height:
        return jsonify({"message": "Error with building height description"}), 400
    prompt = make_image_prompt(building_type, num_stories, color_finishes, primary_materials, location_context, landscape_type, architectural_style, quality_tier, additional_elements, qualitative_height)
    thread = Thread(target=generate_image, args=(prompt, client, session, image_queue))
    thread.start()
    return jsonify({'new_text': 'Loading...'})


@app.route("/check_image")
def check_image():
    if not image_queue.empty():
        image_url = image_queue.get()
        if image_url is None:
            print("No image URL available")
            return jsonify({'status': 'no image'}), 204
        else:
            print("Image URL: ", image_url)
            return jsonify({'status': 'image ready', 'image_url': image_url}), 302
    else:
        return jsonify({'status': 'no image'}), 204
    

# Route to logout   
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect("/login")


# Route to login (Very similar to CS50 Finance)
@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":

        if not request.form.get("username"):
            return jsonify({"message": "Must Provide Username"}), 400
        if not request.form.get("password"):
            return jsonify({"message": "Must Provide Password"}), 400

        rows = db.execute(
            "SELECT * FROM users WHERE name =?", request.form.get("username")
        )

        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return jsonify({"message": "Invalid Username and/or Password"}), 400

        session["user_id"] = rows[0]["id"]
        return redirect("/")

    else:
        return render_template("login.html")


# Route to register (Very similar to CS50 Finance)
@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("password-confirmation")

        if not username:
            return jsonify({"message": "Must insert username"}), 400
        if not password:
            return jsonify({"message": "Must insert pasword"}), 400
        if not confirmation:
            return jsonify({"message": "Must insert password confirmation"}), 400
        if password != confirmation:
            return jsonify({"message" : "Passwords do not match"}), 400

        password = generate_password_hash(password)

        users = db.execute("SELECT * FROM USERS;")
        if any(row["name"] == username for row in users):
            return jsonify({"message": f"The username {username} already exists."}), 400

        id = db.execute(
            "INSERT INTO users (name, hash) VALUES (?, ?)", username, password
        )
        session["user_id"] = id
        flash("Registered!")
        return redirect("/")
    else:
        return render_template("register.html")
    

