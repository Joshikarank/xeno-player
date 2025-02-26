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

# Ensure FFmpeg is accessible
os.environ["PATH"] += os.pathsep + "C:/ffmpeg/bin"

# Set up logging
logging.basicConfig(level=logging.DEBUG)

def generate_unique_filename(extension="mp3"):
    return f"{uuid.uuid4().hex}.{extension}"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    filename = file.filename
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    return jsonify({"message": "Upload successful", "filename": filename}), 200

@app.route("/process_audio", methods=["POST"])
def process_audio():
    data = request.json
    filename = data.get("filename")
    pitch = float(data.get("pitch", 0.0))

    if not filename:
        return jsonify({"error": "Filename is required"}), 400

    input_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(input_path):
        return jsonify({"error": "File not found"}), 404

    output_filename = generate_unique_filename()
    processed_path = os.path.join(PROCESSED_FOLDER, output_filename)

    try:
        # Process audio with FFmpeg (Apply Pitch Shift)
        ffmpeg.input(input_path).filter("asetrate", 44100 * (2 ** (pitch / 12))).output(processed_path).run()

        return jsonify({"message": "Audio processed", "filename": output_filename}), 200
    except Exception as e:
        logging.error(f"Error processing audio: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(PROCESSED_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
