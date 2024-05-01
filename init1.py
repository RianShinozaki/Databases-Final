#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import hashlib
import random
from datetime import datetime, timedelta
import math

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

# ===============================================================================================================



### HOMEPAGE FUNCTIONALITY ###

def homepage_fields():
	username = None
	myFutureFlights = []
	myPastFlights = []
	frequentFliers = None
	pastFlightPageNum = 1
	futureFlightPageNum = 1

	if(session.get('email')):
		cursor = conn.cursor()

		# Get future flights
		if(session.get('admin')):
			query = 'SELECT first_name, last_name FROM airline_staff WHERE username = %s'
			cursor.execute(query, (session.get('email')))
			name = cursor.fetchone()
			username = name['first_name'] + ' ' + name['last_name']

			query = 'SELECT name, num, depTime, arrTime, status, departureAirport, arrivalAirport FROM lookUpFlight WHERE name = %s AND depTime BETWEEN CURRENT_TIMESTAMP() AND DATE_ADD(CURRENT_TIMESTAMP(), INTERVAL 30 DAY) ORDER BY depTime;'
			cursor.execute(query, (session.get('admin')))
			
		else:
			query = 'SELECT first_name, last_name FROM customer WHERE customer_email = %s'
			cursor.execute(query, (session.get('email')))
			name = cursor.fetchone()
			username = name['first_name'] + ' ' + name['last_name']

			query = 'SELECT name, num, depTime, arrTime, ticket_id, status, departureAirport, arrivalAirport FROM lookUpTicket WHERE customer_email = %s AND depTime > CURRENT_TIMESTAMP() ORDER BY depTime;'
			cursor.execute(query, (session.get('email')))
		
		myFutureFlights = cursor.fetchall()

		futureFlightPageNum = len(myFutureFlights)/15
		sliceBegin = ((int(session.get("futureFlightPage")-1) * 15))
		sliceEnd = min( int(session.get("futureFlightPage")) * 15, len(myFutureFlights))
		myFutureFlights = myFutureFlights[sliceBegin : sliceEnd]

		# print(sliceBegin, ":", sliceEnd)
		# Get past flights
		if(session.get('admin')):
			query = 'SELECT name, num, depTime, arrTime, departureAirport, arrivalAirport FROM lookUpFlight WHERE name = %s AND depTime <= CURRENT_TIMESTAMP() ORDER BY depTime DESC;'
			cursor.execute(query, (session.get('admin')))
		else:
			query = 'SELECT name, num, depTime, arrTime, ticket_id, status, departureAirport, arrivalAirport FROM lookUpTicket WHERE customer_email = %s AND depTime < CURRENT_TIMESTAMP() ORDER BY depTime DESC;'
			cursor.execute(query, (session.get('email')))
		
		myPastFlights = cursor.fetchall()
		# print(myPastFlights)

		pastFlightPageNum = len(myPastFlights)/20
		sliceBegin = ((int(session.get("pastFlightPage")-1) * 15))
		sliceEnd = min( int(session.get("pastFlightPage")) * 15, len(myPastFlights))
		myPastFlights = myPastFlights[sliceBegin : sliceEnd]
		
		error = None			
		if(session.get('admin')):
			query = 'SELECT customer_firstname, customer_lastname, COUNT(ticket_id) as flight_amt FROM ticket WHERE airline_name = %s GROUP BY customer_firstname, customer_lastname ORDER BY COUNT(ticket_id) DESC, customer_lastname'
			cursor.execute(query, (session.get('admin')))
			frequentFliers = cursor.fetchall()
		cursor.close()
	return (username, myFutureFlights, myPastFlights, session.get('admin'), frequentFliers, max(1, math.ceil(futureFlightPageNum)), session.get("futureFlightPage"), max(1,math.ceil(pastFlightPageNum)),session.get("pastFlightPage"))

# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------

@app.route('/')
def hello():
	fields = homepage_fields()
	return render_template('index.html', username = fields[0], myFutureFlights = fields[1], myPastFlights = fields[2], admin = fields[3], frequentFliers=fields[4], futureFlightPageNum = fields[5], futureFlightPage = fields[6], pastFlightPageNum = fields[7], pastFlightPage = fields[8])

