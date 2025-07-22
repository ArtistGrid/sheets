from flask import Flask, send_file, send_from_directory, jsonify
from flask_cors import CORS
import threading
import os
import json

from config import HTML_FILENAME, CSV_FILENAME, XLSX_FILENAME
from update_loop import update_loop

app = Flask(__name__)
CORS(app)

# Serve main files
@app.route("/artists.html")
def serve_artists_html():
    return send_file(HTML_FILENAME, mimetype="text/html")

@app.route("/artists.csv")
def serve_artists_csv():
    return send_file(CSV_FILENAME, mimetype="text/csv")

@app.route("/artists.xlsx")
def serve_artists_xlsx():
    return send_file(XLSX_FILENAME, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Serve index and frontend assets
@app.route("/")
@app.route("/index")
@app.route("/index.html")
def serve_index():
    return send_file("templates/index.html", mimetype="text/html")

@app.route("/_next/<path:filename>")
def serve_next_static(filename):
    return send_from_directory("templates/_next", filename)

# Serve /info JSON
@app.route("/info")
def info_json():
    info_path = os.path.join("info", "status.json")
    if os.path.exists(info_path):
        with open(info_path) as f:
            return jsonify(json.load(f))
    return {"error": "Info not available"}, 404

# Serve /info HTML
@app.route("/info/html")
def info_html():
    info_path = os.path.join("info", "status.json")
    if os.path.exists(info_path):
        with open(info_path) as f:
            data = json.load(f)
        html = f"""
        <html>
        <head><title>File Info</title></head>
        <body>
            <h1>Latest File Info</h1>
            <p><strong>Last Updated:</strong> {data.get('last_updated')}</p>
            <ul>
                <li><strong>Artists.html</strong><br>
                    Hash: {data['files']['Artists.html']['hash']}<br>
                    Archived: {data['files']['Artists.html']['last_archived']}
                </li>
                <li><strong>artists.csv</strong><br>
                    Hash: {data['files']['artists.csv']['hash']}
                </li>
                <li><strong>artists.xlsx</strong><br>
                    Hash: {data['files']['artists.xlsx']['hash']}
                </li>
            </ul>
        </body>
        </html>
        """
        return html
    return "<p>Status info not available.</p>", 404

# 404 page
@app.errorhandler(404)
def page_not_found(e):
    return send_file("templates/404.html", mimetype="text/html"), 404

# Start app and updater
if __name__ == "__main__":
    # Run update loop in background
    threading.Thread(target=update_loop, daemon=True).start()

    # Optional: perform initial download/generation if needed
    from downloader import download_zip_and_extract_html, download_xlsx
    from parser import generate_csv

    # Uncomment below if you want to do initial sync before serving
    # download_zip_and_extract_html()
    # download_xlsx()
    # generate_csv()

    app.run(host="0.0.0.0", port=5000)
