import pytest

from database import Database
from populate_database import books


@pytest.fixture(scope='session')
def db():
    mock_db = Database("mock_db")
    mock_db.add_books(books)
    return mock_db
