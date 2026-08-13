import os
from datetime import date
from flask import Flask, redirect, url_for
from flask_login import LoginManager, current_user
from flask_wtf import CSRFProtect

from config import Config
from models import db, Employee, ExpenseRate, CompanySettings

from routes.auth import auth_bp
from routes.employee import employee_bp
from routes.admin import admin_bp
from routes.excel import excel_bp

csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.config["EXPORT_FOLDER"], exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(employee_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(excel_bp)

    @login_manager.user_loader
    def load_user(user_id):
        return Employee.query.get(int(user_id))

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("admin.dashboard" if current_user.is_admin else "employee.dashboard"))
        return redirect(url_for("auth.login"))

    @app.context_processor
    def inject_globals():
        return {"current_year": date.today().year, "app_name": "SIDDHIVINAYAK EXPENSE MANAGER"}

    with app.app_context():
        db.create_all()
        _seed_defaults(app)

    return app


def _seed_defaults(app):
    """Create a default admin account and default rate/settings rows if empty."""
    if not ExpenseRate.query.first():
        db.session.add(ExpenseRate(
            bike_rate=app.config["BIKE_RATE_PER_KM"],
            car_rate=app.config["CAR_RATE_PER_KM"],
            other_rate=app.config["OTHER_VEHICLE_RATE_PER_KM"],
        ))

    if not CompanySettings.query.first():
        db.session.add(CompanySettings(
            company_name=app.config["COMPANY_NAME"],
            address_line1=app.config["COMPANY_ADDRESS_LINE1"],
            address_line2=app.config["COMPANY_ADDRESS_LINE2"],
            mobile=app.config["COMPANY_MOBILE"],
        ))

    if not Employee.query.filter_by(role="admin").first():
        admin = Employee(
            employee_code="ADMIN-001",
            name="System Admin",
            email="admin@siddhivinayak.com",
            designation="Administrator",
            department="Management",
            role="admin",
        )
        admin.set_password("Admin@123")
        db.session.add(admin)

    if not Employee.query.filter_by(role="employee").first():
        demo = Employee(
            employee_code="SVEC-001",
            name="Rajkumar Desai",
            email="rajkumar@siddhivinayak.com",
            mobile="9876543210",
            designation="Sales Engineer",
            department="Sales",
            role="employee",
        )
        demo.set_password("Employee@123")
        db.session.add(demo)

    db.session.commit()


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
