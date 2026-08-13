from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, Employee
from datetime import datetime

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("employee.dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        mobile = request.form.get("mobile", "").strip()
        designation = request.form.get("designation", "").strip()
        department = request.form.get("department", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not all([name, email, password]):
            flash("Name, email and password are required.", "danger")
            return redirect(url_for("auth.register"))

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("auth.register"))

        if Employee.query.filter_by(email=email).first():
            flash("An account with this email already exists.", "danger")
            return redirect(url_for("auth.register"))

        last = Employee.query.order_by(Employee.id.desc()).first()
        next_id = (last.id + 1) if last else 1
        employee_code = f"SVEC-{next_id:03d}"

        emp = Employee(
            employee_code=employee_code,
            name=name,
            email=email,
            mobile=mobile,
            designation=designation,
            department=department,
            joining_date=datetime.utcnow().date(),
            role="employee",
        )
        emp.set_password(password)
        db.session.add(emp)
        db.session.commit()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard" if current_user.is_admin else "employee.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        emp = Employee.query.filter_by(email=email).first()

        if emp is None or not emp.check_password(password):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("auth.login"))

        if emp.is_blocked:
            flash("Your account has been blocked. Contact admin.", "danger")
            return redirect(url_for("auth.login"))

        login_user(emp)
        flash(f"Welcome back, {emp.name.split()[0]}!", "success")
        return redirect(url_for("admin.dashboard" if emp.is_admin else "employee.dashboard"))

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        flash("If this email exists in our system, reset instructions would be sent. "
              "(Email delivery is not wired up in this demo build.)", "info")
        return redirect(url_for("auth.login"))
    return render_template("forgot_password.html")
