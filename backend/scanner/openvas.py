import re
from typing import Optional
from gvm.connections import UnixSocketConnection
from gvm.protocols.gmp import Gmp
from gvm.transforms import EtreeTransform
from icalendar import Calendar
from lxml import etree
import csv
import xlsxwriter
from fpdf import FPDF
from cachetools import cached, TTLCache

# Create a cache with a time-to-live (TTL) of 10 minutes
# maxsize of 100 means the cache will store up to 100 entries
# before evicting the least recently used ones.
cache = TTLCache(maxsize=100, ttl=600)

class OpenVASScanner:
    """
    A class for interfacing with the OpenVAS vulnerability scanner through 
    Unix socket connections. Handles authentication and interaction with 
    the OpenVAS GVM protocol (GMP) using XML transformations.

    Attributes:
        socket_path (str): The path to the Unix socket for OpenVAS.
        username (str): The username to authenticate with.
        password (str): The password to authenticate with.
        connection (UnixSocketConnection): Connection object to communicate with OpenVAS.
        transform (EtreeTransform): XML transformation object for converting responses.
    """

    def __init__(self, socket_path: str, username: str, password: str):
        """
        Initializes the OpenVASScanner object with connection details.

        Args:
            socket_path (str): The path to the Unix socket for OpenVAS communication.
            username (str): Username for authentication with OpenVAS.
            password (str): Password for authentication with OpenVAS.
        """
        self.socket_path = socket_path
        self.username = username
        self.password = password
        # Set up the Unix socket connection to OpenVAS
        self.connection = UnixSocketConnection(path=self.socket_path)
        # EtreeTransform is used to handle the XML responses from GMP
        self.transform = EtreeTransform()

    def _connect(self) -> Gmp:
        """
        Establishes a connection to the OpenVAS GMP service.
        
        Returns:
            Gmp: The GMP (Greenbone Management Protocol) connection object.
        """
        return Gmp(connection=self.connection, transform=self.transform)

    def authenticate(self):
        """
        Authenticates the user with OpenVAS using the provided credentials.
        """
        with self._connect() as gmp:
            # Authenticate with the provided username and password
            gmp.authenticate(self.username, self.password)
            print("Authenticated successfully")




    def get_roles(self):
        """
        Retrieve a list of all roles from OpenVAS.

        :return: A list of dictionaries, each representing a role. Each dictionary contains:
                - id (str): The unique identifier of the role.
                - name (str): The name of the role.
                - description (str): A brief description of the role.
                - permissions (list): A list of permissions associated with the role.
                - creation_time (str): The time when the role was created.
                - modification_time (str): The time when the role was last modified.
        :raises: ValueError if the request fails with an error.
        """
        with self._connect() as gmp:
            # Authenticate the connection with the stored username and password
            gmp.authenticate(self.username, self.password)
            
            # Fetch the list of roles, using the filter "rows=-1" to get all roles
            response = gmp.get_roles(filter_string="rows=-1")
            
            # Handle response based on the status code
            if response.attrib.get('status') == '200':
                # Parse the XML response into an ElementTree object
                root = etree.fromstring(etree.tostring(response))
                
                # Initialize an empty list to store role data
                roles = []
                
                # Iterate through all <role> elements in the response
                for role_element in root.findall('.//role'):
                    # Extract role information such as id, name, description, permissions, etc.
                    role_data = {
                        "id": role_element.get('id'),  # Extract the role ID attribute
                        "name": role_element.findtext('name', default=""),  # Get the role's name
                        "description": role_element.findtext('description', default=""),  # Get the description
                        "permissions": role_element.findtext('permissions', default="").split(','),  # Permissions as a list
                        "creation_time": role_element.findtext('creation_time', default=""),  # Role creation time
                        "modification_time": role_element.findtext('modification_time', default=""),  # Last modification time
                    }
                    roles.append(role_data)  # Add the role data to the list
                
                return roles  # Return the list of roles
            else:
                # If the status is not '200', raise an error with the status and status_text
                status = response.attrib.get('status')
                status_text = response.attrib.get('status_text')
                raise ValueError(f"Error {status}: {status_text}")



    def get_users(self):
        """
        Retrieve a list of all users from OpenVAS, including their roles.

        :return: A list of dictionaries, each representing a user and their associated roles.
        """
        with self._connect() as gmp:
            # Authenticate with OpenVAS
            gmp.authenticate(self.username, self.password)
            
            # Fetch the list of users with no row limit
            response = gmp.get_users(filter_string="rows=-1")

            # Uncomment the following lines to debug and inspect the raw XML response
            # print("Full Users Response:")
            # print(etree.tostring(response, pretty_print=True).decode())

            # Check if the response status is successful (status 200)
            if response.attrib.get('status') == '200':
                # Parse the XML response
                root = etree.fromstring(etree.tostring(response))

                # List to hold user data
                users = []
                
                # Iterate through all user elements in the XML
                for user_element in root.findall('.//user'):
                    user_id = user_element.get('id')  # Extract user ID
                    user_name = user_element.findtext('name', default="")  # Extract username
                    creation_time = user_element.findtext('creation_time', default="")  # Extract creation time
                    modification_time = user_element.findtext('modification_time', default="")  # Extract modification time
                    
                    # Extract roles associated with the user
                    roles = user_element.findall('.//role')
                    user_roles = [
                        {
                            "id": role.get('id'),  # Extract role ID
                            "name": role.findtext('name', default="")  # Extract role name
                        }
                        for role in roles
                    ]

                    # Structure the user data in a dictionary
                    user_data = {
                        "id": user_id,
                        "name": user_name,
                        "creation_time": creation_time,
                        "modification_time": modification_time,
                        "roles": user_roles  # Include the roles of the user
                    }
                    
                    # Append the user data to the list of users
                    users.append(user_data)

                # Return the list of users and their roles
                return users
            else:
                # Raise an error if the response status is not successful
                status = response.attrib.get('status')
                status_text = response.attrib.get('status_text')
                raise ValueError(f"Error {status}: {status_text}")


    def get_user(self, user_id):
        """
        Retrieve a specific user by ID from OpenVAS.

        :param user_id: ID of the user to retrieve.
        :return: A dictionary containing the user's details and associated roles.
        """
        with self._connect() as gmp:
            # Authenticate with OpenVAS
            gmp.authenticate(self.username, self.password)

            # Fetch the user data for the specified user ID
            response = gmp.get_user(user_id=user_id)

            # Parse the XML response
            root = etree.fromstring(etree.tostring(response))

            # Locate the user element with the matching user ID
            user_element = root.find('.//user[@id="' + user_id + '"]')

            # If the user is found, extract the relevant details
            if user_element is not None:
                user_data = {
                    "id": user_element.get('id'),  # Extract user ID
                    "name": user_element.findtext('name', default=""),  # Extract username
                    "creation_time": user_element.findtext('creation_time', default=""),  # Extract creation time
                    "modification_time": user_element.findtext('modification_time', default=""),  # Extract modification time
                    "roles": []  # Initialize roles list
                }

                # Extract roles associated with the user
                roles_elements = user_element.findall('.//role')
                for role in roles_elements:
                    role_data = {
                        "id": role.get('id'),  # Extract role ID
                        "name": role.findtext('name', default="")  # Extract role name
                    }
                    user_data["roles"].append(role_data)  # Append the role to the roles list

                # Return the structured user data
                return user_data
            else:
                # Raise an error if the user element is not found
                status = response.attrib.get('status')
                status_text = response.attrib.get('status_text')
                raise ValueError(f"Error {status}: {status_text}")




    def create_user(self, name, password, role_ids=None):
        """
        Create a new user in OpenVAS.

        :param name: The username for the new user.
        :param password: The password for the new user.
        :param role_ids: A list of role IDs to assign to the user (optional).
        :return: A dictionary with the result of the creation.
        """
        with self._connect() as gmp:
            # Authenticate with OpenVAS
            gmp.authenticate(self.username, self.password)

            # Create the user with the provided name, password, and optional role IDs
            response = gmp.create_user(name=name, password=password, role_ids=role_ids or [])

            # Check if the user creation was successful (status 201)
            if response.attrib.get('status') == '201':
                return {"status": "success", "message": "User created successfully"}  # Return success message
            else:
                # Handle failure cases by raising an error with the status and status text
                status = response.attrib.get('status')
                status_text = response.attrib.get('status_text')
                raise ValueError(f"Error {status}: {status_text}")


    def modify_user(self, user_id, new_username=None, new_password=None, new_roles=None):
        """
        Modify an existing user in OpenVAS.

        :param user_id: The ID of the user to modify.
        :param new_username: The new username for the user (optional).
        :param new_password: The new password for the user (optional).
        :param new_roles: A list of new role IDs to assign to the user (optional).
        :return: A dictionary with the result of the modification.
        """
        with self._connect() as gmp:
            # Authenticate with OpenVAS
            gmp.authenticate(self.username, self.password)

            # Modify the user with the provided user ID, new username, new password, and optional new roles
            response = gmp.modify_user(user_id=user_id, name=new_username, password=new_password, role_ids=new_roles or [])

            # Check if the user modification was successful (status 200)
            if response.attrib.get('status') == '200':
                return {"status": "success", "message": "User modified successfully"}  # Return success message
            else:
                # Handle failure cases by raising an error with the status and status text
                status = response.attrib.get('status')
                status_text = response.attrib.get('status_text')
                raise ValueError(f"Error {status}: {status_text}")



    def delete_user(self, user_id):
        """
        Delete a user from OpenVAS.

        :param user_id: The ID of the user to delete.
        :return: A dictionary with the result of the deletion.
        """
        with self._connect() as gmp:
            # Authenticate with OpenVAS
            gmp.authenticate(self.username, self.password)

            # Attempt to delete the user with the specified user ID
            response = gmp.delete_user(user_id=user_id)

            # Check if the deletion was successful (status 200)
            if response.attrib.get('status') == '200':
                return {"status": "success", "message": "User deleted successfully"}  # Return success message
            else:
                # Handle failure cases by raising an error with the status and status text
                status = response.attrib.get('status')
                status_text = response.attrib.get('status_text')
                raise ValueError(f"Error {status}: {status_text}")



    def clone_user(self, user_id, name=None, comment=None, roles=None):
        """
        Clone an existing user in OpenVAS.

        :param user_id: The ID of the user to clone.
        :param name: Optional; the name for the cloned user. If not provided, a default name will be generated.
        :param comment: Optional; a comment for the cloned user. If not provided, the original user's comment will be used.
        :param roles: Optional; a list of roles to assign to the cloned user.
        :return: A dictionary indicating the success of the cloning operation, along with the name and comment of the cloned user.
        """
        with self._connect() as gmp:
            # Authenticate with OpenVAS
            gmp.authenticate(self.username, self.password)
            
            # Fetch the original user by ID
            original_user_response = gmp.get_users(filter_string=f"id={user_id}")
            original_user = original_user_response.find('.//user')
            
            if original_user is None:
                raise ValueError("User not found.")  # Raise error if the user doesn't exist
            
            # Prepare parameters for the cloned user
            clone_name = name if name is not None else f"{original_user.findtext('name')}_clone"  # Set clone name
            clone_comment = comment if comment is not None else original_user.findtext('comment', default="")  # Set clone comment
            
            # Clone the user by creating a new user with the specified parameters
            gmp.create_user(name=clone_name, comment=clone_comment, roles=roles or [])
            
            return {"status": "User cloned successfully", "name": clone_name, "comment": clone_comment}  # Return success message and details




    def get_configs(self):
        """
        Retrieve a list of all scan configurations from OpenVAS.

        :return: A list of scan configuration elements.
        :raises ValueError: If the scan configurations cannot be retrieved.
        """
        with self._connect() as gmp:
            # Authenticate with OpenVAS
            gmp.authenticate(self.username, self.password)

            # Fetch the scan configurations
            response = gmp.get_scan_configs()
            configs = response.xpath('.//config')  # Extract all config elements
            
            # Check if configs were retrieved
            if not configs:
                status = response.attrib.get('status')
                status_text = response.attrib.get('status_text')
                if status and status_text:
                    raise ValueError(f"Error {status}: {status_text}")  # Raise error with status details
                else:
                    raise ValueError("Failed to retrieve scan configurations")  # Raise error if no status available
            
            return configs  # Return the list of configurations


    def get_hosts(self):
        """
        Retrieve a list of all hosts from OpenVAS.

        :return: A list of dictionaries containing host details.
        :raises ValueError: If the host retrieval fails.
        """
        with self._connect() as gmp:
            # Authenticate with OpenVAS
            gmp.authenticate(self.username, self.password)

            # Fetch the list of hosts
            response = gmp.get_hosts(filter_string="rows=-1")
            
            # Check for errors in the response
            if response.attrib.get('status') == '400':
                status = response.attrib.get('status')
                status_text = response.attrib.get('status_text')
                raise ValueError(f"Error {status}: {status_text}")  # Raise error with status details

            # Extract host data
            hosts = []
            for asset in response.xpath('//asset'):
                host_data = {
                    'id': asset.attrib.get('id')  # Extract the host's ID
                }
                for identifier in asset.xpath('identifiers/identifier'):
                    name = identifier.xpath('name/text()')[0] if identifier.xpath('name/text()') else None
                    value = identifier.xpath('value/text()')[0] if identifier.xpath('value/text()') else None
                    if name and value:
                        host_data[name] = value  # Store host details
                hosts.append(host_data)  # Add the host data to the list
            
            return hosts  # Return the list of hosts


    def delete_host(self, host_id):
        """
        Delete a host from OpenVAS.

        :param host_id: The ID of the host to delete.
        :return: A message indicating the deletion status.
        :raises ValueError: If the host deletion fails or an unexpected error occurs.
        """
        with self._connect() as gmp:
            # Authenticate with OpenVAS
            gmp.authenticate(self.username, self.password)
            
            try:
                # Attempt to delete the host
                response = gmp.delete_host(host_id=host_id)

                # Check if the response contains the status
                status = response.attrib.get('status')
                status_text = response.attrib.get('status_text')
                if status != '200':
                    raise ValueError(f"Error {status}: {status_text}")  # Raise error for non-success status

                return {"message": "Host deleted successfully"}  # Return success message
            
            except Exception as e:
                # Handle unexpected exceptions
                status = response.attrib.get('status') if response.attrib else "unknown"
                status_text = response.attrib.get('status_text') if response.attrib else str(e)
                raise ValueError(f"Error {status}: {status_text}")  # Raise error with details


    def get_scanners(self):
        """
        Retrieve a list of available scanners from OpenVAS.

        :return: A list of tuples containing scanner IDs and names.
        :raises ValueError: If the retrieval of scanners fails.
        """
        with self._connect() as gmp:
            # Authenticate with OpenVAS
            gmp.authenticate(self.username, self.password)

            # Fetch the list of scanners
            response = gmp.get_scanners()
            
            # Check for errors in the response
            if response.attrib.get('status') == '400':
                status = response.attrib.get('status')
                status_text = response.attrib.get('status_text')
                raise ValueError(f"Error {status}: {status_text}")  # Raise error for non-success status
            
            # Extract scanner data
            scanners = response.xpath('.//scanner')
            available_scanners = []
            for scanner in scanners:
                scanner_id = scanner.xpath('@id')[0]  # Get the scanner ID
                scanner_name = scanner.xpath('name/text()')[0]  # Get the scanner name
                available_scanners.append((scanner_id, scanner_name))  # Store scanner details
            
            return available_scanners  # Return the list of available scanners

        
    def get_portlists(self):
        """
        Retrieve a list of all port lists from OpenVAS.

        :return: A list of dictionaries containing port list details (ID, name, comment).
        :raises ValueError: If the retrieval of port lists fails.
        """
        with self._connect() as gmp:
            # Authenticate with OpenVAS
            gmp.authenticate(self.username, self.password)

            # Fetch the list of port lists
            response = gmp.get_port_lists()

            # Check for errors in the response
            if response.attrib.get('status') == '400':
                status = response.attrib.get('status')
                status_text = response.attrib.get('status_text')
                raise ValueError(f"Error {status}: {status_text}")  # Raise error for non-success status
            
            # Extract port list data
            portlists = response.xpath('.//port_list')
            portlist_data = []
            for portlist in portlists:
                portlist_entry = {
                    "id": portlist.xpath('@id')[0] if portlist.xpath('@id') else "N/A",  # Get port list ID
                    "name": portlist.xpath('name/text()')[0] if portlist.xpath('name/text()') else "N/A",  # Get port list name
                    "comment": portlist.xpath('comment/text()')[0] if portlist.xpath('comment/text()') else "No comment"  # Get port list comment
                }
                portlist_data.append(portlist_entry)  # Add the entry to the list
            
            return portlist_data  # Return the list of port list details


    def get_targets(self, filter_string='rows=-1'):
        """
        Retrieve a list of targets from OpenVAS.

        :param filter_string: An optional filter string to limit the targets retrieved (default: 'rows=-1' to fetch all targets).
        :return: A list of dictionaries containing target details (ID, name, comment, hosts, exclude_hosts, port_list, creation_time, modification_time).
        :raises ValueError: If there's an error retrieving the targets.
        """
        with self._connect() as gmp:
            # Authenticate with OpenVAS
            gmp.authenticate(self.username, self.password)

            try:
                # Retrieve targets with the specified filter
                response = gmp.get_targets(filter_string=filter_string)
                
                # Parse the response and extract target details
                targets = []
                for target in response.xpath('//target'):
                    target_data = {
                        'id': target.get('id'),  # Get target ID
                        'name': target.findtext('name'),  # Get target name
                        'comment': target.findtext('comment'),  # Get target comment
                        'hosts': target.findtext('hosts'),  # Get target hosts
                        'exclude_hosts': target.findtext('exclude_hosts'),  # Get excluded hosts
                        'port_list': target.findtext('port_list/name'),  # Get port list name
                        'creation_time': target.findtext('creation_time'),  # Get target creation time
                        'modification_time': target.findtext('modification_time'),  # Get target modification time
                    }
                    targets.append(target_data)  # Add target to the list
                
                return targets  # Return the list of targets
            
            except Exception as e:
                # Raise an error if target retrieval fails
                raise ValueError(f"Error retrieving targets: {str(e)}")



    def create_target(self, name, hosts, port_range=None, port_list_id=None, comment=None):
        """
        Create a new target in OpenVAS.

        :param name: The name of the target.
        :param hosts: The hosts associated with the target (IP addresses or hostnames).
        :param port_range: Optional port range for the target (default: None).
        :param port_list_id: Optional ID of the port list to associate with the target (default: None).
        :param comment: Optional comment for the target (default: None).
        :return: The ID of the created target.
        :raises ValueError: If the target creation fails or if the target ID cannot be retrieved.
        """
        with self._connect() as gmp:
            # Authenticate with OpenVAS
            gmp.authenticate(self.username, self.password)

            # Create the target using the provided details
            response = gmp.create_target(name=name, hosts=hosts, port_range=port_range, port_list_id=port_list_id, comment=comment)

            # Extract the target ID from the response
            target_id_elements = response.xpath('@id')
            if not target_id_elements:
                # Check for detailed error information
                status = response.attrib.get('status')
                status_text = response.attrib.get('status_text')
                if status and status_text:
                    raise ValueError(f"Error {status}: {status_text}")
                else:
                    raise ValueError("Failed to retrieve target ID and no detailed error information available.")

            target_id = target_id_elements[0]  # Get the first target ID
            return target_id  # Return the ID of the created target



    def delete_target(self, target_id):
        """
        Delete a target from OpenVAS.

        :param target_id: The ID of the target to delete.
        :return: A dictionary indicating the result of the deletion.
        :raises ValueError: If the target deletion fails or if an unexpected error occurs.
        """
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)

            try:
                # Attempt to delete the target
                response = gmp.delete_target(target_id=target_id)

                # Check if the response contains the status
                status = response.attrib.get('status')
                status_text = response.attrib.get('status_text')
                if status != '200':
                    raise ValueError(f"Error {status}: {status_text}")

                return {"message": "Target deleted successfully"}

            except Exception as e:
                # Handle unexpected exceptions
                status = response.attrib.get('status') if response.attrib else "unknown"
                status_text = response.attrib.get('status_text') if response.attrib else str(e)
                raise ValueError(f"Error {status}: {status_text}")


    def modify_target(self, target_id, name=None, hosts=None, exclude_hosts=None, port_list_id=None, comment=None):
        """
        Modify an existing target in OpenVAS.

        :param target_id: The ID of the target to modify.
        :param name: The new name for the target (optional).
        :param hosts: The new hosts for the target (optional).
        :param exclude_hosts: The new excluded hosts for the target (optional).
        :param port_list_id: The new port list ID for the target (optional).
        :param comment: The new comment for the target (optional).
        :return: A dictionary with the result of the modification.
        :raises ValueError: If the modification fails or if an unexpected error occurs.
        """
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)

            try:
                # Attempt to modify the target with provided parameters
                response = gmp.modify_target(
                    target_id=target_id,
                    name=name,
                    hosts=hosts,
                    exclude_hosts=exclude_hosts,
                    port_list_id=port_list_id,
                    comment=comment
                )

                status = response.attrib.get('status')
                status_text = response.attrib.get('status_text')

                if status != '200':
                    raise ValueError(f"Error {status}: {status_text}")

                return {
                    "message": "Target modified successfully",
                    "status": status,
                    "status_text": status_text
                }

            except Exception as e:
                raise ValueError(f"Error modifying target: {str(e)}")



    def create_task(self, name, target_id, config_id, scanner_id, schedule_id=None, alert_ids=None):
        """
        Create a new task in OpenVAS.

        :param name: The name of the task to create.
        :param target_id: The ID of the target for the task.
        :param config_id: The configuration ID for the task.
        :param scanner_id: The scanner ID to use for the task.
        :param schedule_id: The optional schedule ID for the task (optional).
        :param alert_ids: The optional list of alert IDs for the task (optional).
        :return: The ID of the created task.
        :raises ValueError: If task creation fails or if the task ID cannot be retrieved.
        """
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            response = gmp.create_task(
                name=name,
                target_id=target_id,
                config_id=config_id,
                scanner_id=scanner_id,
                schedule_id=schedule_id,
                alert_ids=alert_ids
            )
            
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
        """
        Start a task in OpenVAS.

        :param task_id: The ID of the task to start.
        :return: A dictionary containing the status and status text of the operation.
        """
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            response = gmp.start_task(task_id=task_id)
            
            status = response.attrib.get('status', "unknown")
            status_text = response.attrib.get('status_text', "No message")
            
            return {
                "status": status,
                "status_text": status_text
            }

    def stop_task(self, task_id):
        """
        Stop a running task in OpenVAS.

        :param task_id: The ID of the task to stop.
        :return: A dictionary containing the status and status text of the operation.
        """
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            response = gmp.stop_task(task_id=task_id)
            
            status = response.attrib.get('status', "unknown")
            status_text = response.attrib.get('status_text', "No message")
            
            return {
                "status": status,
                "status_text": status_text
            }

    def resume_task(self, task_id):
        """
        Resume a paused task in OpenVAS.

        :param task_id: The ID of the task to resume.
        :return: A dictionary containing the status and status text of the operation.
        """
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            response = gmp.resume_task(task_id=task_id)
            
            status = response.attrib.get('status', "unknown")
            status_text = response.attrib.get('status_text', "No message")
            
            return {
                "status": status,
                "status_text": status_text
            }


    def delete_task(self, task_id):
        """
        Delete a task in OpenVAS.

        :param task_id: The ID of the task to delete.
        :return: A dictionary confirming the task deletion along with status details.
        """
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            
            try:
                # Attempt to delete the task
                response = gmp.delete_task(task_id=task_id)
                
                # Check the response status
                status = response.attrib.get('status')
                status_text = response.attrib.get('status_text')
                
                if status != '200':
                    # If the status is not 200, raise a ValueError
                    raise ValueError(f"Error {status}: {status_text}")
                
                return {
                    "message": "Task deleted successfully",
                    "status": status,
                    "status_text": status_text
                }
            
            except Exception as e:
                # Handle unexpected exceptions
                status = response.attrib.get('status') if response.attrib else "unknown"
                status_text = response.attrib.get('status_text') if response.attrib else str(e)
                raise ValueError(f"Error {status}: {status_text}")



    def modify_task(self, name, task_id, config_id, scanner_id, schedule_id=None, alert_ids=None):
        """
        Modify an existing task in OpenVAS.

        :param name: The new name for the task.
        :param task_id: The ID of the task to modify.
        :param config_id: The configuration ID to apply to the task.
        :param scanner_id: The scanner ID to associate with the task.
        :param schedule_id: Optional; the schedule ID to set for the task.
        :param alert_ids: Optional; a list of alert IDs to associate with the task.
        :return: A dictionary confirming the task modification.
        """
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            
            try:
                # Attempt to modify the task
                response = gmp.modify_task(
                    name=name,
                    task_id=task_id,
                    config_id=config_id,
                    scanner_id=scanner_id,
                    schedule_id=schedule_id,
                    alert_ids=alert_ids
                )
                
                # Check if the response contains the updated task information
                status = response.attrib.get('status')
                status_text = response.attrib.get('status_text')
                if status != '200':
                    raise ValueError(f"Error {status}: {status_text}")

                return {"message": "Task modified successfully"}
            
            except Exception as e:
                # Handle unexpected exceptions
                status = response.attrib.get('status') if response.attrib else "unknown"
                status_text = response.attrib.get('status_text') if response.attrib else str(e)
                raise ValueError(f"Error {status}: {status_text}")



    def get_tasks(self):
        """
        Retrieve all tasks from OpenVAS.

        :return: A list of tasks with their IDs, names, and statuses.
        """
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            response = gmp.get_tasks(filter_string="rows=-1")
            
            # Check for errors in the response
            if response.attrib.get('status') == '400':
                status = response.attrib.get('status')
                status_text = response.attrib.get('status_text')
                raise ValueError(f"Error {status}: {status_text}")
            
            # Extract task information from the response
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


    def get_task(self, task_id: str) -> dict:
        """
        Retrieve information about a specific task in OpenVAS using the GMP API.

        Args:
            task_id: The UUID of the task to retrieve.

        Returns:
            A dictionary containing the task information from OpenVAS.
        """
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            try:
                # Request the specific task using its ID
                response = gmp.get_task(task_id=task_id)
                
                # Check if the task element exists in the response
                task = response.find('task')
                if task is None:
                    raise ValueError("Failed to get task: Task element not found in response")
                
                # Extract task information from the response
                task_info = {
                    "status": response.attrib.get('status', 'Unknown'),
                    "status_text": response.attrib.get('status_text', 'Unknown'),
                    "id": task.attrib.get('id', 'Unknown'),
                    "name": task.findtext('name', default="Not available"),
                    "comment": task.findtext('comment', default="Not available"),
                    "creation_time": task.findtext('creation_time', default="Not available"),
                    "modification_time": task.findtext('modification_time', default="Not available"),
                    "owner": task.find('owner').findtext('name', default="Not available") if task.find('owner') is not None else "Not available",
                    "status": task.findtext('status', default="Not available"),
                    "progress": task.findtext('progress', default="Not available"),
                    "report_count": task.findtext('report_count', default="Not available"),
                    "last_report": {
                        "id": task.find('last_report').find('report').attrib.get('id', 'Not available') if task.find('last_report') is not None and task.find('last_report').find('report') is not None else "Not available",
                        "timestamp": task.find('last_report').find('report').findtext('timestamp', default="Not available") if task.find('last_report') is not None and task.find('last_report').find('report') is not None else "Not available",
                        "scan_start": task.find('last_report').find('report').findtext('scan_start', default="Not available") if task.find('last_report') is not None and task.find('last_report').find('report') is not None else "Not available",
                        "scan_end": task.find('last_report').find('report').findtext('scan_end', default="Not available") if task.find('last_report') is not None and task.find('last_report').find('report') is not None else "Not available",
                    }
                }

                return task_info
            except Exception as e:
                raise ValueError(f"Failed to get task: {str(e)}")




    def get_task_status(self, task_id):
        """
        Retrieve the current status of a specified task in OpenVAS.

        Args:
            task_id: The UUID of the task to check the status for.

        Returns:
            A dictionary containing the task's status, message, and progress.
        """
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            # Fetch the task details
            response = gmp.get_task(task_id=task_id)
            
            # Extract status and status text from the response
            status = response.attrib.get('status')
            status_text = response.attrib.get('status_text')
            
            # Retrieve the progress from the response
            status_elements = response.xpath('.//status/text()')
            progress = status_elements[0] if status_elements else "unknown"
            
            return {
                "status": status,
                "message": status_text,
                "progress": progress
            }


    def get_results(self, task_id):
        """
        Retrieve results for a specified task in OpenVAS.

        Args:
            task_id: The UUID of the task to retrieve results for.

        Returns:
            A list of dictionaries containing the results of the task.
        """
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            # Fetch the results for the task
            response = gmp.get_results(task_id=task_id, filter_string="rows=-1")
            
            # Check for errors in the response
            if response.attrib.get('status') == '400':
                status = response.attrib.get('status')
                status_text = response.attrib.get('status_text')
                raise ValueError(f"Error {status}: {status_text}")
            
            # Extract results from the response
            results = response.xpath('.//result')
            result_list = []
            for result in results:
                # Create a dictionary for each result with relevant information
                result_entry = {
                    "id": result.xpath('@id')[0] if result.xpath('@id') else "N/A",
                    "name": result.xpath('name/text()')[0] if result.xpath('name/text()') else "N/A",
                    "description": result.xpath('description/text()')[0] if result.xpath('description/text()') else "N/A",
                    "severity": result.xpath('severity/text()')[0] if result.xpath('severity/text()') else "N/A"
                }
                result_list.append(result_entry)
            
            return result_list



    def get_reports(self, filter_string='rows=-1'):
        """
        Retrieve a list of reports from OpenVAS using the GMP.

        Args:
            filter_string: Optional filter string to customize the query.
                        Default is 'rows=-1', which retrieves all reports.

        Returns:
            A list of reports, each represented as a dictionary.
        """
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            
            # Fetch the list of reports from OpenVAS
            response = gmp.get_reports(filter_string=filter_string)
            
            # Optional: Print the full response to understand its structure (for debugging)
            # print("Full Reports Response:")
            # print(etree.tostring(response, pretty_print=True).decode())
            
            # Parse the XML response
            root = etree.fromstring(etree.tostring(response))
            
            # Extract report data
            reports = []
            for report_element in root.findall('.//report'):
                report_id = report_element.get('id')
                
                # Extract task ID from the parent or related elements
                task_id_element = report_element.find('.//task')
                task_id = task_id_element.get('id') if task_id_element is not None else "N/A"
                
                report_data = {
                    "id": report_id,
                    "name": report_element.findtext('name', default=""),
                    "creation_time": report_element.findtext('creation_time', default=""),
                    "modification_time": report_element.findtext('modification_time', default=""),
                    "scan_run_status": report_element.findtext('scan_run_status', default=""),
                    "vulns_count": report_element.find('.//vulns/count').text if report_element.find('.//vulns/count') is not None else "0",
                    "task_id": task_id
                }
                
                # Append the report data to the list
                reports.append(report_data)
            
            # Return the list of reports
            return reports


    def get_report_by_id(self, report_id):
        """
        Retrieve a specific report by its ID from OpenVAS using the GMP API.

        Args:
            report_id: The ID of the report to retrieve.

        Returns:
            A dictionary containing the report information, including its results.
        
        Raises:
            ValueError: If the report cannot be found or if there's an error in the response.
        """
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            
            # Fetch the specific report
            response = gmp.get_report(report_id=report_id, filter_string="rows=-1")
            
            # Parse the XML response
            root = etree.fromstring(etree.tostring(response))
            
            # Extract the report element by ID
            report_element = root.find('.//report[@id="' + report_id + '"]')
            if report_element is not None:
                # Extract task ID from related elements
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
                
                # Extract results from the report
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
                # Handle case where the report is not found
                status = response.attrib.get('status')
                status_text = response.attrib.get('status_text')
                raise ValueError(f"Error {status}: {status_text}")


    @cached(cache)
    def get_reports_with_tasks(self, filter_string='rows=-1'):
        """
        Retrieve a list of reports along with associated task details and highest severity.

        Args:
            filter_string: Optional filter string to customize the query.
                        Default is 'rows=-1', which retrieves all reports.

        Returns:
            A list of reports, each represented as a dictionary with task details and highest severity.
        """
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)

            # Fetch the list of reports
            response = gmp.get_reports(filter_string=filter_string)

            # Parse XML response
            root = etree.fromstring(etree.tostring(response))

            # Use a dictionary to store unique reports by report_id
            unique_reports = {}

            # Extract report data
            for report_element in root.findall('.//report'):
                report_id = report_element.get('id')
                task_id_element = report_element.find('.//task')
                task_id = task_id_element.get('id') if task_id_element is not None else "N/A"

                report_data = {
                    "id": report_id,
                    "name": report_element.findtext('name', default=""),
                    "creation_time": report_element.findtext('creation_time', default=""),
                    "modification_time": report_element.findtext('modification_time', default=""),
                    "vulns_count": report_element.find('.//vulns/count').text or "0",
                    "task_id": task_id,
                }

                # Check for existing report with the same ID
                if report_id in unique_reports:
                    existing_report = unique_reports[report_id]
                    # Prefer report with non-empty 'name' and 'creation_time'
                    if not existing_report["name"] and report_data["name"]:
                        unique_reports[report_id] = report_data
                else:
                    unique_reports[report_id] = report_data

            # Fetch all tasks in a single call
            tasks_info = {task["id"]: task for task in self.get_tasks()}

            # Final list of filtered and updated reports
            filtered_reports = []

            # Calculate highest severity and update reports
            for report in unique_reports.values():
                report_id = report["id"]
                task_id = report["task_id"]
                report["task_name"] = tasks_info.get(task_id, {}).get("name", "Not available")

                # Fetch report details for severity calculation
                report_details = self.get_report_by_id(report_id)
                report_results = report_details.get("results", [])

                if report_results:  # Check if results are not empty
                    highest_severity = max(float(result.get("severity", 0)) for result in report_results)
                else:
                    highest_severity = 0  # Set to 0 if there are no results

                report["highest_severity"] = highest_severity

                # Remove the 'scan_run_status' field if it exists
                report.pop("scan_run_status", None)

                # Append the updated report to the final list
                filtered_reports.append(report)

            return filtered_reports



    def export_report_to_csv(self, report_data, filename):
        """
        Export the results of a report to a CSV file.

        Args:
            report_data: A dictionary containing the report details, including results.
            filename: The name of the file to which the report will be exported.

        Returns:
            The filename of the exported CSV.
        """
        with open(filename, 'w', newline='') as csvfile:
            # Define the field names for the CSV
            fieldnames = ['id', 'host', 'port', 'description', 'cve_numbers', 'severity', 'threat']
            
            # Create a DictWriter object with the specified fieldnames
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write the header row to the CSV
            writer.writeheader()
            
            # Write each result to the CSV
            for result in report_data['results']:
                writer.writerow(result)
        
        return filename


    def export_report_to_excel(self, report_data, filename):
        """
        Export the results of a report to an Excel file.

        Args:
            report_data: A dictionary containing the report details, including results.
            filename: The name of the file to which the report will be exported.

        Returns:
            The filename of the exported Excel file.
        """
        # Create a new Excel workbook and add a worksheet
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet()

        # Add headers to the first row of the worksheet
        headers = ['ID', 'Host', 'Port', 'Description', 'CVE Numbers', 'Severity', 'Threat']
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header)

        # Add data rows starting from the second row
        for row_num, result in enumerate(report_data['results'], 1):
            worksheet.write(row_num, 0, result['id'])
            worksheet.write(row_num, 1, result['host'])
            worksheet.write(row_num, 2, result['port'])
            worksheet.write(row_num, 3, result['description'])
            worksheet.write(row_num, 4, ', '.join(result['cve_numbers']))  # Join CVE numbers as a string
            worksheet.write(row_num, 5, result['severity'])
            worksheet.write(row_num, 6, result['threat'])

        # Close the workbook to save the file
        workbook.close()
        return filename


    def export_report_to_pdf(self, report_data, filename):
        """
        Export the results of a report to a PDF file.

        Args:
            report_data: A dictionary containing the report details, including results.
            filename: The name of the file to which the report will be exported.

        Returns:
            The filename of the exported PDF file.
        """
        # Create a new PDF document
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Add title to the PDF
        pdf.cell(200, 10, txt="Scan Report", ln=True, align='C')

        # Add each result's details to the PDF
        for result in report_data['results']:
            pdf.cell(200, 10, txt=f"ID: {result['id']}", ln=True)
            pdf.cell(200, 10, txt=f"Host: {result['host']}", ln=True)
            pdf.cell(200, 10, txt=f"Port: {result['port']}", ln=True)
            pdf.cell(200, 10, txt=f"Description: {result['description']}", ln=True)
            pdf.cell(200, 10, txt=f"CVE Numbers: {', '.join(result['cve_numbers'])}", ln=True)
            pdf.cell(200, 10, txt=f"Severity: {result['severity']}", ln=True)
            pdf.cell(200, 10, txt=f"Threat: {result['threat']}", ln=True)
            pdf.cell(200, 10, txt=" ", ln=True)  # Add empty line between results

        # Output the PDF to the specified filename
        pdf.output(filename)
        return filename

    

    def delete_report(self, report_id):
        """
        Delete a report by its ID from OpenVAS.

        Args:
            report_id: The ID of the report to delete.

        Returns:
            A message indicating the result of the deletion operation.
        """
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            
            try:
                # Attempt to delete the report
                response = gmp.delete_report(report_id=report_id)
                
                # Check the response status
                status = response.attrib.get('status')
                status_text = response.attrib.get('status_text')
                
                if status != '200':
                    # If the status is not 200, raise a ValueError
                    raise ValueError(f"Error {status}: {status_text}")
                
                return {
                    "message": "Report deleted successfully",
                    "status": status,
                    "status_text": status_text
                }
            
            except Exception as e:
                # Handle unexpected exceptions
                status = response.attrib.get('status') if 'response' in locals() else "unknown"
                status_text = response.attrib.get('status_text') if 'response' in locals() else str(e)
                raise ValueError(f"Error {status}: {status_text}")



    def create_schedule(self, name, icalendar_data, timezone='UTC', comment=None):
        """
        Create a new schedule in OpenVAS.

        Args:
            name (str): The name of the schedule.
            icalendar_data (str): The iCalendar data for the schedule.
            timezone (str): The timezone for the schedule. Default is 'UTC'.
            comment (str, optional): Optional comment for the schedule.

        Returns:
            str: The ID of the created schedule.
        """
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)

            # Use GMP's create_schedule method to create the schedule
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

        Args:
            filter_string (str): Optional filter string to customize the query.
                                Default is 'rows=-1', which retrieves all schedules.

        Returns:
            list: A list of schedules, each represented as a dictionary.
        """
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            response = gmp.get_schedules(filter_string=filter_string)

            schedules = []  # Initialize an empty list to store schedules

            # Iterate through each schedule in the response
            for schedule in response.xpath('//schedule'):
                # Construct a dictionary to hold schedule data
                schedule_data = {
                    'id': schedule.get('id'),
                    'name': schedule.findtext('name'),
                    'comment': schedule.findtext('comment'),
                    'timezone': schedule.findtext('timezone'),
                    'period': None,  # Initialize period as None
                    'next_time': schedule.findtext('next_time'),
                    'last_time': schedule.findtext('last_time'),
                    'owner': schedule.findtext('owner'),
                    'creation_time': schedule.findtext('creation_time'),
                    'modification_time': schedule.findtext('modification_time'),
                }

                # Extract and parse iCalendar data if available
                icalendar_data = schedule.findtext('icalendar')
                if icalendar_data:
                    try:
                        # Parse the iCalendar data
                        cal = Calendar.from_ical(icalendar_data)
                        for component in cal.walk():
                            if component.name == "VEVENT":
                                # Extract period from RRULE
                                rrule = component.get('RRULE')
                                if rrule:
                                    freq = rrule.get('FREQ', [''])[0]
                                    interval = rrule.get('INTERVAL', [1])[0]
                                    period_description = None
                                    
                                    # Simplify period format based on frequency
                                    if freq == 'DAILY':
                                        period_description = f"Every {interval} day(s)"
                                    elif freq == 'WEEKLY':
                                        period_description = f"Every {interval} week(s)"
                                    elif freq == 'MONTHLY':
                                        period_description = f"Every {interval} month(s)"
                                    elif freq == 'HOURLY':
                                        period_description = f"Every {interval} hour(s)"
                                    elif freq == 'YEARLY':
                                        period_description = f"Every {interval} year(s)"
                                    
                                    schedule_data['period'] = period_description

                    except Exception as e:
                        print(f"Error parsing iCalendar data: {e}")

                # Append the constructed schedule data to the list
                schedules.append(schedule_data)

            return schedules


    def modify_schedule(self, schedule_id, name=None, icalendar_data=None, timezone='UTC', comment=None):
        """
        Modify an existing schedule in OpenVAS.

        Args:
            schedule_id (str): The ID of the schedule to modify.
            name (str, optional): The new name of the schedule. Defaults to None.
            icalendar_data (str, optional): The new iCalendar data for the schedule. Defaults to None.
            timezone (str): The new timezone for the schedule. Default is 'UTC'.
            comment (str, optional): Optional comment for the schedule.

        Returns:
            dict: A message indicating the result of the modification.
        """
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)

            try:
                # Use GMP's modify_schedule method to update the schedule
                response = gmp.modify_schedule(
                    schedule_id=schedule_id,
                    name=name,
                    icalendar=icalendar_data,
                    timezone=timezone,
                    comment=comment
                )

                # Extract status and status_text from the response
                status = response.attrib.get('status')
                status_text = response.attrib.get('status_text')

                # Check if the modification was successful
                if status == '200':
                    return {"message": "Schedule modified successfully"}
                else:
                    # Raise an error if the status is not 200
                    raise ValueError(f"Error {status}: {status_text}")

            except Exception as e:
                # Handle unexpected exceptions gracefully
                raise ValueError(f"Unexpected error occurred: {str(e)}")


    def delete_schedule(self, schedule_id):
        """
        Delete a schedule in OpenVAS.

        :param schedule_id: The ID of the schedule to be deleted.
        :return: A message indicating whether the deletion was successful.
        """
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            
            try:
                # Attempt to delete the schedule
                response = gmp.delete_schedule(schedule_id=schedule_id)

                # Extract status and status_text
                status = response.attrib.get('status')
                status_text = response.attrib.get('status_text')

                # Check if the operation was successful
                if status != "200":
                    raise ValueError(f"Error {status}: {status_text}")

                return {"message": "Schedule deleted successfully"}

            except Exception as e:
                # Handle unexpected exceptions
                raise ValueError(f"Unexpected error: {str(e)}")

    def create_alert(
            self,
            name: str,
            condition: str,
            event: str,
            method: str,
            *,
            condition_data: Optional[dict[str, str]] = None,
            event_data: Optional[dict[str, str]] = None,
            method_data: Optional[dict[str, str]] = None,
            filter_id: Optional[str] = None,
            comment: Optional[str] = None
        ) -> dict:
        """
        Create a new alert in OpenVAS using the GMP API.

        Args:
            name: The name of the alert.
            condition: The condition that must be satisfied for the alert to occur.
            event: The event that must happen for the alert to occur.
            method: The method by which the user is alerted.
            condition_data: A dictionary defining the condition data.
            event_data: A dictionary defining the event data.
            method_data: A dictionary defining the method data.
            filter_id: The UUID of a filter to apply when executing the alert.
            comment: An optional comment for the alert.

        Returns:
            A dictionary containing the response from OpenVAS.
        """
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            try:
                # Use GMP's create_alert method to create a new alert
                response = gmp.create_alert(
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
                return {
                    "status": response.attrib.get('status'),
                    "status_text": response.attrib.get('status_text'),
                    "id": response.attrib.get('id')  # Extract and return the alert ID
                }
            except Exception as e:
                raise ValueError(f"Failed to create alert: {str(e)}")


    def get_alerts(self) -> dict:
        """
        Retrieve a list of alerts from OpenVAS using the GMP API.

        Returns:
            A dictionary containing the list of alerts and their details.
        """
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            try:
                # Use GMP's get_alerts method to retrieve alerts
                response = gmp.get_alerts() 

                # Extract alert details from the response
                alerts = []
                for alert in response.xpath('//alert'):
                    alert_data = {
                        'id': alert.get('id'),  # Extract alert ID
                        'name': alert.findtext('name'),  # Extract alert name
                        'condition': alert.findtext('condition'),  # Extract alert condition
                        'event': alert.findtext('event'),  # Extract alert event
                        'method': alert.findtext('method'),  # Extract alert method
                        'comment': alert.findtext('comment'),  # Extract optional comment
                        'creation_time': alert.findtext('creation_time'),  # Extract creation time
                        'modification_time': alert.findtext('modification_time')  # Extract modification time
                    }
                    alerts.append(alert_data)

                return {
                    "status": response.attrib.get('status'),  # Extract status
                    "status_text": response.attrib.get('status_text'),  # Extract status text
                    "alerts": alerts  # Return list of alerts
                }
            except Exception as e:
                raise ValueError(f"Failed to get alerts: {str(e)}")  # Handle exceptions

            

    def modify_alert(
            self,
            alert_id: str,
            name: Optional[str] = None,
            condition: Optional[str] = None,
            event: Optional[str] = None,
            method: Optional[str] = None,
            *,
            condition_data: Optional[dict[str, str]] = None,
            event_data: Optional[dict[str, str]] = None,
            method_data: Optional[dict[str, str]] = None,
            filter_id: Optional[str] = None,
            comment: Optional[str] = None
        ) -> dict:
        """
        Modify an existing alert in OpenVAS using the GMP API.

        Args:
            alert_id: The UUID of the alert to modify.
            name: The new name for the alert.
            condition: The new condition for the alert.
            event: The new event for the alert.
            method: The new method for the alert.
            condition_data: Data defining the new condition.
            event_data: Data defining the new event.
            method_data: Data defining the new method.
            filter_id: The new UUID of the filter to apply.
            comment: The new comment for the alert.

        Returns:
            A dictionary containing the response from OpenVAS.
        """
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            try:
                response = gmp.modify_alert(
                    alert_id=alert_id,
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
                return {
                    "status": response.attrib.get('status'),
                    "status_text": response.attrib.get('status_text')
                }
            except Exception as e:
                raise ValueError(f"Failed to modify alert: {str(e)}")

    def delete_alert(self, alert_id: str) -> dict:
        """
        Delete an existing alert in OpenVAS using the GMP API.

        Args:
            alert_id: The UUID of the alert to delete.

        Returns:
            A dictionary containing the response from OpenVAS.
        """
        with self._connect() as gmp:
            gmp.authenticate(self.username, self.password)
            try:
                response = gmp.delete_alert(alert_id=alert_id)
                return {
                    "status": response.attrib.get('status'),
                    "status_text": response.attrib.get('status_text')
                }
            except Exception as e:
                raise ValueError(f"Failed to delete alert: {str(e)}")

