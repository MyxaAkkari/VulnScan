from flask import jsonify, request, Blueprint, send_file
from scanner.openvas import OpenVASScanner
from config.db import User, get_db, UserRole
from config.config import Config
from sqlalchemy.orm import Session
from icalendar import Calendar, Event
from datetime import datetime
import pytz
from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity

scanner_bp = Blueprint('scanner_bp', __name__)
scanner = OpenVASScanner(socket_path = Config.OPENVAS_SOCKET_PATH, username = Config.OPENVAS_USERNAME, password = Config.OPENVAS_PASSWORD)


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
        
        return fn( *args, **kwargs)
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
        
        # Compare with UserRole.ADMIN correctly
        if current_user.role != UserRole.ADMIN:
            print(f"Access Denied: {current_user.role} does not match {UserRole.ADMIN}")
            return jsonify({"error": "Admin access required"}), 403
        
        return fn(*args, **kwargs)
    return wrapper



@scanner_bp.route('/authenticate', methods=['POST'])
@token_required
def authenticate():
    try:
        scanner.authenticate()
        return jsonify({"message": "Authenticated successfully"}), 200
    except ValueError as e:
            # Return the detailed error message
            return jsonify({"error": str(e)}), 500


@scanner_bp.route('/get_roles', methods=['GET'])
@token_required
def get_roles():
    try:
        roles = scanner.get_roles()
        return jsonify(roles), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@scanner_bp.route('/get_users', methods=['GET'])
@token_required
def get_users():
    try:
        users = scanner.get_users()
        return jsonify(users), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@scanner_bp.route('/get_user/<user_id>', methods=['GET'])
@token_required
def get_user(user_id):
    try:
        # Call the method to get user details by ID
        user = scanner.get_user(user_id=user_id)
        return jsonify(user), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400



@scanner_bp.route('/create_user', methods=['POST'])
@admin_required
def create_user():
    data = request.json
    name = data.get('name')
    password = data.get('password')
    role_ids = data.get('role_ids', [])
    
    try:
        result = scanner.create_user(name=name, password=password, role_ids=role_ids)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@scanner_bp.route('/modify_user/<user_id>', methods=['PUT'])
