import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "your-secret-key"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI") or "sqlite:///bbhunter.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL") or "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND") or "redis://localhost:6379/0"
    # Directories for tool output and reports
    OUTPUT_DIR = os.environ.get("OUTPUT_DIR") or os.path.join(os.getcwd(), "output")
    REPORTS_DIR = os.environ.get("REPORTS_DIR") or os.path.join(os.getcwd(), "reports")
    # Paths to external tools (adjust as needed)
    TOOL_PATHS = {
        "assetfinder": os.environ.get("ASSETFINDER_PATH") or "/usr/local/bin/assetfinder",
        "subfinder": os.environ.get("SUBFINDER_PATH") or "/usr/local/bin/subfinder",
        "amass": os.environ.get("AMASS_PATH") or "/usr/local/bin/amass",
        "httpx": os.environ.get("HTTPX_PATH") or "/usr/local/bin/httpx",
        "dnsx": os.environ.get("DNSX_PATH") or "/usr/local/bin/dnsx",
        "katana": os.environ.get("KATANA_PATH") or "/usr/local/bin/katana",
        "gau": os.environ.get("GAU_PATH") or "/usr/local/bin/gau",
        "gospider": os.environ.get("GOSPIDER_PATH") or "/usr/local/bin/gospider",
        "nuclei": os.environ.get("NUCLEI_PATH") or "/usr/local/bin/nuclei",
        "waybackurls": os.environ.get("WAYBACKURLS_PATH") or "/usr/local/bin/waybackurls",
        "ffuf": os.environ.get("FFUF_PATH") or "/usr/local/bin/ffuf",
    }