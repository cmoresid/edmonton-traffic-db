from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from processor.traffic_data_processor import TrafficDataProcessor
from config import settings

from model.base import Base
from model.site import Site
from model.traffic_event import TrafficEvent

import os, sqlalchemy

class TrafficDataDBImport():
    def __init__(self):
        self._processor = TrafficDataProcessor()

    """Orchestration class used to create and insert database records
    based on the in-memory representation of the traffic events and
    sites extracted from the traffic report spreadsheets.
    """
    def traffic_data_import(self, file_names):
        """Creates an in-memory representation of the traffic events
        and sites from the traffic report spreadsheets and imports them
        into a database.

        Keyword arguments:
        file_names -- A list of file paths for traffic report spreadsheets
                      to import into the database.
        """
        # Open a connection to the database and a session
        # to interact with the database.
        engine = create_engine(settings['db_connection'])
        session = sessionmaker()
        session.configure(bind=engine)
        Base.metadata.create_all(engine)    

        # Create an in-memory representation of the traffic events
        # and sites from the 
        processor = TrafficDataProcessor()
        traffic_events = self._processor.process_data_files(file_names)

        session_import = session()
        log_file = open('error_log.txt', 'w+')
    
        print 'Importing processed data into database...'
        
        for traffic_event in traffic_events:
            # Merge existing foreign key relations
            # as to not cause a duplicate key error
            # for shared 'site' objects.
            session_import.merge(traffic_event)

            try:
                session_import.commit()
            except sqlalchemy.exc.IntegrityError as ex:
                # This exception occurs when we try to import a
                # traffic event that has been mislabeled in the
                # spreadsheet. For some of the spreadsheets, the name
                # of the spreadsheet may be '... 2012-May-05.xls' but
                # inside the spreadsheet the date cells may contain
                # 2013-May-05. May 5, 2013 is already inside the database,
                # so this exception happens. You have to manually go through
                # the spreadsheets and update the date fields.
                print 'EXCEPTION: %s' % (ex.message)
                log_file.write('EXCEPTION: %s\n' % (ex.message))
                session_import.rollback()

        log_file.close()

    def traffic_metadata_import(self, metadata_sheet_file_name):
        engine = create_engine(settings['db_connection'])
        session = sessionmaker()
        session.configure(bind=engine)
        Base.metadata.create_all(engine)
        session_q = session()

        site_metadata = self._processor.process_metadata_file(metadata_sheet_file_name)

        for metadata_site in site_metadata:
            site = session_q.query(Site).filter(Site.site_id == metadata_site.site_id).first()

            if (site == None):
                continue

            site = self.__map(metadata_site, site)
            session_q.merge(site)

            try:
                session_q.commit()
            except:
                print 'EXCEPTION: %s' % (ex.message)
                session_q.rollback()

    def __map(self, metadata_site, db_site):
        db_site.street_type = metadata_site.street_type
        db_site.category = metadata_site.category
        db_site.in_service = metadata_site.in_service
        db_site.county = metadata_site.county
        db_site.jurisdiction = metadata_site.jurisdiction
        db_site.primary_purpose = metadata_site.primary_purpose

        return db_site
