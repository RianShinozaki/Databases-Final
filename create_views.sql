CREATE VIEW lookUpFlight AS
SELECT flight.airline_name as name, flight.flight_num as num, 	
 	   flight.departure_date_time as depTime, 
       arrival_date_time as arrTime,
       flight.status as status,		
 	   CAST(flight.departure_date_time as DATE) as depDate, 
       CAST(arrival_date_time as DATE) as arrDate,
	   flight_departure.code as departureAirport, 
       flight_arrival.code as arrivalAirport 
FROM flight, flight_departure, flight_arrival
WHERE flight.departure_date_time = flight_departure.departure_date_time
      AND flight_departure.departure_date_time = flight_arrival.departure_date_time;

