-- Anna Tanaka Viertler & Kai Shinozaki-Conefrey

CREATE TABLE airport(
	code 				varchar(3),
	name 				varchar(50),
	city 				varchar(50),
	country 			varchar(50),
	num_of_terminals 	bigint,
	type 				varchar(50),

	PRIMARY KEY (code)
);

CREATE TABLE flight_arrival(
	code 				varchar(3),
	flight_num 			bigint,
	departure_date_time 		datetime,
	arrival_date_time		datetime,

	FOREIGN KEY (code) REFERENCES airport(code),
	FOREIGN KEY (departure_date_time) REFERENCES flight(departure_date_time),
	FOREIGN KEY (flight_num) REFERENCES flight(flight_num)
);

CREATE TABLE flight_departure(
	code 				varchar(3),
	flight_num 			bigint,
	departure_date_time 		datetime,

	FOREIGN KEY (code) REFERENCES airport(code),
	FOREIGN KEY (departure_date_time) REFERENCES flight(departure_date_time),
	FOREIGN KEY (flight_num) REFERENCES flight(flight_num)
);

CREATE TABLE flight(
	flight_num 			bigint,
	departure_date_time 		datetime,
	airline_name 			varchar(50),
	airplane_id			bigint,
	base_price			decimal(65,2),
	status				varchar(50),

    PRIMARY KEY (flight_num, departure_date_time),
    FOREIGN KEY (airline_name) REFERENCES airline(airline_name),
    FOREIGN KEY (airplane_id) REFERENCES airplane(airplane_id)
);

CREATE TABLE airplane(
    airplane_id				bigint,
    airline_name			varchar(50),
    num_seats				bigint,
    manufacturing_company	varchar(50),
    model_num				bigint,
    manufacturing_date		date,
    age					    bigint,

    PRIMARY KEY (airplane_id),
    FOREIGN KEY (airline_name) REFERENCES airline(airline_name)
);

CREATE TABLE maintenance(
	maintenance_id		bigint,
	airplane_id			bigint,
	start_date			datetime,
	end_date			datetime,	
	
	PRIMARY KEY (maintenance_id),
	FOREIGN KEY (airplane_id) references airplane(airplane_id)
);

CREATE TABLE airline(
    airline_name			    varchar(50),
    tickets_sold 			    bigint,
    total_revenue 			    decimal(65, 2),
    frequent_flier_customer 	varchar(50),

    PRIMARY KEY (airline_name)
);

CREATE TABLE airline_staff(
    username				varchar(50),
    airline_name			varchar(50),
    password				varchar(255),
    first_name				varchar(50),
    last_name				varchar(50),
    DOB					date,

    PRIMARY KEY (username),
    FOREIGN KEY (airline_name) REFERENCES airline(airline_name)
);

CREATE TABLE staff_phone(
    username				varchar(50),
    phone_num				bigint,

    PRIMARY KEY (phone_num),
    FOREIGN KEY (username) REFERENCES airline_staff(username)
);

CREATE TABLE staff_email(
    username				varchar(50),
    email				varchar(50),

    PRIMARY KEY (email),
    FOREIGN KEY (username) REFERENCES airline_staff(username)
);

CREATE TABLE ticket(
    ticket_id				bigint,
    flight_num				bigint,
    departure_date_time			datetime,
    customer_email              varchar(50),
    customer_firstname			varchar(50),
    customer_lastname			varchar(50),
    customer_DOB			date,

    PRIMARY KEY (ticket_id),
    FOREIGN KEY (flight_num) REFERENCES flight(flight_num),
    FOREIGN KEY (departure_date_time) REFERENCES flight(departure_date_time)
);


CREATE TABLE ticket_purchase(
    ticket_id				bigint,
    customer_email			varchar(50),
    purchase_date_time		datetime,
    card_type				varchar(6),
    card_number				bigint,
    card_firstname			varchar(50),
    card_lastname			varchar(50),
    card_expiration_date		date,
    sold_price				decimal(65, 2),

    FOREIGN KEY (ticket_id) REFERENCES ticket(ticket_id),
    FOREIGN KEY (customer_email) REFERENCES customer(customer_email)
);


CREATE TABLE customer (
    customer_email			varchar(50),
    password				varchar(255) not null,
    first_name				varchar(50),
    last_name				varchar(50),
    building_num			bigint,
    street				varchar(50),
    apt_num				bigint,
    city				varchar(50),
    state				varchar(50),
    zip_code				bigint,
    passport_num			varchar(50),
    passport_expiration			date,
    passport_country			varchar(50),
    DOB					date,

    PRIMARY KEY (customer_email)
);

CREATE TABLE cust_phone(
    customer_email			varchar(50),
    phone_num				bigint,

    PRIMARY KEY (phone_num),
    FOREIGN KEY (customer_email) references customer(customer_email)
);

CREATE TABLE customer_review(
    flight_num 				bigint,
    departure_date_time			datetime,
    customer_email			varchar(50),
    rating				bigint,
    comment				varchar(50),

    FOREIGN KEY (flight_num) REFERENCES flight(flight_num),
    FOREIGN KEY (departure_date_time) REFERENCES flight(departure_date_time)
);



