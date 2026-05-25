from datetime import datetime
from app.models import db

class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id', ondelete='CASCADE'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id', ondelete='CASCADE'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Self-referential relationship for threaded replies
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy=True, cascade="all, delete-orphan")
    author = db.relationship('User', backref='comments', lazy=True)

    @classmethod
    def create(cls, book_id, author_id, content, parent_id=None):
        comment = cls(book_id=book_id, author_id=author_id, content=content, parent_id=parent_id)
        db.session.add(comment)
        db.session.commit()
        return comment

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_by_id(cls, comment_id):
        return cls.query.get(comment_id)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()
