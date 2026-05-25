from flask import Blueprint, session, redirect, url_for, flash, request, render_template
from app.models import db
from app.models.book import Book
from app.models.reservation import Reservation

requests_bp = Blueprint('requests', __name__, url_prefix='/requests')

@requests_bp.route('/create/<int:book_id>', methods=['POST'])
def create(book_id):
    """
    POST /requests/create/<book_id>
    Create a new buying or exchanging reservation request for a book.
    """
    if not session.get('user_id'):
        flash('請先登入系統才能送出預約。', 'warning')
        return redirect(url_for('auth.login_page'))
        
    buyer_id = session.get('user_id')
    book = Book.get_by_id(book_id)
    if not book:
        flash('找不到該二手書。', 'danger')
        return redirect(url_for('books.search'))
        
    if book.seller_id == buyer_id:
        flash('您不能預約自己上架的書籍！', 'danger')
        return redirect(url_for('books.detail', book_id=book_id))
        
    if book.status != 'Available':
        flash('該書籍已被預約或售出，無法進行預約。', 'danger')
        return redirect(url_for('books.detail', book_id=book_id))
        
    # 檢查是否已送出過預約請求
    existing_req = Reservation.query.filter_by(book_id=book_id, buyer_id=buyer_id).first()
    if existing_req:
        flash('您已送出過此書的預約請求，請勿重複提交。', 'warning')
        return redirect(url_for('books.detail', book_id=book_id))
        
    message = request.form.get('message', '').strip()
    
    try:
        # 建立預約記錄 (預設 status='Pending')
        Reservation.create(book_id=book_id, buyer_id=buyer_id, message=message, status='Pending')
        flash('預約請求送出成功！已通知書主審核。', 'success')
        return redirect(url_for('books.detail', book_id=book_id))
    except Exception as e:
        flash(f'預約失敗，系統發生錯誤：{str(e)}', 'danger')
        return redirect(url_for('books.detail', book_id=book_id))

@requests_bp.route('/accept/<int:req_id>', methods=['POST'])
def accept(req_id):
    """
    POST /requests/accept/<req_id>
    Accept a buyer's reservation request. Called by the book owner.
    """
    if not session.get('user_id'):
        flash('請先登入系統。', 'warning')
        return redirect(url_for('auth.login_page'))
        
    seller_id = session.get('user_id')
    req = Reservation.get_by_id(req_id)
    if not req:
        flash('找不到該預約請求。', 'danger')
        return redirect(url_for('cabinet.index'))
        
    book = Book.get_by_id(req.book_id)
    if not book or book.seller_id != seller_id:
        flash('您沒有權限操作此預約。', 'danger')
        return redirect(url_for('cabinet.index'))
        
    try:
        # 同意該預約
        req.update(status='Accepted')
        # 將書籍狀態更新為 Reserved (已預約/面交中)
        book.update(status='Reserved')
        
        # 自動拒絕其他對此書的 Pending 預約
        other_reqs = Reservation.query.filter(
            Reservation.book_id == book.id,
            Reservation.id != req.id,
            Reservation.status == 'Pending'
        ).all()
        for r in other_reqs:
            r.update(status='Rejected')
            
        flash('已接受預約請求！書籍已鎖定為預約狀態，已向您顯示買家聯絡資訊。', 'success')
    except Exception as e:
        flash(f'操作失敗，錯誤：{str(e)}', 'danger')
        
    return redirect(url_for('cabinet.index'))

@requests_bp.route('/reject/<int:req_id>', methods=['POST'])
def reject(req_id):
    """
    POST /requests/reject/<req_id>
    Reject a buyer's reservation request. Called by the book owner.
    """
    if not session.get('user_id'):
        flash('請先登入系統。', 'warning')
        return redirect(url_for('auth.login_page'))
        
    seller_id = session.get('user_id')
    req = Reservation.get_by_id(req_id)
    if not req:
        flash('找不到該預約請求。', 'danger')
        return redirect(url_for('cabinet.index'))
        
    book = Book.get_by_id(req.book_id)
    if not book or book.seller_id != seller_id:
        flash('您沒有權限操作此預約。', 'danger')
        return redirect(url_for('cabinet.index'))
        
    try:
        req.update(status='Rejected')
        flash('已拒絕該預約請求。', 'info')
    except Exception as e:
        flash(f'操作失敗，錯誤：{str(e)}', 'danger')
        
    return redirect(url_for('cabinet.index'))
