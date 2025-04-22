# auth.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from flask_mail import Message
from app import bcrypt, mail
import random
from datetime import datetime, timedelta
from .auth_decorator import role_required
import cloudinary
import cloudinary.uploader
from app.models.user import User
from app.models.role import Role
from app.helpers.auth_helpers import validate_email, validate_password

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Register API
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    role_name = data.get('role', 'user')

    is_valid_email, email_error = validate_email(email)
    if not is_valid_email:
        return jsonify({'message': email_error}), 400

    is_valid_password, password_error = validate_password(password)
    if not is_valid_password:
        return jsonify({'message': password_error}), 400

    if User.objects(email=email).first():
        return jsonify({'message': 'Email already exists'}), 409

    role = Role.objects(name=role_name).first()
    if not role:
        return jsonify({'message': 'Invalid role'}), 400

    user = User(
        email=email,
        password=password,
        role=role
    )
    user.hash_password()
    user.save()

    return jsonify({'message': 'User registered successfully'}), 201

# Login API
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    is_valid_email, email_error = validate_email(email)
    if not is_valid_email:
        return jsonify({'message': email_error}), 400

    # Password validation (checking if empty or less than 8 characters)
    if not password:
        return jsonify({'message': 'Password is required'}), 400
    
    user = User.objects(email=email).first()

    if not user:
        return jsonify({'message': 'User with this email does not exist'}), 404

    if not user.check_password(password):
        return jsonify({'message': 'Invalid password'}), 401

    access_token = create_access_token(identity=str(user.id), additional_claims={'role': user.role})

    return jsonify({
        'message': 'Login successful',
        'access_token': access_token
    }), 200


# Forgot Password API (Send OTP)
@auth_bp.route('/send-email-code', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'message': 'Email is required'}), 400

    user = User.objects(email=email).first()
    if not user:
        return jsonify({'message': 'No account associated with this email address'}), 400

    otp = ''.join(random.choices('0123456789', k=6))
    expiry_time = datetime.utcnow() + timedelta(minutes=10)

    user.reset_otp = otp
    user.otp_expiry = expiry_time
    user.save()

    msg = Message(
        subject='Your OTP for Password Reset',
        recipients=[user.email],
        body=f"Your OTP is {otp}. It will expire in 10 minutes."
    )

    try:
        mail.send(msg)
        print(f"OTP email sent successfully to: {user.email}")
        return jsonify({'message': 'OTP sent successfully'}), 200
    except Exception as e:
        print(f"Error sending email: {e}")
        return jsonify({'message': 'Failed to send OTP email'}), 500

# Verify OTP API
@auth_bp.route('/verify-email-code', methods=['POST'])
def verify_email_code():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('code')

    if not email or not otp:
        return jsonify({'message': 'Email and OTP are required'}), 400

    user = User.objects(email=email).first()
    if not user:
        return jsonify({'message': 'Invalid email or OTP'}), 400

    if not user.reset_otp or not user.otp_expiry:
        return jsonify({'message': 'No OTP requested for this email'}), 400

    current_time = datetime.utcnow()
    if user.reset_otp != otp:
        return jsonify({'message': 'Invalid OTP'}), 400
    if current_time > user.otp_expiry:
        return jsonify({'message': 'OTP has expired'}), 400

    user.save()

    return jsonify({'message': 'OTP verified successfully'}), 200

# Reset Password API
@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('code')
    new_password = data.get('password')

    if not email or not otp or not new_password:
        return jsonify({'message': 'Email, OTP, and new password are required'}), 400

    user = User.objects(email=email).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    if user.reset_otp != otp:
        return jsonify({'message': 'Invalid OTP'}), 400

    if user.otp_expiry and user.otp_expiry < datetime.utcnow():
        return jsonify({'message': 'OTP has expired'}), 400

    user.password = new_password
    user.hash_password()
    user.reset_otp = None
    user.otp_expiry = None
    user.save()

    return jsonify({'message': 'Password reset successfully'}), 200
