from flask_login import LoginManager
from .models import db, AdminUser  # use your existing models.py
from flask import Flask, render_template

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "CHANGE_THIS_TO_A_RANDOM_SECRET"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///agency.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # init db
    db.init_app(app)

    # login manager (admin only)
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return AdminUser.query.get(int(user_id))

    # blueprints
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/admin")

    # create tables
    with app.app_context():
        db.create_all()
        
        # ---------------------------
    # Custom Error Pages
    # ---------------------------
    @app.errorhandler(400)
    def bad_request(e):
        return render_template("errors/400.html"), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return render_template("errors/401.html"), 401

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        # If you want: db.session.rollback() here to recover from failed transactions
        return render_template("errors/500.html"), 500

    return app