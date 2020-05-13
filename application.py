import os, json
from forms import *
from models import *

from flask import Flask, session, render_template, redirect, url_for, request, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_bootstrap import Bootstrap

import requests

from helpers import login_required

app = Flask(__name__)

app.config['SECRET_KEY'] = 'thisissecret'

bootstrap = Bootstrap(app)

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
    session.clear()
    form = UserForm()
    alert = None

    if request.method == "POST":    #if form.validate_on_submit():
        #check if the user exists and if the credentials are correct, login the user    
        if db.execute("SELECT username FROM users WHERE username = :username AND password = :password", {"username": form.username.data, "password": form.password.data}).rowcount == 1:
            user_id = db.execute("SELECT id FROM users WHERE username = :username AND password = :password", {"username": form.username.data, "password": form.password.data}).fetchone()[0]
            session["user_id"] = user_id
            session["username"] = form.username.data
            return redirect(url_for('search'))
            
        else:
            alert = 'Invalid username or password'
            return render_template('login.html', form=form, alert=alert)
                
    else:
        return render_template('login.html', form=form, alert=alert)               

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    session.clear()
    form = UserForm()
    alert = None

    if request.method == "POST":    #if form.validate_on_submit():
        
        new_user = User(username=form.username.data, password=form.password.data)
        #check if the username is available
        if db.execute("SELECT username FROM users WHERE username = :new_user", {"new_user": new_user.username}).rowcount == 1:
            alert = 'Username not available'
            return render_template('signup.html', form=form, alert=alert)

        else:
            db.execute("INSERT INTO users (username, password) VALUES (:new_username, :new_password)", {"new_username": new_user.username, "new_password": new_user.password})
            db.commit()
            return redirect(url_for('login'))

    else:
        return render_template('signup.html', form=form, alert=alert)

@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/search/', methods=['GET', 'POST'])
@login_required
def search():
    form = SearchForm()

    if request.method == "POST":      #criar uma lista que guarde todos os valores do db.execute, criar uma pagina html para renderizar esses resultados
        resultsList = list(db.execute("SELECT * FROM books WHERE isbn ILIKE :search OR title ILIKE :search OR author ILIKE :search", {"search": "%" + form.searchinput.data + "%"}).fetchall())
        return render_template('results.html', resultsList=resultsList, term=form.searchinput.data)
                
    else:
        return render_template('search.html', form=form)

@app.route('/books/<int:book_id>', methods=['GET', 'POST'])
@login_required
def book(book_id):
    form = ReviewForm()
    review_tracker = False

    #get info about the book and create a Book object.
    info = db.execute("SELECT * FROM books WHERE id = :book_id", {"book_id": book_id}).fetchall()
    for item in info:
        isbn = item[1]
        title = item[2]
        author = item[3]
        year = item[4]
    book = Book(isbn=isbn, title=title, author=author, year=year)

    """GoodReadsAPI"""
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "rfNzRu53CcBeFfWGQIBg", "isbns": book.isbn})
    
    #JSON 
    resJson = res.json()
    resJson = resJson['books'][0]
    
    #save the info 
    GRinfo = []
    GRinfo.append(resJson)

    #save the user info
    user = session["username"]

    """User reviews"""
    #save all the reviews in a list
    reviewsList = list(db.execute("SELECT * FROM reviews WHERE book_id = :book_id", {"book_id": book_id}).fetchall())

    if request.method == "POST":
        db.execute("INSERT INTO reviews (text, rating, book_id, username) VALUES (:text, :rating, :book_id, :username)", {"text": form.review.data, "rating": form.rating.data, "book_id": book_id, "username": user})
        db.commit()
        return redirect(url_for('book', book_id = book_id))
        
    #if method = "GET"    
    else: 
        #make sure the book exists
        if db.execute("SELECT id FROM books WHERE id = :book_id", {"book_id": book_id}).rowcount == 0:
            return 'ERROR: Book not found'
        
        else:
            #check if the user already made a review
            if db.execute("SELECT review_id FROM reviews WHERE username = :username AND book_id = :book_id", {"username": user, "book_id": book_id}).rowcount == 1:
                review_tracker = True
                return render_template('booktemplate.html', book=book, form=form, review_tracker=review_tracker, book_id=book_id, reviewsList=reviewsList, GRinfo=GRinfo)
            
            else:
                review_tracker = False
                return render_template('booktemplate.html', book=book, form=form, review_tracker=review_tracker, book_id=book_id, reviewsList=reviewsList, GRinfo=GRinfo)

@app.route('/api/<isbn>', methods=['GET'])
def api(isbn):

    #make sure the book exists
    if db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).rowcount == 0:
        return 'ERROR: Book not found'
    
    else:
        
        #get info about the book and create a Book object.
        info = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchall()
        for item in info:
            book_id = item[0]
            title = item[2]
            author = item[3]
            year = item[4]
        book = Book(isbn=isbn, title=title, author=author, year=year)

        #get the review count 
        review_count = db.execute("SELECT review_id FROM reviews WHERE book_id = :book_id", {"book_id": book_id}).rowcount

        """get the avg score"""
        #save all ratings on a list
        reviewsList = list(db.execute("SELECT rating FROM reviews WHERE book_id = :book_id", {"book_id": book_id}).fetchall())

        #find the average of the list
        if reviewsList:
            total = 0.0
            count = 0
            for item in reviewsList:
                total += item[0]
                count += 1
            score_avg = total / count

        else:
            score_avg = 0

        #return jsonify
        return jsonify({
            "title": book.title,
            "author": book.author,
            "year": book.year,
            "isbn": book.isbn,
            "review_count": review_count,
            "average_score": score_avg
        })