from flask import Flask
from config import Config
from models import db
from flask_socketio import SocketIO
from flask_login import LoginManager
from auth.routes import auth_bp
from dashboard.routes import dashboard_bp
from api.routes import api_bp

socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    socketio.init_app(app, message_queue=Config.CELERY_BROKER_URL, async_mode='eventlet')
    login_manager = LoginManager(app)
    login_manager.login_view = "auth.login"

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    # Create DB tables if not present
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)