import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "siddhivinayak-super-secret-key-change-me")

    # --- DATABASE ---
    # By default the app runs on SQLite so it works out of the box with zero
    # setup. To use MySQL (as specified in the brief) just set the
    # DATABASE_URL environment variable, e.g.:
    #   mysql+pymysql://user:password@localhost/siddhivinayak_expense_manager
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'siddhivinayak.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    WTF_CSRF_ENABLED = True

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "images")
    EXPORT_FOLDER = os.path.join(BASE_DIR, "static", "exports")

    # Default company info (editable later from Admin > Settings)
    COMPANY_NAME = "SIDDHIVINAYAK ENGINEERING & TRADING CORPORATION"
    COMPANY_ADDRESS_LINE1 = "169 AAREY MILK COLONY, PODACCITY-3 CO-OP HSGS LTD,"
    COMPANY_ADDRESS_LINE2 = "GOREGAON EAST, MUMBAI SUBURBAN, MAHARASHTRA, 400065"
    COMPANY_MOBILE = "+91 00000 00000"

    # Default per-KM rates (editable later from Admin > Rates)
    BIKE_RATE_PER_KM = 4.50
    CAR_RATE_PER_KM = 10.00
    OTHER_VEHICLE_RATE_PER_KM = 6.00
