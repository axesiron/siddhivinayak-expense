-- Sample data (optional). The app already seeds a demo admin + employee
-- automatically on first run -- this file is for loading a larger demo
-- dataset into a MySQL instance if you want more records to explore.
-- Password hashes below are Werkzeug scrypt hashes for the passwords
-- noted in comments; regenerate them if you change passwords.

USE siddhivinayak_expense_manager;

INSERT INTO expense_rates (bike_rate, car_rate, other_rate, rounding)
VALUES (4.50, 10.00, 6.00, 'nearest');

INSERT INTO company_settings (company_name, address_line1, address_line2, mobile)
VALUES (
  'SIDDHIVINAYAK ENGINEERING & TRADING CORPORATION',
  '169 AAREY MILK COLONY, PODACCITY-3 CO-OP HSGS LTD,',
  'GOREGAON EAST, MUMBAI SUBURBAN, MAHARASHTRA, 400065',
  '+91 00000 00000'
);

-- NOTE: create employees through the app's Register / Admin > Add Employee
-- screens so passwords are hashed correctly. Example expense rows for an
-- existing employee_id = 2 (Rajkumar Desai):

INSERT INTO expenses
  (employee_id, expense_date, reason, mode, from_location, to_location,
   other_amount, cng_bus_amount, km, courier_transport_amount, food_amount,
   km_rate, km_amount, total_amount)
VALUES
  (2, '2026-07-18', 'Shiroli Parcel', 'Bike', 'Office', 'Shiroli', 0, 0, 13, 0, 0, 4.50, 59, 59),
  (2, '2026-07-20', 'Shiroli Parcel', 'Bike', 'Office', 'Shiroli', 0, 0, 13, 0, 0, 4.50, 59, 59),
  (2, '2026-07-21', 'Shiroli Parcel', 'Bike', 'Office', 'Shiroli', 0, 0, 13, 0, 0, 4.50, 59, 59),
  (2, '2026-07-23', 'Travel to Mysore', 'Bus', 'Office', 'Mysore', 0, 0, 0, 1500, 0, 0, 0, 1500),
  (2, '2026-07-24', 'Mysore Installation', 'Auto', 'Mysore', 'Site', 0, 0, 0, 0, 200, 0, 0, 200);
