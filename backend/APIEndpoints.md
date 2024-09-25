## Scanner Endpoints /scanner

### POST /authenticate

**Description**: Authenticates the user with the OpenVAS scanner. This endpoint establishes a connection to the scanner and verifies the user's credentials. 

**Request**: No parameters are required in the request body.

**Response**:
- `200 OK`: Authentication was successful. Returns a success message.
- `500 Internal Server Error`: Authentication failed. Returns an error message explaining the failure.

---

### GET /get_roles

**Description**: Retrieves a list of available user roles from the OpenVAS scanner. This endpoint is used to fetch the different roles that can be assigned to users in the scanner system.

**Request**: No parameters are required.

**Response**:
- `200 OK`: Successfully retrieved the list of roles. Returns roles in JSON format.
- `400 Bad Request`: Failed to retrieve roles. Returns an error message explaining the issue.

---

### GET /get_users

**Description**: Retrieves a list of users from the OpenVAS scanner. This endpoint provides information on all users in the scanner system.

**Request**: No parameters are required.

**Response**:
- `200 OK`: Successfully retrieved the list of users. Returns users in JSON format.
- `400 Bad Request`: Failed to retrieve users. Returns an error message explaining the issue.

---

### GET /get_user/{user_id}

**Description**: Retrieves the details of a specific user based on their user ID.

**Request**: 
- `user_id` (path parameter): The ID of the user to retrieve.

**Response**:
- `200 OK`: Returns the user details in JSON format.
- `400 Bad Request`: Returns an error message if retrieval fails.

---

### POST /create_user

**Description**: Creates a new user with the specified details. Requires admin privileges.

**Request Body**:
- `name` (string): The name of the new user.
- `password` (string): The password for the new user.
- `role_ids` (array, optional): A list of role IDs to assign to the new user.

**Response**:
- `200 OK`: Returns the result of the user creation process.
- `400 Bad Request`: Returns an error message if user creation fails.

---

### PUT /modify_user/{user_id}

**Description**: Modifies the details of an existing user specified by user ID. Requires admin privileges.

**Request**:
- `user_id` (path parameter): The ID of the user to modify.

**Request Body**:
- `name` (string, optional): The new username.
- `password` (string, optional): The new password.
- `role_ids` (array, optional): A list of new role IDs to assign to the user.

**Response**:
- `200 OK`: Returns the result of the user modification process.
- `400 Bad Request`: Returns an error message if modification fails.

---

### DELETE /delete_user/{user_id}

**Description**: Deletes a user specified by user ID. Requires admin privileges.

**Request**: 
- `user_id` (path parameter): The ID of the user to delete.

**Response**:
- `200 OK`: Returns the result of the user deletion process.
- `400 Bad Request`: Returns an error message if deletion fails.

---

### POST /clone_user/{user_id}

**Description**: Clones an existing user specified by user ID. Allows optional fields to set the name, comment, and roles of the cloned user. Requires admin privileges.

**Request**:
- `user_id` (path parameter): The ID of the user to clone.

**Request Body**:
- `name` (string, optional): New name for the cloned user.
- `comment` (string, optional): New comment for the cloned user.
- `roles` (array, optional): New roles to assign to the cloned user.

**Response**:
- `200 OK`: Returns the result of the cloning process.
- `400 Bad Request`: Returns an error message if cloning fails.

---

### GET /get_scanners

**Description**: Retrieves a list of available scanners from the OpenVAS system. Requires token authentication.

**Response**:
- `200 OK`: Returns a formatted list of scanners as key-value pairs (ID and name).
- `500 Internal Server Error`: Returns an error message if retrieval fails.

---

### GET /get_configs

**Description**: Retrieves a list of configuration settings from the OpenVAS scanner. Requires token authentication.

**Response**:
- `200 OK`: Returns a list of configurations with their IDs and names.
- `500 Internal Server Error`: Returns an error message if retrieval fails.

---

### GET /get_portlists

**Description**: Retrieves a list of port lists from the OpenVAS scanner. Requires token authentication.

**Response**:
- `200 OK`: Returns a list of port lists.
- `500 Internal Server Error`: Returns an error message if retrieval fails.

---

### GET /get_hosts

**Description**: Retrieves a list of hosts from the OpenVAS scanner. Requires token authentication.

**Response**:
- `200 OK`: Returns a list of hosts.
- `500 Internal Server Error`: Returns an error message if retrieval fails.

