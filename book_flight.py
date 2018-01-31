#!/usr/bin/env python3
import argparse
import requests
import datetime
import string

def getArgs():
	'''Parse the command-line arguments.'''
	parser = argparse.ArgumentParser()
	# arrival airport
	parser.add_argument("--to",
                    help="specify arrival airport", nargs='?', required=True)
	# departure airport
	parser.add_argument("--from",
                    help="specify departure airport",  dest='from_', nargs='?', required=True)
	# date
	parser.add_argument("--date",
                    help="specify departure date", nargs='?', required=True)
    # either one way (default) or return flight
	group_return = parser.add_mutually_exclusive_group()
	group_return.add_argument("--one-way",
                    help="one-way flight", dest='return_', action='store_const', 
                    const=-1, default=-1)
	group_return.add_argument("--return",
                    help="return flight requires the number of nights at the destination", 
                    dest='return_', nargs='?', type=int)                    
	# number of bags
	parser.add_argument("--bags",
                    help="specify number of bags", nargs='?', type=int, default=0)
    # either the cheapest (default) or the fastest flight
	group_priority = parser.add_mutually_exclusive_group()
	group_priority.add_argument("--cheapest",
                    help="choose the cheapest flight", dest='cheapest', action='store_true', default=True)
	group_priority.add_argument("--fastest",
                    help="choose the fastest flight", dest='cheapest', action='store_const', const=False)                
	return parser.parse_args()

def getParams(args):
	'''Create the dictionary with all the parameters needed for the url to search for the flight.'''
	# check that the airport codes only contain alphabetic symbols
	for letter in args.from_ + args.to:
		if letter not in string.ascii_letters:
			print('PLease provide the codes for departure and arrival airports')
			exit(1)
	departure_airport = args.from_
	arrival_airport = args.to
	# check the date format and change it to the format required for the url
	try: 
		year, month, day = (args.date).split('-')
		date_date = datetime.date(int(year), int(month), int(day))
	except:
		print('Please specify the date in the format "YYYY-MM-DD"')
		exit(1)
	urldate = date_date.strftime('%d/%m/%Y')
	# set basic url parameters
	parameters = { 'flyFrom':departure_airport,
			   'to':arrival_airport,
			   'dateFrom':urldate,
			   'dateTo':urldate,
			   'limit':'1'
			 }
	# set additional url parameters
	if args.return_ > 0:
		parameters['typeFlight'] = 'return'
		parameters['daysInDestinationFrom'] = args.return_
		parameters['daysInDestinationTo'] = args.return_
	if not args.cheapest:
		parameters['sort']='duration'
	return parameters

def formJson(bags, token):
	'''Form the json needed to book the flight.'''
	return {
	"bags": bags,
	"passengers": [
    	{
    	"lastName": "Bondarenko",
    	"documentID": "53111111",
    	"phone": "+7 9031111111",
    	"birthday": "1983-07-07",
    	"nationality": "RU",
    	"firstName": "Elena",
    	"title": "Mrs",
    	"email": "elleno@yandex.ru"
    	}
		],
	"currency": "CZK",
	"booking_token": token
	}

def searchForFlight(parameters):
	'''Look for the flight via Kiwi.com API.'''
	# connect to the search API
	try:
		r = requests.get('https://api.skypicker.com/flights', params=parameters, timeout=1)
	except:
		print("Could not find the flight. Got no response from the server.")
		exit(1)
 	# parse the json provided by the server
	try:
		token = r.json()['data'][0]['booking_token']
	except:
		print("Search failed. Server's reply has unexpected format.")
		exit(1)
	return token

def bookFlight(values):
	'''Book the flight and return the confirmation code.'''
	headers = {'Content-Type': 'application/json'}
	url = "http://128.199.48.38:8080/booking?"
	# connect to the booking API
	try:
		booking = requests.post(url, json=values, headers=headers, timeout=10)
	except:	
		print("Could not book the flight. Got no response from the server.")
		exit(1)
	# parse the json provided
	try:
		final_json = booking.json()
		confirmation = final_json['pnr']
	except:
		print("Booking failed. Server's reply has unexpected format.")
		exit(1)
	return confirmation

#parse the arguments
args = getArgs()
# look for the flight
token = searchForFlight(getParams(args))

# prepare the data needed for the booking
bags = args.bags
values = formJson(bags, token)

# book the flight and print the confirmation code
confirmation = bookFlight(values)
print(confirmation)

