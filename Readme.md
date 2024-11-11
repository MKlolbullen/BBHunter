

---

🕵️‍♂️ <b> BBHunter - Bug Bounty Hunter Automation Tool </b>

BBHunter is a comprehensive web-based application designed for penetration testers, bug bounty hunters, and cybersecurity researchers. It automates reconnaissance and information gathering using a combination of popular tools, providing real-time results, analytics, and detailed reports.

🚀 Features

User Authentication: Secure login, registration, and profile management.

Reconnaissance Automation: Uses popular tools like assetfinder, subfinder, amass, httpx, katana, gau, gospider, nuclei, waybackurls, and ffuf.



---

Real-time Results: Uses Socket.IO to provide live updates of scan results.

Dashboard Analytics: Visualize scan activities, tool usage, and other metrics using interactive charts.

Detailed Reports: Generate and download HTML reports for each scan.

API Integration: Exposes endpoints for starting scans and retrieving results programmatically.

Asynchronous Task Management: Leverages Celery and Redis for handling long-running scans without blocking the web interface.

Extensible: Easily add new tools or extend functionality as needed.



---

📋 Table of Contents

- Installation

- Getting Started

- Usage

- API Documentation

- Dashboard Analytics

- Generating Reports

- Configuration

- Supported Tools

- Contributing

- License



---

🔧 Installation

Before getting started, ensure you have the following installed:

Python 3.8+

Redis

Celery

Node.js (for Socket.IO)

External tools like assetfinder, subfinder, amass, httpx, etc.


1. Clone the Repository

git clone https://github.com/yourusername/bbhunter.git
cd bbhunter

2. Install Python Dependencies

Make sure you have pip installed:

pip install -r requirements.txt

3. Install and Start Redis

On Ubuntu/Debian:

sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server

On macOS:

brew install redis
redis-server

4. Install External Tools

Ensure you have the required tools installed and accessible in your PATH. Update the paths in config.py if necessary.

5. Initialize the Database

python app.py

This will create the SQLite database and the necessary tables.

6. Start the Celery Worker

celery -A tasks.celery worker --loglevel=info

7. Run the Flask Application

python app.py

Navigate to http://localhost:5000 in your browser.


---

🏁 Getting Started

1. Register a New User

Go to http://localhost:5000/register and create a new account.

Once registered, log in using your credentials.


2. Configure Your Profile

Update your email and other profile details as needed.


3. Start a Reconnaissance Scan

Enter a target domain.

Select the tools you want to run.

Click Start Reconnaissance to begin the scan.


4. View Results in Real-Time

Real-time scan results will appear on the home page.

You can view detailed results, download reports, or analyze data on the dashboard.



---

📡 API Documentation

Start a New Scan

Endpoint: /api/start_scan
Method: POST

Payload:

{
  "target_domain": "example.com",
  "selected_tools": ["httpx", "amass"]
}

Response:

{
  "message": "Scan started",
  "scan_id": "unique-scan-id"
}

Get Scan Results

Endpoint: /api/scan/<scan_id>
Method: GET

Response:

{
  "id": 1,
  "domain": "example.com",
  "tool": "httpx",
  "result": "Sample output of the tool..."
}


---

📊 Dashboard Analytics

Visualize scan activity over time.

Track the most frequently used tools.

Gain insights into your reconnaissance efforts.


Dashboard Features

Scan Activity: Line chart showing the number of scans over time.

Tool Usage: Bar chart displaying the frequency of tool usage.



---

📄 Generating Reports

After a scan completes, you can generate detailed HTML reports.

Reports can be downloaded from the home page or accessed via the /download_report/<scan_id> endpoint.



---

⚙️ Configuration

The config.py file contains various settings:

SECRET_KEY: Change this for production.

DATABASE_URI: Modify this if using a different database.

TOOL_PATHS: Update paths to external tools as needed.

REDIS & CELERY: Configure Redis and Celery settings if needed.



---

🛠 Supported Tools

BBHunter integrates with the following tools:

assetfinder: Subdomain enumeration

subfinder: Subdomain discovery

amass: In-depth reconnaissance

httpx: HTTP probing

dnsx: DNS information gathering

katana: Web crawling

gau: Archive URL discovery

gospider: Fast web spidering

nuclei: Vulnerability scanning

waybackurls: Historical URLs

ffuf: Fuzzing



---

🤝 Contributing

Contributions are welcome! Here's how you can get involved:

1. Fork the project.


2. Create a new branch (git checkout -b feature-branch).


3. Commit your changes (git commit -m 'Add new feature').


4. Push to the branch (git push origin feature-branch).


5. Open a pull request.




---

📜 License

This project is licensed under the MIT License - see the LICENSE file for details.


---

💬 Contact

For questions or feedback: 0daybullebprotonmail.com

Open an issue on GitHub.

Reach out to me via 0daybullebprotonmail.com



---

📢 Disclaimer

Legal and Ethical Use: This tool is intended for authorized security assessments and penetration testing only. Ensure you have explicit permission from the domain owners before running any scans. Unauthorized use of this tool may violate applicable laws.


---

⭐️ Acknowledgements

Thanks to the developers of the open-source tools integrated into BBHunter.

Special thanks to the Python, Flask, and Celery communities for their support.



---

Thank you for using BBHunter! We hope this tool helps streamline your bug bounty hunting efforts. 🛡️ Happy Bug Bounty Hunting!

