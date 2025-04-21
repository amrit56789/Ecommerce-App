# app/__init__.py
from flask import Flask
from flask_mongoengine import MongoEngine
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from .config import Config

db = MongoEngine()
jwt = JWTManager()
mail = Mail()
bcrypt = Bcrypt()

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
    
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    return app
