import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    DEBUG = os.getenv('DEBUG') == 'True'
    HOST = os.getenv('HOST')
    PORT = int(os.getenv('PORT'))
    DATABASE_URL = os.getenv('DATABASE_URL')
    LOG_FILE = os.getenv('LOG_FILE')
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES'))
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT'))
    LOG_FORMAT = os.getenv('LOG_FORMAT')
    LOG_LEVEL = os.getenv('LOG_LEVEL')
    OPENVAS_SOCKET_PATH = os.getenv('OPENVAS_SOCKET_PATH')
    OPENVAS_USERNAME = os.getenv('OPENVAS_USERNAME')
    OPENVAS_PASSWORD = os.getenv('OPENVAS_PASSWORD')

print(f"DEBUG: {Config.DEBUG}")
print(f"HOST: {Config.HOST}")
print(f"PORT: {Config.PORT}")
print(f"OPENVAS_PASSWORD: {Config.OPENVAS_PASSWORD}")