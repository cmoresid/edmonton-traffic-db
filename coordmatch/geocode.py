import pandas
import re
import requests
import csv
import json

def normalize_address(entry):
	address_regex = re.compile(r'(?P<addr>\d{1,3}[a-z]? (?:street|avenue)(?: nw| sw)?)')

	return ' and '.join(sanatize_entry(entry, address_regex))

def sanatize_entry(entry, regex):
	entry = re.sub(r'( north | west | east | south | northbound | southbound | eastbound | westbound |of|and)', '', entry.lower())
	entry = filter(lambda x: len(x) > 0, re.sub(r'\s+', ' ', entry))

	matches = regex.finditer(entry)

	tokens = []
	for match in matches:
		tokens.append(match.group())
		entry = entry.replace(match.group(), '')

	if len(entry.strip()) > 0:
		tokens.append(entry.strip())

	if len(tokens) == 1 and tokens[0] == entry:
		tokens = entry.split(' ')

	return tokens

def get_oauth_token():
	# generate a token with your client id and client secret
	return requests.post('https://www.arcgis.com/sharing/rest/oauth2/token/', params={
  		'f': 'json',
  		'client_id': 'z1UwM6gUPmUW377v',
  		'client_secret': '9cd2f2a8455348deb36b3f182f98102c',
  		'grant_type': 'client_credentials',
  		'expiration': '1440'
	}).json()['access_token']

def serialize_to_object():
	records = []

	with open('dump.csv', 'rb') as csvfile:
		data = csv.reader(csvfile, delimiter=',', quotechar='"')
		data.next()

		for index, site in enumerate(data):
			try:
				objectId = int(site[0])
			except ValueError:
				objectId = site[0]

			geocodeObject = {
				"attributes": {
					"OBJECTID": objectId,
					"SingleLine": normalize_address(site[1]) + ", Edmonton, Alberta, Canada"
				}
			}

			records.append(geocodeObject)

	return records

def divide_into_groups(records, batch_size):
	for i in xrange(0, len(records), batch_size):
		yield records[i:i+batch_size]

def begin_geocode():
	records = serialize_to_object()
	batch_iter = divide_into_groups(records, 15)
	token = get_oauth_token()
	location_results = []

	for batch in batch_iter:
		json_payload = json.dumps({ 'records': batch })
		
		print json_payload

		response = requests.post('http://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/geocodeAddresses', params={
  			'f': 'pjson',
  			'token': token,
  			'addresses': json_payload,
  			'sourceCountry': 'CAN',
  			'forStorage': True,
  			'category': 'Address'
		})

		if (response.status_code != 200):
			print response.content

		results = response.json()

		for location_result in results['locations']:
			location_result = location_result['attributes']

			location = { 'site_id': location_result['ResultID'], 
				'location': 'SRID=4326;POINT(%s %s)' % (location_result['X'], location_result['Y']),
				'accuracy': location_result['Score'],
				'matched_addr': location_result['Match_addr']
			}

			with open('data.json', 'a+') as f:
				json.dump(location, f)

			location_results.append(location)

	return location_results

def cleanup_file():
	json_data = open('data.json')
	data = json.load(json_data)

	results = [dict(p) for p in set(tuple(i.items()) for i in data)]
	results = filter(lambda x: x['matched_addr'] != u'', results)

	with open('data_cleanup.json', 'w+') as f:
		json.dump(results, f)
	
	return results

def generate_sql():
	json_data = open('data_cleanup.json')
	data = json.load(json_data)

	with open('update.sql', 'w') as outfile:
		for site in data:
			sql_statement = "UPDATE site SET location='%s' WHERE site_id = '%s';\n" % (site['location'],site['site_id'])
			outfile.write(sql_statement)


