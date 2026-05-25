from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)  # Limit to *.edu.tw in logic
    password_hash = db.Column(db.String(128), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    contact_info = db.Column(db.String(255), nullable=True)  # Line ID / Phone
    is_verified = db.Column(db.Boolean, default=False)
    verification_code = db.Column(db.String(6), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    books = db.relationship('Book', backref='seller', lazy=True, cascade="all, delete-orphan")
    reservations_sent = db.relationship('Reservation', backref='buyer', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def create(cls, email, password, username, contact_info=None, is_verified=False, verification_code=None):
        user = cls(email=email, username=username, contact_info=contact_info, is_verified=is_verified, verification_code=verification_code)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_by_id(cls, user_id):
        return cls.query.get(user_id)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if key == 'password':
                self.set_password(value)
            elif hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()
