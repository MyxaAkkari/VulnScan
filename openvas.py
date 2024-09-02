import re
from gvm.connections import UnixSocketConnection
from gvm.protocols.gmp import Gmp
from gvm.transforms import EtreeTransform
from lxml import etree
import csv
import xlsxwriter
from fpdf import FPDF
from config import Config

class OpenVASScanner:
    def __init__(self, socket_path, username, password):
        self.socket_path = socket_path
        self.username = username
        self.password = password
        self.connection = UnixSocketConnection(path=self.socket_path)
        self.transform = EtreeTransform()

    def _connect(self):
        return Gmp(connection=self.connection, transform=self.transform)

    def authenticate(self):
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            print("Authenticated successfully")

    def create_target(self, name, hosts, port_range= None, port_list_id = None):
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            # Use the library methods to create a target
            response = gmp.create_target(name=name, hosts=[hosts], port_range=port_range, port_list_id= port_list_id)
            
            # Print the full response to understand its structure
            # print("Create Target Response:")
            # print(dir(response))

            # Check for errors or messages in the response
            if response.xpath('//status/text()'):
                status = response.xpath('//status/text()')[0]
                print(f"Response Status: {status}")
            if response.xpath('//message/text()'):
                message = response.xpath('//message/text()')[0]
                print(f"Response Message: {message}")

            # Extract the target ID from the response
            target_id_elements = response.xpath('@id')
            if not target_id_elements:
                raise ValueError("Failed to retrieve target ID")

            target_id = target_id_elements[0]
            print(f"Target created with ID: {target_id}")
            return target_id

    def get_targets(self):
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)

            # Set a filter with a large number for rows to ensure all targets are retrieved
            response = gmp.get_targets(filter_string='rows=-1')  # '-1' should retrieve all rows

            # Parse the targets from the response
            targets = response.xpath('.//target')
            return targets


    def get_configs(self):
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            response = gmp.get_scan_configs()
            configs = response.xpath('.//config')
            return configs

    def get_filters(self):
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            response = gmp.get_filters()
            raw_xml = etree.tostring(response, pretty_print=True).decode()
            return raw_xml

    def get_hosts(self):
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            
            # Get the list of hosts
            response = gmp.get_hosts()
            
            # Convert the raw response to a string and print it
            # raw_xml = etree.tostring(response, pretty_print=True).decode()
            # print("Raw XML Response:")
            # print(raw_xml)
            
            # Process the XML to extract hosts data
            hosts = []
            for asset in response.xpath('//asset'):
                host_data = {}
                
                # Extract identifiers
                for identifier in asset.xpath('identifiers/identifier'):
                    name = identifier.xpath('name/text()')[0] if identifier.xpath('name/text()') else None
                    value = identifier.xpath('value/text()')[0] if identifier.xpath('value/text()') else None
                    if name and value:
                        host_data[name] = value
                
                hosts.append(host_data)
            
            return hosts



    def list_scanners(self):
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            response = gmp.get_scanners()
            scanners = response.xpath('.//scanner')
            
            available_scanners = []
            for scanner in scanners:
                scanner_id = scanner.xpath('@id')[0]
                scanner_name = scanner.xpath('name/text()')[0]
                # print(f"Scanner ID: {scanner_id}, Name: {scanner_name}")
                available_scanners.append((scanner_id, scanner_name))
            
            return available_scanners
        

    def get_portlists(self):
            with self._connect() as gmp:
                gmp.authenticate(self.username, self.password)
                response = gmp.get_port_lists()  # Use the method to get port lists
                
                portlists = response.xpath('.//port_list')  # Extract port list elements
                portlist_data = []
                
                for portlist in portlists:
                    portlist_entry = {
                        "id": portlist.xpath('@id')[0] if portlist.xpath('@id') else "N/A",
                        "name": portlist.xpath('name/text()')[0] if portlist.xpath('name/text()') else "N/A",
                        "comment": portlist.xpath('comment/text()')[0] if portlist.xpath('comment/text()') else "No comment"
                    }
                    portlist_data.append(portlist_entry)
                
                return portlist_data



    def create_task(self, name, target_id, config_id, scanner_id):
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            
            # Create the task with the selected scanner ID
            response = gmp.create_task(name=name, target_id=target_id, config_id=config_id, scanner_id=scanner_id)
            task_id = response.xpath('@id')
            if not task_id:
                raise ValueError("Failed to create task or retrieve task ID")
            # print(f"Task created with ID: {task_id[0]}")
            return task_id[0]


    def start_task(self, task_id):
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            response = gmp.start_task(task_id=task_id)
            
            # Extract the status and any other relevant information
            status = response.xpath('.//status/text()')[0] if response.xpath('.//status/text()') else "unknown"
            message = response.xpath('.//message/text()')[0] if response.xpath('.//message/text()') else "No message"
            
            # Return as a dictionary
            return {
                "status": status,
                "message": message
            }



    def get_tasks(self):
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            response = gmp.get_tasks()  # Fetch the tasks from OpenVAS
            
            tasks = response.xpath('.//task')  # Extract task elements
            task_list = []
            
            for task in tasks:
                task_entry = {
                    "id": task.xpath('@id')[0] if task.xpath('@id') else "N/A",
                    "name": task.xpath('name/text()')[0] if task.xpath('name/text()') else "N/A",
                    "status": task.xpath('status/text()')[0] if task.xpath('status/text()') else "N/A"
                }
                task_list.append(task_entry)
            
            return task_list


    def get_task_status(self, task_id):
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            response = gmp.get_task(task_id=task_id)
            
            # Extract the status, handle cases where the element might not be present
            status_elements = response.xpath('.//status/text()')
            status = status_elements[0] if status_elements else "unknown"
            
            message_elements = response.xpath('.//message/text()')
            message = message_elements[0] if message_elements else "No message"
            # raw_xml = etree.tostring(response, pretty_print=True).decode()
            # print("Raw XML Response:")
            # print(raw_xml)
            # Return as a dictionary
            return {
                "status": status,
                "message": message
            }


    def get_results(self, task_id):
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            response = gmp.get_results(task_id=task_id)
            
            results = response.xpath('.//result')
            result_list = []
            
            for result in results:
                result_entry = {
                    "id": result.xpath('@id')[0] if result.xpath('@id') else "N/A",
                    "name": result.xpath('name/text()')[0] if result.xpath('name/text()') else "N/A",
                    "description": result.xpath('description/text()')[0] if result.xpath('description/text()') else "N/A",
                    "severity": result.xpath('severity/text()')[0] if result.xpath('severity/text()') else "N/A"
                }
                result_list.append(result_entry)
            
            return result_list

    def get_reports(self):
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            response = gmp.get_reports()  # Fetch the reports
            reports = response.xpath('.//report')  # Extract report elements
            report_list = []
            
            for report in reports:
                report_entry = {
                    "id": report.xpath('@id')[0] if report.xpath('@id') else "N/A",
                    "name": report.xpath('name/text()')[0] if report.xpath('name/text()') else "N/A",
                    "status": report.xpath('status/text()')[0] if report.xpath('status/text()') else "N/A"
                }
                report_list.append(report_entry)
            
            return report_list

    def get_report_by_id(self, report_id):
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            
            # Fetch the specific report
            response = gmp.get_report(report_id=report_id)
            
            # Print the full response to understand its structure
            # print("Full Report Response:")
            # print(etree.tostring(response, pretty_print=True).decode())
            
            # Parse XML response
            root = etree.fromstring(etree.tostring(response))
            
            # Extract report data
            report_element = root.find('.//report[@id="' + report_id + '"]')
            if report_element is not None:
                # Extract task ID from the parent or related elements
                task_id_element = root.find('.//task')
                task_id = task_id_element.get('id') if task_id_element is not None else "N/A"
                
                report_data = {
                    "id": report_id,
                    "name": report_element.findtext('name', default=""),
                    "creation_time": report_element.findtext('creation_time', default=""),
                    "modification_time": report_element.findtext('modification_time', default=""),
                    "scan_run_status": report_element.findtext('scan_run_status', default=""),
                    "vulns_count": report_element.find('.//vulns/count').text if report_element.find('.//vulns/count') is not None else "0",
                    "task_id": task_id,
                    "results": []
                }
                
                # Extract results
                results_elements = report_element.findall('.//results/result')
                for result in results_elements:
                    description = result.findtext('description', default="")
                    cve_numbers = re.findall(r'CVE-\d{4}-\d+', description)
                    
                    # Extract port from <details> if available
                    port = "N/A"
                    details_elements = result.find('.//details')
                    if details_elements is not None:
                        for detail in details_elements.findall('.//detail'):
                            name = detail.findtext('name', default="")
                            if name == "location":
                                port = detail.findtext('value', default="").split('/')[0]
                                break
                    
                    result_data = {
                        "id": result.get('id'),
                        "host": result.findtext('host', default=""),
                        "port": port,
                        "description": description,
                        "cve_numbers": cve_numbers,
                        "severity": result.findtext('severity', default=""),
                        "threat": result.findtext('threat', default=""),
                    }
                    report_data["results"].append(result_data)
                
                # Return formatted report data
                return report_data
            else:
                return {"error": "Report not found"}


    def export_report_to_csv(self, report_data, filename):
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = ['id', 'host', 'port', 'description', 'cve_numbers', 'severity', 'threat']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for result in report_data['results']:
                    writer.writerow(result)
            return filename

    def export_report_to_excel(self, report_data, filename):
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet()

        # Add headers
        headers = ['ID', 'Host', 'Port', 'Description', 'CVE Numbers', 'Severity', 'Threat']
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header)

        # Add data rows
        for row_num, result in enumerate(report_data['results'], 1):
            worksheet.write(row_num, 0, result['id'])
            worksheet.write(row_num, 1, result['host'])
            worksheet.write(row_num, 2, result['port'])
            worksheet.write(row_num, 3, result['description'])
            worksheet.write(row_num, 4, ', '.join(result['cve_numbers']))
            worksheet.write(row_num, 5, result['severity'])
            worksheet.write(row_num, 6, result['threat'])

        workbook.close()
        return filename

    def export_report_to_pdf(self, report_data, filename):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Add title
        pdf.cell(200, 10, txt="Scan Report", ln=True, align='C')

        # Add report details
        for result in report_data['results']:
            pdf.cell(200, 10, txt=f"ID: {result['id']}", ln=True)
            pdf.cell(200, 10, txt=f"Host: {result['host']}", ln=True)
            pdf.cell(200, 10, txt=f"Port: {result['port']}", ln=True)
            pdf.cell(200, 10, txt=f"Description: {result['description']}", ln=True)
            pdf.cell(200, 10, txt=f"CVE Numbers: {', '.join(result['cve_numbers'])}", ln=True)
            pdf.cell(200, 10, txt=f"Severity: {result['severity']}", ln=True)
            pdf.cell(200, 10, txt=f"Threat: {result['threat']}", ln=True)
            pdf.cell(200, 10, txt=" ", ln=True)  # Add empty line between results

        pdf.output(filename)
        return filename


# Example usage
# if __name__ == "__main__":
#     scanner = OpenVASScanner(socket_path="/var/run/gvmd/gvmd.sock", username="admin", password="admin123")
#     scanner.authenticate()
#     scanners = scanner.list_scanners()

#     # Assume the user chooses the first scanner
#     chosen_scanner_id = scanners[1][0]  # The user can choose a different scanner here

#     target_id = scanner.create_target(name="DNS_server", hosts=["192.168.1.84"], port_range="T:1-65535")
#     configs = scanner.get_configs()
#     config_id = configs[0].xpath('@id')[0]  # Use the first config ID for simplicity
#     task_id = scanner.create_task(name="My Scan Task", target_id=target_id, config_id=config_id, scanner_id=chosen_scanner_id)
#     scanner.start_task(task_id=task_id)
#     scanner.get_task_status(task_id=task_id)
#     results = scanner.get_results(task_id=task_id)
