from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET'])
def register_page():
    """
    GET /auth/register
    Render the registration form page.
    Inputs: None
    Output: Render 'auth/register.html'
    """
    pass

@auth_bp.route('/register', methods=['POST'])
def register_action():
    """
    POST /auth/register
    Process the user registration.
    Inputs:
        - Form fields: username, email, password, contact_info
    Validation:
        - Check if email ends with '.edu.tw'.
        - Check if password is secure.
        - Check if email already exists in DB.
    Logic:
        - Hash the password.
        - Generate a 6-digit mock verification code.
        - Log/Print the verification code to the Terminal console.
        - Create an unverified User record in DB.
    Output:
        - Success: Redirect to GET /auth/verify (store email in session or pass as query)
        - Error: Redirect or re-render register page with flash message.
    """
    pass

@auth_bp.route('/verify', methods=['GET'])
def verify_page():
    """
    GET /auth/verify
    Render the email verification page.
    Inputs: None
    Output: Render 'auth/verify.html'
    """
    pass

@auth_bp.route('/verify', methods=['POST'])
def verify_action():
    """
    POST /auth/verify
    Validate the 6-digit email verification code.
    Inputs:
        - Form fields: email, verification_code
    Logic:
        - Find the User by email.
        - Verify code matches User.verification_code.
        - Set User.is_verified = True.
    Output:
        - Success: Flash success message, redirect to GET /auth/login
        - Error: Flash error, re-render GET /auth/verify
    """
    pass

@auth_bp.route('/login', methods=['GET'])
def login_page():
    """
    GET /auth/login
    Render the user login page.
    Inputs: None
    Output: Render 'auth/login.html'
    """
    pass

@auth_bp.route('/login', methods=['POST'])
def login_action():
    """
    POST /auth/login
    Authenticate user credentials.
    Inputs:
        - Form fields: email, password
    Logic:
        - Find User by email.
        - Check if user is verified (is_verified == True).
        - Verify password matches password_hash using check_password_hash.
        - Store user_id, username in flask session.
    Output:
        - Success: Redirect to GET / (Home page)
        - Error: Flash warning, redirect/re-render GET /auth/login
    """
    pass

@auth_bp.route('/logout', methods=['GET'])
def logout():
    """
    GET /auth/logout
    Log out the user by clearing the session.
    Inputs: None
    Logic:
        - Clear 'user_id', 'username' from session.
    Output:
        - Redirect to GET / (Home page)
    """
    pass
