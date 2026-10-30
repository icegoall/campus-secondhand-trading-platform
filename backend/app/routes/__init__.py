def register_blueprints(app):
    from .auth import bp as auth_bp
    from .products import bp as products_bp
    from .orders import bp as orders_bp
    from .comments import bp as comments_bp
    from .upload import bp as upload_bp

    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(products_bp, url_prefix="/api")
    app.register_blueprint(orders_bp, url_prefix="/api")
    app.register_blueprint(comments_bp, url_prefix="/api")
    app.register_blueprint(upload_bp, url_prefix="/api")
