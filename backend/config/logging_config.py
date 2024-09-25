import logging  # Import logging module for logging capabilities
from logging.handlers import RotatingFileHandler  # Import RotatingFileHandler for log rotation
from uuid import uuid4  # Import uuid4 for generating unique request IDs
from flask import Flask, jsonify, request  # Import Flask and necessary components from Flask

# Custom formatter class for logging
class CustomFormatter(logging.Formatter):
    def format(self, record):
        log_entry = super().format(record)  # Call the parent class's format method
        
        # Add a separator for INFO logs that include response status
        if record.levelname == 'INFO' and 'Response status' in log_entry:
            return f"{log_entry}\n{'='*100}\n"  # Append separator for better readability
        return log_entry

# Function to set up logging configuration
def setup_logging(app: Flask):
    # Clear any existing handlers to prevent duplicate logs
    if app.logger.hasHandlers():
        app.logger.handlers.clear()

    # Set up a file handler for logging to a file with rotation
    log_handler = RotatingFileHandler(
        app.config['LOG_FILE'],  # Path to the log file from config
        maxBytes=app.config['LOG_MAX_BYTES'],  # Maximum file size before rotation
        backupCount=app.config['LOG_BACKUP_COUNT']  # Number of backup files to keep
    )
    
    # Create a custom formatter for the logs
    formatter = CustomFormatter(app.config['LOG_FORMAT'])  # Use the defined custom formatter
    log_handler.setFormatter(formatter)  # Set the formatter for the log handler
    log_handler.setLevel(app.config['LOG_LEVEL'])  # Set the log level for the handler
    app.logger.addHandler(log_handler)  # Attach the file handler to the app logger

    # Add a console handler if DEBUG mode is enabled
    if app.config['DEBUG']:
        console_handler = logging.StreamHandler()  # Create a stream handler for console output
        console_handler.setFormatter(formatter)  # Set the custom formatter
        console_handler.setLevel(app.config['LOG_LEVEL'])  # Set the log level for the console
        app.logger.addHandler(console_handler)  # Attach the console handler to the app logger

    app.logger.setLevel(app.config['LOG_LEVEL'])  # Set the overall log level for the logger

    # Log request information before handling the request
    @app.before_request
    def log_request_info():
        request_id = str(uuid4())  # Generate a unique request ID
        request.environ['REQUEST_ID'] = request_id  # Store the request ID in the environment
        client_ip = request.remote_addr  # Get the client's IP address
        app.logger.info(f"Request ID: {request_id}")  # Log the request ID
        app.logger.info(f"Client IP: {client_ip}")  # Log the client IP
        app.logger.info(f"Request: {request.method} {request.url}")  # Log the request method and URL
        app.logger.info(f"Headers: {request.headers}")  # Log the request headers
        app.logger.info(f"Body: {request.get_data()}")  # Log the request body

    # Log response information after handling the request
    @app.after_request
    def log_response_info(response):
        client_ip = request.remote_addr  # Get the client's IP address
        app.logger.info(f"Client IP: {client_ip}")  # Log the client IP
        app.logger.info(f"Response status: {response.status}")  # Log the response status
        return response  # Return the response object

    # Handle exceptions globally
    @app.errorhandler(Exception)
    def handle_exception(e):
        client_ip = request.remote_addr  # Get the client's IP address
        app.logger.error(f"Exception occurred for Client IP {client_ip}: {str(e)}", exc_info=True)  # Log the error with traceback
        response = {
            "error": "Internal server error",  # Error message for the client
            "message": str(e)  # Include the exception message
        }
        return jsonify(response), 500  # Return a JSON response with a 500 status code
