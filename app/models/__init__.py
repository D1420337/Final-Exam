from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from app.models.user import User
from app.models.book import Book
from app.models.reservation import Reservation
from app.models.comment import Comment
