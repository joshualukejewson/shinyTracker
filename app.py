"""
Shiny tracker with Pokeapi integration, animated sprites,
pokemon search functionality and interactive GUI.
Made by Joshua Luke.
"""

from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import poketrack

app = Flask(__name__)
stored_pokemon = poketrack.retrieve_pokemon_data()

app.secret_key = "naruto_beats_sasuke_as_adults"

# Configuring an SQL Alchemy DB.
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Database Model
class User(db.Model):
    # Class Variables
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)







"""
Index Route that loads the main page, takes pokemon search input and displays the pokemon to the screen.
@param: None
@return: flask.render_template() function.
"""
@app.route("/", methods=["GET", "POST"])
def index():

    if "username" in session:
        return redirect(url_for('dashboard'))

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


    return render_template("login.html", pokemon=pokemon)

# Login Route
@app.route("/login", methods=["POST"])
def login():
    
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        session['username'] = username
        return redirect(url_for('dashboard'))
    else:
        return render_template("login.html")
    
@app.route("/register", methods=["POST"])
def register():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if user:
        return render_template("login.html", error="User already exists.")
    else:
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        session['username'] = username
        return redirect(url_for('dashboard'))
    
@app.route("/dashboard")
def dashboard():
    if "username" in session:
        return render_template("dashboard.html", username=session['username'])
    return redirect(url_for('index'))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