---

### DELETE /delete_host/<host_id>

**Description**: Deletes a specified host from the OpenVAS scanner. Requires admin authentication.

**Parameters**:
- `host_id` (string): The ID of the host to be deleted.

**Response**:
- `200 OK`: Returns a JSON response with the result of the deletion.
- `500 Internal Server Error`: Returns an error message if deletion fails.

---

### POST /convert_hosts_to_targets

**Description**: Converts a list of hosts into targets for the OpenVAS scanner. Requires admin authentication.

**Request Body**:
- A JSON object with the following structure:
    ```json
    {
        "hosts": [
            {"hostname": "example.com", "ip": "192.168.1.1"},
            ...
        ],
        "port_list_id": "some-port-list-id",
        "port_range": "1-1000"
    }
    ```

**Response**:
- `201 Created`: Returns a JSON response containing the list of created targets.
    ```json
    {
        "created_targets": [
            {"target_name": "example.com", "target_id": "some-target-id"},
            ...
        ]
    }
    ```
- `400 Bad Request`: Returns an error message if an IP address is missing for any host.
- `500 Internal Server Error`: Returns an error message if target creation fails.

---

### GET /get_targets

**Description**: Retrieves a list of targets from the OpenVAS scanner. Requires user authentication via token.

**Response**:
- `200 OK`: Returns a JSON response containing the list of targets.
    ```json
    {
        "targets": [
            {"id": "some-target-id", "name": "example.com", "ip": "192.168.1.1"},
            ...
        ]
    }
    ```
- `500 Internal Server Error`: Returns an error message if the retrieval of targets fails.

---

### POST /create_target

**Description**: Creates a new target in the OpenVAS scanner. Requires admin authentication to execute.

**Request Body**:
```json
{
    "name": "target_name",
    "hosts": "host1, host2, ...",
    "port_range": "1-1000",
    "port_list_id": "some-port-list-id",
    "comment": "Optional comment"
}
```
**Response**
- `201 Created`: Returns a JSON response containing the ID of the created target.
    ```json
        {
        "target_id": "some-target-id"
    }
    ```
- `400 Bad Request`: Returns an error message if required fields are missing or if target creation fails.

---

### DELETE /delete_target/<target_id>

**Description**: Deletes a target from the OpenVAS scanner. Requires admin authentication to execute.

**Path Parameters**:
- `target_id` (string): The ID of the target to be deleted.

**Response**:
- `200 OK`: Returns a JSON response indicating the result of the deletion.
    ```json
    {
        "message": "Target deleted successfully."
    }
    ```
- `500 Internal Server Error`: Returns an error message if deletion fails.
    ```json
    {
        "error": "Detailed error message."
    }
    ```

---

### POST /modify_target/<string:target_id>

**Description**: Modifies an existing target in the OpenVAS scanner. Requires admin authentication to execute.

**Path Parameters**:
- `target_id` (string): The ID of the target to be modified.

**Request Body** (JSON):
```json
{
    "name": "new_target_name",
    "hosts": "new_host1, new_host2, ...",
    "exclude_hosts": "excluded_host1, excluded_host2, ...",
    "port_list_id": "new-port-list-id",
    "comment": "Optional comment"
}
```
**Response**:
- `200 OK`: Returns a JSON response containing the result of the modification.
    ```json
        {
        "message": "Target modified successfully."
    }

    ```
- `500 Internal Server Error`: Returns an error message if modification fails.
    ```json
    {
        "error": "Detailed error message."
    }
    ```
---

### POST /create_task

**Description**: Creates a new task in the OpenVAS scanner. Requires admin authentication to execute.

**Request Body** (JSON):
```json
{
    "name": "task_name",
    "target_id": "target_id",
    "config_id": "config_id",
    "scanner_id": "scanner_id",
    "schedule_id": "optional_schedule_id",
    "alert_ids": "optional_alert_ids"
}
```
**Response**:
- `201 OK`: Returns a JSON response containing the ID of the created task.
    ```json
        {
        "task_id": "new_task_id"
    }

    ```
- `500 Internal Server Error`:  Returns an error message if task creation fails.
    ```json
    {
        "error": "Detailed error message."
    }
    ```
---

### POST /start_task/<task_id>

**Description**: Starts a task based on the provided task ID. Requires admin authentication.

**Path Parameters**:
- `task_id` (string): The ID of the task to start.

