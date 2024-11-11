# app.py

from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from flask_socketio import SocketIO, emit, join_room
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import Api, Resource
from config import Config
from models import db, User, ScanResult
from tasks import run_tool_task
from forms import RegistrationForm, LoginForm, UpdateProfileForm
import os
import re
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from io import BytesIO
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import base64

socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    socketio.init_app(app, message_queue=Config.CELERY_BROKER_URL, async_mode='eventlet')
    api = Api(app)

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

    # Routes
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegistrationForm()
        if form.validate_on_submit():
            hashed_password = generate_password_hash(form.password.data)
            user = User(username=form.username.data, email=form.email.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('home'))
        return render_template('register.html', form=form)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('home'))
            else:
                form.password.errors.append('Invalid username or password')
        return render_template('login.html', form=form)

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

    @app.route('/profile', methods=['GET', 'POST'])
    @login_required
    def profile():
        form = UpdateProfileForm()
        if form.validate_on_submit():
            current_user.email = form.email.data
            db.session.commit()
            return redirect(url_for('profile'))
        elif request.method == 'GET':
            form.email.data = current_user.email
        return render_template('profile.html', form=form)

    @app.route('/dashboard')
    @login_required
    def dashboard():
        scans = ScanResult.query.filter_by(user_id=current_user.id).all()
        scan_counts = {}
        for scan in scans:
            date = scan.timestamp.strftime('%Y-%m-%d')
            scan_counts[date] = scan_counts.get(date, 0) + 1

        # Prepare data for charts
        dates = list(scan_counts.keys())
        counts = list(scan_counts.values())

        # Encode data for charts
        chart_data = {
            'dates': dates,
            'counts': counts,
        }

        # Tool usage
        tool_counts = {}
        for scan in scans:
            tool = scan.tool
            tool_counts[tool] = tool_counts.get(tool, 0) + 1

        tools = list(tool_counts.keys())
        tool_usage = list(tool_counts.values())

        tool_data = {
            'tools': tools,
            'usage': tool_usage,
        }

        return render_template('dashboard.html', chart_data=chart_data, tool_data=tool_data)

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

    # Route to download report
    @app.route('/download_report/<int:scan_id>')
    @login_required
    def download_report(scan_id):
        scan = ScanResult.query.filter_by(id=scan_id, user_id=current_user.id).first()
        if scan:
            # Generate HTML report
            report_html = render_template('report.html', scan=scan)
            # Save report to file
            report_file = os.path.join(Config.REPORTS_DIR, f'{scan.domain}_{scan.tool}_report_{scan.id}.html')
            with open(report_file, 'w') as f:
                f.write(report_html)
            return send_file(report_file, as_attachment=True)
        else:
            return redirect(url_for('home'))

    # SocketIO event for starting reconnaissance
    @socketio.on('start_recon')
    @login_required
    def start_recon(data):
        target_domain = data['target_domain']
        selected_tools = data.get('selected_tools', [])
        scan_id = str(uuid.uuid4())

        if not is_valid_domain(target_domain):
            emit('tool_result', {'tool': 'Validation', 'result': '', 'message': 'Invalid domain format.', 'scan_id': scan_id})
            return

        # Create a unique directory for the scan results
        scan_output_dir = os.path.join(Config.OUTPUT_DIR, scan_id)
        os.makedirs(scan_output_dir, exist_ok=True)

        # Default to all tools if none are selected
        if not selected_tools:
            tools = [
                "assetfinder",
                "subfinder",
                "amass",
                "httpx",
                "dnsx",
                "katana",
                "gau",
                "gospider",
                "nuclei",
                "waybackurls",
                "ffuf"
            ]
        else:
            tools = selected_tools

        # Emit a message that the scan has started
        emit('tool_result', {'tool': 'Scan', 'result': '', 'message': f'Starting reconnaissance on {target_domain}', 'scan_id': scan_id})

        # Join the room for this scan
        join_room(scan_id)

        # Run each tool as a Celery task
        for tool_name in tools:
            run_tool_task.apply_async(args=[tool_name, target_domain, current_user.id, scan_id])

    # API Endpoints
    class ScanAPI(Resource):
        @login_required
        def get(self, scan_id):
            scan = ScanResult.query.filter_by(id=scan_id, user_id=current_user.id).first()
            if scan:
                return {'id': scan.id, 'domain': scan.domain, 'tool': scan.tool, 'result': scan.result}
            else:
                return {'message': 'Scan not found'}, 404

    class StartScanAPI(Resource):
        @login_required
        def post(self):
            data = request.get_json()
            target_domain = data.get('target_domain')
            selected_tools = data.get('selected_tools', [])
            scan_id = str(uuid.uuid4())

            if not is_valid_domain(target_domain):
                return {'message': 'Invalid domain format.'}, 400

            # Create a unique directory for the scan results
            scan_output_dir = os.path.join(Config.OUTPUT_DIR, scan_id)
            os.makedirs(scan_output_dir, exist_ok=True)

            # Default to all tools if none are selected
            if not selected_tools:
                tools = [
                    "assetfinder",
                    "subfinder",
                    "amass",
                    "httpx",
                    "dnsx",
                    "katana",
                    "gau",
                    "gospider",
                    "nuclei",
                    "waybackurls",
                    "ffuf"
                ]
            else:
                tools = selected_tools

            # Run each tool as a Celery task
            for tool_name in tools:
                run_tool_task.apply_async(args=[tool_name, target_domain, current_user.id, scan_id])

            return {'message': 'Scan started', 'scan_id': scan_id}, 202

    api.add_resource(ScanAPI, '/api/scan/<int:scan_id>')
    api.add_resource(StartScanAPI, '/api/start_scan')

    return app

if __name__ == '__main__':
    app = create_app()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)