#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import hashlib
import random
from datetime import datetime, timedelta

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
					   port = 3306,
                       user='root',
                       password='',
                       db='airplane_project',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Define a route to hello function

def homepage_fields():
	username = session.get('email')
	myFutureFlights = []
	myPastFlights = []

	if(session.get('email')):
		cursor = conn.cursor()
		if(session.get('admin')):
			query = 'SELECT name, num, depTime, arrTime, status FROM lookUpFlight WHERE name = %s AND depTime > CURRENT_TIMESTAMP();'
			cursor.execute(query, (session.get('admin')))
			
		else:
			query = 'SELECT name, num, depTime, arrTime, ticket_id, status FROM lookUpFlight, ticket WHERE ticket.customer_email = %s AND ticket.flight_num = lookupflight.num AND depTime > CURRENT_TIMESTAMP();'
			cursor.execute(query, (session.get('email')))
		
		
		myFutureFlights = cursor.fetchall()

		if(session.get('admin')):
			query = 'SELECT name, num, depTime, arrTime FROM lookUpFlight WHERE name = %s AND depTime <= CURRENT_TIMESTAMP();'
			cursor.execute(query, (session.get('admin')))
		else:
			query = 'SELECT name, num, depTime, arrTime, ticket_id FROM lookUpFlight, ticket WHERE ticket.customer_email = %s AND ticket.flight_num = lookupflight.num AND depTime <= CURRENT_TIMESTAMP();'
			cursor.execute(query, (session.get('email')))
		myPastFlights = cursor.fetchall()

		error = None			
		if(session.get('admin')):
			query = 'SELECT customer_firstname, customer_lastname, COUNT(ticket_id) as flight_amt FROM ticket WHERE airline_name = %s GROUP BY customer_firstname, customer_lastname ORDER BY COUNT(ticket_id) DESC, customer_lastname'
			cursor.execute(query, (session.get('admin')))
			data = cursor.fetchall()
			cursor.close()
			return (username, myFutureFlights, myPastFlights, session.get('admin'), data)
		if(myPastFlights):
			cursor.close()
	return (username, myFutureFlights, myPastFlights, session.get('admin'), False)

@app.route('/')
def hello():
	fields = homepage_fields()
	return render_template('index.html', username = fields[0], myFutureFlights = fields[1], myPastFlights = fields[2], admin = fields[3], frequentFliers=fields[4])

@app.route('/logout')
def logout():
	session.pop('email')
	if(session.get('admin')):
		session.pop('admin')
	return redirect('/')

@app.route('/lookUpFlight', methods=['GET', 'POST'])
def lookUpFlight():
	fields = homepage_fields()

	departureAirport = request.form['departureAirport']
	arrivalAirport = request.form['arrivalAirport']
	departureDate = request.form['departureDate']

	cursor = conn.cursor()
	query = 'SELECT name, num, depTime, arrTime FROM lookUpFlight WHERE departureAirport = %s AND arrivalAirport = %s AND depDate = %s'
	cursor.execute(query, (departureAirport, arrivalAirport, departureDate))

	data = cursor.fetchall()
	error = None
	if(data):
		cursor.close()
		return render_template('index.html', username = fields[0], myFutureFlights = fields[1], myPastFlights = fields[2], admin = fields[3], frequentFliers=fields[4], flights = data)
	else:
		error = "No flights match those parameters at this time."
		return render_template('index.html', username = fields[0], myFutureFlights = fields[1], myPastFlights = fields[2], admin = fields[3], frequentFliers=fields[4], flights = data)

@app.route('/login')
def login():
	return render_template('login.html')

### CUSTOMER USE CASES ###

#Authenticates the login
@app.route('/customerLoginAuth', methods=['GET', 'POST'])
def customerLoginAuth():
	#grabs information from the forms
	username = request.form['email']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()

	#executes query
	query = 'SELECT * FROM customer WHERE customer_email = %s and password = %s'
	password = (hashlib.sha256(password.encode('utf-8'))).hexdigest()
	cursor.execute(query, (username, password))
	#stores the results in a variable
	data = cursor.fetchone()

	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	if(data):
		#creates a session for the the user
		#session is a built in
		session['email'] = username
		return redirect('/')
	else:
		#returns an error message to the html page
		error = 'Invalid login or email'
		return render_template('login.html', error=error)

@app.route('/register')
def register():
	return render_template('register.html')

