from flask import Flask, redirect, url_for
from app.extensions import db, jwt, mail, bcrypt
from .config import Config 

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)

    from app.models.user import User
    from app.models.role import Role

    Role.initialize_roles()
    User.create_default_admin()

    from app.routes.auth import auth_bp
    from app.routes.admin_ui import admin_ui
    from app.routes.user import user_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_ui)
    app.register_blueprint(user_bp)

    @app.route('/')
    def index():
        return redirect(url_for('admin_ui.login_page'))

    return app
