import mysql.connector
from mysql.connector import Error
from datetime import datetime

def create_connection():
    """Create and return a MySQL database connection."""
    try:
        connection = mysql.connector.connect(
            host='localhost',  # Replace with your host if needed
            user='',  # Leave blank if no credentials are used
            password='',  # Leave blank if no credentials are used
            database='library_management'
        )
        if connection.is_connected():
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

    def add_book(self):
        """Add a new book to the database."""
        query = "INSERT INTO books (title, author_id, genre_id, isbn, publication_date, availability) VALUES (%s, %s, %s, %s, %s, %s)"
        execute_query(query, (self.title, self.author_id, self.genre_id, self.isbn, self.publication_date, 1))

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

def main_menu():
    """Display the main menu and handle user choices."""
    while True:
        print("\nWelcome to the Library Management System with Database Integration!")
        print("Main Menu:")
        print("1. Book Operations")
        print("2. User Operations")
        print("3. Author Operations")
        print("4. Genre Operations")
        print("5. Quit")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            book_operations_menu()
        elif choice == '2':
            user_operations_menu()
        elif choice == '3':
            author_operations_menu()
        elif choice == '4':
            genre_operations_menu()
        elif choice == '5':
            print("Thank you for using the Library Management System. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 5.")

def book_operations_menu():
    """Display the book operations menu and handle user choices."""
    while True:
        print("\nBook Operations:")
        print("1. Add a new book")
        print("2. Borrow a book")
        print("3. Return a book")
        print("4. Search for a book")
        print("5. Display all books")
        print("6. Back to Main Menu")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            title = input("Enter book title: ")
            author_name = input("Enter book author: ")
            genre_name = input("Enter book genre: ")
            isbn = input("Enter book ISBN: ")
            publication_date = input("Enter book publication date (YYYY-MM-DD): ")

            author = fetch_one_query("SELECT id FROM authors WHERE name = %s", (author_name,))
            genre = fetch_one_query("SELECT id FROM genres WHERE name = %s", (genre_name,))
            
            if author and genre:
                book = Book(title, author[0], genre[0], isbn, publication_date)
                book.add_book()
                print("Book added successfully!")
            else:
                print("Author or Genre not found.")
        
        elif choice == '2':
            user_library_id = input("Enter user library ID: ")
            book_isbn = input("Enter book ISBN to borrow: ")
            user = User("", user_library_id)
            user_id = user.authenticate_user()
            
            if user_id and borrow_book(user_id, book_isbn):
                print("Book borrowed successfully!")
            else:
                print("Borrowing failed. Please check the user ID or book ISBN.")
        
        elif choice == '3':
            user_library_id = input("Enter user library ID: ")
            book_isbn = input("Enter book ISBN to return: ")
            user = User("", user_library_id)
            user_id = user.authenticate_user()
            
            if user_id:
                return_book(user_id, book_isbn)
                print("Book returned successfully!")
            else:
                print("Returning failed. Please check the user ID or book ISBN.")
        
        elif choice == '4':
            search_title = input("Enter book title to search: ")
            query = """
            SELECT b.title, a.name, b.isbn, b.publication_date, b.availability
            FROM books b
            JOIN authors a ON b.author_id = a.id
            WHERE b.title LIKE %s
            """
            results = fetch_query(query, (f"%{search_title}%",))
            if results:
                for result in results:
                    title, author, isbn, pub_date, avail = result
                    availability_status = "Available" if avail else "Borrowed"
                    print(f"Title: {title}, Author: {author}, ISBN: {isbn}, Published: {pub_date}, Status: {availability_status}")
            else:
                print("No books found with the given title.")
        
        elif choice == '5':
            query = """
            SELECT b.title, a.name, b.isbn, b.publication_date, b.availability
            FROM books b
            JOIN authors a ON b.author_id = a.id
            """
            results = fetch_query(query)
            if results:
                for result in results:
                    title, author, isbn, pub_date, avail = result
                    availability_status = "Available" if avail else "Borrowed"
                    print(f"Title: {title}, Author: {author}, ISBN: {isbn}, Published: {pub_date}, Status: {availability_status}")
        
        elif choice == '6':
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 6.")

def user_operations_menu():
    """Display the user operations menu and handle user choices."""
    while True:
        print("\nUser Operations:")
        print("1. Add a new user")
        print("2. View user details")
        print("3. Display all users")
        print("4. Back to Main Menu")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            name = input("Enter user name: ")
            library_id = input("Enter user library ID: ")
            user = User(name, library_id)
            user.add_user()
            print("User added successfully!")
        
        elif choice == '2':
            library_id = input("Enter user library ID to view details: ")
            user = User("", library_id)
            print(user.display_details())
        
        elif choice == '3':
            query = "SELECT name, library_id FROM users"
            results = fetch_query(query)
            if results:
                for result in results:
                    name, library_id = result
                    print(f"Name: {name}, Library ID: {library_id}")
        
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 4.")

def author_operations_menu():
    """Display the author operations menu and handle user choices."""
    while True:
        print("\nAuthor Operations:")
        print("1. Add a new author")
        print("2. View author details")
        print("3. Display all authors")
        print("4. Back to Main Menu")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            name = input("Enter author name: ")
            biography = input("Enter author biography: ")
            author = Author(name, biography)
            author.add_author()
            print("Author added successfully!")
        
        elif choice == '2':
            name = input("Enter author name to view details: ")
            author = Author(name, "")
            print(author.display_details())
        
        elif choice == '3':
            query = "SELECT name, biography FROM authors"
            results = fetch_query(query)
            if results:
                for result in results:
                    name, biography = result
                    print(f"Author: {name}, Biography: {biography}")
        
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 4.")

def genre_operations_menu():
    """Display the genre operations menu and handle user choices."""
    while True:
        print("\nGenre Operations:")
        print("1. Add a new genre")
        print("2. View genre details")
        print("3. Display all genres")
        print("4. Back to Main Menu")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            name = input("Enter genre name: ")
            description = input("Enter genre description: ")
            category = input("Enter genre category: ")
            genre = Genre(name, description, category)
            genre.add_genre()
            print("Genre added successfully!")
        
        elif choice == '2':
            name = input("Enter genre name to view details: ")
            genre = Genre(name, "", "")
            print(genre.display_details())
        
        elif choice == '3':
            query = "SELECT name, description, category FROM genres"
            results = fetch_query(query)
            if results:
                for result in results:
                    name, description, category = result
                    print(f"Genre: {name}, Description: {description}, Category: {category}")
        
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 4.")

if __name__ == "__main__":
    main_menu()