# ===============================================================================================================



### EVRYONE USE CASES ###

@app.route('/login')
def login():
	return render_template('login.html')

@app.route('/logout')
def logout():
	session.clear()
	return redirect('/login')

# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------

@app.route('/lookUpFlight', methods=['GET', 'POST'])
def lookUpFlight():
	fields = homepage_fields()

	departureAirport = request.form['departureAirport']
	arrivalAirport = request.form['arrivalAirport']
	departureDate = request.form['departureDate']

	cursor = conn.cursor()
	query = 'SELECT name, num, depTime, arrTime, base_price, status FROM lookUpFlight WHERE departureAirport = %s AND arrivalAirport = %s AND depDate = %s'
	cursor.execute(query, (departureAirport, arrivalAirport, departureDate))
	data = cursor.fetchall()

	if(session.get('admin')):
		query = 'SELECT name, num, depTime, arrTime, base_price, status FROM lookUpFlight WHERE departureAirport = %s AND arrivalAirport = %s AND depDate = %s AND name = %s'
		cursor.execute(query, (departureAirport, arrivalAirport, departureDate, session.get('admin')))
		data = cursor.fetchall()

	error = None
	if(data):
		cursor.close()
		return render_template('index.html', username = fields[0], myFutureFlights = fields[1], myPastFlights = fields[2], admin = fields[3], frequentFliers=fields[4], flights = data)
	else:
		error = "No flights match those parameters at this time."
		return render_template('index.html', username = fields[0], myFutureFlights = fields[1], myPastFlights = fields[2], admin = fields[3], frequentFliers=fields[4], flights = data, error=error)

# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------

@app.route('/changeFutureFlightPage', methods=['GET', 'POST'])
def changeFutureFlightPage():
	flightPage = int(request.form['futureFlightPage'])
	flightPages = int(request.form['futureFlightPages'])
	session['futureFlightPage'] = max(1, min(flightPage, flightPages))
	return redirect('/')


@app.route('/changePastFlightPage', methods=['GET', 'POST'])
def changePastFlightPage():
	flightPage = int(request.form['pastFlightPage'])
	flightPages = int(request.form['pastFlightPages'])
	session['pastFlightPage'] = max(1, min(flightPage, flightPages))
	return redirect('/')

# ===============================================================================================================




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
		session['futureFlightPage'] = 1
		session['pastFlightPage'] = 1
		return redirect('/')
	else:
		#returns an error message to the html page
		error = 'Invalid login or email'
		return render_template('login.html', error=error)

# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------

@app.route('/register')
def register():
	cursor = conn.cursor()
	query = 'SELECT airline_name FROM airline;'
	cursor.execute(query)
	airlines = cursor.fetchall()
	cursor.close()
	return render_template('register.html', airlines=airlines)


#Authenticates the register
@app.route('/customerRegisterAuth', methods=['GET', 'POST'])
def customerRegisterAuth():
	username = request.form['email']
	password = request.form['password']
	passwordconfirm = request.form['confirmpassword']
	error = None

	cursor = conn.cursor()

	#check password confirmation
	if(password != passwordconfirm):
		error = 'Passwords do not match!'
		query = 'SELECT airline_name FROM airline;'
		cursor.execute(query)
		airlines = cursor.fetchall()
		cursor.close()
		return render_template('register.html', error=error)
	
	
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
		query = 'SELECT airline_name FROM airline;'
		cursor.execute(query)
		airlines = cursor.fetchall()
		cursor.close()
		return render_template('register.html', error=error, airlines=airlines)

# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------

#Takes you to the ticket purchase screen and saves flight_num in question
@app.route('/selectTicket', methods=['GET', 'POST'])
def selectTicket():
	flightInfo = request.form['flight_num'].split("_")
	session['selected_flight'] = flightInfo
	return redirect('ticketPurchase')

# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------

