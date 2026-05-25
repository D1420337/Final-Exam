import os
from flask import Flask, render_template
from app.models import db
from app.routes import auth_bp, books_bp, cabinet_bp, requests_bp

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-secret-key-12345'
    
    # Configure SQLite database path under instance/
    database_path = os.path.join(app.instance_path, 'database.db')
    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)
        
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize db
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(cabinet_bp)
    app.register_blueprint(requests_bp)

    @app.route('/')
    def index():
        from app.models.book import Book
        # Fetch latest available books for landing page
        try:
            recent_books = Book.query.filter_by(status='Available').order_by(Book.created_at.desc()).limit(8).all()
        except Exception:
            recent_books = []
        return render_template('index.html', recent_books=recent_books)

    # Automatically create database tables if they do not exist
    with app.app_context():
        db.create_all()

    return app