**Response**:
- `200 OK`: Returns a JSON response with a success message.
    ```json
    {
        "message": "Task started successfully."
    }
    ```
- `500 Internal Server Error`: Returns an error message if a ValueError occurs.
    ```json
    {
        "error": "Detailed error message."
    }
    ```

---

### POST /stop_task/<task_id>

**Description**: Stops a task based on the provided task ID. Requires admin authentication.

**Path Parameters**:
- `task_id` (string): The ID of the task to stop.

**Response**:
- `200 OK`: Returns a JSON response with a success message.
    ```json
    {
        "message": "Task stopped successfully."
    }
    ```
- `500 Internal Server Error`: Returns an error message if a ValueError occurs.
    ```json
    {
        "error": "Detailed error message."
    }
    ```

---

### POST /resume_task/<task_id>

**Description**: Resumes a task based on the provided task ID. Requires admin authentication.

**Path Parameters**:
- `task_id` (string): The ID of the task to resume.

**Response**:
- `200 OK`: Returns a JSON response with a success message.
    ```json
    {
        "message": "Task resumed successfully."
    }
    ```
- `500 Internal Server Error`: Returns an error message if a ValueError occurs.
    ```json
    {
        "error": "Detailed error message."
    }
    ```
---

### DELETE /delete_task/<task_id>

**Description**: Deletes a task based on the provided task ID. Requires admin authentication.

**Path Parameters**:
- `task_id` (string): The ID of the task to delete.

**Response**:
- `200 OK`: Returns a JSON response with a success message indicating the result of the deletion.
    ```json
    {
        "message": "Task deleted successfully."
    }
    ```
- `400 Bad Request`: Returns an error message if a ValueError occurs.
    ```json
    {
        "error": "Detailed error message."
    }
    ```
- `500 Internal Server Error`: Returns an error message for any unexpected error.
    ```json
    {
        "error": "An unexpected error occurred",
        "details": "Detailed error message."
    }
    ```

---

### PUT /modify_task/<task_id>

**Description**: Modifies a task based on the provided task ID and updates it with new data. Requires admin authentication.

**Path Parameters**:
- `task_id` (string): The ID of the task to modify.

**Request Body**:
- JSON object containing fields to update (optional):
    ```json
    {
        "name": "new_task_name",
        "config_id": "new_config_id",
        "scanner_id": "new_scanner_id",
        "schedule_id": "optional_schedule_id",
        "alert_ids": "optional_alert_ids"
    }
    ```

**Response**:
- `200 OK`: Returns a JSON response with a success message indicating the result of the modification.
    ```json
    {
        "message": "Task modified successfully."
    }
    ```
- `500 Internal Server Error`: Returns an error message if a ValueError occurs.
    ```json
    {
        "error": "Detailed error message."
    }
    ```
---

### GET /get_task/<task_id>

**Description**: Retrieves information about a specific task based on the provided task ID. Requires token authentication.

**Path Parameters**:
- `task_id` (string): The ID of the task to retrieve.

**Response**:
- `200 OK`: Returns a JSON response with the task information.
    ```json
    {
        "task_id": "example_task_id",
        "name": "Example Task",
        "status": "Running",
        "details": "Additional task details here."
    }
    ```
- `400 Bad Request`: Returns an error message if `task_id` is not provided or a ValueError occurs.
    ```json
    {
        "status": "error",
        "message": "Detailed error message."
    }
    ```
- `500 Internal Server Error`: Returns an error message for any unexpected error.
    ```json
    {
        "status": "error",
        "message": "An unexpected error occurred"
    }
    ```

---

### GET /get_task_status/<task_id>

**Description**: Retrieves the status of a specific task based on the provided task ID. Requires token authentication.

**Path Parameters**:
- `task_id` (string): The ID of the task for which to retrieve the status.

**Response**:
- `200 OK`: Returns a JSON response with the task status.
    ```json
    {
        "task_id": "example_task_id",
        "status": "Completed",
        "progress": "100%"
    }
    ```
- `404 Not Found`: Returns an error message if the task is not found or no status is available.
    ```json
    {
        "error": "Task not found or no status available."
    }
    ```
- `500 Internal Server Error`: Returns an error message if a ValueError occurs.
    ```json
    {
        "error": "Failed to retrieve task status.",
        "details": "Detailed error message."
    }
    ```
---

### GET /get_tasks

**Description**: Retrieves a list of all tasks. Requires token authentication.

