from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from traffic_data_processor import TrafficDataProcessor
from config import settings

from model.base import Base
from model.site import Site
from model.traffic_event import TrafficEvent

import os, sqlalchemy

class TrafficDataDBImport():
    def traffic_data_import(self, files):
        engine = create_engine(settings['db_connection'])

        session = sessionmaker()
        session.configure(bind=engine)
        Base.metadata.create_all(engine)    

        processor = TrafficDataProcessor()
        traffic_events = processor.process_data_files(files)

        session_import = session()
        log_file = open('error_log.txt', 'w+')
    
        print 'Importing processed data into database...'
        
        for traffic_event in traffic_events:
            session_import.merge(traffic_event)

            try:
                session_import.commit()
            except sqlalchemy.exc.IntegrityError as ex:
                print 'EXCEPTION: %s' % (ex.message)
                log_file.write('EXCEPTION: %s\n' % (ex.message))
                session_import.rollback()

        log_file.close()