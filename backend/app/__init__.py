from flask import Flask, g, jsonify, send_from_directory
from .config import SECRET_KEY, UPLOAD_DIR
from .database import close_db, init_schema
from .routes import register_blueprints


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["JSON_AS_ASCII"] = False
    app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024

    init_schema()
    app.teardown_appcontext(close_db)

    register_blueprints(app)

    @app.after_request
    def add_cors_headers(resp):
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return resp

    @app.errorhandler(404)
    def not_found(e):
        return jsonify(code=404, message="Resource not found"), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify(code=500, message="Internal server error"), 500

    @app.route("/")
    def index():
        return jsonify(code=0, message="Campus Market API is running", data={"name": "campus-market"})

    @app.route("/uploads/<path:filename>")
    def serve_upload(filename):
        return send_from_directory(UPLOAD_DIR, filename)

    return app
