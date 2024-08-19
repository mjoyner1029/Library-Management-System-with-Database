import mysql.connector
from mysql.connector import Error
from datetime import datetime

def create_connection():
    """Create and return a MySQL database connection."""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='your_username',
            password='your_password',
            database='library_management'
        )
        if connection.is_connected():
            print("Connected to the database.")
            return connection
    except Error as e:
        print(f"Error: {e}")
    return None

def execute_query(query, params=(), fetchone=False, fetchall=False):
    """Execute a query with the given parameters and return results."""
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute(query, params)
            connection.commit()
            if fetchone:
                return cursor.fetchone()
            elif fetchall:
                return cursor.fetchall()
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            connection.close()

def fetch_query(query, params=()):
    """Execute a query and fetch all results."""
    return execute_query(query, params, fetchall=True)

def fetch_one_query(query, params=()):
    """Execute a query and fetch one result."""
    return execute_query(query, params, fetchone=True)

class Book:
    def __init__(self, title, author_id, genre_id, isbn, publication_date):
        self.title = title
        self.author_id = author_id
        self.genre_id = genre_id
        self.isbn = isbn
        self.publication_date = publication_date

    def borrow_book(self):
        """Attempt to borrow the book."""
        query = "UPDATE books SET availability = 0 WHERE isbn = %s AND availability = 1"
        result = execute_query(query, (self.isbn,), fetchone=True)
        return result is not None

    def return_book(self):
        """Return the borrowed book."""
        query = "UPDATE books SET availability = 1 WHERE isbn = %s"
        execute_query(query, (self.isbn,))

    def display_details(self):
        """Return a string of book details."""
        query = """
        SELECT b.title, a.name, b.isbn, b.publication_date, b.availability
        FROM books b
        JOIN authors a ON b.author_id = a.id
        WHERE b.isbn = %s
        """
        result = fetch_one_query(query, (self.isbn,))
        if result:
            title, author, isbn, pub_date, avail = result
            availability_status = "Available" if avail else "Borrowed"
            return f"Title: {title}, Author: {author}, ISBN: {isbn}, Published: {pub_date}, Status: {availability_status}"
        return "Book not found."

class User:
    def __init__(self, name, library_id):
        self.name = name
        self.library_id = library_id

    def add_user(self):
        """Add a new user to the database."""
        query = "INSERT INTO users (name, library_id) VALUES (%s, %s)"
        execute_query(query, (self.name, self.library_id))

    def authenticate_user(self):
        """Authenticate user credentials."""
        query = "SELECT id FROM users WHERE library_id = %s"
        result = fetch_one_query(query, (self.library_id,))
        return result[0] if result else None

    def display_details(self):
        """Return a string of user details."""
        query = "SELECT name FROM users WHERE library_id = %s"
        result = fetch_one_query(query, (self.library_id,))
        if result:
            return f"Name: {result[0]}, Library ID: {self.library_id}"
        return "User not found."

class Author:
    def __init__(self, name, biography):
        self.name = name
        self.biography = biography

    def add_author(self):
        """Add a new author to the database."""
        query = "INSERT INTO authors (name, biography) VALUES (%s, %s)"
        execute_query(query, (self.name, self.biography))

    def display_details(self):
        """Return a string of author details."""
        query = "SELECT name, biography FROM authors WHERE name = %s"
        result = fetch_one_query(query, (self.name,))
        if result:
            return f"Author: {result[0]}, Biography: {result[1]}"
        return "Author not found."

class Genre:
    def __init__(self, name, description, category):
        self.name = name
        self.description = description
        self.category = category

    def add_genre(self):
        """Add a new genre to the database."""
        query = "INSERT INTO genres (name, description, category) VALUES (%s, %s, %s)"
        execute_query(query, (self.name, self.description, self.category))

    def display_details(self):
        """Return a string of genre details."""
        query = "SELECT name, description, category FROM genres WHERE name = %s"
        result = fetch_one_query(query, (self.name,))
        if result:
            return f"Genre: {result[0]}, Description: {result[1]}, Category: {result[2]}"
        return "Genre not found."

def add_book(title, author_id, genre_id, isbn, publication_date):
    """Add a new book to the database."""
    new_book = Book(title, author_id, genre_id, isbn, publication_date)
    query = "INSERT INTO books (title, author_id, genre_id, isbn, publication_date, availability) VALUES (%s, %s, %s, %s, %s, %s)"
    execute_query(query, (title, author_id, genre_id, isbn, publication_date, 1))

def borrow_book(user_id, book_isbn):
    """Allow a user to borrow a book."""
    book = Book("", 0, 0, book_isbn, "")
    if book.borrow_book():
        book_id = fetch_one_query("SELECT id FROM books WHERE isbn = %s", (book_isbn,))[0]
        query = "INSERT INTO borrowed_books (user_id, book_id, borrow_date) VALUES (%s, %s, %s)"
        execute_query(query, (user_id, book_id, datetime.now().date()))
        return True
    return False

def return_book(user_id, book_isbn):
    """Allow a user to return a book."""
    book = Book("", 0, 0, book_isbn, "")
    book.return_book()
    query = "UPDATE borrowed_books SET return_date = %s WHERE book_id = (SELECT id FROM books WHERE isbn = %s) AND user_id = %s AND return_date IS NULL"
    execute_query(query, (datetime.now().date(), book_isbn, user_id))

def search_book(title):
    """Search for a book by title."""
    query = "SELECT * FROM books WHERE title LIKE %s"
    results = fetch_query(query, (f'%{title}%',))
    for result in results:
        print(f"ID: {result[0]}, Title: {result[1]}, Author ID: {result[2]}, Genre ID: {result[3]}, ISBN: {result[4]}, Publication Date: {result[5]}, Availability: {result[6]}")

def display_books():
    """Display all books."""
    query = "SELECT * FROM books"
    results = fetch_query(query)
    for result in results:
        print(f"ID: {result[0]}, Title: {result[1]}, Author ID: {result[2]}, Genre ID: {result[3]}, ISBN: {result[4]}, Publication Date: {result[5]}, Availability: {result[6]}")

def add_user(name, library_id):
    """Add a new user to the database."""
    new_user = User(name, library_id)
    new_user.add_user()

def authenticate_user(library_id):
    """Authenticate user credentials."""
    user = User("", library_id)
    return user.authenticate_user()

def add_author(name, biography):
    """Add a new author to the database."""
    new_author = Author(name, biography)
    new_author.add_author()

def add_genre(name, description, category):
    """Add a new genre to the database."""
    new_genre = Genre(name, description, category)
    new_genre.add_genre()

def display_users():
    """Display all users."""
    query = "SELECT * FROM users"
    results = fetch_query(query)
    for result in results:
        print(f"ID: {result[0]}, Name: {result[1]}, Library ID: {result[2]}")

def display_authors():
    """Display all authors."""
    query = "SELECT * FROM authors"
    results = fetch_query(query)
    for result in results:
        print(f"ID: {result[0]}, Name: {result[1]}, Biography: {result[2]}")

def display_genres():
    """Display all genres."""
    query = "SELECT * FROM genres"
    results = fetch_query(query)
    for result in results:
        print(f"ID: {result[0]}, Name: {result[1]}, Description: {result[2]}, Category: {result[3]}")
