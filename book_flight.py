#!/usr/bin/env python3
import argparse
import requests
import datetime
import string

def getArgs():
	'''Parse the command-line arguments'''
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
    # either one way or return flight
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
    # either the cheapest or fastest flight
	group_priority = parser.add_mutually_exclusive_group()
	group_priority.add_argument("--cheapest",
                    help="choose the cheapest flight", dest='cheapest', action='store_true', default=True)
	group_priority.add_argument("--fastest",
                    help="choose the fastest flight", dest='cheapest', action='store_const', const=False)                
	return parser.parse_args()

def getParams():
	'''Create the dictionary with all the parameters needed for the url to search for the flight'''
	args = getArgs()
	for letter in args.from_ + args.to:
		if letter not in string.ascii_letters:
			print('PLease provide the codes for departure and arrival airports')
			exit(1)
	departure_airport = args.from_
	arrival_airport = args.to
	# change the date format
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
	bags = args.bags
	return (parameters, bags)

def formJson(bags, token):
	'''Form the json needed to book the flight'''
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


# look for the flight
parameters, bags = getParams()
try:
	r = requests.get('https://api.skypicker.com/flights', params=parameters, timeout=7)
except:
	print("Could not find the flight. Got no response from the server.")
	exit(1)
 
try:
	token = r.json()['data'][0]['booking_token']
except:
	print("Search failed. Server's reply has unexpected format.")
	exit(1)

# prepare the data needed for the booking
values = formJson(bags, token)
headers = {'Content-Type': 'application/json'}
url = "http://128.199.48.38:8080/booking?"

# book the flight
try:
	booking = requests.post(url, json=values, headers=headers, timeout=7)
except:	
	print("Could not book the flight. Got no response from the server.")
	exit(1)

try:
	final_json = booking.json()
	print(final_json['pnr'])
except:
	print("Booking failed. Server's reply has unexpected format.")
	exit(1)
