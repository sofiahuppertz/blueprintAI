from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify, url_for, make_response
from flask_session import Session
from helpers import generate_image, create_tables
import os
from openai import OpenAI
from queue import Queue
from threading import Thread
from werkzeug.security import check_password_hash, generate_password_hash

# Configure application
app = Flask(__name__)

image_queue = Queue()

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

create_tables()
# Database for users
db = SQL("sqlite:///blueprintai.db")

# Create 'users' table
db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, hash TEXT)")

# Create 'images' table
db.execute("CREATE TABLE IF NOT EXISTS images (id INTEGER PRIMARY KEY AUTOINCREMENT, prompt TEXT NOT NULL, image_data BLOB NOT NULL, user_id INTEGER NOT NULL)")

# OpenAI API Client
openai_api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# I took this from the CS50 Finance project
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Define the route for the index page
@app.route("/", methods=["GET", "POST"])
def index():
    # If the user is not logged in, redirect them to the login page
    if session.get("user_id") is None:
        return redirect("/login")

    # If the request method is GET, render the index page
    if request.method == "GET":
        return render_template("index.html")
    else:
        # If the request method is POST, get the form values
        building_type = request.form.get("buildingType")
        num_stories = request.form.get("heightStories")
        color_finishes = request.form.get("colorFinishes")
        primary_materials = request.form.get("primaryMaterials")
        location_context = request.form.get("locationContext")
        architectural_style = request.form.get("architecturalStyle")
        quality_tier = request.form.get("qualityTier")
        additional_elements = request.form.get("additionalElements")

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
        if not architectural_style:
            return jsonify({"message": "You forgot to enter an Architectural Style"}), 400
        if not quality_tier:
            return jsonify({"message": "You forgot to enter a Quality Tier"}), 400

        # Define the template for the building description
        building_description_template = (
            "Generate an image of a {num_stories}-story {building_type} "
            "building with a {color_finishes} facade. The building should be located in a {location_context} "
            "setting. Highlight the building's {quality_tier} design in the {architectural_style} architectural style with"
            " {color_finishes} and built primarily with {primary_materials}. DO NOT WRITE TEXT ON THE IMAGE."
            "ADD these additional elements to the building: {additional_elements}."
        )

        # Fill in the placeholders in the template with the form values
        building_description = building_description_template.format(
            num_stories=num_stories,
            building_type=building_type,
            color_finishes=color_finishes,
            location_context=location_context,
            architectural_style=architectural_style,
            quality_tier=quality_tier,
            primary_materials=primary_materials,
            additional_elements=additional_elements,
        )

        # Start a new thread to generate the image
        thread = Thread(target=generate_image, args=(building_description, client, session['user_id'], db, image_queue))
        thread.start()

        # Render the index page
        return render_template("index.html")

# Route to check if the image is ready
@app.route("/check_image")
def check_image():
    if not image_queue.empty():
        session['image_path'] = image_queue.get() 
        response = make_response("", 302)
        response.headers['X-Redirect'] = '/building'
        return response
    else:
        return "", 204

# Route to display loading page, in which ajax with check_image() will check if the image is ready every 2 seconds.
@app.route("/loading")
def loading():
    return render_template("loading.html")


# Route to display the building page
@app.route("/building", methods=["GET", "POST"])
def building():

    # If the user is not logged in, redirect them to the login page
    if session.get("user_id") is None:
        return redirect("/login")
    # Button to take quiz
    if "takeQuiz" in request.form:
        return redirect("/")
    # Button to logout
    elif "logout" in request.form:
        session.clear()
        return redirect("/login")
    image_path = session.get('image_path')
    print(image_path)
    return render_template("building.html", image_path=image_path), 200
   

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
    

