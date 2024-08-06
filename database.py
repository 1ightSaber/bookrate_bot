from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

from helpers import strip_punctuation

Base = declarative_base()


class User(Base):
    __tablename__ = 'Users'
    user_id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)


class Book(Base):
    __tablename__ = 'Books'
    book_id = Column(Integer, primary_key=True, autoincrement=True)
    book_title = Column(String(255), nullable=False)
    year = Column(Integer)


class Rating(Base):
    __tablename__ = 'Ratings'
    rating_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('Users.user_id'))
    book_id = Column(Integer, ForeignKey('Books.book_id'))
    rating = Column(Float, nullable=False)
    user = relationship(User)
    book = relationship(Book)


class Database:
    def __init__(self, db_name: str = "bookrate.db"):
        self.engine = create_engine(f'sqlite:///{db_name}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def set_rate(self, user_id: int, book_title: str, rate: str) -> None:
        book = self.session.query(Book).filter_by(book_title=book_title).first()
        if not book:
            raise ValueError(f"Book with title '{book_title}' not found.")
        rating = self.session.query(Rating).filter_by(book_id=book.book_id, user_id=user_id).first()
        if rating:
            rating.rating = float(rate)
        else:
            new_rating = Rating(book_id=book.book_id, user_id=user_id, rating=float(rate))
            self.session.add(new_rating)
        self.session.commit()

    def get_rate(self, title: str) -> float:
        avg_rating = self.session.query(func.avg(Rating.rating)).join(Book).filter(Book.book_title == title).scalar()
        return avg_rating

    def get_all_books(self) -> list:
        books = self.session.query(Book.book_title).all()
        return [book[0] for book in books]

    def get_books_on_year(self, year: int) -> list:
        books = self.session.query(Book.book_title).filter_by(year=year).all()
        return [book[0] for book in books]

    def add_book(self, title: str, year: int = datetime.now().year) -> None:
        new_book = Book(book_title=title, year=year)
        self.session.add(new_book)
        self.session.commit()

    def add_books(self, books: list[tuple[str, int]]) -> None:
        for title, year in books:
            self.add_book(title, year)
