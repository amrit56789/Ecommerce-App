from flask import Blueprint, render_template, session, redirect, url_for, request, g
from app.models import User
from mongoengine import Q
from mongoengine.queryset.visitor import Q
from constants import  Login_WEB_URL, SIGNUP_WEB_URL, FORGOT_PASSWORD_WEB_URL, VERIFY_OTP_WEB_URL, RESET_PASSWORD_WEB_URL, DASHBOARD_WEB_URL, ALL_USER_LIST_WEB_URL

admin_ui = Blueprint("admin_ui", __name__, url_prefix="")

@admin_ui.route(Login_WEB_URL)
def login_page():
    if 'access_token' in session:
        return redirect(url_for('admin_ui.dashboard'))

    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        user = User.objects(username=username, password=password).first()

        if user:
            session['access_token'] = user.access_token
            session['user_id'] = str(user.id)
            return redirect(url_for('admin_ui.dashboard'))
        else:
            return render_template("admin/authFlow/login.html", error="Invalid credentials")

    return render_template("admin/authFlow/login.html")

@admin_ui.route(SIGNUP_WEB_URL)
def signup_page():
    return render_template('admin/authFlow/signup.html')

@admin_ui.route(FORGOT_PASSWORD_WEB_URL)
def forgot_password():
    return render_template('admin/authFlow/forgot_password.html')

@admin_ui.route(VERIFY_OTP_WEB_URL)
def verify_otp():
    return render_template('admin/authFlow/verify-otp.html')

@admin_ui.route(RESET_PASSWORD_WEB_URL)
def reset_password():
    return render_template('admin/authFlow/reset-password.html')


@admin_ui.route(DASHBOARD_WEB_URL)
def dashboard():
    if g.current_user is None:
        return redirect(url_for('admin_ui.login_page'))
    return render_template("admin/dashboardPage/dashboard.html", users=g.current_user)



@admin_ui.route(ALL_USER_LIST_WEB_URL)
def all_users():
    if 'user_id' not in session:
        return redirect(url_for('admin_ui.login_page'))

    search = request.args.get('search', '')
    users_data = []

    if search:
        # Use MongoDB aggregation for search
        raw_users = User.objects.aggregate([
            {
                "$lookup": {
                    "from": "role",
                    "localField": "role",
                    "foreignField": "_id",
                    "as": "role_info"
                }
            },
            {
                "$unwind": {
                    "path": "$role_info",
                    "preserveNullAndEmptyArrays": True
                }
            },
            {
                "$match": {
                    "$or": [
                        {"first_name": {"$regex": search, "$options": "i"}},
                        {"last_name": {"$regex": search, "$options": "i"}},
                        {"email": {"$regex": search, "$options": "i"}},
                        {"role_info.name": {"$regex": search, "$options": "i"}}
                    ]
                }
            }
        ])
    else:
        raw_users = User.objects()

    for u in raw_users:
        if isinstance(u, dict):
            users_data.append({
                "first_name": u.get("first_name", "---") or "---",
                "last_name": u.get("last_name", "---") or "---",
                "email": u.get("email", "---") or "---",
                "phone_number": u.get("phone_number", "---") or "---",
                "role": u.get("role_info", {}).get("name", "---") if u.get("role_info") else "---"
            })
        else:
            users_data.append({
                "first_name": u.first_name or "---",
                "last_name": u.last_name or "---",
                "email": u.email or "---",
                "phone_number": u.phone_number or "---",
                "role": u.role.name if u.role and u.role.name else "---"
            })

    return render_template("admin/users/allUserList.html", allUsersList=users_data, filters={'search': search})


@admin_ui.route('/users/add')
def add_user():
    if 'user_id' not in session:
        return redirect(url_for('admin_ui.login_page'))
    return render_template("admin/users/add.html")