#Page data for the ticket purchase screen
@app.route('/ticketPurchase')
def purchaseTicket():
	cursor = conn.cursor()
	query = 'SELECT name, num, depTime, arrTime, base_price FROM lookUpFlight WHERE num = %s AND name = %s AND depTime = %s;'
	cursor.execute(query, (session.get('selected_flight')[0],session.get('selected_flight')[1],session.get('selected_flight')[2]))
	flightInfo = cursor.fetchall()
	error = None

	query = 'SELECT COUNT(ticket_id) FROM ticket WHERE flight_num = %s AND airline_name = %s AND departure_date_Time = %s; '
	cursor.execute(query, (session.get('selected_flight')[0],session.get('selected_flight')[1],session.get('selected_flight')[2]))
	ticket_count = cursor.fetchone()
	query = 'SELECT num_seats FROM airplane, flight WHERE flight_num = %s AND flight.airline_name = %s AND departure_date_Time = %s AND airplane.airplane_id = flight.airplane_id'
	cursor.execute(query, (session.get('selected_flight')[0],session.get('selected_flight')[1],session.get('selected_flight')[2]))
	numseats = cursor.fetchone()
	seatsLeft = numseats['num_seats'] - ticket_count['COUNT(ticket_id)']
	sellPrice = flightInfo[0]['base_price']

	cursor.close()

	if(seatsLeft <= numseats['num_seats'] * 0.8):
		sellPrice = float(sellPrice) * 1.25
	
	if not seatsLeft:
		fields = homepage_fields()
		error = "There are no more seats available for " + session.get('selected_flight')[1] + " #" + session.get('selected_flight')[0]
		return render_template('index.html', username = fields[0], myFutureFlights = fields[1], myPastFlights = fields[2], error = error)
	sellPrice = round(sellPrice, 2)
	sellPrice = "%0.2f" % sellPrice

	session['ticketSellPrice'] = sellPrice

	return render_template('ticketpurchase.html', flightInfo = flightInfo, seatsLeft = seatsLeft, sellPrice = sellPrice)

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
	cursor.execute(query, (ticketid, session.get('email'), datetime.now(), request.form.get('cardtype'), request.form['cardnumber'], request.form['cardfirstname'], request.form['cardlastname'], request.form['cardexpirationdate'], session.get("ticketSellPrice")))

	#Insert into ticket
	query = 'INSERT INTO ticket VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
	cursor.execute(query, (ticketid, session.get('selected_flight')[0], session.get('selected_flight')[1], session.get('selected_flight')[2],session.get('email'), request.form['firstname'], request.form['lastname'], request.form['birthday']))
	cursor.close()

	session.pop('selected_flight')
	return redirect('/')

# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------

@app.route('/deleteTicket', methods=['GET', 'POST'])
def deleteTicket():
	#Doesn't check if ticket is more than 24 hours in the future.
	ticket_id = request.form['ticket_id']
	cursor = conn.cursor()
	query = 'DELETE FROM ticket WHERE ticket_id = %s'
	cursor.execute(query, ticket_id)

	return redirect('/')

# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------

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
	query = 'SELECT airline_name, flight_num, departure_date_time, customer_firstname, customer_lastname, departureAirport, arrivalAirport FROM ticket NATURAL JOIN flight NATURAL JOIN lookupflight WHERE ticket_id = %s;'
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

# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------

