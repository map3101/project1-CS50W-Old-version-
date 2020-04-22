import os
from forms import *
from models import *

from flask import Flask, session, render_template
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_bootstrap import Bootstrap

app = Flask(__name__)

app.config['SECRET_KEY'] = 'thisissecret'

bootstrap = Bootstrap(app)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    return render_template("home.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = UserForm()

    if form.validate_on_submit():
        return '<h1>' + form.username.data + ' ' + form.password.data + '<h1>'

    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = UserForm()

    if form.validate_on_submit():
        new_user = User(username=form.username.data, password=form.password.data)
        
        if db.execute("SELECT username FROM users WHERE username = :new_user", {"new_user": new_user.username}).rowcount == 1:
            return "<h1>USERNAME NOT AVAILABLE</h1>"

        else:
            db.execute("INSERT INTO users (username, password) VALUES (:new_username, :new_password)", {"new_username": new_user.username, "new_password": new_user.password})
            db.commit()
            return 'USER CREATED'

    return render_template('signup.html', form=form)