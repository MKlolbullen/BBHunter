# config.py

class Config:
    SECRET_KEY = 'your_secret_key_here'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    OUTPUT_DIR = '/path/to/output'
    TOOL_PATHS = {
        'httpx': '/usr/local/bin/httpx',
        'katana': '/usr/local/bin/katana',
        'gospider': '/usr/local/bin/gospider',
        'gau': '/usr/local/bin/gau',
        'chaos': '/usr/local/bin/chaos',
        'assetfinder': '/usr/local/bin/assetfinder',
        'subfinder': '/usr/local/bin/subfinder'
    }