-- SIDDHIVINAYAK EXPENSE MANAGER
-- MySQL schema (reference). The app auto-creates these tables via
-- SQLAlchemy on first run for both SQLite and MySQL, so running this
-- file by hand is optional -- useful mainly for DBA review or manual
-- provisioning.

CREATE DATABASE IF NOT EXISTS siddhivinayak_expense_manager
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE siddhivinayak_expense_manager;

CREATE TABLE IF NOT EXISTS employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    mobile VARCHAR(20),
    designation VARCHAR(100),
    department VARCHAR(100),
    password_hash VARCHAR(255) NOT NULL,
    joining_date DATE,
    role VARCHAR(20) DEFAULT 'employee',
    is_blocked BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    expense_date DATE NOT NULL,
    reason VARCHAR(255) NOT NULL,
    mode VARCHAR(20) NOT NULL,
    from_location VARCHAR(120),
    to_location VARCHAR(120),
    other_amount DECIMAL(10,2) DEFAULT 0,
    cng_bus_amount DECIMAL(10,2) DEFAULT 0,
    km DECIMAL(10,2) DEFAULT 0,
    courier_transport_amount DECIMAL(10,2) DEFAULT 0,
    food_amount DECIMAL(10,2) DEFAULT 0,
    km_rate DECIMAL(10,2) DEFAULT 0,
    km_amount DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(10,2) DEFAULT 0,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS expense_rates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bike_rate DECIMAL(6,2) DEFAULT 4.50,
    car_rate DECIMAL(6,2) DEFAULT 10.00,
    other_rate DECIMAL(6,2) DEFAULT 6.00,
    rounding VARCHAR(20) DEFAULT 'nearest'
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS company_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(255),
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    mobile VARCHAR(50),
    logo_path VARCHAR(255)
) ENGINE=InnoDB;
