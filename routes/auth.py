from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from config.db import get_db, User, UserRole
from config.config import Config
from functools import wraps
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

auth_bp = Blueprint('auth', __name__)
SECRET_KEY = Config.SECRET_KEY


def admin_required(fn):
    """
    Decorator to enforce admin access on routes.

    Args:
        fn: The original function to be wrapped.

    Returns:
        The wrapped function with admin access check.
    """
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        # Access the database session
        db: Session = next(get_db())
        # Get the current user's ID from the token
        current_user_id = get_jwt_identity()
        # Retrieve the user from the database
        current_user = db.query(User).filter_by(id=current_user_id).first()

        if not current_user:
            return jsonify({"error": "User not found!"}), 403
        
        # Compare with UserRole.ADMIN correctly
        if current_user.role != UserRole.ADMIN:
            print(f"Access Denied: {current_user.role} does not match {UserRole.ADMIN}")
            return jsonify({"error": "Admin access required"}), 403
        
        return fn(*args, **kwargs)
    return wrapper



@auth_bp.route('/signup', methods=['POST'])
def signup():
    """
    Endpoint for user registration (signup).

    Expects a JSON payload with username, email, password, and an optional comment.
    Only regular users can be created (admin role is not allowed).

    Returns:
        JSON response with a success or error message.
    """
    db: Session = next(get_db())
    data = request.json

    # Extract data from the request
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = 'USER'  # Force role to 'USER' to prevent admin creation
    comment = data.get('comment', '')

    # Check if the username already exists
    if db.query(User).filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400
    # Check if the email already exists
    if db.query(User).filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    # Create a new user instance
    new_user = User(
        username=username,
        email=email,
        role=role,  # Role is forced to 'USER'
        comment=comment
    )
    # Set the user's password using the hashed version
    new_user.set_password(str(password))

    # Add the user to the session and commit to the database
    db.add(new_user)
    db.commit()

    return jsonify({"message": "User created successfully"}), 201


@auth_bp.route('/create_admin', methods=['POST'])
@admin_required
def create_admin():
    """
    Endpoint for creating a new admin user.

    Requires admin access. Expects a JSON payload with username, email, password, and an optional comment.

    Returns:
        JSON response with a success or error message.
    """
    db: Session = next(get_db())
    data = request.json

    # Extract data from the request
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = 'ADMIN'  # Force role to 'ADMIN'
    comment = data.get('comment', '')

    # Check if the username already exists
    if db.query(User).filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400
    # Check if the email already exists
    if db.query(User).filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    # Create a new admin user instance
    new_admin = User(
        username=username,
        email=email,
        role=role,
        comment=comment
    )
    # Set the admin's password using the hashed version
    new_admin.set_password(password)

    # Add the admin to the session and commit to the database
    db.add(new_admin)
    db.commit()

    return jsonify({"message": "Admin created successfully"}), 201

@auth_bp.route('/signin', methods=['POST'])
def signin():
    """
    Endpoint for user sign-in.

    Expects a JSON payload with email and password. 
    If the credentials are valid, returns a JWT access token and user details.

    Returns:
        JSON response containing the access token and user information or an error message.
    """
    db: Session = next(get_db())
    data = request.json

    # Extract email and password from the request
    email = data.get('email').lower()
    password = data.get('password')

    # Find the user by email in the database
    user = db.query(User).filter_by(email=email).first()
    
    # If the user does not exist or the password is incorrect, return an error response
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    # Create the JWT access token with the user's ID as the identity
    access_token = create_access_token(identity=user.id)

    # Convert the user's role to a string (if UserRole is an enum or custom class)
    user_role = str(user.role)

    # Return the access token and user details in the response
    return jsonify({
        "access_token": access_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user_role  # Ensure this is a string representation of the role
        }
    }), 200



@auth_bp.route('/modify_user/<int:user_id>', methods=['PUT'])
@admin_required
def modify_user(user_id):
    """
    Endpoint to modify an existing user's details.

    Requires admin access. Expects a JSON payload with user attributes to modify.
    The user is identified by the user_id in the URL.

    Args:
        user_id (int): ID of the user to modify.

    Returns:
        JSON response indicating success or error.
    """
    db: Session = next(get_db())
    data = request.json

    # Find the user by ID in the database
    user = db.query(User).filter_by(id=user_id).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    # Update user details based on the provided data
    if 'username' in data:
        # Check if the new username already exists
        if db.query(User).filter_by(username=data['username']).first():
            return jsonify({"error": "Username already exists"}), 400
        user.username = data['username']
    
    if 'email' in data:
        # Check if the new email already exists
        if db.query(User).filter_by(email=data['email']).first():
            return jsonify({"error": "Email already exists"}), 400
        user.email = data['email']
    
    if 'role' in data:
        # Validate the specified role
        if data['role'] not in [UserRole.USER, UserRole.ADMIN]:
            return jsonify({"error": "Invalid role specified"}), 400
        user.role = data['role']
    
    if 'password' in data:
        # Set the new password
        user.set_password(data['password'])

    if 'comment' in data:
        # Update the comment if provided
        user.comment = data['comment']

    # Commit the changes to the database
    db.commit()

    # Return a success message
    return jsonify({"message": "User updated successfully"}), 200



@auth_bp.route('/delete_user/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """
    Endpoint to delete an existing user.

    Requires admin access. The user to be deleted is identified by the user_id in the URL.

    Args:
        user_id (int): ID of the user to delete.

    Returns:
        JSON response indicating success or error.
    """
    db: Session = next(get_db())

    # Find the user by ID in the database
    user = db.query(User).filter_by(id=user_id).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    # Delete the user from the database
    db.delete(user)
    db.commit()

    # Return a success message
    return jsonify({"message": "User deleted successfully"}), 200


@auth_bp.route('/get_user', methods=['GET'])
@jwt_required()
def get_user():
    """
    Endpoint to retrieve information about the currently logged-in user.

    Requires a valid JWT token for authentication.

    Returns:
        JSON response containing the user's details or an error message.
    """
    db: Session = next(get_db())
    
    # Get the current user's ID from the JWT token
    current_user_id = get_jwt_identity()

    # Find the user in the database using the ID
    user = db.query(User).filter_by(id=current_user_id).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    # Return user details in the response
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.name if hasattr(user.role, 'name') else str(user.role),  # Ensure role is serializable
        "comment": user.comment,
    }), 200



@auth_bp.route('/get_users', methods=['GET'])
@admin_required
def get_users():
    """
    Endpoint to retrieve information for all users.

    Admin access is required to view the user list.

    Returns:
        JSON response containing a list of users with their details.
    """
    db: Session = next(get_db())
    
    # Get all users from the database
    users = db.query(User).all()

    # Map users to a list of dictionaries with relevant information
    users_info = [{
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.name if hasattr(user.role, 'name') else str(user.role),  # Ensure role is serializable
        "comment": user.comment,
    } for user in users]

    # Return the list of user information in the response
    return jsonify(users_info), 200