#Authenticates the register
@app.route('/customerRegisterAuth', methods=['GET', 'POST'])
def customerRegisterAuth():
	username = request.form['email']
	password = request.form['password']
	passwordconfirm = request.form['confirmpassword']
	error = None

	#check password confirmation
	if(password != passwordconfirm):
		error = 'Passwords do not match!'
		return render_template('register.html', error=error)
	
	cursor = conn.cursor()
	
	#check if the user already exists.
	query = 'SELECT * FROM customer WHERE customer_email = %s'
	cursor.execute(query, (username))
	data = cursor.fetchone()

	#this is not all the data needed for a cusomter yet!
	if(not data):
		session['email'] = username
		query = 'INSERT INTO customer VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
		password = (hashlib.sha256(password.encode('utf-8'))).hexdigest()
		cursor.execute(query, (username, password, request.form['firstName'],request.form['lastName'],request.form['buildingNum'],request.form['street'],request.form['aptNum'], request.form['city'], request.form['state'], request.form['zipCode'],request.form['passportNum'],request.form['passportExpiration'],request.form['passportCountry'],request.form['dob']))
		cursor.close()
		return redirect('/')
	else:
		error = 'Email already in use.'
		cursor.close()
		return render_template('register.html', error=error)

#Takes you to the ticket purchase screen and saves flight_num in question
@app.route('/selectTicket', methods=['GET', 'POST'])
def selectTicket():
	flightInfo = request.form['flight_num'].split("_")
	flight_num = flightInfo[0]
	session['selected_flight'] = flight_num
	return redirect('ticketPurchase')

#Page data for the ticket purchase screen
@app.route('/ticketPurchase')
def purchaseTicket():
	cursor = conn.cursor()
	query = 'SELECT name, num, depTime, arrTime FROM lookUpFlight WHERE num = %s;'
	cursor.execute(query, (session.get('selected_flight')))
	flightInfo = cursor.fetchall()
	error = None
	cursor.close()
	return render_template('ticketpurchase.html', flightInfo = flightInfo)

#When you press "purchase" on the ticket screen
@app.route('/confirmPurchaseTicket', methods = ['GET', 'POST'])
def confirmPurchaseTicket():
	cursor = conn.cursor()
	# This doesn't guarantee unique tickets, so we should look into that
 
	# fix?
	ticketid = random.randrange(0, 99999)
	query = 'SELECT * FROM ticket WHERE ticket_id = %s'
	cursor.execute(query, (ticketid))
	exist = cursor.fetchall()
	while exist:
		ticketid = random.randrange(0, 99999)
		cursor.execute(query, (ticketid))
		exist = cursor.fetchall()

	#Insert into ticket_purchase using ticket ID
	query = 'INSERT INTO ticket_purchase VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
	cursor.execute(query, (ticketid, session.get('email'), datetime.now(), request.form.get('cardtype'), request.form['cardnumber'], request.form['cardfirstname'], request.form['cardlastname'], request.form['cardexpirationdate'], 100.00))

	#Get more flight info using saved flight num
	query = 'SELECT name, num, depTime, arrTime FROM lookUpFlight WHERE num = %s;'
	cursor.execute(query, (session.get('selected_flight')))
	flightInfo = cursor.fetchone()

	#Insert into ticket
	query = 'INSERT INTO ticket VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
	cursor.execute(query, (ticketid, session.get('selected_flight'), flightInfo['name'], flightInfo['depTime'],session.get('email'), request.form['firstname'], request.form['lastname'], request.form['birthday']))
	cursor.close()

	session.pop('selected_flight')
	return redirect('/')

@app.route('/deleteTicket', methods=['GET', 'POST'])
def deleteTicket():
	#Doesn't check if ticket is more than 24 hours in the future.
	ticket_id = request.form['ticket_id']
	cursor = conn.cursor()
	query = 'DELETE FROM ticket WHERE ticket_id = %s'
	cursor.execute(query, ticket_id)

	return redirect('/')



#Takes you to the ticket review screen and saves flight_num in question
@app.route('/reviewTicket', methods=['GET', 'POST'])
def reviewTicket():
	flight_num = request.form['ticket_id']
	session['selected_flight'] = flight_num
	return redirect('ticketReview')

#Page data for the ticket review screen
@app.route('/ticketReview')
def ticketReview():
	cursor = conn.cursor()
	query = 'SELECT airline_name, flight_num, departure_date_time, customer_firstname, customer_lastname FROM ticket NATURAL JOIN flight WHERE ticket_id = %s;'
	cursor.execute(query, (session.get('selected_flight')))
	flightInfo = cursor.fetchall()
	cursor.close()
	return render_template('ticketreview.html', flightInfo = flightInfo)


