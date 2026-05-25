import os
from flask import Blueprint, session, redirect, url_for, flash, request, render_template
from app.models import db
from app.models.book import Book
from app.models.reservation import Reservation

cabinet_bp = Blueprint('cabinet', __name__, url_prefix='/cabinet')

@cabinet_bp.route('', methods=['GET'])
@cabinet_bp.route('/dashboard', methods=['GET'])
def index():
    if not session.get('user_id'):
        flash('請先登入系統才能管理個人書櫃。', 'warning')
        return redirect(url_for('auth.login_page'))
        
    user_id = session.get('user_id')
    
    # 撈出當前登入使用者所擁有的所有書籍，並按狀態分類
    available_books = Book.query.filter_by(seller_id=user_id, status='Available').order_by(Book.created_at.desc()).all()
    reserved_books = Book.query.filter_by(seller_id=user_id, status='Reserved').order_by(Book.created_at.desc()).all()
    sold_books = Book.query.filter_by(seller_id=user_id, status='Sold').order_by(Book.created_at.desc()).all()
    
    # 撈出該賣家所有上架書籍中，收到的 Pending 預約請求
    incoming_requests = Reservation.query.join(Book).filter(
        Book.seller_id == user_id,
        Reservation.status == 'Pending'
    ).order_by(Reservation.created_at.desc()).all()
    
    return render_template('cabinet/index.html',
                           available_books=available_books,
                           reserved_books=reserved_books,
                           sold_books=sold_books,
                           incoming_requests=incoming_requests)

@cabinet_bp.route('/edit/<int:book_id>', methods=['GET'])
def edit_page(book_id):
    if not session.get('user_id'):
        flash('請先登入系統。', 'warning')
        return redirect(url_for('auth.login_page'))
        
    user_id = session.get('user_id')
    book = Book.get_by_id(book_id)
    
    if not book:
        flash('找不到該書籍。', 'danger')
        return redirect(url_for('cabinet.index'))
        
    if book.seller_id != user_id:
        flash('您沒有權限修改此書籍！', 'danger')
        return redirect(url_for('cabinet.index'))
        
    return render_template('cabinet/edit.html', book=book)

@cabinet_bp.route('/edit/<int:book_id>', methods=['POST'])
def edit_action(book_id):
    if not session.get('user_id'):
        flash('請先登入系統。', 'warning')
        return redirect(url_for('auth.login_page'))
        
    user_id = session.get('user_id')
    book = Book.get_by_id(book_id)
    
    if not book:
        flash('找不到該書籍。', 'danger')
        return redirect(url_for('cabinet.index'))
        
    if book.seller_id != user_id:
        flash('您沒有權限修改此書籍！', 'danger')
        return redirect(url_for('cabinet.index'))
        
    # 取得修改表單資料
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

    # 驗證必要欄位（包括強制的出版年份與版本）
    if not title or not author or not publish_year or not edition or not condition:
        flash('請填寫所有必要欄位。', 'danger')
        return render_template('cabinet/edit.html', book=book)
        
    price = 0
    is_exchange = False
    if is_exchange_str == 'true':
        is_exchange = True
        price = 0
        if not exchange_item:
            flash('選擇僅限交換模式時，請填寫期望交換的書單或類型。', 'danger')
            return render_template('cabinet/edit.html', book=book)
    else:
        try:
            price = int(price_str)
            if price < 0:
                raise ValueError()
        except ValueError:
            flash('請輸入有效的出售價格。', 'danger')
            return render_template('cabinet/edit.html', book=book)
            
    # 處理選擇性圖片修改
    image_url = book.image_url
    file = request.files.get('book_image')
    if file and file.filename != '':
        # 圖片 2MB 大小限制
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > 2 * 1024 * 1024:
            flash('上傳的圖片檔案過大，限制在 2MB 以內。', 'danger')
            return render_template('cabinet/edit.html', book=book)
            
        from werkzeug.utils import secure_filename
        from time import time
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if ext not in ALLOWED_EXTENSIONS:
            flash('不支援的圖片格式。', 'danger')
            return render_template('cabinet/edit.html', book=book)
            
        upload_folder = os.path.join('app', 'static', 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
            
        filename = secure_filename(file.filename)
        unique_filename = f"{int(time())}_{filename}"
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        image_url = f"/static/uploads/{unique_filename}"
        
    try:
        book.update(
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
            dept=dept,
            subject=subject
        )
        flash('書籍資訊更新成功！', 'success')
        return redirect(url_for('cabinet.index'))
    except Exception as e:
        flash(f'更新失敗，系統錯誤：{str(e)}', 'danger')
        return render_template('cabinet/edit.html', book=book)

@cabinet_bp.route('/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    if not session.get('user_id'):
        flash('請先登入系統。', 'warning')
        return redirect(url_for('auth.login_page'))
        
    user_id = session.get('user_id')
    book = Book.get_by_id(book_id)
    
    if not book:
        flash('找不到該書籍。', 'danger')
        return redirect(url_for('cabinet.index'))
        
    if book.seller_id != user_id:
        flash('您沒有權限下架此書籍！', 'danger')
        return redirect(url_for('cabinet.index'))
        
    try:
        book.delete()
        flash('書籍已成功下架與刪除。', 'success')
    except Exception as e:
        flash(f'刪除失敗，錯誤：{str(e)}', 'danger')
        
    return redirect(url_for('cabinet.index'))

@cabinet_bp.route('/complete/<int:book_id>', methods=['POST'])
def complete_transaction(book_id):
    if not session.get('user_id'):
        flash('請先登入系統。', 'warning')
        return redirect(url_for('auth.login_page'))
        
    user_id = session.get('user_id')
    book = Book.get_by_id(book_id)
    
    if not book:
        flash('找不到該書籍。', 'danger')
        return redirect(url_for('cabinet.index'))
        
    if book.seller_id != user_id:
        flash('您沒有權限管理此書籍交易！', 'danger')
        return redirect(url_for('cabinet.index'))
        
    if book.status != 'Reserved':
        flash('此書籍尚未被確認預約，無法直接變更為成交。', 'warning')
        return redirect(url_for('cabinet.index'))
        
    try:
        book.update(status='Sold')
        flash('交易已順利完成！該書籍已標記為「已成交」並存檔。', 'success')
    except Exception as e:
        flash(f'操作失敗，錯誤：{str(e)}', 'danger')
        
    return redirect(url_for('cabinet.index'))
