from flask import Blueprint

requests_bp = Blueprint('requests', __name__, url_prefix='/requests')

@requests_bp.route('/create/<int:book_id>', methods=['POST'])
def create(book_id):
    """
    POST /requests/create/<book_id>
    Create a new buying or exchanging reservation request for a book.
    Inputs:
        - URL Parameter: book_id (integer)
        - Form fields: message (buyer's custom note / exchange proposal)
    Logic:
        - Verify login state.
        - Verify the buyer is not the seller of the book.
        - Verify book status is 'Available'.
        - Call Reservation.create(book_id, buyer_id, message, status='Pending') in DB.
        - (Optional Should-Have) Update book status indicator or alert the seller.
    Output:
        - Redirect to GET /books/<book_id> with success flash message.
    """
    pass

@requests_bp.route('/accept/<int:req_id>', methods=['POST'])
def accept(req_id):
    """
    POST /requests/accept/<req_id>
    Accept a buyer's reservation request. Called by the book owner.
    Inputs:
        - URL Parameter: req_id (integer)
    Logic:
        - Verify login state.
        - Fetch Reservation by req_id.
        - Verify book belongs to the logged-in user.
        - Update Reservation status to 'Accepted'.
        - Call Book.update(status='Reserved') to lock the book listing from other buyers.
        - Reject all other 'Pending' requests for this same book.
    Output:
        - Redirect to GET /cabinet with success flash (revealing buyer's email/Line ID).
    """
    pass

@requests_bp.route('/reject/<int:req_id>', methods=['POST'])
def reject(req_id):
    """
    POST /requests/reject/<req_id>
    Reject a buyer's reservation request. Called by the book owner.
    Inputs:
        - URL Parameter: req_id (integer)
    Logic:
        - Verify login state.
        - Fetch Reservation by req_id.
        - Verify book belongs to the logged-in user.
        - Update Reservation status to 'Rejected'.
        - Call Book.update(status='Available') if no other accepted reservations exist.
    Output:
        - Redirect to GET /cabinet with informative flash message.
    """
    pass