#When you press "Submit Review" on the review screen
@app.route('/confirmReviewTicket', methods = ['GET', 'POST'])
def confirmReviewTicket():
	cursor = conn.cursor()

	#Get more flight info using saved ticket
	query = 'SELECT flight_num, departure_date_time, airline_name, customer_firstname, customer_lastname FROM ticket NATURAL JOIN flight WHERE ticket_id = %s;'
	cursor.execute(query, (session.get('selected_flight')))
	flightInfo = cursor.fetchone()

	#Insert into customer_review using all values
	query = 'INSERT INTO customer_review VALUES (%s, %s, %s, %s, %s, %s)'
	cursor.execute(query, (flightInfo['flight_num'], flightInfo['departure_date_time'], flightInfo['airline_name'], session.get("email"), request.form['reviewScore'], request.form['reviewComment']))


	session.pop('selected_flight')
	return redirect('/')

@app.route('/employeeLoginAuth', methods=['GET', 'POST'])
def employeeLoginAuth():
	username = request.form['username']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()

	#executes query
	query = 'SELECT * FROM airline_staff WHERE username = %s and password = %s'
	password = (hashlib.sha256(password.encode('utf-8'))).hexdigest()
	cursor.execute(query, (username, password))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	if(data):
		#creates a session for the the user
		#session is a built in
		session['email'] = username
		# authorization level of login
		session["admin"] = data['airline_name']
		return redirect('/')
	else:
		#returns an error message to the html page
		error = 'Invalid login or email'
		return render_template('login.html', error=error)
	
#Authenticates the register
@app.route('/employeeRegisterAuth', methods=['GET', 'POST'])
def employeeRegisterAuth():
	airline_name = request.form['airline']
	first_name = request.form['first_name']
	last_name = request.form['last_name']
	dob = request.form['dob']
	username = request.form['username']
	password = request.form['password']
	passwordconfirm = request.form['confirmpassword']
	error = None

	#check password confirmation
	if(password != passwordconfirm):
		error = 'Passwords do not match!'
		return render_template('register.html', error=error)
	
	cursor = conn.cursor()

	query = 'SELECT * FROM airline WHERE airline_name = %s'
	cursor.execute(query, (airline_name))
	airline = cursor.fetchall()
	
	#check if the user already exists.
	query = 'SELECT * FROM airline_staff WHERE username = %s'
	cursor.execute(query, (username))
	data = cursor.fetchone()

	#this is not all the data needed for a cusomter yet!
	if(not data and airline):
		session['email'] = username
		session['admin'] = airline
		query = 'INSERT INTO airline_staff VALUES (%s, %s, %s, %s, %s, %s)'
		password = (hashlib.sha256(password.encode('utf-8'))).hexdigest()
		cursor.execute(query, (username, airline_name, password, first_name, last_name, dob))
		cursor.close()
		return redirect('/')
	else:
		if(not airline):
			error = 'Airline is not registered in the system'
		else: 
			error = 'Email already in use.'
		cursor.close()
		return render_template('register.html', error=error)


@app.route('/maintenance')
def maintenance():
	fields = homepage_fields()
	return render_template("maintenance.html", username = fields[0], admin = fields[3])

@app.route('/maintenanceForm', methods=['GET', 'POST'])
def maintenanceForm():
	# things to consider:
	# 	- start date in the past
	#   - end date before start date

	fields = homepage_fields()

	start = request.form['start']
	end = request.form['end']
	id = request.form['id']
	airline = session.get('admin')
	error = None
	noID = None

	if not airline: 
		return redirect('/')
	
	cursor = conn.cursor()

	query = 'SELECT * FROM airplane WHERE airplane_id = %s'
	cursor.execute(query, (id))
	data = cursor.fetchall()
	if not data:
		error = "No plane exists with that ID. Here are your airline's current planes:"
		query = 'SELECT airplane_id FROM airplane WHERE airline_name = %s'
		cursor.execute(query, (airline))
		data = cursor.fetchall()
		cursor.close()
		return render_template('maintenance.html', username = fields[0], admin = fields[3], noID = error, maintenance = data)


	query = 'SELECT * FROM maintenance WHERE airplane_id = %s AND airline_name = %s AND ((start_date BETWEEN %s AND %s) OR (end_date BETWEEN %s AND %s))'
	cursor.execute(query, (id, airline, start, end, start, end))
	data = cursor.fetchall()

	if data:
		cursor.close()
		error = "There is already maintenance scheduled for the following time frame(s)"
		return render_template('maintenance.html', username = fields[0], admin = fields[3], error = error, maintenance = data)

	maintenance_id = random.randrange(0, 99999)
	query = 'SELECT * FROM ticket WHERE ticket_id = %s'
	cursor.execute(query, (maintenance_id))
	exist = cursor.fetchall()
	while exist:
		maintenance_id = random.randrange(0, 99999)
		cursor.execute(query, (maintenance_id))
		exist = cursor.fetchall()

	query = 'INSERT INTO maintenance VALUES (%s, %s, %s, %s, %s)'
	cursor.execute(query, (maintenance_id, id, airline, start, end))
	cursor.close()

	data = {'start_date' : start, 'end_date' : end, 'id' : id}
	return render_template('maintenance.html', username = fields[0], admin = fields[3], maintenance = data, success = True)

	# set up a view & ensure the maintenances on the same
    # plane don't overlap

