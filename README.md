# CS-UY 3038 : Airport Database
## by : Anna Tanaka Viertler (at5076@nyu.edu) & Kai Shinozaki-Conefrey (krs8750@nyu.edu)

### Home page when not logged-in:
When the user is not logged-in, the following cases should be available in the home page:
1. ✅ `View Public Info`: All users, whether logged in or not, can:
    - Search for future flights based on source city/airport name, destination city/airport name,
departure date for one way (departure and return dates for round trip).
    - Will be able to see the flights status based on airline name, flight number, arrival/departure
date.
2.  `Register`: 2 types of user registrations (Customer, and Airline Staff) option via forms as mentioned in
the part 1 of the project.
3. ✅ `Login`: 2 types of user login (Customer, and Airline Staff). Users enters their username (email address
will be used as username for customer) - x, and password - y, via forms on login page. This data is sent
as POST parameters to the login-authentication component, which checks whether there is a tuple in
the corresponding user’s table with username=x and the password = md5(y) :
    - If so, login is successful. A session is initiated with the member’s username stored as a
session variable. 
        - Optionally, you can store other session variables. Control is redirected to a
component that displays the user’s home page.
    - If not, login is unsuccessful. A message is displayed indicating this to the user.
Once a user has logged in, reservation system should display his/her home page according to user’s
role. Also, after other actions or sequences of related actions, are executed, control will return to
component that displays the home page. The home page should display an error message if the previous
action was not successful.
Some mechanism for the user to choose the use case he/she wants to execute:
        - You may choose to provide links to other URLs that will present the interfaces for other use cases, or
you may include those interfaces directly on the home page.

> Any other information you’d like to include:
For example, you might want to show customer's future flights information on the customer's home
page, or you may prefer to just show them when he/she does some of the following use cases.

### Customer use cases:
After logging in successfully a user(customer) may do any of the following use cases:

1. ✅ `View My flights`: Provide various ways for the user to see flights information which he/she purchased.
The default should be showing for the future flights. Optionally you may include a way for the user to
specify a range of dates, specify destination and/or source airport name or city name etc.

2. ✅ `Search for flights`: Search for future flights (one way or round trip) based on source city/airport name,
destination city/airport name, dates (departure or return).

3. `Purchase tickets`: Customer chooses a flight and purchase ticket for this flight, providing all the
needed data, via forms. You may find it easier to implement this along with a use case to search for
flights.

4. `Cancel Trip`: Customer chooses a purchased ticket for a flight that will take place more than 24 hours
in the future and cancel the purchase. After cancellation, the ticket will no longer belong to the
customer. The ticket will be available again in the system and purchasable by other customers.

5. `Give Ratings and Comment on previous flights`: Customer will be able to rate and comment on their
previous flights (for which he/she purchased tickets and already took that flight) for the airline they
logged in.

6. `Track My Spending`: Default view will be total amount of money spent in the past year and a bar
chart/table showing month wise money spent for last 6 months. He/she will also have option to specify
a range of dates to view total amount of money spent within that range and a bar chart/table showing
month wise money spent within that range.

7. ✅ `Logout`: The session is destroyed and a “goodbye” page or the login page is displayed.

### Airline Staff use cases:
After logging in successfully an airline staff may do any of the following use cases:

1. `View flights`: Defaults will be showing all the future flights operated by the airline he/she works for
the next 30 days. He/she will be able to see all the current/future/past flights operated by the airline
he/she works for based range of dates, source/destination airports/city etc. He/she will be able to see
all the customers of a particular flight.

2. `Create new flights`: He or she creates a new flight, providing all the needed data, via forms. The
application should prevent unauthorized users from doing this action. While creating a flight, a check
should be performed that if an airport is domestic, it should only be able to handle domestic flights, and
same applies for international airports. 

> [Note]
> Defaults will be showing all the future flights operated by the airline he/she works for the next 30 days.

3. `Change Status of flights`: He or she changes a flight status (from on-time to delayed or vice versa) via
forms.

4. `Add airplane in the system`: He or she adds a new airplane, providing all the needed data, via forms.
The application should prevent unauthorized users from doing this action. In the confirmation page,
she/he will be able to see all the airplanes owned by the airline he/she works for.

5. `Add new airport in the system`: He or she adds a new airport, providing all the needed data, via
forms. The application should prevent unauthorized users from doing this action.

6. `View flight ratings`: Airline Staff will be able to see each flight’s average ratings and all the comments
and ratings of that flight given by the customers.

7. `Schedule Maintenance`: Airline staff should be able to schedule maintenance (by providing start date
and time and end date and time) for a particular airplane (identified by airline name and airplane id).
Airplanes under maintenance cannot be assigned to a flight during the maintenance period.

8. `View frequent customers`: Airline Staff will also be able to see the most frequent customer within
the last year. In addition, Airline Staff will be able to see a list of all flights a particular Customer has
taken only on that particular airline.

9. `View Earned Revenue`: Show total amount of revenue earned from ticket sales in the last month and
last year.

10. ✅ `Logout`: The session is destroyed and a “goodbye” page or the login page is displayed