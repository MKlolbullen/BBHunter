from celery import Celery
from config import Config
import subprocess
import os
from flask_socketio import SocketIO
from models import db, ScanResult
from flask import Flask
import logging
import shlex

# Set up structured logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def make_celery(app):
    celery = Celery(app.import_name, broker=Config.CELERY_BROKER_URL)
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
socketio = SocketIO(message_queue=Config.CELERY_BROKER_URL)
celery = make_celery(app)

@celery.task()
def run_tool_task(tool, target, user_id, scan_id):
    output_dir = os.path.join(Config.OUTPUT_DIR, scan_id)
    output_file = os.path.join(output_dir, f"{target}_{tool}_results.txt")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    try:
        # Construct the command based on the tool
        if tool == "assetfinder":
            cmd = f"{Config.TOOL_PATHS['assetfinder']} --subs-only {target}"
        elif tool == "subfinder":
            cmd = f"{Config.TOOL_PATHS['subfinder']} -d {target}"
        elif tool == "amass":
            cmd = f"{Config.TOOL_PATHS['amass']} enum -d {target}"
        elif tool == "httpx":
            subdomains_file = os.path.join(output_dir, f"{target}_subdomains.txt")
            cmd = f"{Config.TOOL_PATHS['httpx']} -silent -title -status-code -follow-redirects -o {output_file} -l {subdomains_file}"
        elif tool == "dnsx":
            subdomains_file = os.path.join(output_dir, f"{target}_subdomains.txt")
            cmd = f"{Config.TOOL_PATHS['dnsx']} -a -aaaa -cname -mx -ns -txt -resp -o {output_file} -l {subdomains_file}"
        elif tool == "katana":
            cmd = f"{Config.TOOL_PATHS['katana']} -u {target} -o {output_file}"
        elif tool == "gau":
            cmd = f"{Config.TOOL_PATHS['gau']} {target}"
        elif tool == "gospider":
            cmd = f"{Config.TOOL_PATHS['gospider']} -s {target} -o {Config.OUTPUT_DIR}"
        elif tool == "nuclei":
            cmd = f"{Config.TOOL_PATHS['nuclei']} -target {target} -t /path/to/nuclei-templates/ -o {output_file}"
        elif tool == "waybackurls":
            cmd = f"echo {target} | {Config.TOOL_PATHS['waybackurls']} > {output_file}"
        elif tool == "ffuf":
            wordlist = "/usr/share/wordlists/dirb/common.txt"
            cmd = f"{Config.TOOL_PATHS['ffuf']} -u http://{target}/FUZZ -w {wordlist} -o {output_file}"
        else:
            cmd = f"{tool} {target}"

        logger.info(f"Executing command: {cmd}")
        # Use shlex.split() if no shell redirection or pipes are present
        if '>' not in cmd and '|' not in cmd:
            cmd_args = shlex.split(cmd)
            process = subprocess.Popen(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        else:
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            result = stdout.strip()
            message = f"Completed {tool} on {target}"
        else:
            result = stderr.strip()
            message = f"Error running {tool} on {target}"
        
        # Save result to file
        with open(output_file, 'w') as f:
            f.write(result)
        
        # Store the scan result in the database
        scan_result = ScanResult(
            user_id=user_id,
            domain=target,
            tool=tool,
            result=result,
            scan_id=scan_id
        )
        db.session.add(scan_result)
        db.session.commit()
        logger.info(f"{tool} completed on {target}.")
        # Emit the result via Socket.IO
        socketio.emit('tool_result', {
            'tool': tool,
            'result': result,
            'message': message,
            'scan_id': scan_id
        }, room=scan_id)
    except Exception as e:
        error_message = f"Exception running {tool} on {target}: {str(e)}"
        logger.error(error_message)
        socketio.emit('tool_result', {
            'tool': tool,
            'result': '',
            'message': error_message,
            'scan_id': scan_id
        }, room=scan_id)