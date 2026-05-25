from datetime import datetime
from app.models import db

class Reservation(db.Model):
    __tablename__ = 'reservations'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id', ondelete='CASCADE'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    message = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Pending')  # 'Pending', 'Accepted', 'Rejected'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def create(cls, book_id, buyer_id, message=None, status='Pending'):
        reservation = cls(book_id=book_id, buyer_id=buyer_id, message=message, status=status)
        db.session.add(reservation)
        db.session.commit()
        return reservation

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_by_id(cls, reservation_id):
        return cls.query.get(reservation_id)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()
