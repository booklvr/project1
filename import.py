""" Import: Provided for you in this project is a file called books.csv, which is a spreadsheet in CSV format of 5000 different books. Each one has an ISBN number, a title, an author, and a publication year. In a Python file called import.py separate from your web application, write a program that will take the books and import them into your PostgreSQL database. You will first need to decide what table(s) to create, what columns those tables should have, and how they should relate to one another. Run this program by running python3 import.py to import the books into your database, and submit this program with the rest of your project code.

At minimum, you’ll probably want at least one table to keep track of users, one table to keep track of books, and one table to keep track of reviews. But you’re not limited to just these tables, if you think others would be helpful!"""

import os
import csv

from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# metadata = MetaData()
# users = Table('users', metadata,
#     Column('id', Integer, primary_key=True),
#     Column('username', String),
#     Column('password', String),
# )

# books = Table('books', metadata,
#               Column('id', Integer, primary_key=True),
#               Column('ISBN', String),
#               Column('Title', String),
#               Column('Author', String),
#               Column('Year', String))


# metadata.create_all(engine)
def main():

    with open('books.csv', 'r') as csvBooks:
        book_list = csv.reader(csvBooks)

        next(book_list)
        for isbn, title, author, year in book_list:
            db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)", {
                       "isbn": isbn,
                       "title": title,
                       "author": author,
                       "year": year
                       })
        print("finished")
        db.commit()


if __name__ == "__main__":
    main()

