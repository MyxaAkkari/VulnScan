# VulnScan Backend

This repository contains the backend of the VulnScan project, built with Python and Flask. It integrates with the OpenVAS scanner to manage and run vulnerability scans, generate reports, handle tasks, and manage schedules and alerts.

## Requirements

- Python 3.x
- OpenVAS [Recommended Installation Guide](https://www.youtube.com/watch?v=J7SrS4qDzM0)
- Flask
- Git

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/MyxaAkkari/VulnScan.git
    ```

2. Navigate to the backend directory:

    ```bash
    cd VulnScan/backend
    ```

3. Create a virtual environment:

    ```bash
    python3 -m venv venv
    ```

4. Activate the virtual environment:

    - On Linux/MacOS:

      ```bash
      source venv/bin/activate
      ```

    - On Windows:

      ```bash
      venv\Scripts\activate
      ```

5. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1. Rename the `.env.example` file to `.env` and update the environment variables, including OpenVAS login credentials, API keys, and any other relevant configurations.

    ```bash
    mv .env.example .env
    ```

2. Update the necessary fields in the `.env` file.

## Running the Server

To run the Flask development server, use the following command:

```bash
flask run
```
The server will start at http://localhost:5000 by default.

## Admin Credentials

The default user credentials are:
- Email: admin@vulnscan.com
- Password: admin

## API Endpoints

For detailed API documentation, refer to the [API Endpoints](./APIEndpoints.md) file.

## Deployment

For production environments, configure a WSGI server (e.g., Gunicorn) to serve the Flask app.
```bash
gunicorn -w 4 app:app
```