**Response**:
- `200 OK`: Returns a JSON response containing the list of tasks.
    ```json
    {
        "tasks": [
            {
                "task_id": "example_task_id_1",
                "name": "Task 1",
                "status": "Completed"
            },
            {
                "task_id": "example_task_id_2",
                "name": "Task 2",
                "status": "Running"
            }
        ]
    }
    ```
- `500 Internal Server Error`: Returns an error message if a ValueError occurs.
    ```json
    {
        "error": "Detailed error message."
    }
    ```

---

### POST /get_results

**Description**: Retrieves results for a specific task based on the provided task ID. Requires token authentication.

**Request Body**:
- JSON object with the following structure:
    ```json
    {
        "task_id": "example_task_id"
    }
    ```

**Response**:
- `200 OK`: Returns a JSON response containing the results for the specified task.
    ```json
    {
        "results": {
            "result_id": "example_result_id",
            "details": "Result details here."
        }
    }
    ```
- `500 Internal Server Error`: Returns an error message if a ValueError occurs.
    ```json
    {
        "error": "Detailed error message."
    }
    ```

---

### GET /get_reports

**Description**: Retrieves a list of all reports. Requires token authentication.

**Response**:
- `200 OK`: Returns a JSON response containing the list of reports.
    ```json
    {
        "reports": [
            {
                "report_id": "example_report_id_1",
                "name": "Report 1",
                "status": "Generated"
            },
            {
                "report_id": "example_report_id_2",
                "name": "Report 2",
                "status": "Pending"
            }
        ]
    }
    ```
- `500 Internal Server Error`: Returns an error message if a ValueError occurs.
    ```json
    {
        "error": "Detailed error message."
    }
    ```
---

### GET /get_report/<report_id>

**Description**: Retrieves detailed information about a specific report based on the provided report ID. Requires token authentication.

**Arguments**:
- `report_id` (str): The ID of the report to retrieve.

**Response**:
- `200 OK`: Returns the report data if found.
    ```json
    {
        "report_id": "example_report_id",
        "name": "Report 1",
        "status": "Generated",
        "details": "Detailed report information here."
    }
    ```
- `404 Not Found`: Returns an error message if the report cannot be found.
    ```json
    {
        "error": "Report not found."
    }
    ```

---

### GET /get_reports_with_tasks

**Description**: Retrieves a list of reports along with their associated task details. Requires token authentication.

**Response**:
- `200 OK`: Returns a JSON response containing the reports with tasks.
    ```json
    {
        "reports": [
            {
                "report_id": "example_report_id_1",
                "name": "Report 1",
                "status": "Generated",
                "associated_tasks": [
                    {
                        "task_id": "example_task_id_1",
                        "task_name": "Task 1"
                    }
                ]
            },
            {
                "report_id": "example_report_id_2",
                "name": "Report 2",
                "status": "Pending",
                "associated_tasks": []
            }
        ]
    }
    ```
- `500 Internal Server Error`: Returns an error message if a ValueError occurs.
    ```json
    {
        "error": "Detailed error message."
    }
    ```

---

### DELETE /delete_report/<report_id>

**Description**: Deletes a specific report based on the provided report ID. Requires admin authentication.

**Arguments**:
- `report_id` (str): The ID of the report to delete.

**Response**:
- `200 OK`: Returns a success message with the result of the deletion.
    ```json
    {
        "message": "Report deleted successfully."
    }
    ```
- `400 Bad Request`: Returns an error message if a ValueError occurs.
    ```json
    {
        "error": "Detailed error message."
    }
    ```
---

### GET /export_report/<report_id>/<format>

**Description**: Exports a specific report in the requested format (CSV, Excel, PDF). Requires token authentication.

**Arguments**:
- `report_id` (str): The ID of the report to export.
- `format` (str): The format in which to export the report (csv, xlsx, pdf).

**Response**:
- `200 OK`: Returns a file attachment of the exported report if successful.
    - **Content-Disposition**: `attachment; filename=report_<report_id>.<format>`
- `404 Not Found`: Returns an error message if the report cannot be found.
    ```json
    {
        "error": "Report not found."
    }
    ```
- `400 Bad Request`: Returns an error message if the requested format is unsupported.
    ```json
    {
        "error": "Unsupported format."
    }
    ```
- `500 Internal Server Error`: Returns an error message if a ValueError occurs.
    ```json
    {
        "error": "Detailed error message."
    }
    ```

