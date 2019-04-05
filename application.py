 # goodreads api
# key: j4VETR9rJWrRhNbNuyVhIw
# secret: ooqqthDif8dOMCe7b4BwqC5p6EaZrdfBXIgNJFFlBBw

# database url: postgres://wnzqoxljmdgcau:094e3158d7fb3153adf572a8278c32d7053bbf483c4f28ed531bf457a17e8a18@ec2-54-221-243-211.compute-1.amazonaws.com:5432/dbs13fsh1no3u9


import os
import requests

from flask import Flask, session, render_template, request, redirect, jsonify, abort
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from functools import wraps
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
@login_required
def index():
    return render_template("search.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Registration: Users should be able to register for your website,
    providing (at minimum) a username and password."""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("/error.html", message="Please provide a username")

        if not request.form.get("password"):
            return render_template("/error.html", message="Please provide a password")

        if not request.form.get("confirmation"):
            return render_template("/error.html", message="Please confirm password")


        if request.form.get("password") != request.form.get('confirmation'):
            return render_template("/error.html", message="Passwords do not match")

        username = request.form.get("username")
        hash_pass = request.form.get("password")

        user_exists = db.execute("SELECT * FROM users WHERE username = :username",
                   {"username": username}).fetchall()


        # if username is free
        if not user_exists:
            hash_pass = generate_password_hash(request.form.get("password"))

            set_session = db.execute("SELECT * FROM users WHERE username = :username",
                   {"username": username}).fetchone()

            session["user_id"] = set_session

        # if a row with the user already exists apologize to user
        else:
            return render_template("/error.html", message="username taken")

        return render_template("search.html")


    # user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/check", methods=["GET"])
def check():

    username = request.args.get("username")

    names = db.execute("SELECT username FROM users WHERE username =:username", {"username": username}).fetchone()

    if names and username:
        return jsonify(False)
    elif not names and username:
        return jsonify(True)
    else:
        return jsonify(False)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Login: Users, once registered, should be able to log in to your
    website with their username and password."""

    # forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was  submitted
        if not request.form.get('username'):
            return render_template("/error.html", message="Enter Username.")

        # Ensure password was submitted
        elif not request.form.get('password'):
            return render_template("/error.html", message="Enter Password")

        # Querry database for username
        row = db.execute("SELECT * FROM users WHERE username = :username",
                          {"username": request.form.get("username")}).fetchone()

        # Ensure username exists and password is correct
        if not row or not check_password_hash(row["password"], request.form.get("password")):
            return render_template("/error.html", message="Invalid username and/or password")

        # Remeber which user has logged in
        session["user_id"] = row["id"]

        return redirect("/search")



    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    """Search: Once a user has logged in, they should be taken to a page where
    they can search for a book. Users should be able to type in the ISBN number
    of a book, the title of a book, or the author of a book. After performing
    the search, your website should display a list of possible matching
    results, or some sort of message if there were no matches. If the user
    typed in only part of a title, ISBN, or author name, your search page
    should find matches for those as well!"""

    if request.method == "POST":

        if not request.form.get("book"):
            return render_template("/error.html",
                                   message="Enter a search query")

        else:
            query = "%" + request.form.get('book') + "%"
        # author = request.form.get('title')
        # year = request.form.get('year')
        # isbn = request.form.get('isbn')




        books = db.execute("SELECT * FROM books WHERE title like :query or author like :query or year like :query or isbn like :query",
                          {"query": query}).fetchall()

        #if books.rowcount == 0:
        if not books:
                return render_template('error.html', message='there are no books with that title')

        # books = rows.fetchall()

        return render_template("result.html", books=books)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("search.html")

@app.route("/book/<string:isbn>", methods=["GET", "POST"])
@login_required
def book(isbn):

    if request.method == "POST":

        if not request.form.get("score"):
            return render_template("/error.html",
                                   message="Enter a score")

        if not request.form.get("review"):
            return render_template('/error.html', message="Enter a review")

        if request.form.get('review'):
            review = request.form.get('review')

        score = int(request.form.get("score"))

        book = db.execute("SELECT id FROM books WHERE isbn = :isbn", {
                            "isbn": isbn}).fetchone()

        book_id = book.id

        has_review = db.execute("SELECT * FROM reviews WHERE user_id = :user_id AND book_id = :book_id", {
                                "user_id": session["user_id"],
                                "book_id": book_id,
                                }).fetchall()

        if has_review:
            return render_template("error.html", message="you have already given a review for this book")

        db.execute("INSERT INTO reviews (book_id, user_id, score, review) VALUES (:book_id, :user_id, :score, :review)", {
                   "book_id": book_id,
                   "user_id": session["user_id"],
                   "score": score,
                   "review": review
                   })
        db.commit()

        return render_template("/error.html",
                                   message="you did something")



    if request.method == "GET":
        book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {
                          "isbn": isbn
                          }).fetchone()

        if not book:
            return render_template("error.html", message="No such book")

        has_review = db.execute("SELECT * FROM reviews WHERE user_id = :user_id AND book_id = :book_id", {
                                "user_id": session["user_id"],
                                "book_id": book.id,
                                }).fetchone()

        if has_review:
            score = has_review.score
            review = has_review.review
        else:
            score = ''
            review = ''


        # access goodreads api
        goodreads = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "j4VETR9rJWrRhNbNuyVhIw", "isbns": isbn}).json()['books'][0]

        #goodreads = goodreads['books'][0]

        return render_template("book.html", book=book, score=score, review=review, goodreads=goodreads)

# @app.route("/flights/<int:flight_id>")
# def flight(flight_id):
# @app.route("/search/<int:####") # add something to this akin to flights
# def book_page():
    """Book Page: When users click on a book from the results of the search
    page, they should be taken to a book page, with details about the book: its
    title, author, publication year, ISBN number, and any reviews that users
    have left for the book on your website.


    Review Submission: On the book page, users should be able to submit a
    review: consisting of a rating on a scale of 1 to 5, as well as a text
    component to the review where the user can write their opinion about a
    book. Users should not be able to submit multiple reviews for the same book."""

    # CREATE TABLE reviews (id serial primary key, book_id integer references books, user_id references users, review varchar not null)


@app.route("/api/<isbn>", methods=["GET", "POST"])
@login_required
def api(isbn):

    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {
                          "isbn": isbn
                          }).fetchone()

    if not book:
        abort(404)

    goodreads = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "j4VETR9rJWrRhNbNuyVhIw", "isbns": isbn}).json()['books'][0]

    data = {}
    data['title'] = book.title
    data['author'] = book.author
    data['year'] = book.year
    data['isbn'] = book.isbn
    data['reviews_count'] = goodreads['reviews_count']
    data['average_rating'] = goodreads['average_rating']

    return render_template("api.html", data=data)



