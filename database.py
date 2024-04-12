import os
import sqlite3
import string

from datetime import datetime


class Database:
    def __init__(self, db_name: str = "bookrate.db"):
        """
        Creates or opens database if exists using SQLite3
        """
        try:
            if db_name in os.listdir():
                self.db = sqlite3.connect(db_name)
                self.cr = self.db.cursor()
            else:
                self.db = sqlite3.connect(db_name)
                self.cr = self.db.cursor()

                # Create users table
                self.cr.execute("""CREATE TABLE Users (
                                        user_id INT PRIMARY KEY,
                                        username VARCHAR(50) NOT NULL
                                        );""")

                # Create books table
                self.cr.execute("""CREATE TABLE Books (
                                        book_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        book_title VARCHAR(255) NOT NULL,
                                        year INTEGER
                                        );""")

                # Create ratings table
                self.cr.execute("""CREATE TABLE Ratings (
                                        rating_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        user_id INT,
                                        book_id INT,
                                        rating DECIMAL(3, 2) NOT NULL,
                                        FOREIGN KEY (user_id) REFERENCES Users(user_id),
                                        FOREIGN KEY (book_id) REFERENCES Books(book_id)
                                    );""")
        except sqlite3.OperationalError:
            os.remove(db_name)

    def set_rate(self, user_id: int, book_title: str, rate: str) -> None:
        self.cr.execute("SELECT book_id FROM Books WHERE book_title = (?);", (book_title,))
        book_id = self.cr.fetchall()[0]
        self.cr.execute("SELECT rating_id FROM Ratings WHERE book_id=(?) AND user_id=(?);", (int(book_id[0]), user_id))
        rating_id = self.cr.fetchall()
        if rating_id:
            self.cr.execute("UPDATE Ratings SET rating=(?) WHERE rating_id=(?);", (int(rate), int(rating_id[0][0])))
            self.db.commit()
        else:
            self.cr.execute(f"INSERT INTO Ratings (book_id, user_id, rating) VALUES (?, ?, ?);",
                            (int(book_id[0]), user_id, int(rate)))
            self.db.commit()

    def get_rate(self, title: str) -> int:
        title = self.strip_punctuation(title)
        self.cr.execute(f"""SELECT AVG(rating) FROM Ratings
                            WHERE book_id=(SELECT book_id FROM Books WHERE book_title=(?));""", (title,))
        rate = self.cr.fetchall()[0]
        return rate[0]

    def get_all_books(self) -> list:
        self.cr.execute("SELECT book_title FROM Books")
        return [el[0] for el in self.cr.fetchall()]

    def get_books_on_year(self, year: str) -> list:
        self.cr.execute("SELECT book_title FROM Books WHERE year=?;", (year,))
        return [el[0] for el in self.cr.fetchall()]

    def add_book(self, title: str, year: int = datetime.now().year) -> None:
        title = self.strip_punctuation(title)
        self.cr.execute(f"INSERT INTO Books (book_title, year) VALUES (?, ?);", (title, year))
        self.db.commit()

    def add_books(self, books: list[tuple[str, int]]) -> None:
        for book in books:
            title = self.strip_punctuation(book[0])
            self.add_book(title, book[1])

    @staticmethod
    def strip_punctuation(text: str) -> str:
        return ''.join([char for char in text if char not in set(string.punctuation)])