---

### GET /get_schedules

**Description**: Retrieves a list of schedules. Requires token authentication.

**Response**:
- `200 OK`: Returns a JSON response containing the list of schedules.
    ```json
    {
        "schedules": [
            {
                "schedule_id": "example_schedule_id_1",
                "name": "Daily Scan",
                "time": "08:00",
                "timezone": "UTC"
            },
            {
                "schedule_id": "example_schedule_id_2",
                "name": "Weekly Report",
                "time": "12:00",
                "timezone": "UTC"
            }
        ]
    }
    ```
- `500 Internal Server Error`: Returns an error message if a ValueError occurs.
    ```json
    {
        "error": "Detailed error message."
    }
    ```
---

### POST /create_schedule

**Description**: Creates a new schedule based on the provided parameters. This endpoint requires admin authentication.

**Request Payload**:
- **Content-Type**: `application/json`
- **Body**: A JSON object containing the following fields:
    - `name` (str): The name of the schedule (required).
    - `dtstart` (str): The start date and time in ISO 8601 format (YYYY-MM-DDTHH:MM:SS) (required).
    - `timezone` (str, optional): The timezone for the schedule (default is 'UTC').
    - `comment` (str, optional): Additional comments for the schedule (default is an empty string).
    - `frequency` (str, optional): Frequency of the schedule (default is 'daily').
    - `interval` (int, optional): Interval for the frequency (default is 1).
    - `count` (int, optional): The number of occurrences for the schedule.

**Response**:
- `201 Created`: Returns a JSON response with the ID of the newly created schedule.
    ```json
    {
        "schedule_id": "example_schedule_id"
    }
    ```
- `400 Bad Request`: Returns an error message if required fields are missing or invalid.
    ```json
    {
        "error": "Detailed error message."
    }
    ```
- `500 Internal Server Error`: Returns an error message if a ValueError occurs during processing.
    ```json
    {
        "error": "Detailed error message."
    }
    ```
---

### POST /modify_schedule

**Description**: Modifies an existing schedule based on the provided parameters. This endpoint requires admin authentication.

**Request Payload**:
- **Content-Type**: `application/json`
- **Body**: A JSON object containing the following fields:
    - `schedule_id` (str): The ID of the schedule to modify (required).
    - `name` (str): The new name of the schedule (required).
    - `dtstart` (str): The new start date and time in ISO 8601 format (YYYY-MM-DDTHH:MM:SS) (required).
    - `timezone` (str, optional): The new timezone for the schedule.
    - `comment` (str, optional): Updated comments for the schedule.
    - `frequency` (str, optional): Updated frequency of the schedule.
    - `interval` (int, optional): Updated interval for the frequency.
    - `count` (int, optional): The number of occurrences for the schedule.

**Response**:
- `200 OK`: Returns a JSON response confirming the successful modification of the schedule.
    ```json
    {
        "message": "Schedule modified successfully"
    }
    ```
- `400 Bad Request`: Returns an error message if required fields are missing or invalid.
    ```json
    {
        "error": "Detailed error message."
    }
    ```
- `404 Not Found`: Returns an error message if the specified schedule ID does not exist.
    ```json
    {
        "error": "Schedule not found."
    }
    ```
- `500 Internal Server Error`: Returns an error message if a ValueError occurs during processing.
    ```json
    {
        "error": "Detailed error message."
    }
    ```

---

### DELETE /delete_schedule/<schedule_id>

**Description**: Deletes a specified schedule identified by the provided schedule ID. This endpoint requires admin authentication.

**URL Parameters**:
- `schedule_id` (str): The ID of the schedule to be deleted (required).

**Response**:
- `200 OK`: Returns a JSON response confirming the successful deletion of the schedule.
    ```json
    {
        "message": "Schedule deleted successfully"
    }
    ```
- `400 Bad Request`: Returns an error message if the schedule cannot be found or if an issue occurs during the deletion process.
    ```json
    {
        "error": "Detailed error message."
    }
    ```

---

### POST /create_alert

**Description**: Creates a new alert based on the provided parameters. This endpoint requires admin authentication.

