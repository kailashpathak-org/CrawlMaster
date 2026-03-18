import sqlite3
import sys
from flask import Flask, render_template
from scanner.detector import run_scan

app = Flask(__name__)

DB_PATH = "storage/threat_monitor.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM findings")
    total_findings = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM findings WHERE severity='HIGH'")
    high_findings = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM findings WHERE severity='CRITICAL'")
    critical_findings = cursor.fetchone()[0]

    cursor.execute("""
        SELECT company, repo, file_path, keyword, severity, last_seen
        FROM findings
        ORDER BY last_seen DESC
        LIMIT 10
    """)
    recent_findings = cursor.fetchall()

    cursor.execute("""
        SELECT severity, COUNT(*) as count
        FROM findings
        GROUP BY severity
    """)
    severity_data = cursor.fetchall()

    severity_labels = []
    severity_counts = []

    for row in severity_data:
        severity_labels.append(row["severity"])
        severity_counts.append(row["count"])

    cursor.execute("""
        SELECT DATE(last_seen) as date, COUNT(*) as count
        FROM findings
        GROUP BY DATE(last_seen)
        ORDER BY DATE(last_seen)
    """)
    time_data = cursor.fetchall()

    dates = []
    counts = []

    for row in time_data:
        dates.append(row["date"])
        counts.append(row["count"])

    conn.close()

    return render_template(
        "dashboard.html",
        total_findings=total_findings,
        high_findings=high_findings,
        critical_findings=critical_findings,
        recent_findings=recent_findings,
        severity_labels=severity_labels,
        severity_counts=severity_counts,
        dates=dates,
        counts=counts
    )


# CLI scanning
if __name__ == "__main__":

    if len(sys.argv) > 1 and sys.argv[1] == "scan":

        if len(sys.argv) < 3:
            print("Usage: python3 app.py scan <company>")
            sys.exit(1)

        company = sys.argv[2]

        print(f"[INFO] Scanning company: {company}")

        run_scan(company)

    else:
        app.run(debug=True)
