from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from db import get_db, Group, Target

groups_bp = Blueprint('groups', __name__)

@groups_bp.route('/create_group', methods=['POST'])
def create_group():
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
def get_groups():
    db: Session = next(get_db())
    groups = db.query(Group).all()
    groups_data = [{"id": g.id, "name": g.name} for g in groups]

    return jsonify(groups_data), 200

@groups_bp.route('/rename_group/<int:group_id>', methods=['PUT'])
def rename_group(group_id):
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
def delete_group(group_id):
    db: Session = next(get_db())
    group = db.query(Group).filter(Group.id == group_id).first()
    
    if not group:
        return jsonify({"error": "Group not found"}), 404
    
    db.delete(group)
    db.commit()

    return jsonify({"message": "Group deleted"}), 200

@groups_bp.route('/remove_from_group', methods=['POST'])
def remove_from_group():
    data = request.json
    target_id = data.get('target_id')
    group_id = data.get('group_id')
    
    if not target_id or not group_id:
        return jsonify({"error": "target_id and group_id are required"}), 400
    
    db: Session = next(get_db())
    target = db.query(Target).filter(Target.id == target_id, Target.group_id == group_id).first()
    
    if not target:
        return jsonify({"error": "Target not found in group"}), 404
    
    target.group_id = None
    db.commit()

    return jsonify({"message": "Target removed from group"}), 200


@groups_bp.route('/add_target', methods=['POST'])
def add_target():
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
def get_group_targets(group_id):
    db: Session = next(get_db())
    targets = db.query(Target).filter(Target.group_id == group_id).all()
    targets_data = [{"id": t.id, "name": t.name, "ip_address": t.ip_address} for t in targets]

    return jsonify(targets_data), 200
