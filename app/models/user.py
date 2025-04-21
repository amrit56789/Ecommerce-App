from app import db
from flask_bcrypt import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Document):
    email = db.StringField(required=True, unique=True)
    password = db.StringField(required=True, min_length=6)
    first_name = db.StringField()
    last_name = db.StringField()
    phone_number = db.StringField()
    gender = db.StringField(choices=["male", "female", "other"])
    role = db.StringField(default='user', choices=['user', 'seller', 'admin'])
    created_at = db.DateTimeField(default=datetime.utcnow)
    reset_token = db.StringField()
    reset_otp = db.StringField()
    otp_expiry = db.DateTimeField()
    profile_picture = db.StringField()
    cloudinary_id = db.StringField()

    def hash_password(self):
        self.password = generate_password_hash(self.password).decode('utf8')

    def check_password(self, password):
        return check_password_hash(self.password, password)
