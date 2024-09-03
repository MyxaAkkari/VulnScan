from flask import Flask
from routes.scanner_routes import scanner_bp
from routes.groups_routes import groups_bp
from config.db import init_db
from config.config import Config
from config.logging_config import setup_logging

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
