-- Anna Tanaka Viertler & Kai Shinozaki-Conefrey

-- airports
INSERT INTO airport 
VALUES ('JFK', 'John F. Kennedy', 'New York City', 'United States', 4, 'both'),
('PVG', 'Shanghai Pudong International Airport', 'Shanghai', 'China', 4, 'international'),
('SFO', 'San Francisco International Airport', 'San Francisco', 'United States', 4, 'both'),
('NRT', 'Narita International Airport', 'Narita', 'Japan', 3, 'both');


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
(1234, 'JetBlue', 80, 'Boeing', 0001, '2003-04-06'),
(1235, 'JetBlue', 80, 'Textron', 0303, '2002-02-09'),
(1236, 'JetBlue', 80, 'Airbus', 2306, '2001-01-04'),
(1237, 'United Airlines', 80, 'Boeing', 0001, '2003-04-06'),
(1238, 'United Airlines', 80, 'Textron', 0303, '2002-02-09'),
(1239, 'United Airlines', 80, 'Airbus', 2306, '2001-01-04'),
(1240, 'Delta Airlines', 80, 'Boeing', 0001, '2003-04-06'),
(1241, 'Delta Airlines', 80, 'Textron', 0303, '2002-02-09'),
(1242, 'Delta Airlines', 80, 'Airbus', 2306, '2001-01-04'),
(1243, 'Frontier Airlines', 80, 'Boeing', 0001, '2003-04-06'),
(1244, 'Frontier Airlines', 80, 'Textron', 0303, '2002-02-09'),
(1245, 'Frontier Airlines', 80, 'Airbus', 2306, '2001-01-04'),
(1246, 'Spirit Airlines', 80, 'Boeing', 0001, '2003-04-06'),
(1247, 'Spirit Airlines', 80, 'Textron', 0303, '2002-02-09'),
(1248, 'Spirit Airlines', 80, 'Airbus', 2306, '2001-01-04');

ALTER TABLE airplane 
ADD age bigint;

UPDATE airplane
SET age = (DATEDIFF(NOW(), manufacturing_date)) / 365;


-- airline
INSERT INTO airline
VALUES ('JetBlue', 0, 0, null),
('United Airlines', 0, 0, null),
('Delta Airlines', 0, 0, null),
('Frontier Airlines', 0, 0, null);

-- airline staff
INSERT INTO airline_staff (username, airline_name, password, first_name, last_name, DOB) VALUES 
('pookie123', 'JetBlue', '3c1de7c0ce41d67d0cdbc4f416d0a77ecf539560c47292a7070cbea8e52e6666', 'Bill', 'Clinton', '1946-08-19'),
('admin', 'JetBlue', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'admin', '', NULL);


INSERT INTO staff_phone (username, phone_num)
VALUES ('pookie123', 4169890143);

INSERT INTO staff_email (username, email)
VALUES ('pookie123', 'pookie@gmail.com'),
('pookie123', 'bill@hotmail.com'); 


-- flight
INSERT INTO flight (flight_num, departure_date_time, airline_name, airplane_id, base_price, status)
VALUES (725, '2025-01-15 04:22:17', 'JetBlue', 1234, 5, 'On-Time'),
(980, '2024-04-01 11:30:08', 'JetBlue', 1235, 120, 'Delayed'),
(112, '2020-09-11 12:30:42', 'JetBlue', 1236, 200, 'On-time'),
(305, '1971-11-24 15:15:18', 'JetBlue', 1234, 15, 'On-time');

INSERT INTO flight_departure VALUES
('PVG', 725, '2025-01-15 04:22:17', 'JetBlue'), 
('JFK', 980, '2024-04-01 11:30:08', 'JetBlue'), 
('PVG', 112, '2020-09-11 12:30:42', 'JetBlue'), 
('JFK', 305, '1971-11-24 15:15:18', 'JetBlue'); 

INSERT INTO flight_arrival VALUES
('JFK', 725, '2025-01-15 04:22:17', '2025-02-15 08:22:17', 'JetBlue'),
('PVG', 980, '2024-04-01 11:30:08', '2024-04-01 15:30:08', 'JetBlue'), 
('JFK', 112, '2020-09-11 12:30:42', '2020-09-11 20:30:42', 'JetBlue'), 
('PVG', 305, '1971-11-24 15:15:18', '1971-11-24 23:58:32', 'JetBlue'); 

-- ticket
INSERT INTO ticket (ticket_id, flight_num, airline_name, customer_email, departure_date_time, customer_firstname, customer_lastname, customer_dob)
VALUES (87642, 725, 'JetBlue', 'bob@gmail.com', '2025-01-15 04:22:17', 'Bob', 'Duncan', '1964-11-12'),
(12345, 980, 'JetBlue', 'bob@gmail.com', '2024-04-01 11:30:08', 'Bob', 'Duncan', '1964-11-12'),
(12346, 980, 'JetBlue', 'amelia@gmail.com', '2024-04-01 11:30:08', 'Amelia', 'Earhart', '1897-07-24'),
(10987, 112, 'JetBlue', 'george@hotmail.com', '2020-09-11 12:30:42', 'George', 'Bush', '1946-06-06'),
(89302, 305, 'JetBlue', 'db@outlook.com', '1971-11-24 15:15:18', 'D.B.', 'Cooper', NULL);

INSERT INTO ticket_purchase (ticket_id, customer_email, purchase_date_time, card_type, card_number, card_firstname, card_lastname, card_expiration_date, sold_price)
VALUES (87642, 'bob@gmail.com', '2024-03-28 21:15:03', 'debit', 546781,'Bob', 'Duncan', '2028-12-11', 128.57),
(12345, 'bob@gmail.com', '2024-03-28 21:19:53', 'credit', 439047, 'Amy', 'Duncan', '2035-08-30', 478.77),
(12345, 'amelia@gmail.com', '2023-07-19 16:29:13', 'credit', 208984,'Mary', 'Earhart', '2025-03-15', 8.53),
(10987, 'george@hotmail.com', '2018-04-06 11:29:00', 'debit', 546781, 'Bob', 'Duncan', '2028-12-11', 302.83),
(89302, 'db@outlook.com', '1971-11-03 02:00:43', 'credit', 123873, 'D.B.', 'Cooper', '2024-10-19', 50.14);