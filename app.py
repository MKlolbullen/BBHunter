from flask import Flask, render_template, request, send_file
from flask_socketio import SocketIO
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from concurrent.futures import ThreadPoolExecutor
import subprocess
import os
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key
socketio = SocketIO(app)
executor = ThreadPoolExecutor()

# User authentication setup
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, id):
        self.id = id

users = {'admin': {'password': 'password'}}  # Replace with a database in production

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            user = User(username)
            login_user(user)
            return redirect('/')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route('/')
@login_required
def home():
    return render_template('index.html')

def is_valid_domain(domain):
    regex = r'^(?!-)[A-Za-z0-9-]{1,63}(?<!-)\.[A-Za-z]{2,6}$'
    return re.match(regex, domain) is not None

def run_tool(tool, target, sid):
    try:
        # Prepare the command based on the tool
        if tool == "amass":
            cmd = f"amass enum -d {target}"
        elif tool == "httpx":
            cmd = f"httpx -silent -title -status-code -follow-redirects -o {target}_httpx_results.txt"
        elif tool == "dnsx":
            cmd = f"dnsx -a -www -o {target}_dnsx_results.txt"
        elif tool == "katana":
            cmd = f"katana -d {target}"
        elif tool == "gau":
            cmd = f"gau {target}"
        elif tool == "gospider":
            cmd = f"gospider -s {target}"
        elif tool == "xsstrike":
            cmd = f"xsstrike -u {target}"
        elif tool == "nuclei":
            cmd = f"nuclei -target {target} -t /path/to/nuclei-templates/"  # Adjust the path to your templates
        else:
            cmd = f"{tool} {target}"

        output = subprocess.check_output(cmd, shell=True).decode("utf-8")
        socketio.emit('tool_result', {'tool': tool, 'result': output}, room=sid)
    except subprocess.CalledProcessError as e:
        socketio.emit('tool_result', {'tool': tool, 'result': f"Error running {tool}: {str(e)}"}, room=sid)

@socketio.on('start_recon')
def start_recon(data):
    target_domain = data['target_domain']
    sid = request.sid

    if not is_valid_domain(target_domain):
        socketio.emit('tool_result', {'tool': 'Validation', 'result': 'Invalid domain format.'}, room=sid)
        return

    tools = {
        "assetfinder": "assetfinder",
        "subfinder": "subfinder",
        "amass": "amass",
        "httpx": "httpx",
        "dnsx": "dnsx",
        "katana": "katana",
        "gau": "gau",
        "gospider": "gospider",
        "xsstrike": "xsstrike",
        "nuclei": "nuclei"
    }

    for tool_name in tools.keys():
        executor.submit(run_tool, tool_name, target_domain, sid)

if __name__ == '__main__':
    socketio.run(app, debug=True)
