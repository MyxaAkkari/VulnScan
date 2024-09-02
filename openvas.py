import re
from gvm.connections import UnixSocketConnection
from gvm.protocols.gmp import Gmp
from gvm.transforms import EtreeTransform
from lxml import etree
import csv
import xlsxwriter
from fpdf import FPDF


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

    def create_target(self, name, hosts, port_range=None, port_list_id=None):
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            
            # Create the target using the provided details
            response = gmp.create_target(name=name, hosts=[hosts], port_range=port_range, port_list_id=port_list_id)
            
            # Extract target ID from the response
            target_id_elements = response.xpath('@id')
            if not target_id_elements:
                # Check for detailed error information
                status = response.attrib.get('status')
                status_text = response.attrib.get('status_text')
                if status and status_text:
                    raise ValueError(f"Error {status}: {status_text}")
                else:
                    raise ValueError("Failed to retrieve target ID and no detailed error information available.")

            target_id = target_id_elements[0]
            return target_id




    def get_configs(self):
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            response = gmp.get_scan_configs()
            configs = response.xpath('.//config')
            if not configs:
                status = response.attrib.get('status')
                status_text = response.attrib.get('status_text')
                if status and status_text:
                    raise ValueError(f"Error {status}: {status_text}")
                else:
                    raise ValueError("Failed to retrieve scan configurations")
            return configs


    def get_hosts(self):
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            response = gmp.get_hosts(filter_string="rows=-1")
            if response.attrib.get('status') == '400':
                status = response.attrib.get('status')
                status_text = response.attrib.get('status_text')
                raise ValueError(f"Error {status}: {status_text}")
                
            hosts = []
            for asset in response.xpath('//asset'):
                host_data = {}
                for identifier in asset.xpath('identifiers/identifier'):
                    name = identifier.xpath('name/text()')[0] if identifier.xpath('name/text()') else None
                    value = identifier.xpath('value/text()')[0] if identifier.xpath('value/text()') else None
                    if name and value:
                        host_data[name] = value
                hosts.append(host_data)
            
            return hosts



    def get_scanners(self):
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            response = gmp.get_scanners()
            if response.attrib.get('status') == '400':
                status = response.attrib.get('status')
                status_text = response.attrib.get('status_text')
                raise ValueError(f"Error {status}: {status_text}")
            
            scanners = response.xpath('.//scanner')
            available_scanners = []
            for scanner in scanners:
                scanner_id = scanner.xpath('@id')[0]
                scanner_name = scanner.xpath('name/text()')[0]
                available_scanners.append((scanner_id, scanner_name))
            
            return available_scanners
        

    def get_portlists(self):
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            response = gmp.get_port_lists()
            if response.attrib.get('status') == '400':
                status = response.attrib.get('status')
                status_text = response.attrib.get('status_text')
                raise ValueError(f"Error {status}: {status_text}")
            
            portlists = response.xpath('.//port_list')
            portlist_data = []
            for portlist in portlists:
                portlist_entry = {
                    "id": portlist.xpath('@id')[0] if portlist.xpath('@id') else "N/A",
                    "name": portlist.xpath('name/text()')[0] if portlist.xpath('name/text()') else "N/A",
                    "comment": portlist.xpath('comment/text()')[0] if portlist.xpath('comment/text()') else "No comment"
                }
                portlist_data.append(portlist_entry)
            
            return portlist_data



    def create_task(self, name, target_id, config_id, scanner_id, schedule_id=None):
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            response = gmp.create_task(name=name, target_id=target_id, config_id=config_id, scanner_id=scanner_id, schedule_id=schedule_id)
            task_id = response.xpath('@id')
            if not task_id:
                status = response.attrib.get('status')
                status_text = response.attrib.get('status_text')
                if status and status_text:
                    raise ValueError(f"Error {status}: {status_text}")
                else:
                    raise ValueError("Failed to create task or retrieve task ID")
            return task_id[0]


    def start_task(self, task_id):
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            response = gmp.start_task(task_id=task_id)
            status = response.attrib.get('status') if response.attrib.get('status') else "unknown"
            status_text = response.attrib.get('status_text') if response.attrib.get('status_text') else "No message"
            return {
                "status": status,
                "status_text": status_text
            }



    def get_tasks(self):
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            response = gmp.get_tasks()
            if response.attrib.get('status') == '400':
                status = response.attrib.get('status')
                status_text = response.attrib.get('status_text')
                raise ValueError(f"Error {status}: {status_text}")
            
            tasks = response.xpath('.//task')
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
            status = response.attrib.get('status')
            status_text = response.attrib.get('status_text')
            status_elements = response.xpath('.//status/text()')
            progress = status_elements[0] if status_elements else "unknown"
            # raw_xml = etree.tostring(response, pretty_print=True).decode()
            # print("Raw XML Response:")
            # print(raw_xml)
            return {
                "status": status,
                "message": status_text,
                "progress": progress
            }


    def get_results(self, task_id):
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            response = gmp.get_results(task_id=task_id)
            if response.attrib.get('status') == '400':
                status = response.attrib.get('status')
                status_text = response.attrib.get('status_text')
                raise ValueError(f"Error {status}: {status_text}")
            
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

    def get_results(self, task_id):
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            response = gmp.get_results(task_id=task_id)
            if response.attrib.get('status') == '400':
                status = response.attrib.get('status')
                status_text = response.attrib.get('status_text')
                raise ValueError(f"Error {status}: {status_text}")
            
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
                status = response.attrib.get('status')
                status_text = response.attrib.get('status_text')
                raise ValueError(f"Error {status}: {status_text}")


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
    

    def create_schedule(self, name, icalendar_data, timezone='UTC', comment=None):
        """
        Create a new schedule in OpenVAS.

        :param name: The name of the schedule.
        :param icalendar_data: The iCalendar data for the schedule.
        :param timezone: The timezone for the schedule. Default is 'UTC'.
        :param comment: Optional comment for the schedule.
        :return: The ID of the created schedule.
        """
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)

            # Use GMP's create_schedule method
            response = gmp.create_schedule(
                name=name,
                icalendar=icalendar_data,
                timezone=timezone,
                comment=comment
            )
            
            # Extract the schedule ID from the response
            schedule_id = response.xpath('//create_schedule_response/@id')[0]
            
            return schedule_id


    def get_schedules(self, filter_string='rows=-1'):
        """
        Retrieve a list of all schedules from OpenVAS using GMP.

        :param filter_string: Optional filter string to customize the query.
                            Default is 'rows=-1', which retrieves all schedules.
        :return: A list of schedules, each represented as a dictionary.
        """
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            response = gmp.get_schedules(filter_string=filter_string)

            # Parse the response to extract schedule data
            schedules = []
            for schedule in response.xpath('//schedule'):
                schedule_data = {
                    'id': schedule.get('id'),
                    'name': schedule.findtext('name'),
                    'comment': schedule.findtext('comment'),
                    'timezone': schedule.findtext('timezone'),
                    'duration': schedule.findtext('duration'),
                    'period': schedule.findtext('period'),
                    'next_time': schedule.findtext('next_time'),
                    'last_time': schedule.findtext('last_time'),
                    'owner': schedule.findtext('owner'),
                    'creation_time': schedule.findtext('creation_time'),
                    'modification_time': schedule.findtext('modification_time'),
                }
                schedules.append(schedule_data)

            return schedules
