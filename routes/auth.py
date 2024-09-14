from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from config.db import get_db, User, UserRole
from config.config import Config
from functools import wraps
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

auth_bp = Blueprint('auth', __name__)
SECRET_KEY = Config.SECRET_KEY


def admin_required(fn):
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
    db: Session = next(get_db())
    data = request.json

    # Extract data
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = 'USER'  # Force role to 'user' to prevent admin creation
    comment = data.get('comment', '')

    # Check if the username or email already exists
    if db.query(User).filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400
    if db.query(User).filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    # Create a new user instance
    new_user = User(
        username=username,
        email=email,
        role=role,  # Role is forced to 'user'
        comment=comment
    )
    new_user.set_password(str(password))

    # Add the user to the session and commit
    db.add(new_user)
    db.commit()

    return jsonify({"message": "User created successfully"}), 201

@auth_bp.route('/create_admin', methods=['POST'])
@admin_required
def create_admin():
    db: Session = next(get_db())
    data = request.json

    # Extract data
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = 'ADMIN'  # Force role to 'admin'
    comment = data.get('comment', '')

    # Check if the username or email already exists
    if db.query(User).filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400
    if db.query(User).filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    # Create a new admin user instance
    new_admin = User(
        username=username,
        email=email,
        role=role,
        comment=comment
    )
    new_admin.set_password(password)

    # Add the admin to the session and commit
    db.add(new_admin)
    db.commit()

    return jsonify({"message": "Admin created successfully"}), 201

@auth_bp.route('/signin', methods=['POST'])
def signin():
    db: Session = next(get_db())
    data = request.json

    # Extract data
    email = data.get('email').lower()
    password = data.get('password')

    # Find the user by username
    user = db.query(User).filter_by(email=email).first()
    
    # If the user does not exist or the password is incorrect, return an error
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    # Create the JWT access token
    access_token = create_access_token(identity=user.id)

    # Convert the role to a string (if UserRole is an enum or custom class)
    user_role = str(user.role)

    # Return the token
    return jsonify({
        "access_token": access_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user_role  # Ensure this is a string
        }
    }), 200


@auth_bp.route('/modify_user/<int:user_id>', methods=['PUT'])
@admin_required
def modify_user(user_id):
    db: Session = next(get_db())
    data = request.json

    # Find the user by ID
    user = db.query(User).filter_by(id=user_id).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    # Update user details
    if 'username' in data:
        if db.query(User).filter_by(username=data['username']).first():
            return jsonify({"error": "Username already exists"}), 400
        user.username = data['username']
    
    if 'email' in data:
        if db.query(User).filter_by(email=data['email']).first():
            return jsonify({"error": "Email already exists"}), 400
        user.email = data['email']
    
    if 'role' in data:
        if data['role'] not in [UserRole.USER, UserRole.ADMIN]:
            return jsonify({"error": "Invalid role specified"}), 400
        user.role = data['role']
    
    if 'password' in data:
        user.set_password(data['password'])

    if 'comment' in data:
        user.comment = data['comment']

    # Commit the changes to the database
    db.commit()

    return jsonify({"message": "User updated successfully"}), 200


@auth_bp.route('/delete_user/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    db: Session = next(get_db())

    # Find the user by ID
    user = db.query(User).filter_by(id=user_id).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    # Delete the user
    db.delete(user)
    db.commit()

    return jsonify({"message": "User deleted successfully"}), 200

@auth_bp.route('/get_user', methods=['GET'])
@jwt_required()
def get_user():
    """
    Retrieve information about the currently logged-in user.
    """
    db: Session = next(get_db())
    
    # Get the current user's ID from the JWT token
    current_user_id = get_jwt_identity()

    # Find the user in the database
    user = db.query(User).filter_by(id=current_user_id).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    # Return user details
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "comment": user.comment,
        "created_at": user.created_at,
        "updated_at": user.updated_at
    }), 200


@auth_bp.route('/get_users', methods=['GET'])
@admin_required
def get_users():
    """
    Retrieve information for all users. Admin access required.
    """
    db: Session = next(get_db())
    
    # Get all users from the database
    users = db.query(User).all()

    # Map users to a list of dictionaries with relevant info
    users_info = [{
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "comment": user.comment,
        "created_at": user.created_at,
        "updated_at": user.updated_at
    } for user in users]

    return jsonify(users_info), 200