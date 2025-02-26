import os
from flask import Flask, render_template, request, jsonify, send_from_directory
import ffmpeg
import uuid
import logging

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.DEBUG)

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(extension="mp3"):
    return f"{uuid.uuid4().hex}.{extension}"

@app.route("/")
def index():
    return render_template("2index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    unique_filename = generate_unique_filename(file.filename.rsplit('.', 1)[1].lower())
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    file.save(file_path)

    return jsonify({"filename": unique_filename})

@app.route("/process_audio", methods=["POST"])
def process_audio():
    data = request.json
    if not data or "filename" not in data or "pitch" not in data:
        return jsonify({"error": "Missing required fields"}), 400

    filename = data["filename"]
    pitch = float(data["pitch"])

    input_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(input_path):
        return jsonify({"error": "File not found"}), 404

    try:
        output_filename = generate_unique_filename()
        output_path = os.path.join(PROCESSED_FOLDER, output_filename)

        # Apply pitch shift using FFmpeg
        ffmpeg.input(input_path).filter("asetrate", 44100 * (2 ** (pitch / 12))).output(output_path).run()

        return jsonify({"message": "Audio processed", "filename": output_filename})
    except Exception as e:
        logging.error(f"Error processing audio: {e}")
        return jsonify({"error": str(e)}), 500



@app.route("/download/<filename>")
def download_file(filename):
    file_path = os.path.join(PROCESSED_FOLDER, filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    return send_from_directory(PROCESSED_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