**Request Body**: Expects a JSON payload containing the following fields:
- `name` (str): The name of the alert (required).
- `condition` (str): The condition that triggers the alert (required).
- `event` (str): The specific event that triggers the alert (required).
- `method` (str): The method of notification for the alert (required).
- `condition_data` (dict, optional): Additional data related to the condition for the alert.
- `event_data` (dict, optional): Additional data related to the event that triggers the alert.
- `method_data` (dict, optional): Additional data related to the notification method.
- `filter_id` (str, optional): An optional filter ID for the alert.
- `comment` (str, optional): An optional comment providing additional information about the alert.

**Response**:
- `201 Created`: Returns a success message with the ID of the newly created alert.
    ```json
    {
        "status": "success",
        "message": "Alert created successfully.",
        "alert_id": "<alert_id>"
    }
    ```
- `500 Internal Server Error`: Returns an error message if the alert creation fails.
    ```json
    {
        "status": "error",
        "message": "Failed to create alert: Detailed error message."
    }
    ```

---

### GET /get_alerts

**Description**: Retrieves a list of alerts from the system. This endpoint requires user authentication via a token.

**Response**:
- `200 OK`: Returns a JSON array containing the list of alerts.
    ```json
    [
        {
            "id": "<alert_id>",
            "name": "<alert_name>",
            "condition": "<alert_condition>",
            "event": "<alert_event>",
            "method": "<notification_method>",
            "status": "<alert_status>",
            "comment": "<optional_comment>"
        },
        ...
    ]
    ```
- `400 Bad Request`: Returns an error message if there is a value-related error while fetching alerts.
    ```json
    {
        "status": "error",
        "message": "<error_message>"
    }
    ```
- `500 Internal Server Error`: Returns an error message for unexpected failures during the operation.
    ```json
    {
        "status": "error",
        "message": "An unexpected error occurred"
    }
    ```

---

### POST /modify_alert

**Description**: Endpoint to modify an existing alert. This operation requires administrative privileges.

**Request**:
- **Headers**:
  - `Authorization`: Bearer token for admin authentication.
- **Body** (JSON):
    ```json
    {
        "alert_id": "<alert_id>",
        "name": "<new_alert_name>",
        "condition": "<new_alert_condition>",
        "event": "<new_alert_event>",
        "method": "<new_notification_method>",
        "condition_data": { /* Additional data for the condition */ },
        "event_data": { /* Additional data for the event */ },
        "method_data": { /* Additional data for the method */ },
        "filter_id": "<optional_filter_id>",
        "comment": "<optional_comment>"
    }
    ```

**Response**:
- `200 OK`: Returns a JSON object with the details of the modified alert.
    ```json
    {
        "status": "success",
        "alert_id": "<alert_id>",
        "name": "<new_alert_name>",
        "condition": "<new_alert_condition>",
        "event": "<new_alert_event>",
        "method": "<new_notification_method>",
        "comment": "<optional_comment>"
    }
    ```
- `400 Bad Request`: Returns an error message if `alert_id` is missing or if a value-related error occurs while modifying the alert.
    ```json
    {
        "status": "error",
        "message": "<error_message>"
    }
    ```
- `500 Internal Server Error`: Returns an error message for unexpected failures during the operation.
    ```json
    {
        "status": "error",
        "message": "An unexpected error occurred"
    }
    ```

---


### DELETE /delete_alert/<alert_id>

**Description**: Endpoint to delete an alert identified by its ID. This operation requires administrative privileges.

**Request**:
- **Headers**:
  - `Authorization`: Bearer token for admin authentication.
- **URL Parameters**:
  - `alert_id` (string): The ID of the alert to delete.

**Response**:
- `200 OK`: Returns a JSON object indicating successful deletion of the alert.
    ```json
    {
        "status": "success",
        "message": "Alert deleted successfully."
    }
    ```
- `400 Bad Request`: Returns an error message if `alert_id` is missing or if a value-related error occurs while attempting to delete the alert.
    ```json
    {
        "status": "error",
        "message": "<error_message>"
    }
    ```
- `500 Internal Server Error`: Returns an error message for unexpected failures during the deletion process.
    ```json
    {
        "status": "error",
        "message": "An unexpected error occurred"
    }
    ```

---

## Auth Endpoints /auth


### POST /signup

**Description**: Endpoint for user registration (signup). This endpoint allows new users to register by providing their username, email, and password. Only regular users can be created; admin roles are not permitted.

**Request**:
- **Headers**:
  - `Content-Type`: application/json
- **Body**:
    - `username` (string): The desired username for the new account.
    - `email` (string): The email address associated with the account.
    - `password` (string): The password for the new account.
    - `comment` (string, optional): Additional comments or information about the user.

