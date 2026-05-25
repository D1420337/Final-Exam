from datetime import datetime
from app.models import db

class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    publisher = db.Column(db.String(255), nullable=True)
    isbn = db.Column(db.String(13), nullable=True)
    price = db.Column(db.Integer, default=0)
    is_exchange = db.Column(db.Boolean, default=False)
    exchange_item = db.Column(db.String(255), nullable=True)
    condition = db.Column(db.String(50), nullable=False)  # '全新', '接近全新', '輕微劃記', '劃記繁多', '書頁破損'
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='Available')  # 'Available', 'Reserved', 'Sold'
    dept = db.Column(db.String(100), nullable=True)
    subject = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    reservations = db.relationship('Reservation', backref='book', lazy=True, cascade="all, delete-orphan")
    comments = db.relationship('Comment', backref='book', lazy=True, cascade="all, delete-orphan")

    @classmethod
    def create(cls, seller_id, title, author, publisher=None, isbn=None, price=0, is_exchange=False, exchange_item=None, condition='輕微劃記', description=None, image_url=None, status='Available', dept=None, subject=None):
        book = cls(seller_id=seller_id, title=title, author=author, publisher=publisher, isbn=isbn, price=price, is_exchange=is_exchange, exchange_item=exchange_item, condition=condition, description=description, image_url=image_url, status=status, dept=dept, subject=subject)
        db.session.add(book)
        db.session.commit()
        return book

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_by_id(cls, book_id):
        return cls.query.get(book_id)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()