def trackSpendingLogic(currentDateTime, beginRangeDateTime):
	
	startMonth = beginRangeDateTime.month
	startYear = beginRangeDateTime.year

	endMonth = currentDateTime.month
	endYear = currentDateTime.year

	cursor = conn.cursor()
	query = 'SELECT purchase_date_time, sold_price FROM ticket_purchase WHERE customer_email = %s AND purchase_date_time between %s and %s;'
	cursor.execute(query, (session.get('email'), beginRangeDateTime, currentDateTime))
	ticketInfo = cursor.fetchall()
	# print(ticketInfo)

	monthlySpendingDict = {}

	monthIter = int(startMonth)
	yearIter = int(startYear)

	monthYear = str(yearIter) + "-" + str(monthIter).zfill(2)
	monthlySpendingDict[monthYear] = 0
	
	while(monthIter < int(endMonth) or yearIter < int(endYear)):
		monthIter += 1
		if(monthIter == 13):
			monthIter = 1
			yearIter += 1

		monthYear = str(yearIter) + "-" + str(monthIter).zfill(2)
		monthlySpendingDict[monthYear] = 0
		

	for ticket in ticketInfo:
		month = ticket['purchase_date_time'].month
		year = ticket['purchase_date_time'].year
		monthYear = str(year) + "-" + str(month).zfill(2)
		if(monthYear in monthlySpendingDict):
			monthlySpendingDict[monthYear] += ticket['sold_price']

	ordered_data = sorted(monthlySpendingDict.items(), key = lambda x:datetime.strptime(x[0], '%Y-%m'), reverse=True)

	currentMonth = str(currentDateTime.month).zfill(2)
	currentYear = str(currentDateTime.year)
	currentMonthYear = currentYear + "-" + currentMonth

	beginRangeMonth = str(beginRangeDateTime.month).zfill(2)
	beginRangeYear = str(beginRangeDateTime.year)
	beginRangeMonthYear = beginRangeYear + "-" + beginRangeMonth

	if(beginRangeDateTime >= currentDateTime):
		return render_template('trackspending.html', startingMonth = beginRangeMonthYear, endingMonth = beginRangeMonthYear, ordered_data = [], error = "End date must be after beginning date")
	
	return render_template('trackspending.html', startingMonth = beginRangeMonthYear, endingMonth = currentMonthYear, ordered_data = ordered_data)


@app.route('/trackSpendingRefresh', methods=['GET', 'POST'])
def trackSpendingRefresh():
	begin = request.form['start']
	end = request.form['end']

	beginDateTime = datetime.strptime(begin, "%Y-%m")
	endDateTime = getLastDayOfMonth(end)

	return trackSpendingLogic(endDateTime, beginDateTime)


@app.route('/trackSpending', methods=['GET', 'POST'])
def trackSpending():
	nowMonthYear = str(datetime.now().year) + "-" + str(datetime.now().month)
	return trackSpendingLogic(getLastDayOfMonth(nowMonthYear), getSixMonthsAgo(nowMonthYear))

# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------

def getLastDayOfMonth(monthYear):
	dateTime = datetime.strptime(monthYear, "%Y-%m")
	newMonth = int(dateTime.month)+1
	year = int(dateTime.year)
	newYear = year
	if(newMonth == 13):
		newMonth = 1
		newYear = year + 1

	newMonthYear = str(newYear) + "-" + str(newMonth)
	newDateTime = datetime.strptime(newMonthYear, "%Y-%m")
	newDateTime += timedelta(days=-1)

	return(newDateTime)

# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------

def getSixMonthsAgo(monthYear):
	dateTime = datetime.strptime(monthYear, "%Y-%m")
	newMonth = int(dateTime.month)
	year = int(dateTime.year)
	newYear = year
	for i in range(4):
		newMonth -= 1
		if(newMonth == 0):
			newMonth = 12
			newYear -= 1

	newMonthYear = str(newYear) + "-" + str(newMonth)
	newDateTime = datetime.strptime(newMonthYear, "%Y-%m")
	newDateTime += timedelta(days=-1)

	return(newDateTime)

# ===============================================================================================================



### STAFF USE CASES ###

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
		session['futureFlightPage'] = 1
		session['pastFlightPage'] = 1
		return redirect('/')
	else:
		#returns an error message to the html page
		error = 'Invalid login or email'
		return render_template('login.html', error=error)
	
# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------

# Authenticates the register
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

	cursor = conn.cursor()

	#check password confirmation
	if(password != passwordconfirm):
		error = 'Passwords do not match!'
		query = 'SELECT airline_name FROM airline;'
		cursor.execute(query)
		airlines = cursor.fetchall()
		return render_template('register.html', error=error, airlines=airlines)
	

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
		session['admin'] = airline_name
		session['futureFlightPage'] = 1
		session['pastFlightPage'] = 1

		query = 'INSERT INTO airline_staff VALUES (%s, %s, %s, %s, %s, %s)'
		password = (hashlib.sha256(password.encode('utf-8'))).hexdigest()
		cursor.execute(query, (username, airline_name, password, first_name, last_name, dob))
		cursor.close()
		return redirect('/')
	else:
		if(not airline):
			error = 'Airline is not registered in the system'
		else: 
			error = "Username's already in use."
		query = 'SELECT airline_name FROM airline;'
		cursor.execute(query)
		airlines = cursor.fetchall()
		cursor.close()
		
		return render_template('register.html', error=error, airlines=airlines)

# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------

@app.route('/reviews', methods=['GET', 'POST'])
def reviews():
	fields = homepage_fields()
	
	flight_num = request.form['num']
	departure = request.form['depTime']

	cursor = conn.cursor()
	query = 'SELECT departureAirport, arrivalAirport FROM lookupflight WHERE num = %s AND depTime = %s AND name = %s'
	cursor.execute(query, (flight_num, departure, session.get('admin')))
	flight = cursor.fetchone()

	query = 'SELECT customer_email, rating, comment FROM customer_review NATURAL JOIN flight WHERE departure_date_time = %s AND flight_num = %s AND airline_name = %s'
	cursor.execute(query, (departure, flight_num, session.get('admin')))
	data = cursor.fetchall()

	error = None
	if(data):
		query = 'SELECT round(avg(rating), 1) as average FROM customer_review;'
		cursor.execute(query)
		avg = cursor.fetchone()
		cursor.close()
		return render_template('reviews.html', username = fields[0], admin = fields[3], num=flight_num, departure=departure, flights=data, depArr=flight, avg=avg['average'])
	else:
		cursor.close()
		error = "There are no reviews for this flight yet."
		return render_template('index.html', username = fields[0], myflights = fields[1], myPastFlights = fields[2], admin = fields[3], frequentFliers=fields[4], error = error)

# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------

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
	query = 'UPDATE airplane SET age = (DATEDIFF(NOW(), manufacturing_date)) / 365 WHERE airline_name = %s AND model_num = %s'
	cursor.execute (query, (session.get('admin'), request.form['model_num']))
	cursor.close()

	return redirect('/')

# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------

#Page data for the ticket purchase screen
@app.route('/addFlight')
def addFlight():
	cursor = conn.cursor()
	query = 'SELECT code FROM airport WHERE 1;'
	cursor.execute(query)
	airports = cursor.fetchall()

	return render_template('addflight.html', airports = airports, airline = session.get("admin"))


