from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from traffic_data_processor import TrafficDataProcessor
from config import settings

from model.base import Base
from model.site import Site
from model.traffic_event import TrafficEvent

import os, sqlalchemy

class TrafficDataDBImport():
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
        traffic_events = processor.process_data_files(file_names)

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