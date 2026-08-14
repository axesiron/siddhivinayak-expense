import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "siddhivinayak-super-secret-key-change-me")

    _database_url = os.environ.get("DATABASE_URL")
    if _database_url:
        if _database_url.startswith("postgres://"):
            _database_url = _database_url.replace("postgres://", "postgresql://", 1)
        if _database_url.startswith("postgresql://"):
            _database_url = _database_url.replace("postgresql://", "postgresql+pg8000://", 1)

    SQLALCHEMY_DATABASE_URI = _database_url or f"sqlite:///{os.path.join(BASE_DIR, 'siddhivinayak.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    WTF_CSRF_ENABLED = True

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "images")
    EXPORT_FOLDER = os.path.join(BASE_DIR, "static", "exports")

    COMPANY_NAME = "SIDDHIVINAYAK ENGINEERING & TRADING CORPORATION"
    COMPANY_ADDRESS_LINE1 = "169 AAREY MILK COLONY, PODACCITY-3 CO-OP HSGS LTD,"
    COMPANY_ADDRESS_LINE2 = "GOREGAON EAST, MUMBAI SUBURBAN, MAHARASHTRA, 400065"
    COMPANY_MOBILE = "+91 00000 00000"

    BIKE_RATE_PER_KM = 4.50
    CAR_RATE_PER_KM = 10.00
    OTHER_VEHICLE_RATE_PER_KM = 6.00
