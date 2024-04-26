-- Anna Tanaka Viertler & Kai Shinozaki-Conefrey
-- airports
INSERT INTO airport 
VALUES ('JFK', 'John F. Kennedy', 'New York City', 'United States', 4, 'both'),
('PVG', 'Shanghai Pudong International Airport', 'Shanghai', 'China', 4, 'international');


-- customers
INSERT INTO customer 
-- iAmBob
-- bermudaTriangleLmao
-- PentagonAndOn
-- wheeeeee
VALUES ('bob@gmail.com', 'f3dd8d2e5251f3cd495a2c1774285e37b6cf4af381883126282af8f63f40a9be', 'Bob', 'Duncan', 501, 'Palmetto Drive', null, 'Pasadena', 'California', 91105, '12345678', '2024-04-30', 'United States', '1964-11-12'),
('amelia@gmail.com', '7913321816497ce982ae5cc8e82659a1ccb139a2854326456e58863b51a3b596', 'Amelia', 'Earhart', 223, 'N Terrace St.', null, 'Atchison', 'Kansas', 66002, '87654321', '2026-07-30', 'Germany', '1897-07-24'),
('george@hotmail.com', '6516f422fad75fe6f5c0be624139e5d07b8404de009100c55d22e228b96bc1c8', 'George', 'Bush', 1600, 'Pennsylvania Avenue NW', null, 'Washington', 'DC', 20500, '42358432', '2028-02-15', 'United States', '1946-06-06'),
('db@outlook.com', '991514a65caff6dd61ab07287df1bd190eca850470049a67f00441d3aa49dbb5', 'D.B.', 'Cooper', 999, 'Pineapple Drive', null, 'Timbuktu', 'Arkansas', 1235, '93394023', '2024-05-30', 'Canada', null);

INSERT INTO cust_phone (customer_email, phone_num)
VALUES ('bob@gmail.com', 9028557134),
('amelia@gmail.com', 2134453987),
('george@hotmail.com', 2028990923),
('db@outlook.com', 7719897091);


-- airplanes
INSERT INTO airplane VALUES 
(1234, 'Jet Blue', 80, 'Boeing', 0001, '2003-04-06', 20),
(1235, 'Jet Blue', 80, 'Textron', 0303, '2002-02-09', 21),
(1236, 'Jet Blue', 80, 'Airbus', 2306, '2001-01-04', 22);


-- airline
INSERT INTO airline
VALUES ('Jet Blue', 0, 0, null);

-- airline staff
INSERT INTO airline_staff (username, airline_name, password, first_name, last_name, DOB)
VALUES ('pookie123', 'JetBlue', 'pookielicious', 'Bill', 'Clinton', '1946-08-19');

INSERT INTO staff_phone (username, phone_num)
VALUES ('pookie123', 4169890143);

INSERT INTO staff_email (username, email)
VALUES ('pookie123', 'pookie@gmail.com'),
('pookie123', 'bill@hotmail.com'); 


-- flight
INSERT INTO flight (flight_num, departure_date_time, airline_name, airplane_id, base_price, status)
VALUES (725, '2025-01-15 04:22:17', 'JetBlue', 1234, 5, 'on-time'),
(980, '2024-04-01 11:30:08', 'JetBlue', 1235, 120, 'delayed'),
(112, '2020-09-11 12:30:42', 'JetBlue', 1236, 200, 'on-time'),
(305, '1971-11-24 15:15:18', 'JetBlue', 1234, 15, 'on-time');

INSERT INTO flight_departure VALUES
('PVG', 725, '2025-01-15 04:22:17'), 
('JFK', 980, '2024-04-01 11:30:08'), 
('PVG', 112, '2020-09-11 12:30:42'), 
('JFK', 305, '1971-11-24 15:15:18'); 

INSERT INTO flight_arrival VALUES
('JFK', 725, '2025-01-15 04:22:17', '2025-02-15 08:22:17'),
('PVG', 980, '2024-04-01 11:30:08', '2024-04-01 15:30:08'), 
('JFK', 112, '2020-09-11 12:30:42', '2020-09-11 20:30:42'), 
('PVG', 305, '1971-11-24 15:15:18', '1971-11-24 23:58:32'); 



-- ticket
INSERT INTO ticket (ticket_id, flight_num, customer_email, departure_date_time, customer_firstname, customer_lastname, customer_dob)
VALUES (87642, 725, 'bob@gmail.com', '2025-01-15 04:22:17', 'Bob', 'Duncan', '1964-11-12'),
(12345, 980, 'bob@gmail.com', '2024-04-01 11:30:08', 'Bob', 'Duncan', '1964-11-12'),
(12346, 980, 'amelia@gmail.com', '2024-04-01 11:30:08', 'Amelia', 'Earhart', '1897-07-24'),
(10987, 112, 'george@hotmail.com', '2020-09-11 12:30:42', 'George', 'Bush', '1946-06-06'),
(89302, 305, 'db@outlook.com', '1971-11-24 15:15:18', 'D.B.', 'Cooper', NULL);

INSERT INTO ticket_purchase (ticket_id, customer_email, purchase_date_time, card_type, card_number, card_firstname, card_lastname, card_expiration_date, sold_price)
VALUES (87642, 'bob@gmail.com', '2024-03-28 21:15:03', 'debit', 546781,'Bob', 'Duncan', '2028-12-11', 128.57),
(12345, 'bob@gmail.com', '2024-03-28 21:19:53', 'credit', 439047, 'Amy', 'Duncan', '2035-08-30', 478.77),
(12345, 'amelia@gmail.com', '2023-07-19 16:29:13', 'credit', 208984,'Mary', 'Earhart', '2025-03-15', 8.53),
(10987, 'george@hotmail.com', '2018-04-06 11:29:00', 'debit', 546781, 'Bob', 'Duncan', '2028-12-11', 302.83),
(89302, 'db@outlook.com', '1971-11-03 02:00:43', 'credit', 123873, 'D.B.', 'Cooper', '2024-10-19', 50.14);