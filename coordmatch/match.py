from xml.etree import ElementTree as ET
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from model.base import Base
from model.site import Site

from fuzzywuzzy import fuzz

import re

THRESHOLD = 100

def get_coords(point_node):
	lng = point_node.find('./ExtendedData/Data[@name="Longitude"]/value').text
	lat = point_node.find('./ExtendedData/Data[@name="Lattitude"]/value').text

	return 'SRID=4326;POINT(%s %s)' % (lng, lat)

def match_from_kml():
	log = open('match_log.txt', 'w+')

	tree = ET.parse('coordmatch/traffic_sites.xml')
	points = tree.getroot().findall('./Document/Placemark')
	regex = re.compile(r'(?P<addr>\d{1,3}[a-z]? (?:street|avenue)(?: nw| sw)?)')

	point_addresses = map(lambda point: point.find('name').text.strip(), points)
	normalized_point_addresses = map(normalize_address, point_addresses)

	engine = create_engine('postgresql://localhost/traffic')
	session = sessionmaker()
	session.configure(bind=engine)
	Base.metadata.create_all(engine)
	qsession = session()

	sites_from_db = qsession.query(Site).all()
	for site in sites_from_db:
		site_address = normalize_address(site.address)

		results = []
		for index, address in enumerate(normalized_point_addresses):
			score = fuzz.ratio(site_address, address)

			if score >= THRESHOLD:
				results.append((index, address, score))

		if len(results) == 0:
			log.write('*** No match found for database entry \'%s\' in KML.\n' % (site.address,))
		elif len(results) == 1:
			# Get results
			index, address, ratio = results.pop()
			# Remove point from search space.
			kml_point = points.pop(index)
			kml_address = kml_point.find('./name').text

			normalized_point_addresses.pop(index)
			# Set the site's location
			site.location = get_coords(kml_point)
			# Save to database
			qsession.merge(site)
			qsession.commit()

			log.write('* Matched \'%s\' in database -> \'%s\' in KML with %f match.\n' % (site.address, kml_address, ratio))
		else:
			log.write('*** More than one match found for \'%s\'. Asking user to decide.\n' % (site.address,))
			print '*** More than one match found for \'%s\'\n\n' % (site.address,)

			for index, (point_index, address, ratio) in enumerate(results):
				print '%d. \'%s\' -> %f%% match.' % (index, points[point_index].find('./name').text, ratio)

			print '\nEnter your choice: '
			choice = int(raw_input())

			index, _, ratio = results[choice]

			# Remove point from search space.
			kml_point = points.pop(index)
			kml_address = kml_point.find('./name').text

			normalized_point_addresses.pop(index)
			#Set the site's location.
			site.location = get_coords(kml_point)
			# Save to database.
			qsession.merge(site)
			qsession.commit()

			log.write('* Matched \'%s\' in database -> \'%s\' in KML with %f match.\n' % (site.address, kml_address, ratio))

	log.close()

def normalize_address(entry):
	address_regex = re.compile(r'(?P<addr>\d{1,3}[a-z]? (?:street|avenue)(?: nw| sw)?)')

	return ' and '.join(sanatize_entry(entry, address_regex))

def sanatize_entry(entry, regex):
	entry = re.sub(r'( north | west | east | south | northbound | southbound | eastbound | westbound |of|and)', '', entry.lower())
	entry = filter(lambda x: len(x) > 0, re.sub(r'\s+', ' ', entry))
`
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
