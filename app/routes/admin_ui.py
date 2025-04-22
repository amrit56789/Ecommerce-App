from flask import Blueprint, render_template, session, redirect, url_for
from functools import wraps

admin_ui = Blueprint("admin_ui", __name__, url_prefix="/admin")

@admin_ui.route("/login")
def login_page():
    if 'access_token' in session:
        return redirect(url_for('admin_ui.dashboard'))
    return render_template("admin/login.html")

@admin_ui.route('/dashboard')
def dashboard():
    return render_template('admin/dashboard.html')


@admin_ui.route('/signup')
def signup_page():
    return render_template('admin/signup.html')

@admin_ui.route('/forgot-password')
def forgot_password():
    return render_template('admin/forgot_password.html')