**Response**:
- `201 Created`: Returns a JSON object indicating successful user creation.
    ```json
    {
        "message": "User created successfully"
    }
    ```
- `400 Bad Request`: Returns an error message if the username or email already exists in the system.
    ```json
    {
        "error": "Username already exists"
    }
    ```
    or
    ```json
    {
        "error": "Email already exists"
    }
    ```
---

### POST /create_admin

**Description**: Endpoint for creating a new admin user. This endpoint allows an existing admin to register a new admin user by providing their username, email, password, and an optional comment.

**Authorization**: Requires admin access.

**Request**:
- **Headers**:
  - `Content-Type`: application/json
- **Body**:
    - `username` (string): The desired username for the new admin account.
    - `email` (string): The email address associated with the admin account.
    - `password` (string): The password for the new admin account.
    - `comment` (string, optional): Additional comments or information about the admin.

**Response**:
- `201 Created`: Returns a JSON object indicating successful admin creation.
    ```json
    {
        "message": "Admin created successfully"
    }
    ```
- `400 Bad Request`: Returns an error message if the username or email already exists in the system.
    ```json
    {
        "error": "Username already exists"
    }
    ```
    or
    ```json
    {
        "error": "Email already exists"
    }
    ```

---

### POST /signin

**Description**: Endpoint for user sign-in. This endpoint validates the user's credentials and, if successful, returns a JSON Web Token (JWT) access token along with user details.

**Request**:
- **Headers**:
  - `Content-Type`: application/json
- **Body**:
    - `email` (string): The email address of the user (case insensitive).
    - `password` (string): The password associated with the user's account.

**Response**:
- `200 OK`: Returns a JSON object containing the access token and user information upon successful sign-in.
    ```json
    {
        "access_token": "JWT_ACCESS_TOKEN",
        "user": {
            "id": "USER_ID",
            "username": "USERNAME",
            "email": "EMAIL",
            "role": "USER_ROLE"
        }
    }
    ```
- `401 Unauthorized`: Returns an error message if the provided email or password is invalid.
    ```json
    {
        "error": "Invalid email or password"
    }
    ```

---

### PUT /modify_user/<user_id>

**Description**: Endpoint to modify an existing user's details. This endpoint requires admin access and allows the modification of user attributes. The user is identified by the `user_id` provided in the URL.

**Parameters**:
- **Path Parameters**:
    - `user_id` (int): The ID of the user to modify.

**Request**:
- **Headers**:
  - `Content-Type`: application/json
- **Body**:
    - JSON object containing any of the following fields to modify:
        - `username` (string): The new username for the user.
        - `email` (string): The new email address for the user.
        - `role` (string): The new role for the user, should be either `"USER"` or `"ADMIN"`.
        - `password` (string): The new password for the user.
        - `comment` (string): An optional comment for the user.

**Response**:
- `200 OK`: Returns a JSON object indicating the user was updated successfully.
    ```json
    {
        "message": "User updated successfully"
    }
    ```
- `404 Not Found`: Returns an error message if the specified user does not exist.
    ```json
    {
        "error": "User not found"
    }
    ```
- `400 Bad Request`: Returns an error message if:
    - The provided username already exists.
    - The provided email already exists.
    - An invalid role is specified.
    ```json
    {
        "error": "Username already exists" // or "Email already exists" or "Invalid role specified"
    }
    ```

---

### DELETE /delete_user/<user_id>

**Description**: Endpoint to delete an existing user. This endpoint requires admin access and identifies the user to be deleted by the `user_id` provided in the URL.

**Parameters**:
- **Path Parameters**:
    - `user_id` (int): The ID of the user to delete.

**Response**:
- `200 OK`: Returns a JSON object indicating the user was deleted successfully.
    ```json
    {
        "message": "User deleted successfully"
    }
    ```
- `404 Not Found`: Returns an error message if the specified user does not exist.
    ```json
    {
        "error": "User not found"
    }
    ```

---

### GET /get_user

**Description**: Endpoint to retrieve information about the currently logged-in user. This endpoint requires a valid JWT token for authentication.

**Response**:
- `200 OK`: Returns a JSON object containing the user's details.
    ```json
    {
        "id": <user_id>,
        "username": "<username>",
        "email": "<email>",
        "role": "<user_role>",
        "comment": "<user_comment>"
    }
    ```
