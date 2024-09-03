from flask import jsonify, request, Blueprint, send_file
from openvas import OpenVASScanner
from config import Config
from icalendar import Calendar, Event
from datetime import datetime
import pytz

scanner_bp = Blueprint('scanner_bp', __name__)
scanner = OpenVASScanner(socket_path = Config.OPENVAS_SOCKET_PATH, username = Config.OPENVAS_USERNAME, password = Config.OPENVAS_PASSWORD)

@scanner_bp.route('/authenticate', methods=['POST'])
def authenticate():
    try:
        scanner.authenticate()
        return jsonify({"message": "Authenticated successfully"}), 200
    except ValueError as e:
            # Return the detailed error message
            return jsonify({"error": str(e)}), 500

@scanner_bp.route('/get_scanners', methods=['GET'])
def get_scanners():
    try:
        scanners = scanner.get_scanners()
        return jsonify(scanners), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    

@scanner_bp.route('/get_configs', methods=['GET'])
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
def get_portlists():
    try:
        portlists = scanner.get_portlists()
        return jsonify({"portlists": portlists}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500


@scanner_bp.route('/get_hosts', methods=['GET'])
def get_hosts():
    try:
        hosts = scanner.get_hosts()
        return jsonify({"hosts": hosts}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500


@scanner_bp.route('/convert_hosts_to_targets', methods=['POST'])
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
def get_targets():
    try:
        targets = scanner.get_targets()
        return jsonify(targets), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500



@scanner_bp.route('/create_target', methods=['POST'])
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
def delete_target(target_id):
    try:
        result = scanner.delete_target(target_id=target_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500


@scanner_bp.route('/modify_target/<string:target_id>', methods=['POST'])
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
def create_task():
    data = request.json
    name = data.get('name')
    target_id = data.get('target_id')
    config_id = data.get('config_id')
    scanner_id = data.get('scanner_id')
    schedule_id = data.get('schedule_id', None)
    
    try:
        task_id = scanner.create_task(name=name, target_id=target_id, config_id=config_id, scanner_id=scanner_id, schedule_id = schedule_id)
        return jsonify({"task_id": task_id}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 500

@scanner_bp.route('/start_task', methods=['POST'])
def start_task():
    data = request.json
    task_id = data.get('task_id')
    
    try:
        response = scanner.start_task(task_id=task_id)
        return jsonify(response), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500

@scanner_bp.route('/delete_task/<task_id>', methods=['DELETE'])
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
def modify_task(task_id):
    data = request.json
    name = data.get('name')
    config_id = data.get('config_id')
    scanner_id = data.get('scanner_id')
    schedule_id = data.get('schedule_id')
    
    try:
        result = scanner.modify_task(task_id=task_id, name=name, config_id=config_id, scanner_id=scanner_id, schedule_id=schedule_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500



@scanner_bp.route('/get_task_status', methods=['POST'])
def get_task_status():
    data = request.json
    if not data or 'task_id' not in data:
        return jsonify({"error": "Missing or invalid 'task_id' in request body."}), 400

    task_id = data.get('task_id')

    try:
        response = scanner.get_task_status(task_id=task_id)
        if response is None:
            return jsonify({"error": "Task not found or no status available."}), 404
        return jsonify(response), 200
    except ValueError as e:
        return jsonify({"error": "Failed to retrieve task status.", "details": str(e)}), 500



@scanner_bp.route('/get_tasks', methods=['GET'])
def get_tasks():
    try:
        tasks = scanner.get_tasks()
        return jsonify({"tasks": tasks}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500



@scanner_bp.route('/get_results', methods=['POST'])
def get_results():
    data = request.json
    task_id = data.get('task_id')
    
    try:
        results = scanner.get_results(task_id=task_id)
        return jsonify({"results": results}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500


@scanner_bp.route('/get_reports', methods=['GET'])
def get_reports():
    try:
        reports = scanner.get_reports()
        return jsonify({"reports": reports}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500


@scanner_bp.route('/get_report/<report_id>', methods=['GET'])
def get_report(report_id):
    report_data = scanner.get_report_by_id(report_id)
    if "error" in report_data:
        return jsonify(report_data), 404
    return jsonify(report_data), 200


@scanner_bp.route('/delete_report/<report_id>', methods=['DELETE'])
def delete_report(report_id):
    try:
        result = scanner.delete_report(report_id=report_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    

@scanner_bp.route('/export_report/<report_id>/<format>', methods=['GET'])
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
def get_schedules():
    try:
        schedules = scanner.get_schedules()
        # Process the schedules if needed. Assuming `schedules` is already in a dictionary format.
        return jsonify({"schedules": schedules}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500


@scanner_bp.route('/create_schedule', methods=['POST'])
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
def delete_schedule(schedule_id):

    try:
        result = scanner.delete_schedule(schedule_id=schedule_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