@app.route('/reviews', methods=['GET', 'POST'])
def reviews():
	fields = homepage_fields()
	
	flight_num = request.form['num']
	departure = request.form['depTime']

	cursor = conn.cursor()
	query = 'SELECT customer_email, rating, comment FROM customer_review NATURAL JOIN flight WHERE departure_date_time = %s AND flight_num = %s AND airline_name = %s'
	cursor.execute(query, (departure, flight_num, session.get('admin')))

	data = cursor.fetchall()
	cursor.close()
	error = None
	if(data):
		return render_template('reviews.html', username = fields[0], admin = fields[3], num=flight_num, date=departure, flights=data)
	else:
		error = "There are no reviews for this flight yet."
		return render_template('index.html', username = fields[0], myflights = fields[1], myPastFlights = fields[2], admin = fields[3], frequentFliers=fields[4], error = error)
	
#Page data for the add airplane screen
@app.route('/addAirplane')
def addAirplane():
	return render_template('addairplane.html', airline = session.get("admin"))

#When you press submit on the airplane add screen
@app.route('/confirmAddAirplane', methods = ['GET', 'POST'])
def confirmAddAirplane():

	cursor = conn.cursor()
	airplane_id = random.randrange(0, 99999)
	query = 'SELECT * FROM airplane WHERE airplane_id = %s'
	cursor.execute(query, (airplane_id))
	exist = cursor.fetchall()
	while exist:
		airplane_id = random.randrange(0, 99999)
		cursor.execute(query, (airplane_id))
		exist = cursor.fetchall()

	#Insert into airplane
	query = 'INSERT INTO airplane VALUES (%s, %s, %s, %s, %s, %s, %s)'
	cursor.execute(query, (airplane_id, session.get('admin'), request.form['num_seats'], request.form['manufacturing_company'], request.form['model_num'], request.form['manufacturing_date'], 0))
	cursor.close()

	return redirect('/')

#Page data for the ticket purchase screen
@app.route('/addFlight')
def addFlight():
	cursor = conn.cursor()
	query = 'SELECT code FROM airport WHERE 1;'
	cursor.execute(query)
	airports = cursor.fetchall()

	return render_template('addflight.html', airports = airports, airline = session.get("admin"))

#When you press "purchase" on the ticket screen
@app.route('/confirmAddFlight', methods = ['GET', 'POST'])
def confirmAddFlight():

	cursor = conn.cursor()
	flight_num = random.randrange(0, 999)
	query = 'SELECT * FROM flight WHERE flight_num = %s AND departure_date_time = %s AND airline_name = %s'
	cursor.execute(query, (flight_num, request.form['departure_date_time'], request.form['arrival_date_time']))
	exist = cursor.fetchall()
	while exist:
		flight_num = random.randrange(0, 999)
		cursor.execute(query, (flight_num, request.form['departure_date_time'], request.form['arrival_date_time']))
		exist = cursor.fetchall()

	#Insert into airplane
	query = 'INSERT INTO flight VALUES (%s, %s, %s, %s, %s, %s)'
	cursor.execute(query, (flight_num, request.form['departure_date_time'], session.get('admin'), request.form['airplane_id'], request.form['base_price'], "on-time"))

	query = 'INSERT INTO flight_arrival VALUES (%s, %s, %s, %s, %s)'
	cursor.execute(query, (request.form['arrivalAirport'], flight_num, request.form['departure_date_time'], request.form['arrival_date_time'], session.get('admin')))

	query = 'INSERT INTO flight_departure VALUES (%s, %s, %s, %s)'
	cursor.execute(query, (request.form['departureAirport'], flight_num, request.form['departure_date_time'], session.get('admin')))
	cursor.close()

	return redirect('/')

