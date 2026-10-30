import os
import uuid
from flask import Blueprint, request, jsonify
from ..config import UPLOAD_DIR, ALLOWED_IMAGE_EXT, MAX_UPLOAD_SIZE
from ..utils import login_required

bp = Blueprint("upload", __name__)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXT


@bp.route("/upload", methods=["POST"])
@login_required
def upload():
    if "file" not in request.files:
        return jsonify(code=400, message="No file provided"), 400
    f = request.files["file"]
    if not f or not f.filename:
        return jsonify(code=400, message="No file selected"), 400
    if not allowed_file(f.filename):
        return jsonify(code=400, message="Only image files are allowed (png, jpg, jpeg, gif, webp)"), 400

    f.seek(0, os.SEEK_END)
    size = f.tell()
    f.seek(0)
    if size > MAX_UPLOAD_SIZE:
        return jsonify(code=400, message="Image must be smaller than 5 MB"), 400

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = f.filename.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    f.save(os.path.join(UPLOAD_DIR, filename))
    return jsonify(code=0, message="Image uploaded", data={"url": f"/uploads/{filename}"})