# adding a new flight to the system
@app.route('/confirmAddFlight', methods = ['GET', 'POST'])
def confirmAddFlight():

	cursor = conn.cursor()
	flight_num = random.randrange(0, 999)
	query = 'SELECT * FROM flight WHERE flight_num = %s AND departure_date_time = %s AND airline_name = %s'
	cursor.execute(query, (flight_num, request.form['departure_date_time'], session.get('admin')))
	exist = cursor.fetchall()
	while exist:
		flight_num = random.randrange(0, 999)
		cursor.execute(query, (flight_num, request.form['departure_date_time'], session.get('admin')))
		exist = cursor.fetchall()

	query = 'SELECT code FROM airport;'
	cursor.execute(query)
	airports = cursor.fetchall()
	
	# enforce domestic/international
	query = 'SELECT * FROM airport WHERE code = %s'
	cursor.execute(query, (request.form['departureAirport']))
	daInfo = cursor.fetchone()

	query = 'SELECT * FROM airport WHERE code = %s'
	cursor.execute(query, (request.form['arrivalAirport']))
	aaInfo = cursor.fetchone()

	if daInfo['type'] == 'domestic':
		if daInfo['country'] != aaInfo['country']:
			error = request.form['departureAirport'] + " only hosts domestic flights!"
			return render_template('addflight.html', airports = airports, airline = session.get("admin"), error=error)
	elif aaInfo['type'] == 'domestic':
		if daInfo['country'] != aaInfo['country']:
			error = request.form['arrivalAirport'] + " only hosts domestic flights!"
			return render_template('addflight.html', airports = airports, airline = session.get("admin"), error=error)
	elif daInfo['type'] == 'international':
		if daInfo['country'] == aaInfo['country']:
			error = request.form['departureAirport'] + " only hosts international flights!"
			return render_template('addflight.html', airports = airports, airline = session.get("admin"), error=error)
	elif aaInfo['type'] == 'international':
		if daInfo['country'] == aaInfo['country']:
			error = request.form['arrivalAirport'] + " only hosts international flights!"
			return render_template('addflight.html', airports = airports, airline = session.get("admin"), error=error)




	# overlap with maintenance
	query = 'SELECT * FROM maintenance WHERE airplane_id = %s AND airline_name = %s AND %s BETWEEN start_date and end_date'
	cursor.execute(query, (request.form['airplane_id'], session.get('admin'), request.form['departure_date_time']))
	exist_start = cursor.fetchall()

	if exist_start:
		error = "There's maintenance schedueld for Plane#" + str(request.form['airplane_id']) + " during the following time periods:"
		return render_template('addflight.html', airports = airports, airline = session.get("admin"), error=error, maintenance=exist_start)
	
	query = 'SELECT * FROM maintenance WHERE airplane_id = %s AND airline_name = %s AND %s BETWEEN start_date and end_date'
	cursor.execute(query, (request.form['airplane_id'], session.get('admin'), request.form['arrival_date_time']))
	exist_end = cursor.fetchall()

	if exist_end:
		error = "There's maintenance schedueld for Plane#" + str(request.form['airplane_id']) + " during the following time periods:"
		return render_template('addflight.html', airports = airports, airline = session.get("admin"), error=error, maintenance=exist_end)


	# overlap with another flight
	query = 'SELECT * FROM flight_arrival NATURAL JOIN flight WHERE airplane_id = %s AND airline_name = %s AND flight_arrival.departure_date_time BETWEEN %s and %s'
	cursor.execute(query, (request.form['airplane_id'], session.get('admin'), request.form['departure_date_time'], request.form['arrival_date_time']))
	exist_start = cursor.fetchall()

	if exist_start:
		print(exist_start)
		error = "Plane#" + str(request.form['airplane_id']) + " is scheduled for the following flights during that time:"
		return render_template('addflight.html', airports = airports, airline = session.get("admin"), error=error, flight=exist_start)
	
	query = 'SELECT * FROM flight_arrival NATURAL JOIN flight WHERE airplane_id = %s AND airline_name = %s AND flight_arrival.arrival_date_time BETWEEN %s and %s'
	cursor.execute(query, (request.form['airplane_id'], session.get('admin'), request.form['departure_date_time'], request.form['arrival_date_time']))
	exist_start = cursor.fetchall()

	if exist_end:
		error = "Plane#" + str(request.form['airplane_id']) + " is scheduled for the following flights during that time:"
		return render_template('addflight.html', airports = airports, airline = session.get("admin"), error=error, flight=exist_end)



	#Insert into airplane
	query = 'INSERT INTO flight VALUES (%s, %s, %s, %s, %s, %s)'
	cursor.execute(query, (flight_num, request.form['departure_date_time'], session.get('admin'), request.form['airplane_id'], request.form['base_price'], "On-Time"))

	query = 'INSERT INTO flight_arrival VALUES (%s, %s, %s, %s, %s)'
	cursor.execute(query, (request.form['arrivalAirport'], flight_num, request.form['departure_date_time'], request.form['arrival_date_time'], session.get('admin')))

	query = 'INSERT INTO flight_departure VALUES (%s, %s, %s, %s)'
	cursor.execute(query, (request.form['departureAirport'], flight_num, request.form['departure_date_time'], session.get('admin')))
	cursor.close()

	return redirect('/')

# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------

@app.route('/frequency', methods=['GET', 'POST'])
def frequency():
	# fields = homepage_fields()
	cursor = conn.cursor()
	query = 'SELECT * FROM ticket WHERE customer_firstname = %s AND customer_lastname = %s AND airline_name = %s'
	cursor.execute(query, (request.form['first'], request.form['last'], session.get('admin')))
	data = cursor.fetchall()
	return render_template('/frequentFliers.html', first=request.form['first'], last=request.form['last'], flights = data)

# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------