@admin_required
def modify_user(user_id):
    data = request.json
    new_username = data.get('name')
    new_password = data.get('password')
    new_roles = data.get('role_ids', [])
    
    try:
        result = scanner.modify_user(user_id=user_id, new_username=new_username, new_password=new_password, role_ids=new_roles)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@scanner_bp.route('/delete_user/<user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    try:
        result = scanner.delete_user(user_id=user_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400



@scanner_bp.route('/clone_user/<user_id>', methods=['POST'])
@admin_required
def clone_user(user_id):
    # Retrieve JSON data from the request
    data = request.json
    
    # Extract optional fields for modification
    new_name = data.get('name', None)
    new_comment = data.get('comment', None)
    new_roles = data.get('roles', None)
    
    try:
        # Call the clone_user method with optional parameters
        result = scanner.clone_user(user_id=user_id, name=new_name, comment=new_comment, roles=new_roles)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@scanner_bp.route('/get_scanners', methods=['GET'])
@token_required
def get_scanners():
    try:
        scanners = scanner.get_scanners()
        return jsonify(scanners), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    

@scanner_bp.route('/get_configs', methods=['GET'])
@token_required
def get_configs():
    try:
        configs = scanner.get_configs()
        config_list = []
        for config in configs:
            config_id = config.xpath('@id')[0]
            config_name = config.xpath('name/text()')[0]
            config_list.append({"config_id": config_id, "config_name": config_name})
        return jsonify(config_list), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500



@scanner_bp.route('/get_portlists', methods=['GET'])
@token_required
def get_portlists():
    try:
        portlists = scanner.get_portlists()
        return jsonify({"portlists": portlists}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500


@scanner_bp.route('/get_hosts', methods=['GET'])
@token_required
def get_hosts():
    try:
        hosts = scanner.get_hosts()
        return jsonify({"hosts": hosts}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500


@scanner_bp.route('/convert_hosts_to_targets', methods=['POST'])
@admin_required
def convert_hosts_to_targets():
    data = request.json
    hosts = data.get('hosts', [])
    port_list_id = data.get('port_list_id', None)
    port_range = data.get('port_range', None)
    
    created_targets = []

    # Fetch existing targets
    existing_targets = scanner.get_targets()
    existing_target_names = {target.findtext('name') for target in existing_targets}

    for host in hosts:
        # Extract hostname and IP
        hostname = host.get('hostname')
        ip = host.get('ip')

        if not ip:
            return jsonify({"error": "IP address is required for each host"}), 400

        # Use hostname if available, otherwise use IP as the target name
        target_name = hostname if hostname else ip

        # Skip creating the target if it already exists
        if target_name in existing_target_names:
            continue

        try:
            # Create target with the extracted name and IP
            target_id = scanner.create_target(name=target_name, hosts=ip, port_list_id=port_list_id, port_range=port_range)
            created_targets.append({"target_name": target_name, "target_id": target_id})
        except ValueError as e:
            # Return the detailed error message
            return jsonify({"error": str(e)}), 500

    return jsonify({"created_targets": created_targets}), 201


@scanner_bp.route('/get_targets', methods=['GET'])
@token_required
def get_targets():
    try:
        targets = scanner.get_targets()
        return jsonify(targets), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500



@scanner_bp.route('/create_target', methods=['POST'])
@admin_required
def create_target():
    data = request.json
    name = data.get('name')
    hosts = data.get('hosts')
    port_range = data.get('port_range')
    port_list_id = data.get('port_list_id')

    if not name or not hosts:
        return jsonify({"error": "Name and hosts are required."}), 400

    try:
        target_id = scanner.create_target(name=name, hosts=hosts, port_range=port_range, port_list_id=port_list_id)
        return jsonify({"target_id": target_id}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@scanner_bp.route('/delete_target/<target_id>', methods=['DELETE'])
@admin_required
def delete_target(target_id):
    try:
        result = scanner.delete_target(target_id=target_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500


@scanner_bp.route('/modify_target/<string:target_id>', methods=['POST'])
@admin_required
def modify_target(target_id):
    data = request.json
    try:
        # Extract parameters from the JSON request
        name = data.get('name')
        hosts = data.get('hosts')
        exclude_hosts = data.get('exclude_hosts')
        port_list_id = data.get('port_list_id')
        comment = data.get('comment')

        # Call the modify_target method with the extracted parameters
        result = scanner.modify_target(
            target_id=target_id,
            name=name,
            hosts=hosts,
            exclude_hosts=exclude_hosts,
            port_list_id=port_list_id,
            comment=comment
        )

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 500



@scanner_bp.route('/create_task', methods=['POST'])
@admin_required
def create_task():
    data = request.json
    name = data.get('name')
    target_id = data.get('target_id')
    config_id = data.get('config_id')
    scanner_id = data.get('scanner_id')
    schedule_id = data.get('schedule_id', None)
    alert_ids = data.get('alert_ids', None)
    
    try:
        task_id = scanner.create_task(name=name, target_id=target_id, config_id=config_id, scanner_id=scanner_id, schedule_id = schedule_id, alert_ids= alert_ids)
        return jsonify({"task_id": task_id}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 500

@scanner_bp.route('/start_task/<task_id>', methods=['POST'])
@admin_required
def start_task(task_id):    
    try:
        response = scanner.start_task(task_id=task_id)
        return jsonify(response), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500

@scanner_bp.route('/delete_task/<task_id>', methods=['DELETE'])
@admin_required
def delete_task(task_id):
    try:
        result = scanner.delete_task(task_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        # Handle unexpected errors
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500



@scanner_bp.route('/modify_task/<task_id>', methods=['PUT'])
@admin_required
def modify_task(task_id):
    data = request.json
    name = data.get('name')
    config_id = data.get('config_id')
    scanner_id = data.get('scanner_id')
    schedule_id = data.get('schedule_id')
    alert_ids = data.get('alert_ids')
    
    try:
        result = scanner.modify_task(task_id=task_id, name=name, config_id=config_id, scanner_id=scanner_id, schedule_id=schedule_id, alert_ids= alert_ids)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500

@scanner_bp.route('/get_task/<task_id>', methods=['GET'])
@token_required
def get_task(task_id):
    """
    Endpoint to retrieve information about a specific task.
    """
    if not task_id:
        return jsonify({"status": "error", "message": "task_id is required"}), 400

    try:
        response = scanner.get_task(task_id)
        return jsonify(response), 200
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": "An unexpected error occurred"}), 500


@scanner_bp.route('/get_task_status/<task_id>', methods=['GET'])
@token_required
def get_task_status(task_id):

    try:
        response = scanner.get_task_status(task_id=task_id)
        if response is None:
            return jsonify({"error": "Task not found or no status available."}), 404
        return jsonify(response), 200
    except ValueError as e:
        return jsonify({"error": "Failed to retrieve task status.", "details": str(e)}), 500



@scanner_bp.route('/get_tasks', methods=['GET'])
@token_required
def get_tasks():
    try:
        tasks = scanner.get_tasks()
        return jsonify({"tasks": tasks}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500



@scanner_bp.route('/get_results', methods=['POST'])
@token_required
def get_results():
    data = request.json
    task_id = data.get('task_id')
    
    try:
        results = scanner.get_results(task_id=task_id)
        return jsonify({"results": results}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500


@scanner_bp.route('/get_reports', methods=['GET'])
@token_required
def get_reports():
    try:
        reports = scanner.get_reports()
        return jsonify({"reports": reports}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500


@scanner_bp.route('/get_report/<report_id>', methods=['GET'])
@token_required
def get_report(report_id):
    report_data = scanner.get_report_by_id(report_id)
    if "error" in report_data:
        return jsonify(report_data), 404
    return jsonify(report_data), 200


@scanner_bp.route('/delete_report/<report_id>', methods=['DELETE'])
@admin_required
def delete_report(report_id):
    try:
        result = scanner.delete_report(report_id=report_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    

@scanner_bp.route('/export_report/<report_id>/<format>', methods=['GET'])
@token_required
def export_report(report_id, format):
    try:
        report_data = scanner.get_report_by_id(report_id)
        if "error" in report_data:
            return jsonify(report_data), 404

        filename = f"report_{report_id}.{format}"
        if format == 'csv':
            filepath = scanner.export_report_to_csv(report_data, filename)
        elif format == 'xlsx':
            filepath = scanner.export_report_to_excel(report_data, filename)
        elif format == 'pdf':
            filepath = scanner.export_report_to_pdf(report_data, filename)
        else:
            return jsonify({"error": "Unsupported format"}), 400

        return send_file(filepath, as_attachment=True)

    except ValueError as e:
        return jsonify({"error": str(e)}), 500

@scanner_bp.route('/get_schedules', methods=['GET'])
@token_required
def get_schedules():
    try:
        schedules = scanner.get_schedules()
        # Process the schedules if needed. Assuming `schedules` is already in a dictionary format.
        return jsonify({"schedules": schedules}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500


@scanner_bp.route('/create_schedule', methods=['POST'])
@admin_required
def create_schedule():
    data = request.json
    name = data['name']
    dtstart = datetime.strptime(data['dtstart'], '%Y-%m-%dT%H:%M:%S')
    timezone = data.get('timezone', 'UTC')
    comment = data.get('comment', '')
    frequency = data.get('frequency', 'daily')  # Default to daily
    interval = data.get('interval', 1)  # Default interval to 1
    count = data.get('count')  # Optional: number of occurrences

    # Create the iCalendar data
    cal = Calendar()
    cal.add('prodid', '-//VulunScan//')
    cal.add('version', '2.0')

    event = Event()
    event.add('dtstamp', datetime.now(tz=pytz.UTC))
    event.add('dtstart', dtstart)

    # Define recurrence rule based on frequency
    rrule_params = {
        'freq': frequency,
        'interval': interval
    }
    if count:
        rrule_params['count'] = count

    event.add('rrule', rrule_params)

    # Add the event to the calendar
    cal.add_component(event)

    # Convert the calendar to iCalendar format
    icalendar_data = cal.to_ical().decode()

    # Create the schedule using the simplified method
    schedule_id = scanner.create_schedule(
        name=name,
        icalendar_data=icalendar_data,
        timezone=timezone,
        comment=comment
    )

    return jsonify({"schedule_id": schedule_id}), 201

@scanner_bp.route('/modify_schedule', methods=['POST'])
@admin_required
def modify_schedule():
    data = request.json
    schedule_id = data['schedule_id']
    name = data['name']
    dtstart = datetime.strptime(data['dtstart'], '%Y-%m-%dT%H:%M:%S')
    timezone = data.get('timezone')
    comment = data.get('comment')
    frequency = data.get('frequency')  
    interval = data.get('interval')  
    count = data.get('count')  # Optional: number of occurrences

    # Create the iCalendar data
    cal = Calendar()
    cal.add('prodid', '-//VulunScan//')
    cal.add('version', '2.0')

    event = Event()
    event.add('dtstamp', datetime.now(tz=pytz.UTC))
    event.add('dtstart', dtstart)

    # Define recurrence rule based on frequency
    rrule_params = {
        'freq': frequency,
        'interval': interval
    }
    if count:
        rrule_params['count'] = count

    event.add('rrule', rrule_params)

    # Add the event to the calendar
    cal.add_component(event)

    # Convert the calendar to iCalendar format
    icalendar_data = cal.to_ical().decode()

    # Modify the schedule using the modified method
    scanner.modify_schedule(
        schedule_id=schedule_id,
        name=name,
        icalendar_data=icalendar_data,
        timezone=timezone,
        comment=comment
    )

    return jsonify({"message": "Schedule modified successfully"}), 200


@scanner_bp.route('/delete_schedule/<schedule_id>', methods=['DELETE'])
@admin_required
def delete_schedule(schedule_id):

    try:
        result = scanner.delete_schedule(schedule_id=schedule_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@scanner_bp.route('/create_alert', methods=['POST'])
@admin_required
def create_alert():
    try:
        data = request.json
        name = data.get('name')
        condition = data.get('condition')
        event = data.get('event')
        method = data.get('method')
        condition_data = data.get('condition_data', {})
        event_data = data.get('event_data', {})
        method_data = data.get('method_data', {})
        filter_id = data.get('filter_id')
        comment = data.get('comment')

        # Create the alert using the OpenVAS scanner's method
        alert_response = scanner.create_alert(
            name=name,
            condition=condition,
            event=event,
            method=method,
            condition_data=condition_data,
            event_data=event_data,
            method_data=method_data,
            filter_id=filter_id,
            comment=comment
        )

        return jsonify({
            "status": "success",
            "message": "Alert created successfully.",
            "alert_id": alert_response.get('id')
        }), 201

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to create alert: {str(e)}"
        }), 500
    

@scanner_bp.route('/get_alerts', methods=['GET'])
@token_required
def get_alerts():
    """
    Endpoint to retrieve a list of alerts.
    """
    try:
        alerts = scanner.get_alerts()
        return jsonify(alerts), 200
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": "An unexpected error occurred"}), 500


@scanner_bp.route('/modify_alert', methods=['POST'])
@admin_required
def modify_alert():
    """
    Endpoint to modify an existing alert.
    """
    data = request.json
    alert_id = data.get('alert_id')
    if not alert_id:
        return jsonify({"status": "error", "message": "alert_id is required"}), 400

    try:
        response = scanner.modify_alert(
            alert_id=alert_id,
            name=data.get('name'),
            condition=data.get('condition'),
            event=data.get('event'),
            method=data.get('method'),
            condition_data=data.get('condition_data'),
            event_data=data.get('event_data'),
            method_data=data.get('method_data'),
            filter_id=data.get('filter_id'),
            comment=data.get('comment')
        )
        return jsonify(response), 200
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": "An unexpected error occurred"}), 500


@scanner_bp.route('/delete_alert/<alert_id>', methods=['DELETE'])
@admin_required
def delete_alert(alert_id):
    """
    Endpoint to delete an alert.
    """
    if not alert_id:
        return jsonify({"status": "error", "message": "alert_id is required"}), 400

    try:
        response = scanner.delete_alert(alert_id=alert_id)
        return jsonify(response), 200
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": "An unexpected error occurred"}), 500