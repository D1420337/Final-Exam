from flask import Blueprint

cabinet_bp = Blueprint('cabinet', __name__, url_prefix='/cabinet')

@cabinet_bp.route('', methods=['GET'])
def index():
    """
    GET /cabinet
    Render the seller's personal book cabinet console.
    Inputs: None (identifies logged-in user via session)
    Logic:
        - Verify login state.
        - Fetch all books owned by the logged-in user, grouped by status:
            - 'Available' (上架中)
            - 'Reserved' (已預約/處理中)
            - 'Sold' (已成交)
        - Fetch any incoming reservation requests for the owner's books.
    Output:
        - Render 'cabinet/index.html' passing books and reservation requests lists.
    """
    pass

@cabinet_bp.route('/edit/<int:book_id>', methods=['GET'])
def edit_page(book_id):
    """
    GET /cabinet/edit/<book_id>
    Render the edit book page.
    Inputs:
        - URL Parameter: book_id (integer)
    Logic:
        - Verify login state.
        - Fetch book by book_id.
        - Verify book belongs to the logged-in user, and status is 'Available'.
    Output:
        - Success: Render 'cabinet/edit.html'
        - Error: Redirect to /cabinet with flash error.
    """
    pass

@cabinet_bp.route('/edit/<int:book_id>', methods=['POST'])
def edit_action(book_id):
    """
    POST /cabinet/edit/<book_id>
    Process the book details update.
    Inputs:
        - URL Parameter: book_id (integer)
        - Form fields: title, author, publisher, isbn, price, is_exchange, exchange_item, condition, description, dept, subject
    Logic:
        - Verify login state.
        - Fetch book by book_id.
        - Verify book belongs to the logged-in user.
        - Call Book.update() to save new information in DB.
    Output:
        - Success: Redirect to GET /cabinet with success flash
        - Error: Redirect/Re-render with validation errors.
    """
    pass

@cabinet_bp.route('/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    """
    POST /cabinet/delete/<book_id>
    Delete or off-shelf a second-hand book.
    Inputs:
        - URL Parameter: book_id (integer)
    Logic:
        - Verify login state.
        - Fetch book by book_id.
        - Verify book belongs to the logged-in user.
        - Call Book.delete() to remove from DB (comments and requests are deleted via cascade).
    Output:
        - Redirect to GET /cabinet with success flash.
    """
    pass

@cabinet_bp.route('/complete/<int:book_id>', methods=['POST'])
def complete_transaction(book_id):
    """
    POST /cabinet/complete/<book_id>
    Confirm the transaction is complete (face-to-face deal done).
    Inputs:
        - URL Parameter: book_id (integer)
    Logic:
        - Verify login state.
        - Fetch book by book_id.
        - Verify book belongs to user, and current status is 'Reserved'.
        - Call Book.update(status='Sold') to close listing.
    Output:
        - Redirect to GET /cabinet with success flash.
    """
    pass
