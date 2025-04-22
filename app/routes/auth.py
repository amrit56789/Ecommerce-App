from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_mail import Message
from app import bcrypt, mail
import random
from datetime import datetime, timedelta
from .auth_decorator import role_required
import cloudinary
import cloudinary.uploader

auth_bp = Blueprint('auth', __name__)

from flask import request, jsonify
from app.models.user import User
from app.models.role import Role

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not all(key in data for key in ['email', 'password']):
        return jsonify({'message': 'Missing required fields'}), 400

    if data.get('role'):
        role = Role.objects(name=data['role']).first()
        if not role:
            return jsonify({'message': 'Invalid role'}), 400
    else:
        role = Role.objects(name='user').first()
    
    if User.objects(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 409

    user = User(
        email=data['email'],
        password=data['password'],
        role=role.name
    )
    user.hash_password()
    user.save()

    return jsonify({'message': 'User registered successfully'}), 201


# user login api
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not all(key in data for key in ['email', 'password']):
        return jsonify({'message': 'Missing email or password'}), 400

    user = User.objects(email=data['email']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Please enter a valid password'}), 401

    access_token = create_access_token(identity=str(user.id), additional_claims={'role': user.role})
    return jsonify({'access_token': access_token, 'role': user.role}), 200

# forget password api
@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'message': 'Email is required'}), 400

    user = User.objects(email=email).first()
    if not user:
        return jsonify({'message': 'If this email exists, an OTP has been sent'}), 200

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

# reset password
@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')
    new_password = data.get('new_password')

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

# get user profile
@auth_bp.route('/user-profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    user_id = get_jwt_identity()
    user = User.objects(id=user_id).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    profile = {
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'gender': user.gender,
        'phone_number': user.phone_number,
        'profile_picture': user.profile_picture,
        'created_at': user.created_at
    }

    return jsonify({
        'role': user.role,
        'profile': profile
    }), 200

# update user profile
@auth_bp.route('/update-profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()

    user = User.objects(id=user_id).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    data = request.get_json()

    first_name = data.get('first_name')
    last_name = data.get('last_name')
    phone_number = data.get('phone_number')
    gender = data.get('gender')

    if first_name:
        user.first_name = first_name
    if last_name:
        user.last_name = last_name
    if phone_number:
        user.phone_number = phone_number
    if gender:
        user.gender = gender

    user.save()

    return jsonify({'message': 'Profile updated successfully'}), 200

# update user profile picture
@auth_bp.route('/update-profile-picture', methods=['POST'])
@jwt_required()
def update_profile_picture():
    user_id = get_jwt_identity()
    user = User.objects(id=user_id).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    if 'profile_picture' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    file = request.files['profile_picture']

    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    try:
        if user.cloudinary_id:
            cloudinary.uploader.destroy(user.cloudinary_id)

        upload_result = cloudinary.uploader.upload(file)
        profile_url = upload_result.get('secure_url')
        public_id = upload_result.get('public_id')

        user.profile_picture = profile_url
        user.cloudinary_id = public_id
        user.save()

        return jsonify({
            'message': 'Profile picture updated successfully',
            'profile_picture': profile_url
        }), 200

    except Exception as e:
        return jsonify({'message': 'Upload failed', 'error': str(e)}), 500

# delete user profile picture
@auth_bp.route('/delete-profile-picture', methods=['DELETE'])
@jwt_required()
def delete_profile_picture():
    user_id = get_jwt_identity()
    user = User.objects(id=user_id).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    if not user.cloudinary_id:
        return jsonify({'message': 'No profile picture found'}), 404

    try:
        cloudinary.uploader.destroy(user.cloudinary_id)

        user.profile_picture = None
        user.cloudinary_id = None
        user.save()

        return jsonify({'message': 'Profile picture deleted successfully'}), 200

    except Exception as e:
        return jsonify({'message': 'Deletion failed', 'error': str(e)}), 500
