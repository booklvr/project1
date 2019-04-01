# goodreads api
# key: j4VETR9rJWrRhNbNuyVhIw
# secret: ooqqthDif8dOMCe7b4BwqC5p6EaZrdfBXIgNJFFlBBw

import os
import requests

from flask import Flask, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['DATABASE_URL'] = "postgres://user:password@server_ip:5432/booklvr-project1"


Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return "Project 1: TODO"


@app.registration("/register")
def register():
    """Registration: Users should be able to register for your website, providing (at minimum) a username and password."""


@app.login("/login")
def login():
    """Login: Users, once registered, should be able to log in to your website with their username and password."""


@app.logout("/logout")
def logout():
    """Logout: Logged in users should be able to log out of the site."""


@app.search("/search")
def search():
    """Search: Once a user has logged in, they should be taken to a page where they can search for a book. Users should be able to type in the ISBN number of a book, the title of a book, or the author of a book. After performing the search, your website should display a list of possible matching results, or some sort of message if there were no matches. If the user typed in only part of a title, ISBN, or author name, your search page should find matches for those as well!"""


# @app.route("/flights/<int:flight_id>")
# def flight(flight_id):
@app.search("/search/<int:####") # add something to this akin to flights
def book_page():
    """Book Page: When users click on a book from the results of the search page, they should be taken to a book page, with details about the book: its title, author, publication year, ISBN number, and any reviews that users have left for the book on your website.""


    Review Submission: On the book page, users should be able to submit a review: consisting of a rating on a scale of 1 to 5, as well as a text component to the review where the user can write their opinion about a book. Users should not be able to submit multiple reviews for the same book.







