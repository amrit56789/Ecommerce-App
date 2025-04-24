from flask import Blueprint, render_template, session, redirect, url_for
from functools import wraps

admin_ui = Blueprint("admin_ui", __name__, url_prefix="")

@admin_ui.route("/login")
def login_page():
    if 'access_token' in session:
        return redirect(url_for('admin_ui.dashboard'))
    return render_template("admin/authFlow/login.html")

@admin_ui.route('/signup')
def signup_page():
    return render_template('admin/authFlow/signup.html')

@admin_ui.route('/forgot-password')
def forgot_password():
    return render_template('admin/authFlow/forgot_password.html')

@admin_ui.route('/verify-otp')
def verify_otp():
    return render_template('admin/authFlow/verify-otp.html')

@admin_ui.route('/reset-password')
def reset_password():
    return render_template('admin/authFlow/reset-password.html')



@admin_ui.route('/dashboard')
def dashboard():
    return render_template('admin/dashboardPage/dashboard.html')