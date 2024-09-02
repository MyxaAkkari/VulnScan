from flask import Flask
from scanner_routes import scanner_bp
from groups_routes import groups_bp
from db import init_db
from config import Config
from logging_config import setup_logging

app = Flask(__name__)
app.config.from_object(Config)
app.register_blueprint(scanner_bp, url_prefix='/scanner')
app.register_blueprint(groups_bp, url_prefix='/groups')

setup_logging(app)


# Initialize the database
with app.app_context():
    init_db()
    
if __name__ == '__main__':
    app.run(host=app.config['HOST'], port=app.config['PORT'], debug=app.config['DEBUG'])
