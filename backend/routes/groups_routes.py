from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from config.db import get_db, Group, Target, UserRole, User
from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity

groups_bp = Blueprint('groups', __name__)

def token_required(fn):
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
        
        return fn(*args, **kwargs)
    return wrapper

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
        
        # Ensure the user has admin privileges
        if current_user.role != UserRole.ADMIN:
            print(f"Access Denied: {current_user.role} does not match {UserRole.ADMIN}")
            return jsonify({"error": "Admin access required"}), 403
        
        return fn(*args, **kwargs)
    return wrapper

@groups_bp.route('/create_group', methods=['POST'])
@admin_required
def create_group():
    """
    Endpoint to create a new group.
    Admin access is required.
    """
    data = request.json
    group_name = data.get('group_name')
    
    if not group_name:
        return jsonify({"error": "group_name is required"}), 400
    
    db: Session = next(get_db())
    group = Group(name=group_name)
    db.add(group)
    db.commit()

    return jsonify({"message": "Group created", "group_id": group.id}), 201

@groups_bp.route('/get_groups', methods=['GET'])
@token_required
def get_groups():
    """
    Endpoint to retrieve all groups.
    Any authenticated user can access this.
    """
    db: Session = next(get_db())
    groups = db.query(Group).all()
    groups_data = [{"id": g.id, "name": g.name} for g in groups]

    return jsonify(groups_data), 200

@groups_bp.route('/rename_group/<int:group_id>', methods=['PUT'])
@admin_required
def rename_group(group_id):
    """
    Endpoint to rename an existing group.
    Admin access is required.
    """
    data = request.json
    new_name = data.get('group_name')
    
    if not new_name:
        return jsonify({"error": "group_name is required"}), 400
    
    db: Session = next(get_db())
    group = db.query(Group).filter(Group.id == group_id).first()
    
    if not group:
        return jsonify({"error": "Group not found"}), 404
    
    group.name = new_name
    db.commit()

    return jsonify({"message": "Group renamed", "new_name": group.name}), 200

@groups_bp.route('/delete_group/<int:group_id>', methods=['DELETE'])
@admin_required
def delete_group(group_id):
    """
    Endpoint to delete a group by its ID.
    Admin access is required.
    """
    db: Session = next(get_db())
    group = db.query(Group).filter(Group.id == group_id).first()
    
    if not group:
        return jsonify({"error": "Group not found"}), 404
    
    db.delete(group)
    db.commit()

    return jsonify({"message": "Group deleted"}), 200

@groups_bp.route('/remove_from_group', methods=['POST'])
@admin_required
def remove_from_group():
    """
    Endpoint to remove a target from a group.
    Admin access is required.
    """
    data = request.json
    target_id = data.get('target_id')
    group_id = data.get('group_id')
    
    if not target_id or not group_id:
        return jsonify({"error": "target_id and group_id are required"}), 400
    
    db: Session = next(get_db())
    target = db.query(Target).filter(Target.id == target_id, Target.group_id == group_id).first()
    
    if not target:
        return jsonify({"error": "Target not found in group"}), 404
    
    # Remove the target from the group
    target.group_id = None
    db.commit()

    return jsonify({"message": "Target removed from group"}), 200

@groups_bp.route('/add_target', methods=['POST'])
@admin_required
def add_target():
    """
    Endpoint to add a new target to a group.
    Admin access is required.
    """
    data = request.json
    name = data.get('name')
    ip_address = data.get('ip_address')
    group_id = data.get('group_id')

    db: Session = next(get_db())
    target = Target(name=name, ip_address=ip_address, group_id=group_id)
    db.add(target)
    db.commit()

    return jsonify({"message": "Target added", "target_id": target.id}), 201

@groups_bp.route('/get_group_targets/<int:group_id>', methods=['GET'])
@token_required
def get_group_targets(group_id):
    """
    Endpoint to retrieve all targets in a specific group.
    Any authenticated user can access this.
    """
    db: Session = next(get_db())
    targets = db.query(Target).filter(Target.group_id == group_id).all()
    targets_data = [{"id": t.id, "name": t.name, "ip_address": t.ip_address} for t in targets]

    return jsonify(targets_data), 200
