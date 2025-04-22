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
    role = db.ReferenceField('Role', required=True)
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

    @staticmethod
    def create_default_admin():
        from app.models.role import Role

        if not User.objects(email='admin@admin.com').first():
            role = Role.objects(name='admin').first()
            if role:
                admin = User(
                    email='admin@admin.com',
                    password='admin123',
                    role=role
                )
                admin.hash_password()
                admin.save()
                print("Default admin user created.")
            else:
                print("Admin role not found. Cannot create default admin.")
        else:
            print("Admin user already exists.")
