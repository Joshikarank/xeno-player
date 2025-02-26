from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import ffmpeg

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files["file"]
    filename = file.filename
    file.save(os.path.join(UPLOAD_FOLDER, filename))
    return jsonify({"message": "File uploaded", "filename": filename})

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(PROCESSED_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
