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
# Initialize the OpenVASScanner with the specified configuration
scanner = OpenVASScanner(socket_path=Config.OPENVAS_SOCKET_PATH, username=Config.OPENVAS_USERNAME, password=Config.OPENVAS_PASSWORD)

def token_required(fn):
    """
    Decorator to ensure the user is authenticated by checking for a valid JWT token.
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
        
        return fn(*args, **kwargs)
    return wrapper

def admin_required(fn):
    """
    Decorator to ensure that the user has admin privileges.
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
        
        # Check if the current user has admin role
        if current_user.role != UserRole.ADMIN:
            print(f"Access Denied: {current_user.role} does not match {UserRole.ADMIN}")
            return jsonify({"error": "Admin access required"}), 403
        
        return fn(*args, **kwargs)
    return wrapper



@scanner_bp.route('/authenticate', methods=['POST'])
@token_required
def authenticate():
    """
    Authenticate the user with the OpenVAS scanner.
    Returns a success message if authentication is successful.
    """
    try:
        scanner.authenticate()  # Attempt to authenticate the scanner
        return jsonify({"message": "Authenticated successfully"}), 200  # Return success message
    except ValueError as e:
        # Return the detailed error message
        return jsonify({"error": str(e)}), 500  # Return error if authentication fails


@scanner_bp.route('/get_roles', methods=['GET'])
@token_required
def get_roles():
    """
    Retrieve a list of user roles from the OpenVAS scanner.
    Returns the roles in JSON format.
    """
    try:
        roles = scanner.get_roles()  # Get user roles from the scanner
        return jsonify(roles), 200  # Return roles as JSON
    except ValueError as e:
        return jsonify({"error": str(e)}), 400  # Return error if role retrieval fails


@scanner_bp.route('/get_users', methods=['GET'])
@token_required
def get_users():
    """
    Retrieve a list of users from the OpenVAS scanner.
    Returns the users in JSON format.
    """
    try:
        users = scanner.get_users()  # Get users from the scanner
        return jsonify(users), 200  # Return users as JSON
    except ValueError as e:
        return jsonify({"error": str(e)}), 400  # Return error if user retrieval fails



@scanner_bp.route('/get_user/<user_id>', methods=['GET'])
@token_required
def get_user(user_id):
    """
    Retrieve details of a specific user by their ID.
    Returns user information in JSON format.
    """
    try:
        # Call the method to get user details by ID
        user = scanner.get_user(user_id=user_id)  # Retrieve user details using the scanner
        return jsonify(user), 200  # Return user details as JSON
    except ValueError as e:
        return jsonify({"error": str(e)}), 400  # Return error if user retrieval fails


@scanner_bp.route('/create_user', methods=['POST'])
@admin_required
def create_user():
    """
    Create a new user with the specified details.
    Requires admin privileges to execute.
    Returns the result of the user creation operation.
    """
    data = request.json  # Get JSON data from the request
    name = data.get('name')  # Extract the user's name
    password = data.get('password')  # Extract the user's password
    role_ids = data.get('role_ids', [])  # Extract role IDs, defaulting to an empty list
    
    try:
        result = scanner.create_user(name=name, password=password, role_ids=role_ids)  # Create user
        return jsonify(result), 200  # Return the result of user creation
    except ValueError as e:
        return jsonify({"error": str(e)}), 400  # Return error if user creation fails



@scanner_bp.route('/modify_user/<user_id>', methods=['PUT'])
@admin_required
def modify_user(user_id):
    """
    Modify the details of an existing user specified by user ID.
    Requires admin privileges to execute.
    Returns the result of the user modification operation.
    """
    data = request.json  # Get JSON data from the request
    new_username = data.get('name')  # Extract the new username
    new_password = data.get('password')  # Extract the new password
    new_roles = data.get('role_ids', [])  # Extract new role IDs, defaulting to an empty list
    
    try:
        result = scanner.modify_user(user_id=user_id, new_username=new_username, new_password=new_password, role_ids=new_roles)  # Modify user
        return jsonify(result), 200  # Return the result of user modification
    except ValueError as e:
        return jsonify({"error": str(e)}), 400  # Return error if user modification fails


