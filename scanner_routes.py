from flask import jsonify, request, Blueprint, send_file
from openvas import OpenVASScanner
from config import Config

scanner_bp = Blueprint('scanner_bp', __name__)
scanner = OpenVASScanner(socket_path = Config.OPENVAS_SOCKET_PATH, username = Config.OPENVAS_USERNAME, password = Config.OPENVAS_PASSWORD)

@scanner_bp.route('/authenticate', methods=['POST'])
def authenticate():
    try:
        scanner.authenticate()
        return jsonify({"message": "Authenticated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@scanner_bp.route('/list_scanners', methods=['GET'])
def list_scanners():
    try:
        scanners = scanner.list_scanners()
        return jsonify(scanners), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@scanner_bp.route('/list_configs', methods=['GET'])
def list_configs():
    try:
        configs = scanner.get_configs()
        config_list = []
        for config in configs:
            config_id = config.xpath('@id')[0]
            config_name = config.xpath('name/text()')[0]
            config_list.append({"config_id": config_id, "config_name": config_name})
        return jsonify(config_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@scanner_bp.route('/list_targets', methods=['GET'])
def list_targets():
    try:
        targets = scanner.get_targets()
        target_list = []
        for target in targets:
            target_id = target.xpath('@id')[0]
            target_name = target.xpath('name/text()')[0]
            target_list.append({"target_id": target_id, "target_name": target_name})
        return jsonify(target_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@scanner_bp.route('/get_filters', methods=['GET'])
def get_filters():
    try:
        filters = scanner.get_filters()
        return jsonify({"filters": filters}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@scanner_bp.route('/get_portlists', methods=['GET'])
def get_portlists():
    try:
        portlists = scanner.get_portlists()
        return jsonify({"portlists": portlists}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@scanner_bp.route('/hosts', methods=['GET'])
def get_hosts():
    try:
        hosts = scanner.get_hosts()
        return jsonify({"hosts": hosts}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@scanner_bp.route('/convert_hosts_to_targets', methods=['POST'])
def convert_hosts_to_targets():
    data = request.json
    hosts = data.get('hosts', [])
    port_list_id = data.get('port_list_id', None)
    port_range = data.get('port_range', None)
    
    created_targets = []

    for host in hosts:
        # Extract hostname and IP
        hostname = host.get('hostname')
        ip = host.get('ip')

        if not ip:
            return jsonify({"error": "IP address is required for each host"}), 400

        # Use hostname if available, otherwise use IP as the target name
        target_name = hostname if hostname else ip

        try:
            # Create target with the extracted name and IP
            target_id = scanner.create_target(name=target_name, hosts=ip, port_list_id=port_list_id, port_range=port_range)
            created_targets.append({"target_name": target_name, "target_id": target_id})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"created_targets": created_targets}), 201



@scanner_bp.route('/discover_hosts', methods=['POST'])
def discover_hosts():
    data = request.json
    network = data.get('network', '192.168.14.0/24')  # Default to a common local network range
    port_list_id= data.get('port_list_id')
    # You can use the known Host Discovery config ID directly
    host_discovery_config_id = '2d3f051c-55ba-11e3-bf43-406186ea4fc5'
    
    try:
        # Create a target for the network/subnet
        target_id = scanner.create_target(name="Host Discovery Target", hosts=[network], port_list_id=port_list_id)
        
        # Fetch the list of available scanners
        scanners = scanner.list_scanners()
        chosen_scanner_id = scanners[1][0]  # Select the first available scanner, or prompt the user to choose
        
        # Create a task for host discovery
        task_id = scanner.create_task(name="Host Discovery Task", target_id=target_id, config_id=host_discovery_config_id, scanner_id=chosen_scanner_id)
        
        # Start the host discovery task
        response = scanner.start_task(task_id=task_id)
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@scanner_bp.route('/create_target', methods=['POST'])
def create_target():
    data = request.json
    name = data.get('name')
    hosts = data.get('hosts')
    port_range = data.get('port_range')
    port_list_id = data.get('port_list_id')
    
    try:
        target_id = scanner.create_target(name=name, hosts=hosts, port_range=port_range, port_list_id=port_list_id)
        return jsonify({"target_id": target_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@scanner_bp.route('/create_task', methods=['POST'])
def create_task():
    data = request.json
    name = data.get('name')
    target_id = data.get('target_id')
    config_id = data.get('config_id')
    scanner_id = data.get('scanner_id')
    
    try:
        task_id = scanner.create_task(name=name, target_id=target_id, config_id=config_id, scanner_id=scanner_id)
        return jsonify({"task_id": task_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@scanner_bp.route('/start_task', methods=['POST'])
def start_task():
    data = request.json
    task_id = data.get('task_id')
    
    try:
        response = scanner.start_task(task_id=task_id)
        return jsonify(response), 200
    except Exception as e:
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
    except Exception as e:
        return jsonify({"error": "Failed to retrieve task status.", "details": str(e)}), 500



@scanner_bp.route('/get_tasks', methods=['GET'])
def get_tasks():
    try:
        tasks = scanner.get_tasks()
        return jsonify({"tasks": tasks}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@scanner_bp.route('/get_results', methods=['POST'])
def get_results():
    data = request.json
    task_id = data.get('task_id')
    
    try:
        results = scanner.get_results(task_id=task_id)
        return jsonify({"results": results}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@scanner_bp.route('/get_reports', methods=['GET'])
def get_reports():
    try:
        reports = scanner.get_reports()
        return jsonify({"reports": reports}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@scanner_bp.route('/get_report/<report_id>', methods=['GET'])
def get_report(report_id):
    report_data = scanner.get_report_by_id(report_id)
    if "error" in report_data:
        return jsonify(report_data), 404
    return jsonify(report_data), 200


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

    except Exception as e:
        return jsonify({"error": str(e)}), 500


