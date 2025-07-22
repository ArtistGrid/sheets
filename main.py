from flask import Flask, send_file, send_from_directory
from flask_cors import CORS
import threading

from config import HTML_FILENAME, CSV_FILENAME, XLSX_FILENAME
from update_loop import update_loop

app = Flask(__name__)
CORS(app)

@app.route("/artists.html")
def serve_artists_html():
    return send_file(HTML_FILENAME, mimetype="text/html")

@app.route("/artists.csv")
def serve_artists_csv():
    return send_file(CSV_FILENAME, mimetype="text/csv")

@app.route("/artists.xlsx")
def serve_artists_xlsx():
    return send_file(XLSX_FILENAME, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@app.route("/")
@app.route("/index")
@app.route("/index.html")
def serve_index():
    return send_file("templates/index.html", mimetype="text/html")

@app.route("/_next/<path:filename>")
def serve_next_static(filename):
    return send_from_directory("templates/_next", filename)

@app.errorhandler(404)
def page_not_found(e):
    return send_file("templates/404.html", mimetype="text/html"), 404

if __name__ == "__main__":
    threading.Thread(target=update_loop, daemon=True).start()
    from downloader import download_zip_and_extract_html, download_xlsx
    from parser import generate_csv

    try:
        download_zip_and_extract_html()
        download_xlsx()
        generate_csv()
    except Exception as e:
        print(f"⚠️ Initial update failed: {e}")

    app.run(host="0.0.0.0", port=5000)
