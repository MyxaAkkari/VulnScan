from datetime import timedelta  # Import timedelta for setting token expiration
import os  # Import os for interacting with the operating system
from dotenv import load_dotenv  # Import load_dotenv for loading environment variables from .env file

# Load environment variables from .env file
load_dotenv()  # Load environment variables defined in the .env file

class Config:
    DEBUG = os.getenv('DEBUG') == 'True'  # Set DEBUG mode based on environment variable
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)  # Set JWT access token expiration time to 1 hour
    HOST = os.getenv('HOST')  # Get host address from environment variable
    PORT = int(os.getenv('PORT'))  # Get port number from environment variable and convert to integer
    DATABASE_URL = os.getenv('DATABASE_URL')  # Get database URL from environment variable
    LOG_FILE = os.getenv('LOG_FILE')  # Get log file path from environment variable
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES'))  # Get maximum log file size from environment variable
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT'))  # Get number of backup log files from environment variable
    LOG_FORMAT = os.getenv('LOG_FORMAT')  # Get log format from environment variable
    LOG_LEVEL = os.getenv('LOG_LEVEL')  # Get log level from environment variable
    OPENVAS_SOCKET_PATH = os.getenv('OPENVAS_SOCKET_PATH')  # Get OpenVAS socket path from environment variable
    OPENVAS_USERNAME = os.getenv('OPENVAS_USERNAME')  # Get OpenVAS username from environment variable
    OPENVAS_PASSWORD = os.getenv('OPENVAS_PASSWORD')  # Get OpenVAS password from environment variable
    API_KEY = os.getenv('API_KEY')  # Get API key from environment variable
    SECRET_KEY = os.getenv('SECRET_KEY')  # Get secret key for cryptographic operations from environment variable
