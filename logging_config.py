import logging
from logging.handlers import RotatingFileHandler
from uuid import uuid4
from flask import Flask, jsonify, request

class CustomFormatter(logging.Formatter):
    def format(self, record):
        log_entry = super().format(record)
        
        if record.levelname == 'INFO' and 'Response status' in log_entry:
            return f"{log_entry}\n{'='*100}\n"
        return log_entry

def setup_logging(app: Flask):
    # Clear any existing handlers to prevent duplicate logs
    if app.logger.hasHandlers():
        app.logger.handlers.clear()

    # Set up a file handler to store logs with rotation
    log_handler = RotatingFileHandler(
        app.config['LOG_FILE'],
        maxBytes=app.config['LOG_MAX_BYTES'],
        backupCount=app.config['LOG_BACKUP_COUNT']
    )
    
    # Use the custom formatter
    formatter = CustomFormatter(app.config['LOG_FORMAT'])
    log_handler.setFormatter(formatter)
    log_handler.setLevel(app.config['LOG_LEVEL'])
    app.logger.addHandler(log_handler)

    # Add console handler only if DEBUG mode is True
    if app.config['DEBUG']:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(app.config['LOG_LEVEL'])
        app.logger.addHandler(console_handler)

    app.logger.setLevel(app.config['LOG_LEVEL'])

    @app.before_request
    def log_request_info():
        request_id = str(uuid4())
        request.environ['REQUEST_ID'] = request_id
        client_ip = request.remote_addr
        app.logger.info(f"Request ID: {request_id}")
        app.logger.info(f"Client IP: {client_ip}")
        app.logger.info(f"Request: {request.method} {request.url}")
        app.logger.info(f"Headers: {request.headers}")
        app.logger.info(f"Body: {request.get_data()}")

    @app.after_request
    def log_response_info(response):
        client_ip = request.remote_addr
        app.logger.info(f"Client IP: {client_ip}")
        app.logger.info(f"Response status: {response.status}")
        return response

    @app.errorhandler(Exception)
    def handle_exception(e):
        client_ip = request.remote_addr
        app.logger.error(f"Exception occurred for Client IP {client_ip}: {str(e)}", exc_info=True)
        response = {
            "error": "Internal server error",
            "message": str(e)
        }
        return jsonify(response), 500
