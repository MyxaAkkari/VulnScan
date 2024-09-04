from flask import Flask
from flask_jwt_extended import JWTManager
from routes.scanner_routes import scanner_bp
from routes.groups_routes import groups_bp
from routes.auth import auth_bp
from routes.AI import ai_bp
from config.db import init_db
from config.config import Config
from config.logging_config import setup_logging

app = Flask(__name__)
app.config.from_object(Config)
app.register_blueprint(scanner_bp, url_prefix='/scanner')
app.register_blueprint(groups_bp, url_prefix='/groups')
app.register_blueprint(ai_bp, url_prefix='/ai')
app.register_blueprint(auth_bp, url_prefix= '/auth')
jwt = JWTManager(app)
setup_logging(app)


# Initialize the database
with app.app_context():
    init_db()
    
if __name__ == '__main__':
    app.run(host=app.config['HOST'], port=app.config['PORT'], debug=app.config['DEBUG'])
