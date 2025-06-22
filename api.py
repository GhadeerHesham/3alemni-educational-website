import os
import uuid
import tempfile
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Local imports from PdfToBrainrot
import sys
sys.path.append(str(Path(__file__).parent / "PdfToBrainrot" / "src"))
from main import main
from utils.file_utils import get_random_file_from_directory

app = Flask(__name__)
CORS(app)

# Ensure generated reels folder exists
REELS_DIR = Path("static/generated_reels")
REELS_DIR.mkdir(parents=True, exist_ok=True)

@app.route("/generate-reel", methods=["POST"])
def generate_reel():
    if "file" not in request.files:
        return {"error": "No file provided"}, 400

    uploaded_file = request.files["file"]
    lang = request.form.get("lang", "en")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_input:
        uploaded_file.save(temp_input.name)
        input_path = Path(temp_input.name)

    # Output will be saved permanently in static/generated_reels/
    output_filename = f"{uuid.uuid4()}.mp4"
    output_path = REELS_DIR / output_filename

    video_path = get_random_file_from_directory(Path("PdfToBrainrot/video"))
    audio_path = get_random_file_from_directory(Path("PdfToBrainrot/audio"))

    try:
        main(
            input_path=input_path,
            output_path=output_path,
            video_path=video_path,
            audio_path=audio_path,
            no_sub=False,
            no_summary=False,
            lang=lang,
            model="gemini-1.5-flash",
            voice_provider="google",
            volume=0.3,
        )
        return jsonify({"success": True, "filename": output_filename})
    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/list-reels", methods=["GET"])
def list_reels():
    if not REELS_DIR.exists():
        return jsonify([])

    video_urls = [
        f"/static/generated_reels/{file.name}"
        for file in REELS_DIR.glob("*.mp4")
    ]
    return jsonify(video_urls)


@app.route("/static/generated_reels/<filename>")
def serve_reel(filename):
    file_path = REELS_DIR / filename
    if not file_path.exists():
        return {"error": "File not found"}, 404
    return send_file(file_path, mimetype="video/mp4")


if __name__ == "__main__":
    app.run(debug=True)