@app.route('/frequency', methods=['GET', 'POST'])
def frequency():
	# fields = homepage_fields()
	cursor = conn.cursor()
	query = 'SELECT * FROM ticket WHERE customer_firstname = %s AND customer_lastname = %s AND airline_name = %s'
	cursor.execute(query, (request.form['first'], request.form['last'], session.get('admin')))
	data = cursor.fetchall()
	return render_template('/frequentFliers.html', first=request.form['first'], last=request.form['last'], flights = data)
	

@app.route('/addAirport', methods = ['GET', 'POST'])
def addAirport():
	return render_template('/addAirport.html')

@app.route('/newAirport', methods = ['GET', 'POST'])
def newAirport():	
	cursor = conn.cursor()
	query = 'SELECT * FROM airport WHERE code = %s'
	cursor.execute(query, (request.form['code'])) 
	data = cursor.fetchall()

	if data:
		error = "This airport already exists"
		cursor.close()
		return render_template('/addAirport.html', error=error)
	
	query = 'INSERT INTO airport VALUES (%s, %s, %s, %s, %s, %s)'
	cursor.execute(query, (request.form['code'], request.form['name'], request.form['city'], request.form['country'], request.form['terminals'], request.form['type']))
	cursor.close()
	return redirect('/')

@app.route('/earnedRevenue', methods = ['GET', 'POST'])
def earnedRevenue():
	cursor = conn.cursor()
	query = 'SELECT SUM(sold_price) FROM ticket NATURAL JOIN ticket_purchase WHERE airline_name = %s AND purchase_date_time BETWEEN %s and %s;'

	cursor.execute(query, (session.get('admin'), datetime.now() + timedelta(days=-31), datetime.now())) 
	monthly = cursor.fetchone()["SUM(sold_price)"]

	cursor.execute(query, (session.get('admin'), datetime.now() + timedelta(days=-365), datetime.now())) 
	yearly = cursor.fetchone()["SUM(sold_price)"]
	return render_template('/earnedrevenue.html', monthly = monthly, yearly = yearly)

@app.route('/changeStatus', methods=['GET', 'POST'])
def changeStatus():
	cursor = conn.cursor()
	query = 'UPDATE flight SET status = %s WHERE flight_num = %s AND departure_date_time = %s AND airline_name = %s'
	cursor.execute(query, (request.form['status'], request.form['num'], request.form['departure'], session.get('admin')))
	cursor.close()

	fields = homepage_fields()
	return render_template('index.html', username = fields[0], myFutureFlights = fields[1], myPastFlights = fields[2], admin = fields[3], frequentFliers=fields[4])
"""
#Define route for login
@app.route('/login')
def login():
	return render_template('login.html')

#Define route for register
@app.route('/register')
def register():
	return render_template('register.html')

#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM user WHERE username = %s and password = %s'
	cursor.execute(query, (username, password))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	if(data):
		#creates a session for the the user
		#session is a built in
		session['username'] = username
		return redirect(url_for('home'))
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('login.html', error=error)

#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM user WHERE username = %s'
	cursor.execute(query, (username))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('register.html', error = error)
	else:
		ins = 'INSERT INTO user VALUES(%s, %s)'
		cursor.execute(ins, (username, password))
		conn.commit()
		cursor.close()
		return render_template('index.html')

@app.route('/home')
def home():
    
    username = session['username']
    cursor = conn.cursor();
    query = 'SELECT ts, blog_post FROM blog WHERE username = %s ORDER BY ts DESC'
    cursor.execute(query, (username))
    data1 = cursor.fetchall() 
    for each in data1:
        print(each['blog_post'])
    cursor.close()
    return render_template('home.html', username=username, posts=data1)

		
@app.route('/post', methods=['GET', 'POST'])
def post():
	username = session['username']
	cursor = conn.cursor();
	blog = request.form['blog']
	query = 'INSERT INTO blog (blog_post, username) VALUES(%s, %s)'
	cursor.execute(query, (blog, username))
	conn.commit()
	cursor.close()
	return redirect(url_for('home'))

@app.route('/logout')
def logout():
	session.pop('username')
	return redirect('/')
"""


app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)