@scanner_bp.route('/delete_user/<user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """
    Delete a user specified by user ID.
    Requires admin privileges to execute.
    Returns the result of the user deletion operation.
    """
    try:
        result = scanner.delete_user(user_id=user_id)  # Delete user
        return jsonify(result), 200  # Return the result of user deletion
    except ValueError as e:
        return jsonify({"error": str(e)}), 400  # Return error if user deletion fails




@scanner_bp.route('/clone_user/<user_id>', methods=['POST'])
@admin_required
def clone_user(user_id):
    """
    Clone an existing user specified by user ID.
    Requires admin privileges to execute.
    Accepts optional fields for name, comment, and roles for the cloned user.
    Returns the result of the cloning operation.
    """
    # Retrieve JSON data from the request
    data = request.json
    
    # Extract optional fields for modification
    new_name = data.get('name', None)  # New name for the cloned user, if provided
    new_comment = data.get('comment', None)  # New comment for the cloned user, if provided
    new_roles = data.get('roles', None)  # New roles for the cloned user, if provided
    
    try:
        # Call the clone_user method with optional parameters
        result = scanner.clone_user(user_id=user_id, name=new_name, comment=new_comment, roles=new_roles)
        return jsonify(result), 200  # Return the result of cloning the user
    except ValueError as e:
        return jsonify({"error": str(e)}), 400  # Return error if cloning fails


@scanner_bp.route('/get_scanners', methods=['GET'])
@token_required
def get_scanners():
    """
    Retrieve a list of available scanners.
    Requires token authentication to execute.
    Returns a formatted list of scanners as key-value pairs.
    """
    try:
        scanners = scanner.get_scanners()  # Retrieve scanners from the OpenVAS
        # Refactor output to key-value pairs
        formatted_scanners = [{"id": scanner[0], "name": scanner[1]} for scanner in scanners]  # Format scanner data
        return jsonify(formatted_scanners), 200  # Return formatted scanners
    except ValueError as e:
        return jsonify({"error": str(e)}), 500  # Return error if retrieval fails


@scanner_bp.route('/get_configs', methods=['GET'])
@token_required
def get_configs():
    """
    Retrieve a list of configuration settings from the OpenVAS scanner.
    Requires token authentication to execute.
    Returns a list of configurations with their IDs and names.
    """
    try:
        configs = scanner.get_configs()  # Retrieve configurations from the OpenVAS
        config_list = []  # Initialize a list to store formatted config data
        for config in configs:
            config_id = config.xpath('@id')[0]  # Extract the config ID
            config_name = config.xpath('name/text()')[0]  # Extract the config name
            config_list.append({"config_id": config_id, "config_name": config_name})  # Add to the list
        return jsonify(config_list), 200  # Return the list of configurations
    except ValueError as e:
        return jsonify({"error": str(e)}), 500  # Return error if retrieval fails


@scanner_bp.route('/get_portlists', methods=['GET'])
@token_required
def get_portlists():
    """
    Retrieve a list of port lists from the OpenVAS scanner.
    Requires token authentication to execute.
    Returns a list of port lists.
    """
    try:
        portlists = scanner.get_portlists()  # Retrieve port lists from the OpenVAS
        return jsonify({"portlists": portlists}), 200  # Return port lists
    except ValueError as e:
        return jsonify({"error": str(e)}), 500  # Return error if retrieval fails


@scanner_bp.route('/get_hosts', methods=['GET'])
@token_required
def get_hosts():
    """
    Retrieve a list of hosts from the OpenVAS scanner.
    Requires token authentication to execute.
    Returns a list of hosts.
    """
    try:
        hosts = scanner.get_hosts()  # Retrieve hosts from the OpenVAS
        return jsonify({"hosts": hosts}), 200  # Return the list of hosts
    except ValueError as e:
        return jsonify({"error": str(e)}), 500  # Return error if retrieval fails


@scanner_bp.route('/delete_host/<host_id>', methods=['DELETE'])
@admin_required
def delete_host(host_id):
    """
    Delete a specified host from the OpenVAS scanner.
    Requires admin authentication to execute.
    
    Args:
        host_id (str): The ID of the host to be deleted.
    
    Returns:
        JSON response with the result of the deletion.
    """
    try:
        result = scanner.delete_host(host_id=host_id)  # Attempt to delete the host by ID
        return jsonify(result), 200  # Return the result of the deletion
    except ValueError as e:
        return jsonify({"error": str(e)}), 500  # Return error if deletion fails


@scanner_bp.route('/convert_hosts_to_targets', methods=['POST'])
@admin_required
def convert_hosts_to_targets():
    """
    Convert a list of hosts into targets for the OpenVAS scanner.
    Requires admin authentication to execute.
    
    Expects JSON data with the following structure:
    {
        "hosts": [
            {"hostname": "example.com", "ip": "192.168.1.1"},
            ...
        ],
        "port_list_id": "some-port-list-id",
        "port_range": "1-1000"
    }
    
    Returns:
        JSON response containing the list of created targets.
    """
    data = request.json  # Retrieve JSON data from the request
    hosts = data.get('hosts', [])  # Extract the list of hosts
    port_list_id = data.get('port_list_id', None)  # Extract the port list ID
    port_range = data.get('port_range', None)  # Extract the port range

    created_targets = []  # Initialize a list to store created targets

    # Fetch existing targets
    existing_targets = scanner.get_targets()  # Retrieve existing targets from the OpenVAS
    existing_target_names = {target.findtext('name') for target in existing_targets}  # Create a set of existing target names

    for host in hosts:
        # Extract hostname and IP
        hostname = host.get('hostname')  # Get the hostname from the host data
        ip = host.get('ip')  # Get the IP address from the host data

        if not ip:
            return jsonify({"error": "IP address is required for each host"}), 400  # Return error if IP is missing

        # Use hostname if available, otherwise use IP as the target name
        target_name = hostname if hostname else ip

        # Skip creating the target if it already exists
        if target_name in existing_target_names:
            continue  # Skip to the next host if the target already exists

        try:
            # Create target with the extracted name and IP
            target_id = scanner.create_target(name=target_name, hosts=ip, port_list_id=port_list_id, port_range=port_range)
            created_targets.append({"target_name": target_name, "target_id": target_id})  # Add created target to the list
        except ValueError as e:
            # Return the detailed error message
            return jsonify({"error": str(e)}), 500  # Return error if target creation fails

    return jsonify({"created_targets": created_targets}), 201  # Return the list of created targets



@scanner_bp.route('/get_targets', methods=['GET'])
@token_required
def get_targets():
    """
    Retrieve a list of targets from the OpenVAS scanner.
    Requires user authentication via token.

    Returns:
        JSON response containing the list of targets.
    """
    try:
        targets = scanner.get_targets()  # Call the method to retrieve targets
        return jsonify(targets), 200  # Return the list of targets as JSON
    except ValueError as e:
        return jsonify({"error": str(e)}), 500  # Return error if retrieval fails


@scanner_bp.route('/create_target', methods=['POST'])
@admin_required
def create_target():
    """
    Create a new target in the OpenVAS scanner.
    Requires admin authentication to execute.
    
    Expects JSON data with the following structure:
    {
        "name": "target_name",
        "hosts": "host1, host2, ...",
        "port_range": "1-1000",
        "port_list_id": "some-port-list-id",
        "comment": "Optional comment"
    }

    Returns:
        JSON response containing the ID of the created target.
    """
    data = request.json  # Retrieve JSON data from the request
    name = data.get('name')  # Extract the target name
    hosts = data.get('hosts')  # Extract the hosts
    port_range = data.get('port_range')  # Extract the port range
    port_list_id = data.get('port_list_id')  # Extract the port list ID
    comment = data.get('comment')  # Extract the optional comment

    if not name or not hosts:
        return jsonify({"error": "Name and hosts are required."}), 400  # Return error if required fields are missing

    # Split hosts by comma and strip whitespace
    hosts_list = [host.strip() for host in hosts.split(',')] if isinstance(hosts, str) else hosts  # Prepare the hosts list

    try:
        # Create the target using the provided parameters
        target_id = scanner.create_target(name=name, hosts=hosts_list, port_range=port_range, port_list_id=port_list_id, comment=comment)
        return jsonify({"target_id": target_id}), 201  # Return the ID of the created target
    except ValueError as e:
        return jsonify({"error": str(e)}), 400  # Return error if creation fails




@scanner_bp.route('/delete_target/<target_id>', methods=['DELETE'])
@admin_required
def delete_target(target_id):
    """
    Delete a target from the OpenVAS scanner.
    Requires admin authentication to execute.

    Args:
        target_id (str): The ID of the target to be deleted.

    Returns:
        JSON response indicating the result of the deletion.
    """
    try:
        result = scanner.delete_target(target_id=target_id)  # Call the method to delete the target
        return jsonify(result), 200  # Return the result of the deletion
    except ValueError as e:
        return jsonify({"error": str(e)}), 500  # Return error if deletion fails


@scanner_bp.route('/modify_target/<string:target_id>', methods=['POST'])
@admin_required
def modify_target(target_id):
    """
    Modify an existing target in the OpenVAS scanner.
    Requires admin authentication to execute.

    Args:
        target_id (str): The ID of the target to be modified.

    Expects JSON data with the following structure:
    {
        "name": "new_target_name",
        "hosts": "new_host1, new_host2, ...",
        "exclude_hosts": "excluded_host1, excluded_host2, ...",
        "port_list_id": "new-port-list-id",
        "comment": "Optional comment"
    }

    Returns:
        JSON response containing the result of the modification.
    """
    data = request.json  # Retrieve JSON data from the request
    try:
        name = data.get('name')  # Extract the new target name
        hosts = data.get('hosts')  # Extract the new hosts
        exclude_hosts = data.get('exclude_hosts')  # Extract the excluded hosts
        port_list_id = data.get('port_list_id')  # Extract the new port list ID
        comment = data.get('comment')  # Extract the optional comment

        # Split hosts by comma and strip whitespace
        hosts_list = [host.strip() for host in hosts.split(',')] if isinstance(hosts, str) else hosts  # Prepare the hosts list

        # Call the method to modify the target with the provided parameters
        result = scanner.modify_target(
            target_id=target_id,
            name=name,
            hosts=hosts_list,
            exclude_hosts=exclude_hosts,
            port_list_id=port_list_id,
            comment=comment
        )

        return jsonify(result), 200  # Return the result of the modification

    except ValueError as e:
        return jsonify({"error": str(e)}), 500  # Return error if modification fails





@scanner_bp.route('/create_task', methods=['POST'])
@admin_required
def create_task():
    """
    Create a new task in the OpenVAS scanner.
    Requires admin authentication to execute.

    Expects JSON data with the following structure:
    {
        "name": "task_name",
        "target_id": "target_id",
        "config_id": "config_id",
        "scanner_id": "scanner_id",
        "schedule_id": "optional_schedule_id",
        "alert_ids": "optional_alert_ids"
    }

    Returns:
        JSON response containing the ID of the created task.
    """
    data = request.json  # Retrieve JSON data from the request
    name = data.get('name')  # Extract the task name
    target_id = data.get('target_id')  # Extract the target ID for the task
    config_id = data.get('config_id')  # Extract the configuration ID for the task
    scanner_id = data.get('scanner_id')  # Extract the scanner ID
    schedule_id = data.get('schedule_id', None)  # Extract the optional schedule ID
    alert_ids = data.get('alert_ids', None)  # Extract the optional alert IDs
    
    try:
        # Call the method to create the task with the provided parameters
        task_id = scanner.create_task(
            name=name,
            target_id=target_id,
            config_id=config_id,
            scanner_id=scanner_id,
            schedule_id=schedule_id,
            alert_ids=alert_ids
        )
        return jsonify({"task_id": task_id}), 201  # Return the ID of the created task
    except ValueError as e:
        return jsonify({"error": str(e)}), 500  # Return error if task creation fails


@scanner_bp.route('/start_task/<task_id>', methods=['POST'])
@admin_required
def start_task(task_id):    
    """Starts a task based on the provided task ID.

    Args:
        task_id (str): The ID of the task to start.

    Returns:
        JSON response: A success message with the response from starting the task, or an error message if a ValueError occurs.
    """
    try:
        response = scanner.start_task(task_id=task_id)
        return jsonify(response), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    

@scanner_bp.route('/stop_task/<task_id>', methods=['POST'])
@admin_required
def stop_task(task_id):    
    """Stops a task based on the provided task ID.

    Args:
        task_id (str): The ID of the task to stop.

    Returns:
        JSON response: A success message with the response from stopping the task, or an error message if a ValueError occurs.
    """
    try:
        response = scanner.stop_task(task_id=task_id)
        return jsonify(response), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    

@scanner_bp.route('/resume_task/<task_id>', methods=['POST'])
@admin_required
def resume_task(task_id):    
    """Resumes a task based on the provided task ID.

    Args:
        task_id (str): The ID of the task to resume.

    Returns:
        JSON response: A success message with the response from resuming the task, or an error message if a ValueError occurs.
    """
    try:
        response = scanner.resume_task(task_id=task_id)
        return jsonify(response), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500


@scanner_bp.route('/delete_task/<task_id>', methods=['DELETE'])
@admin_required
def delete_task(task_id):
    """Deletes a task based on the provided task ID.

    Args:
        task_id (str): The ID of the task to delete.

    Returns:
        JSON response: A success message with the result of the deletion, or an error message if a ValueError occurs (400) or any other unexpected error (500).
    """
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
    """Modifies a task based on the provided task ID and updates it with new data.

    Args:
        task_id (str): The ID of the task to modify.
        data (JSON): A JSON object containing the fields to update (name, config_id, scanner_id, schedule_id, alert_ids).

    Returns:
        JSON response: A success message with the result of the modification, or an error message if a ValueError occurs (500).
    """
    data = request.json
    name = data.get('name')
    config_id = data.get('config_id')
    scanner_id = data.get('scanner_id')
    schedule_id = data.get('schedule_id')
    alert_ids = data.get('alert_ids')
    
    try:
        result = scanner.modify_task(task_id=task_id, name=name, config_id=config_id, scanner_id=scanner_id, schedule_id=schedule_id, alert_ids=alert_ids)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500


@scanner_bp.route('/get_task/<task_id>', methods=['GET'])
@token_required
def get_task(task_id):
    """Retrieves information about a specific task based on the provided task ID.

    Args:
        task_id (str): The ID of the task to retrieve.

    Returns:
        JSON response: A success message with the task information, or an error message if task_id is not provided (400), a ValueError occurs (400), or any other unexpected error (500).
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
    """Retrieves the status of a specific task based on the provided task ID.

    Args:
        task_id (str): The ID of the task for which to retrieve the status.

    Returns:
        JSON response: A success message with the task status, or an error message if the task is not found (404) or if a ValueError occurs (500).
    """
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
    """Retrieves a list of all tasks.

    Returns:
        JSON response: A success message containing the list of tasks, or an error message if a ValueError occurs (500).
    """
    try:
        tasks = scanner.get_tasks()
        return jsonify({"tasks": tasks}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500


@scanner_bp.route('/get_results', methods=['POST'])
@token_required
def get_results():
    """Retrieves results for a specific task based on the provided task ID.

    Args:
        task_id (str): The ID of the task whose results are to be retrieved.

    Returns:
        JSON response: A success message containing the results for the specified task, or an error message if a ValueError occurs (500).
    """
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
    """Retrieves a list of all reports.

    Returns:
        JSON response: A success message containing the list of reports, or an error message if a ValueError occurs (500).
    """
    try:
        reports = scanner.get_reports()
        return jsonify({"reports": reports}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500



@scanner_bp.route('/get_report/<report_id>', methods=['GET'])
@token_required
def get_report(report_id):
    """Retrieves detailed information about a specific report based on the provided report ID.

    Args:
        report_id (str): The ID of the report to retrieve.

    Returns:
        JSON response: The report data if found, or an error message if the report cannot be found (404).
    """
    report_data = scanner.get_report_by_id(report_id)
    if "error" in report_data:
        return jsonify(report_data), 404
    return jsonify(report_data), 200


@scanner_bp.route('/get_reports_with_tasks', methods=['GET'])
@token_required
def get_reports_with_tasks():
    """Retrieves a list of reports along with their associated task details.

    Returns:
        JSON response: A success message containing the reports with tasks, or an error message if a ValueError occurs (500).
    """
    try:
        reports_with_tasks = scanner.get_reports_with_tasks()
        return jsonify({"reports": reports_with_tasks}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500


@scanner_bp.route('/delete_report/<report_id>', methods=['DELETE'])
@admin_required
def delete_report(report_id):
    """Deletes a specific report based on the provided report ID.

    Args:
        report_id (str): The ID of the report to delete.

    Returns:
        JSON response: A success message with the result of the deletion, or an error message if a ValueError occurs (400).
    """
    try:
        result = scanner.delete_report(report_id=report_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    

@scanner_bp.route('/export_report/<report_id>/<format>', methods=['GET'])
@token_required
def export_report(report_id, format):
    """Exports a specific report in the requested format (CSV, Excel, PDF).

    Args:
        report_id (str): The ID of the report to export.
        format (str): The format in which to export the report (csv, xlsx, pdf).

    Returns:
        Response: A file attachment of the exported report if successful, or an error message if the report cannot be found (404), unsupported format (400), or a ValueError occurs (500).
    """
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
    """Retrieves a list of schedules.

    Returns:
        JSON response: A success message containing the list of schedules, or an error message if a ValueError occurs (500).
    """
    try:
        schedules = scanner.get_schedules()
        # Process the schedules if needed. Assuming `schedules` is already in a dictionary format.
        return jsonify({"schedules": schedules}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500



@scanner_bp.route('/create_schedule', methods=['POST'])
@admin_required
def create_schedule():
    """Creates a new schedule based on the provided parameters.

    Expects a JSON payload with the following fields:
        - name (str): The name of the schedule.
        - dtstart (str): The start date and time in ISO 8601 format (YYYY-MM-DDTHH:MM:SS).
        - timezone (str, optional): The timezone for the schedule (default is 'UTC').
        - comment (str, optional): Additional comments for the schedule (default is an empty string).
        - frequency (str, optional): Frequency of the schedule (default is 'daily').
        - interval (int, optional): Interval for the frequency (default is 1).
        - count (int, optional): The number of occurrences for the schedule.

    Returns:
        JSON response: A success message containing the newly created schedule ID (201).
    """
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
    """Modifies an existing schedule based on the provided parameters.

    Expects a JSON payload with the following fields:
        - schedule_id (str): The ID of the schedule to modify.
        - name (str): The new name of the schedule.
        - dtstart (str): The new start date and time in ISO 8601 format (YYYY-MM-DDTHH:MM:SS).
        - timezone (str, optional): The new timezone for the schedule.
        - comment (str, optional): Updated comments for the schedule.
        - frequency (str, optional): Updated frequency of the schedule.
        - interval (int, optional): Updated interval for the frequency.
        - count (int, optional): The number of occurrences for the schedule.

    Returns:
        JSON response: A success message indicating the schedule was modified (200).
    """
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
    """Deletes a specified schedule.

    Expects the schedule_id as a URL parameter.

    Args:
        schedule_id (str): The ID of the schedule to be deleted.

    Returns:
        JSON response: The result of the deletion (200) or an error message (400) if the schedule cannot be found or deleted.
    """
    try:
        result = scanner.delete_schedule(schedule_id=schedule_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400



@scanner_bp.route('/create_alert', methods=['POST'])
@admin_required
def create_alert():
    """Creates a new alert based on the provided parameters.

    Expects the alert details as JSON in the request body.

    Returns:
        JSON response: Success message with alert ID (201) or an error message (500) if the creation fails.
    """
    try:
        data = request.json
        name = data.get('name')  # The name of the alert
        condition = data.get('condition')  # Condition for the alert
        event = data.get('event')  # Event that triggers the alert
        method = data.get('method')  # Method of notification
        condition_data = data.get('condition_data', {})  # Additional data for the condition
        event_data = data.get('event_data', {})  # Additional data for the event
        method_data = data.get('method_data', {})  # Additional data for the method
        filter_id = data.get('filter_id')  # Optional filter ID for the alert
        comment = data.get('comment')  # Optional comment for the alert

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
            "alert_id": alert_response.get('id')  # Return the ID of the created alert
        }), 201

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to create alert: {str(e)}"  # Return error message on failure
        }), 500

    

@scanner_bp.route('/get_alerts', methods=['GET'])
@token_required
def get_alerts():
    """Retrieves a list of alerts.

    Returns:
        JSON response: List of alerts (200) or error messages (400/500) in case of failure.
    """
    try:
        alerts = scanner.get_alerts()  # Fetch the alerts using the scanner's method
        return jsonify(alerts), 200  # Return the alerts with a 200 status
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400  # Handle value errors with a 400 status
    except Exception as e:
        return jsonify({"status": "error", "message": "An unexpected error occurred"}), 500  # Handle unexpected errors with a 500 status



@scanner_bp.route('/modify_alert', methods=['POST'])
@admin_required
def modify_alert():
    """Endpoint to modify an existing alert.

    Returns:
        JSON response: Details of the modified alert (200) or error messages (400/500) in case of failure.
    """
    data = request.json  # Get the JSON data from the request
    alert_id = data.get('alert_id')  # Retrieve alert_id from the request data
    if not alert_id:  # Check if alert_id is provided
        return jsonify({"status": "error", "message": "alert_id is required"}), 400  # Respond with an error if missing

    try:
        # Call the scanner's method to modify the alert with the provided data
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
        return jsonify(response), 200  # Return the modified alert details with a 200 status
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400  # Handle value errors with a 400 status
    except Exception as e:
        return jsonify({"status": "error", "message": "An unexpected error occurred"}), 500  # Handle unexpected errors with a 500 status


@scanner_bp.route('/delete_alert/<alert_id>', methods=['DELETE'])
@admin_required
def delete_alert(alert_id):
    """Endpoint to delete an alert.

    Args:
        alert_id (str): The ID of the alert to delete.

    Returns:
        JSON response: Status message indicating the result of the deletion (200) or error messages (400/500) in case of failure.
    """
    if not alert_id:  # Check if alert_id is provided
        return jsonify({"status": "error", "message": "alert_id is required"}), 400  # Respond with an error if missing

    try:
        # Call the scanner's method to delete the alert using the provided alert_id
        response = scanner.delete_alert(alert_id=alert_id)
        return jsonify(response), 200  # Return the response indicating successful deletion with a 200 status
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400  # Handle value errors with a 400 status
    except Exception as e:
        return jsonify({"status": "error", "message": "An unexpected error occurred"}), 500  # Handle unexpected errors with a 500 status

