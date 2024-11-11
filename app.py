# app.py

from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit, join_room
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from config import Config
from models import db, User, ScanResult
from tasks import run_tool_task
import os
import re
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    socketio.init_app(app, message_queue=Config.CELERY_BROKER_URL, async_mode='eventlet')

    # User authentication setup
    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
        # Create an admin user if none exists
        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin', password=generate_password_hash('password'))
            db.session.add(admin_user)
            db.session.commit()

    # Routes
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('home'))
            else:
                return render_template('login.html', error='Invalid credentials')
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    @app.route('/')
    @login_required
    def home():
        scans = ScanResult.query.filter_by(user_id=current_user.id).order_by(ScanResult.timestamp.desc()).all()
        return render_template('index.html', scans=scans)

    # Function to validate domain names
    def is_valid_domain(domain):
        regex = r'^(?:(?:[a-zA-Z0-9\-]{1,63}\.)+(?:[a-zA-Z]{2,63}))$'
        return re.match(regex, domain) is not None

    # Route to get scan result
    @app.route('/get_scan_result', methods=['GET'])
    @login_required
    def get_scan_result():
        scan_id = request.args.get('scan_id')
        scan = ScanResult.query.filter_by(id=scan_id, user_id=current_user.id).first()
        if scan:
            return {'result': scan.result}
        else:
            return {'result': 'No result found.'}

    # SocketIO event for starting reconnaissance
    @socketio.on('start_recon')
    @login_required
    def start_recon(data):
        target_domain = data['target_domain']
        scan_id = str(uuid.uuid4())

        if not is_valid_domain(target_domain):
            emit('tool_result', {'tool': 'Validation', 'result': '', 'message': 'Invalid domain format.', 'scan_id': scan_id})
            return

        # Create a unique directory for the scan results
        scan_output_dir = os.path.join(Config.OUTPUT_DIR, scan_id)
        os.makedirs(scan_output_dir, exist_ok=True)

        # List of tools to run
        tools = [
            "assetfinder",
            "subfinder",
            "amass",
            "httpx",
            "dnsx",
            "katana",
            "gau",
            "gospider",
            "nuclei"
        ]

        # Emit a message that the scan has started
        emit('tool_result', {'tool': 'Scan', 'result': '', 'message': f'Starting reconnaissance on {target_domain}', 'scan_id': scan_id})

        # Join the room for this scan
        join_room(scan_id)

        # Run each tool as a Celery task
        for tool_name in tools:
            run_tool_task.apply_async(args=[tool_name, target_domain, current_user.id, scan_id])

    return app

if __name__ == '__main__':
    app = create_app()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)