from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
import cloudinary.uploader
user_bp = Blueprint('user', __name__, url_prefix='/user')

# Get user profile
@user_bp.route('/me', methods=['GET'])
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
        'profile': profile
    }), 200


# Update user profile
@user_bp.route('/update-profile', methods=['POST'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.objects(id=user_id).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    data = request.get_json()
    user.first_name = data.get('first_name', user.first_name)
    user.last_name = data.get('last_name', user.last_name)
    user.phone_number = data.get('mobile', user.phone_number)
    user.gender = data.get('gender', user.gender)
    user.save()

    return jsonify({'message': 'Profile updated successfully'}), 200


@user_bp.route('/update-profile-pic', methods=['POST'])
@jwt_required()
def update_profile_picture():
    user_id = get_jwt_identity()
    user = User.objects(id=user_id).first()
    
    if not user:
        return {"message": "User not found"}, 404

    if 'profile_picture' not in request.files:
        return {"message": "No file part"}, 400

    file = request.files['profile_picture']
    if file.filename == '':
        return {"message": "No selected file"}, 400

    try:
        if user.cloudinary_id:
            cloudinary.uploader.destroy(user.cloudinary_id)

        upload_result = cloudinary.uploader.upload(file.stream)
        user.profile_picture = upload_result['secure_url']
        user.cloudinary_id = upload_result['public_id']
        user.save()

        return {
            "message": "Profile picture updated",
            "profile_picture": user.profile_picture
        }, 200

    except Exception as e:
        return {"message": "Upload failed", "error": str(e)}, 500

# Delete profile picture
@user_bp.route('/delete-profile-pic', methods=['DELETE'])
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
