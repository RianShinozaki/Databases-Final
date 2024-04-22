#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import random
import datetime

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
	username = session.get('username')
	myflights = []
	if(session.get('username')):
		cursor = conn.cursor()
		query = 'SELECT name, num, depTime, arrTime FROM lookUpFlight, ticket WHERE ticket.customer_email = %s AND ticket.flight_num = lookupflight.num;'
		cursor.execute(query, (session.get('username')))
		myflights = cursor.fetchall()
		error = None
		if(myflights):
			print(myflights)
			cursor.close()
	return (username, myflights)

@app.route('/')
def hello():
	fields = homepage_fields()
	return render_template('index.html', username = fields[0], myflights = fields[1])

@app.route('/login')
def login():
	return render_template('login.html')

@app.route('/logout')
def logout():
	session.pop('username')
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
		for flight in data:
			print(flight['depTime'])
		cursor.close()
		return render_template('index.html', username = fields[0], myflights = fields[1], flights=data)
	else:
		error = "No flights match those parameters at this time."
		return render_template('index.html', username = fields[0], myflights = fields[1], error = error)


#Authenticates the login
@app.route('/customerLoginAuth', methods=['GET', 'POST'])
def customerLoginAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM customer WHERE customer_email = %s and password = %s'
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
		return redirect('/')
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('login.html', error=error)
	
#Authenticates the login
@app.route('/employeeLoginAuth', methods=['GET', 'POST'])
def employeeLoginAuth():
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
		return redirect(url_for('/'))
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('login.html', error=error)

#Takes you to the ticket purchase screen and saves flight_num in question
@app.route('/selectTicket', methods=['GET', 'POST'])
def selectTicket():
	flight_num = request.form['flight_num']
	session['selected_flight'] = flight_num
	print(flight_num)
	return redirect('ticketPurchase')

#Page data for the ticket purchase screen
@app.route('/ticketPurchase')
def purchaseTicket():
	cursor = conn.cursor()
	query = 'SELECT name, num, depTime, arrTime FROM lookUpFlight WHERE num = %s;'
	cursor.execute(query, (session.get('selected_flight')))
	flightInfo = cursor.fetchall()
	error = None
	print(flightInfo)
	print(flightInfo)
	cursor.close()
	return render_template('ticketpurchase.html', flightInfo = flightInfo)

#When you press "purchase" on the ticket screen
@app.route('/confirmPurchaseTicket', methods = ['GET', 'POST'])
def confirmPurchaseTIcket():
	cursor = conn.cursor()
	# This doesn't guarantee unique tickets, so we should look into that
	ticketid = random.randrange(0, 99999)

	#Insert into ticket_purchase using ticket ID
	query = 'INSERT INTO ticket_purchase VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
	cursor.execute(query, (ticketid, session.get('username'), datetime.datetime.now(), request.form.get('cardtype'), request.form['cardnumber'], request.form['cardfirstname'], request.form['cardlastname'], request.form['cardexpirationdate'], 100.00))

	#Get more flight info using saved flight num
	query = 'SELECT name, num, depTime, arrTime FROM lookUpFlight WHERE num = %s;'
	cursor.execute(query, (session.get('selected_flight')))
	flightInfo = cursor.fetchone()

	#Insert into ticket
	query = 'INSERT INTO ticket VALUES (%s, %s, %s, %s, %s, %s, %s)'
	cursor.execute(query, (ticketid, session.get('selected_flight'), flightInfo['depTime'],session.get('username'), request.form['firstname'], request.form['lastname'], request.form['birthday']))
	cursor.close()

	session.pop('selected_flight')
	return redirect('/')

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
