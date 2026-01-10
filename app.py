"""
Shiny tracker with Pokeapi integration, animated sprites,
pokemon search functionality and interactive GUI.
Made by Joshua Luke.
"""

from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from user import db, User
import poketrack

app = Flask(__name__)
stored_pokemon = poketrack.retrieve_pokemon_data()

app.secret_key = "naruto_beats_sasuke_as_adults"

# Configuring an SQL Alchemy DB.
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

"""
Index Route that loads the main page, takes pokemon search input and displays the pokemon to the screen.
@param: None
@return: flask.render_template() function.
"""


@app.route("/", methods=["GET", "POST"])
def index():

    pokemon = None  # This is what we pass to the template

    if request.method == "POST":

        # --- SEARCH BUTTON ---
        if "search_btn" in request.form:
            pokemon_search = request.form.get("pokemon_search", "").strip().lower()
            if pokemon_search:
                # Fetch Pokémon if not already stored
                if pokemon_search not in stored_pokemon:
                    fetched_pokemon = poketrack.fetch_pokemon_data(pokemon_search, 0)
                    stored_pokemon[pokemon_search] = fetched_pokemon
                # Retrieve from dictionary for rendering
                pokemon = stored_pokemon[pokemon_search]
                poketrack.save_data(stored_pokemon)

        # --- INCREMENT BUTTON ---
        elif "increment_btn" in request.form:
            pokemon_name = request.form.get("pokemon_name", "").strip().lower()
            if pokemon_name and pokemon_name in stored_pokemon:
                pokemon = stored_pokemon[pokemon_name]
                pokemon.increment()
                poketrack.save_data(stored_pokemon)
            else:
                pokemon = None

        # --- RESET BUTTON ---
        elif "reset_btn" in request.form:
            pokemon_name = request.form.get("pokemon_name", "").strip().lower()
            if pokemon_name and pokemon_name in stored_pokemon:
                pokemon = stored_pokemon[pokemon_name]
                pokemon.reset_count()
                poketrack.save_data(stored_pokemon)
            else:
                pokemon = None

    if session.get("username"):
        return render_template("index.html", pokemon=pokemon, username=session["username"])
    else:
        return render_template("index.html", pokemon=pokemon)


# Login Route
@app.route("/login", methods=["POST", "GET"])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session["username"] = username
            return redirect(url_for("index"))
        else:
            return render_template("login.html")

    else:
        return render_template("login.html")


@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]
    user = User.query.filter_by(username=username).first()
    if user:
        return render_template("login.html", error="User already exists.")
    else:
        new_user = User(username=username)  # type: ignore
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        session["username"] = username
        return redirect(url_for("index"))


@app.route("/dashboard")
def dashboard():
    if "username" in session:
        return render_template("dashboard.html", username=session["username"])
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
