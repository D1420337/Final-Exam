import os
from time import time
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from app.models import db
from app.models.book import Book

books_bp = Blueprint('books', __name__, url_prefix='/books')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@books_bp.route('/search', methods=['GET'])
def search():
    dept = request.args.get('dept', '').strip()
    subject = request.args.get('subject', '').strip()
    isbn = request.args.get('isbn', '').strip()
    query = request.args.get('query', '').strip()
    
    # Base query - only show Available books
    book_query = Book.query.filter_by(status='Available')
    
    # 1. 精確篩選：系所 (dept)
    if dept:
        book_query = book_query.filter_by(dept=dept)
        
    # 2. 精確篩選：ISBN
    if isbn:
        book_query = book_query.filter_by(isbn=isbn)
        
    # 3. 模糊篩選：科目名稱 (subject)
    if subject:
        book_query = book_query.filter(Book.subject.ilike(f"%{subject}%"))
        
    # 4. 模糊篩選：通用書名/作者/關鍵字 (query)
    if query:
        book_query = book_query.filter(
            db.or_(
                Book.title.ilike(f"%{query}%"),
                Book.author.ilike(f"%{query}%"),
                Book.publisher.ilike(f"%{query}%")
            )
        )
        
    # 依上架時間倒序排序，確保最新商品在最前面
    books = book_query.order_by(Book.created_at.desc()).all()
    
    return render_template('books/search.html', 
                           books=books, 
                           dept=dept, 
                           subject=subject, 
                           isbn=isbn, 
                           query=query)

@books_bp.route('/upload', methods=['GET'])
def upload_page():
    """
    GET /books/upload
    Render the book upload form. Restricted to logged-in users.
    """
    if not session.get('user_id'):
        flash('請先登入系統才能上架書籍。', 'warning')
        return redirect(url_for('auth.login_page'))
    return render_template('books/upload.html')

@books_bp.route('/upload', methods=['POST'])
def upload_action():
    """
    POST /books/upload
    Process the book upload form submission.
    """
    if not session.get('user_id'):
        flash('請先登入系統才能上架書籍。', 'warning')
        return redirect(url_for('auth.login_page'))
    
    # 1. 取得表單資料
    title = request.form.get('title', '').strip()
    author = request.form.get('author', '').strip()
    publisher = request.form.get('publisher', '').strip()
    publish_year = request.form.get('publish_year', '').strip()
    edition = request.form.get('edition', '').strip()
    isbn = request.form.get('isbn', '').strip()
    price_str = request.form.get('price', '0').strip()
    is_exchange_str = request.form.get('is_exchange')  # 'true' or None
    exchange_item = request.form.get('exchange_item', '').strip()
    condition = request.form.get('condition', '').strip()
    description = request.form.get('description', '').strip()
    dept = request.form.get('dept', '').strip()
    subject = request.form.get('subject', '').strip()

    # 2. 欄位驗證 - 強制要求填寫出版年份與版本防版次混亂
    if not title or not author or not publish_year or not edition or not condition:
        flash('請填寫所有必要欄位（書名、作者、出版年份、版本、書況）。', 'danger')
        return render_template('books/upload.html', form_data=request.form)

    # 3. 處理價格/交換類型
    price = 0
    is_exchange = False
    if is_exchange_str == 'true':
        is_exchange = True
        price = 0
        if not exchange_item:
            flash('選擇僅限交換模式時，請填寫期望交換的書單或類型。', 'danger')
            return render_template('books/upload.html', form_data=request.form)
    else:
        try:
            price = int(price_str)
            if price < 0:
                raise ValueError()
        except ValueError:
            flash('請輸入有效的出售價格。', 'danger')
            return render_template('books/upload.html', form_data=request.form)

    # 4. 處理圖片上傳與限制 (限制在 2MB 以內)
    image_url = None
    file = request.files.get('book_image')
    
    if file and file.filename != '':
        # 檢查檔案大小限制
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > 2 * 1024 * 1024:
            flash('上傳的圖片檔案過大，限制在 2MB 以內。', 'danger')
            return render_template('books/upload.html', form_data=request.form)
            
        if not allowed_file(file.filename):
            flash('不支援的圖片格式，請上傳 PNG, JPG, JPEG, GIF 或 WEBP。', 'danger')
            return render_template('books/upload.html', form_data=request.form)

        # 安全儲存
        upload_folder = os.path.join('app', 'static', 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
            
        filename = secure_filename(file.filename)
        unique_filename = f"{int(time())}_{filename}"
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        image_url = f"/static/uploads/{unique_filename}"
    else:
        flash('上架書籍必須上傳至少一張封面照。', 'danger')
        return render_template('books/upload.html', form_data=request.form)

    # 5. 寫入資料庫
    try:
        seller_id = session.get('user_id')
        Book.create(
            seller_id=seller_id,
            title=title,
            author=author,
            publish_year=publish_year,
            edition=edition,
            publisher=publisher,
            isbn=isbn,
            price=price,
            is_exchange=is_exchange,
            exchange_item=exchange_item,
            condition=condition,
            description=description,
            image_url=image_url,
            status='Available',
            dept=dept,
            subject=subject
        )
        flash('二手書成功上架！', 'success')
        return redirect(url_for('cabinet.index'))
    except Exception as e:
        flash(f'上架失敗，資料庫發生錯誤：{str(e)}', 'danger')
        return render_template('books/upload.html', form_data=request.form)

@books_bp.route('/<int:book_id>', methods=['GET'])
def detail(book_id):
    from app.models.reservation import Reservation
    from app.models.comment import Comment
    
    book = Book.get_by_id(book_id)
    if not book:
        return "找不到該書籍", 404
        
    # 取得留言列表
    comments = Comment.query.filter_by(book_id=book_id).order_by(Comment.created_at.asc()).all()
    
    # 檢查當前登入使用者是否已送出過預約請求
    user_id = session.get('user_id')
    user_req = None
    if user_id:
        user_req = Reservation.query.filter_by(book_id=book_id, buyer_id=user_id).first()
        
    return render_template('books/detail.html', 
                           book=book, 
                           comments=comments, 
                           user_req=user_req)

@books_bp.route('/<int:book_id>/comment', methods=['POST'])
def add_comment(book_id):
    if not session.get('user_id'):
        flash('請先登入系統才能發表留言。', 'warning')
        return redirect(url_for('auth.login_page'))
        
    author_id = session.get('user_id')
    content = request.form.get('content', '').strip()
    parent_id_str = request.form.get('parent_id', '').strip()
    
    if not content:
        flash('留言內容不能為空。', 'danger')
        return redirect(url_for('books.detail', book_id=book_id))
        
    parent_id = None
    if parent_id_str:
        try:
            parent_id = int(parent_id_str)
        except ValueError:
            pass
            
    try:
        from app.models.comment import Comment
        Comment.create(book_id=book_id, author_id=author_id, content=content, parent_id=parent_id)
        flash('留言成功發表！', 'success')
    except Exception as e:
        flash(f'發表留言失敗，錯誤：{str(e)}', 'danger')
        
    return redirect(url_for('books.detail', book_id=book_id))
