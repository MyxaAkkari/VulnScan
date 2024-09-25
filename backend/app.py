from flask import Flask  # Import Flask framework for creating web applications
from flask_jwt_extended import JWTManager  # Import JWTManager for handling JSON Web Tokens
from routes.scanner_routes import scanner_bp  # Import scanner routes blueprint
from routes.groups_routes import groups_bp  # Import groups routes blueprint
from routes.auth import auth_bp  # Import authentication routes blueprint
from routes.AI import ai_bp  # Import AI routes blueprint
from config.db import init_db  # Import database initialization function
from config.config import Config  # Import configuration settings
from config.logging_config import setup_logging  # Import logging setup function
from flask_cors import CORS  # Import CORS for handling Cross-Origin Resource Sharing

app = Flask(__name__)  # Create a Flask application instance
app.config.from_object(Config)  # Load configuration settings from Config object
app.register_blueprint(scanner_bp, url_prefix='/scanner')  # Register scanner routes under '/scanner' prefix
app.register_blueprint(groups_bp, url_prefix='/groups')  # Register groups routes under '/groups' prefix
app.register_blueprint(ai_bp, url_prefix='/ai')  # Register AI routes under '/ai' prefix
app.register_blueprint(auth_bp, url_prefix='/auth')  # Register authentication routes under '/auth' prefix

jwt = JWTManager(app)  # Initialize JWTManager for managing tokens
setup_logging(app)  # Set up logging for the application
CORS(app)  # Enable CORS for the Flask app

# Initialize the database within the application context
with app.app_context():
    init_db()  # Call the database initialization function
    
# Run the application if this script is executed directly
if __name__ == '__main__':
    app.run(host=app.config['HOST'], port=app.config['PORT'], debug=app.config['DEBUG'])  # Start the Flask server
