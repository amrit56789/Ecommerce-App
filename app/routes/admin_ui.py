from flask import Blueprint, render_template, session, redirect, url_for

admin_ui = Blueprint("admin_ui", __name__, url_prefix="/admin")

@admin_ui.route("/login")
def login_page():
    return render_template("admin/login.html")

@admin_ui.route("/dashboard")
def dashboard():
    return render_template("admin/dashboard.html")