@app.route('/earnedRevenue', methods = ['GET', 'POST'])
def earnedRevenue():
	cursor = conn.cursor()
	query = 'SELECT SUM(sold_price) FROM ticket NATURAL JOIN ticket_purchase WHERE airline_name = %s AND purchase_date_time BETWEEN %s and %s;'

	cursor.execute(query, (session.get('admin'), datetime.now() + timedelta(days=-31), datetime.now())) 
	monthly = cursor.fetchone()["SUM(sold_price)"]

	cursor.execute(query, (session.get('admin'), datetime.now() + timedelta(days=-365), datetime.now())) 
	yearly = cursor.fetchone()["SUM(sold_price)"]
	return render_template('/earnedrevenue.html', airline = session.get("admin"), monthly = monthly, yearly = yearly)

# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------

@app.route('/changeStatus', methods=['GET', 'POST'])
def changeStatus():
	cursor = conn.cursor()
	query = 'UPDATE flight SET status = %s WHERE flight_num = %s AND departure_date_time = %s AND airline_name = %s'
	cursor.execute(query, (request.form['status'], request.form['num'], request.form['departure'], session.get('admin')))
	cursor.close()

	return redirect('/')

# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------

@app.route('/seeCustomers', methods=['GET', 'POST'])
def seeCustomers():
	flight_num = request.form['flight_num']
	departure_date = request.form['depTime']
	airline = session.get('admin')

	cursor = conn.cursor()
	query = 'SELECT * FROM ticket WHERE airline_name = %s AND flight_num = %s AND departure_date_time = %s ORDER BY ticket_id'
	cursor.execute(query, (airline, flight_num, departure_date))
	data = cursor.fetchall()
	cursor.close()

	if not data:
		error = "There are no customers in this flight."
		fields = homepage_fields()
		return render_template('index.html', username = fields[0], myFutureFlights = fields[1], myPastFlights = fields[2], admin = fields[3], frequentFliers=fields[4], error=error)
	
	return render_template('/seeCustomers.html', flight_num=flight_num, depDate=departure_date, data=data)

# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------

@app.route('/autoPopulate', methods=['GET', 'POST'])
def autoPopulate():
	cursor = conn.cursor()
	query = 'SELECT code FROM airport WHERE 1;'
	cursor.execute(query)
	airports = cursor.fetchall()
	query = 'SELECT airline_name FROM airline WHERE 1;'
	cursor.execute(query)
	airlines = cursor.fetchall()

	for airline in airlines:
		for i in range(15):
			for airportDepart in airports:
				for airportArrive in airports:
					if(airportArrive == airportDepart):
						continue

					query = 'SELECT airplane_id FROM airplane WHERE airline_name = %s'
					cursor.execute(query, (airline['airline_name']))
					airplane_model = cursor.fetchone()
					
					departureDay = datetime.today().strftime('%Y-%m-%d')
					departureTime = datetime.strptime(departureDay, '%Y-%m-%d') + timedelta(minutes = random.randrange(0, 1440)) + timedelta(days=i)
					arrivalTime = departureTime + timedelta(hours = 6)
					
					flight_num = random.randrange(0, 999)
					query = 'SELECT * FROM flight WHERE flight_num = %s AND departure_date_time = %s AND airline_name = %s'
					cursor.execute(query, (flight_num, departureTime, airline['airline_name']))
					exist = cursor.fetchall()
					while exist:
						flight_num = random.randrange(0, 999)
						cursor.execute(query, (flight_num, departureTime, airline['airline_name']))
						exist = cursor.fetchall()

					query = 'INSERT INTO flight VALUES (%s, %s, %s, %s, %s, %s)'
					cursor.execute(query, (flight_num, departureTime, airline['airline_name'], airplane_model['airplane_id'], random.randint(200, 400), "on-time"))

					query = 'INSERT INTO flight_arrival VALUES (%s, %s, %s, %s, %s)'
					cursor.execute(query, (airportArrive['code'], flight_num, departureTime, arrivalTime, airline['airline_name']))

					query = 'INSERT INTO flight_departure VALUES (%s, %s, %s, %s)'
					cursor.execute(query, (airportDepart['code'], flight_num, departureTime, airline['airline_name']))
	cursor.close()
	return redirect('/')
# ===============================================================================================================

app.secret_key = '4dafc53ee6f057374339199f1dd06f24a3da2f4625bdce8c55dc1e068c283230'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)
