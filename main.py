# main.py
import json
import logging
import os
import threading

from flask import Flask, jsonify, send_file, send_from_directory
from flask_cors import CORS

from config import CSV_FILENAME, HTML_FILENAME, XLSX_FILENAME
from update_loop import update_loop

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)


@app.route("/")
def serve_index():
    return send_file("templates/index.html")


@app.route("/artists.html")
def serve_artists_html():
    return send_file(HTML_FILENAME)


@app.route("/artists.csv")
def serve_artists_csv():
    return send_file(CSV_FILENAME)


@app.route("/artists.xlsx")
def serve_artists_xlsx():
    return send_file(XLSX_FILENAME)


@app.route("/_next/<path:filename>")
def serve_next_static(filename):
    return send_from_directory("templates/_next", filename)


def get_status_data():
    info_path = os.path.join("info", "status.json")
    if not os.path.exists(info_path):
        return None
    try:
        with open(info_path, "r") as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        logger.error(f"Failed to read or parse status.json: {e}")
        return None


@app.route("/info")
def info_json():
    data = get_status_data()
    if data:
        return jsonify(data)
    return jsonify({"error": "Info not available"}), 404


@app.route("/info/html")
def info_html():
    data = get_status_data()
    if not data:
        return "<p>Status info not available.</p>", 404

    files_info = data.get("files", {})
    html_info = files_info.get(HTML_FILENAME, {})
    csv_info = files_info.get(CSV_FILENAME, {})
    xlsx_info = files_info.get(XLSX_FILENAME, {})

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>File Info</title>
        <style>body {{ font-family: sans-serif; }} li {{ margin-bottom: 1em; }}</style>
    </head>
    <body>
        <h1>Latest File Info</h1>
        <p><strong>Last Updated:</strong> {data.get('last_updated', 'N/A')}</p>
        <ul>
            <li><strong>{HTML_FILENAME}</strong><br>
                Hash: {html_info.get('hash', 'N/A')}<br>
                Archived: {html_info.get('last_archived', 'N/A')}
            </li>
            <li><strong>{CSV_FILENAME}</strong><br>
                Hash: {csv_info.get('hash', 'N/A')}
            </li>
            <li><strong>{XLSX_FILENAME}</strong><br>
                Hash: {xlsx_info.get('hash', 'N/A')}
            </li>
        </ul>
    </body>
    </html>
    """


@app.errorhandler(404)
def page_not_found(e):
    return send_file("templates/404.html"), 404


if __name__ == "__main__":
    logger.info("Starting background update thread...")
    threading.Thread(target=update_loop, daemon=True).start()
    logger.info("Starting Flask server...")
    app.run(host="0.0.0.0", port=5000)