- `404 Not Found`: Returns an error message if the user does not exist in the database.
    ```json
    {
        "error": "User not found"
    }
    ```

---

### GET /get_users

**Description**: Endpoint to retrieve information for all users. This endpoint requires admin access to view the user list.

**Response**:
- `200 OK`: Returns a JSON array containing a list of users with their details.
    ```json
    [
        {
            "id": <user_id>,
            "username": "<username>",
            "email": "<email>",
            "role": "<user_role>",
            "comment": "<user_comment>"
        },
        ...
    ]
    ```

---

## Groups Endpoints /groups

### POST /create_group

**Description**: Endpoint to create a new group. This endpoint requires admin access.

**Request Payload**:
- A JSON object containing the following key:
    - `group_name` (string, required): The name of the group to be created.

**Response**:
- `201 Created`: Returns a JSON object indicating the group has been successfully created.
    ```json
    {
        "message": "Group created",
        "group_id": <group_id>
    }
    ```

---

### GET /get_groups

**Description**: Endpoint to retrieve all groups. This endpoint is accessible to any authenticated user.

**Response**:
- `200 OK`: Returns a JSON array containing details of all groups.
    ```json
    [
        {
            "id": <group_id>,
            "name": "<group_name>"
        },
        ...
    ]
    ```

---

### DELETE /delete_group/<group_id>

**Description**: Endpoint to delete a group by its ID. This endpoint requires admin access.

**Parameters**:
- `group_id` (int): The ID of the group to be deleted.

**Response**:
- `200 OK`: Returns a success message indicating the group was deleted.
    ```json
    {
        "message": "Group deleted"
    }
    ```

- `404 Not Found`: Returns an error message if the group with the specified ID does not exist.
    ```json
    {
        "error": "Group not found"
    }
    ```

---

### POST /remove_from_group

**Description**: Endpoint to remove a target from a group. This endpoint requires admin access.

**Request Body**:
- **JSON Object**:
    - `target_id` (int): The ID of the target to be removed from the group.
    - `group_id` (int): The ID of the group from which the target will be removed.

**Response**:
- `200 OK`: Returns a success message indicating the target was removed from the group.
    ```json
    {
        "message": "Target removed from group"
    }
    ```

- `400 Bad Request`: Returns an error message if either `target_id` or `group_id` is not provided in the request.
    ```json
    {
        "error": "target_id and group_id are required"
    }
    ```

- `404 Not Found`: Returns an error message if the specified target does not belong to the specified group.
    ```json
    {
        "error": "Target not found in group"
    }
    ```

---

### POST /add_target

**Description**: Endpoint to add a new target to a group. This endpoint requires admin access.

**Request Body**:
- **JSON Object**:
    - `name` (string): The name of the target to be added.
    - `ip_address` (string): The IP address of the target to be added.
    - `group_id` (int): The ID of the group to which the target will be added.

**Response**:
- `201 Created`: Returns a success message indicating the target was added and includes the ID of the newly created target.
    ```json
    {
        "message": "Target added",
        "target_id": <target_id>
    }
    ```

---

### GET /get_group_targets/<group_id>

**Description**: Endpoint to retrieve all targets in a specific group. This endpoint is accessible to any authenticated user.

**Path Parameters**:
- `group_id` (int): The ID of the group for which targets are being retrieved.

**Response**:
- `200 OK`: Returns a list of targets associated with the specified group.
    ```json
    [
        {
            "id": <target_id>,
            "name": "<target_name>",
            "ip_address": "<target_ip_address>"
        },
        ...
    ]
    ```

---

## AI Endpoint /ai

### POST /analyze_cve

**Description**: Analyzes CVEs from the provided scan results and retrieves explanations and mitigation strategies from the Generative AI model.

**Authentication**: This endpoint requires a valid JWT token for access.

**Request Body**:
- The request should contain a JSON object with the following structure:
    ```json
    {
        "results": [
            {
                "severity": <float>,
                "cve_numbers": ["<CVE-ID-1>", "<CVE-ID-2>", ...],
                "description": "<vulnerability_description>"
            },
            ...
        ]
    }
    ```

**Response**:
- `200 OK`: Returns a JSON array containing the analysis results for each CVE.
    ```json
    [
        {
            "cve": "<CVE-ID>",
            "answer": "<explanation_and_mitigation_steps>"
        },
        ...
    ]
    ```
















