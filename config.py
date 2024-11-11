# config.py

import os

class Config:
    SECRET_KEY = 'your_secret_key_here'
    SECURITY_PASSWORD_SALT = 'your_password_salt_here'  # For password reset tokens
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    OUTPUT_DIR = os.path.join(BASE_DIR, 'scan_results')

    # Paths to the external tools
    TOOL_PATHS = {
        'httpx': '/usr/local/bin/httpx',
        'katana': '/usr/local/bin/katana',
        'gospider': '/usr/local/bin/gospider',
        'gau': '/usr/local/bin/gau',
        'assetfinder': '/usr/local/bin/assetfinder',
        'subfinder': '/usr/local/bin/subfinder',
        'dnsx': '/usr/local/bin/dnsx',
        'amass': '/usr/bin/amass',
        'nuclei': '/usr/local/bin/nuclei',
        # Add paths for additional tools
        'waybackurls': '/usr/local/bin/waybackurls',
        'ffuf': '/usr/local/bin/ffuf',
    }

    # Celery configuration
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

    # Flask-Mail configuration (for password resets)
    MAIL_SERVER = 'smtp.example.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'you@example.com'
    MAIL_PASSWORD = 'your_email_password'