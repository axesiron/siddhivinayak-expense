from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Employee(UserMixin, db.Model):
    __tablename__ = "employees"

    id = db.Column(db.Integer, primary_key=True)
    employee_code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobile = db.Column(db.String(20))
    designation = db.Column(db.String(100))
    department = db.Column(db.String(100))
    password_hash = db.Column(db.String(255), nullable=False)
    joining_date = db.Column(db.Date, default=date.today)
    role = db.Column(db.String(20), default="employee")  # employee | admin
    is_blocked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    expenses = db.relationship(
        "Expense", backref="employee", lazy=True, cascade="all, delete-orphan"
    )

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    @property
    def is_active(self):
        return not self.is_blocked

    @property
    def is_admin(self):
        return self.role == "admin"


class Expense(db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)

    expense_date = db.Column(db.Date, nullable=False, default=date.today)
    reason = db.Column(db.String(255), nullable=False)
    mode = db.Column(db.String(20), nullable=False)  # Bike/Bus/Train/Car/Auto/Cab/Other
    from_location = db.Column(db.String(120))
    to_location = db.Column(db.String(120))

    other_amount = db.Column(db.Float, default=0)
    cng_bus_amount = db.Column(db.Float, default=0)
    km = db.Column(db.Float, default=0)
    courier_transport_amount = db.Column(db.Float, default=0)
    food_amount = db.Column(db.Float, default=0)

    km_rate = db.Column(db.Float, default=0)
    km_amount = db.Column(db.Float, default=0)
    total_amount = db.Column(db.Float, default=0)

    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ExpenseRate(db.Model):
    __tablename__ = "expense_rates"

    id = db.Column(db.Integer, primary_key=True)
    bike_rate = db.Column(db.Float, default=4.50)
    car_rate = db.Column(db.Float, default=10.00)
    other_rate = db.Column(db.Float, default=6.00)
    rounding = db.Column(db.String(20), default="nearest")  # nearest | up | down | none


class CompanySettings(db.Model):
    __tablename__ = "company_settings"

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(255))
    address_line1 = db.Column(db.String(255))
    address_line2 = db.Column(db.String(255))
    mobile = db.Column(db.String(50))
    logo_path = db.Column(db.String(255))
