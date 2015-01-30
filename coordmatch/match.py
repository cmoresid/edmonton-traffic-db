from xml.etree import ElementTree as ET
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from model.base import Base
from model.site import Site

from fuzzywuzzy import fuzz

import re

def get_all_site_ids():
	tree = ET.parse('coordmatch/traffic_sites.xml')
	site_ids = map(lambda val: val.text, tree.getroot().findall('./Document/Placemark/ExtendedData/Data[@name="Site Number"]/value'))

	return site_ids

def find_all_matches(site_ids):
	engine = create_engine('postgresql://localhost/traffic')
	session = sessionmaker()
	session.configure(bind=engine)
	Base.metadata.create_all(engine)

	qsession = session()

	results = qsession.query(Site).filter(Site.site_id.in_(site_ids)).all()

	return results

def match():
	log = open('missing_log.txt', 'w+')

	tree = ET.parse('coordmatch/traffic_sites.xml')
	points = tree.getroot().findall('./Document/Placemark')

	engine = create_engine('postgresql://localhost/traffic')
	session = sessionmaker()
	session.configure(bind=engine)
	Base.metadata.create_all(engine)
	qsession = session()

	regex = re.compile(r'(?P<addr>\d{1,3} (?:street|avenue)(?: nw| sw)?)')

	for point in points:
		address =  point.find('name').text.strip()
		address_components = ' '.join(address.split(' ')[:2])

		partial_matches = qsession.query(Site).filter(Site.address.like('%' + address_components + '%')).all()

		print 'Looking for ', address, '...'

		matches = []
		for pmatch in partial_matches:
			pmatch_address = pmatch.address.lower().replace('of', 'and')
			
			ratio = fuzz.token_sort_ratio(address.lower(), pmatch_address)

			if (ratio > 80):
				matches.append((pmatch, ratio))

		num_of_matches = len(matches)
		print matches
		if num_of_matches > 0:
			print '\nMATCHES FOUND: \n'

			for i in range(num_of_matches):
				print '%d. %s -- %f' % (i+1, matches[i][0].address, matches[i][1])

			print '\nEnter your choice: '
			choice = int(raw_input())

			if (choice == 0):
				log.write(point.find('name').text + "\n")
			else:
				match = matches[choice-1][0]
				match.location = get_coords(point)

				qsession.merge(match)
				qsession.commit()
		else:
			log.write(point.find('name').text + "\n")

	log.close()

def get_coords(point_node):
	lng = point_node.find('./ExtendedData/Data[@name="Longitude"]/value').text
	lat = point_node.find('./ExtendedData/Data[@name="Lattitude"]/value').text

	return 'SRID=4326;POINT(%s %s)' % (lng, lat)

def sanatize_db_entry(entry, regex):
	entry = re.sub(r'( north | west | east| south |of|and)', '', entry.lower())
	entry = filter(lambda x: len(x) > 0, re.sub(r'\s+', ' ', entry))

	matches = regex.finditer(entry)

	tokens = []
	for match in matches:
		tokens.append(match.group())
		entry = filter(lambda x: x != '', entry.rsplit(entry[match.start():match.end()]))[0]

	tokens.append(entry.strip())

	if len(tokens) == 1 and tokens[0] == entry:
		tokens = entry.split(' ')

	return tokens
