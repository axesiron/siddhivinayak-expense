import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "siddhivinayak-super-secret-key-change-me")

    # --- DATABASE ---
    # By default the app runs on SQLite so it works out of the box with zero
    # setup. This is fine for local development, but most free hosts
    # (Render, Railway, etc.) wipe local disk on every deploy/restart, so
    # SQLite data would not persist in production. Set DATABASE_URL to use
    # a real database instead, e.g.:
    #   MySQL:      mysql+pymysql://user:password@host/dbname
    #   PostgreSQL: postgresql://user:password@host/dbname   (Render's free
    #               Postgres add-on provides this — see README for setup)
    _database_url = os.environ.get("DATABASE_URL")
    if _database_url:
        if _database_url.startswith("postgres://"):
            # Some hosts (Render, Heroku) hand out the old "postgres://"
            # scheme; SQLAlchemy 1.4+/2.x requires "postgresql://".
            _database_url = _database_url.replace("postgres://", "postgresql://", 1)
        if _database_url.startswith("postgresql://"):
            # Route through the pg8000 driver (pure Python, no compiled C
            # extension) instead of the default psycopg2 — this avoids
            # binary-compatibility failures on hosts that pick a very new
            # Python version psycopg2's prebuilt wheels don't support yet.
            _database_url = _database_url.replace("postgresql://", "postgresql+pg8000://", 1)

    SQLALCHEMY_DATABASE_URI = _database_url or f"sqlite:///{os.path.join(BASE_DIR, 'siddhivinayak.db')}"
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
    CAR_PETROL_RATE_PER_KM = 10.00
    CAR_CNG_RATE_PER_KM = 6.00
    OTHER_VEHICLE_RATE_PER_KM = 6.00
