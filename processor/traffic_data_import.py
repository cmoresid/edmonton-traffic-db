from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from traffic_data_processor import TrafficDataProcessor
from config import settings

from model.base import Base
from model.site import Site
from model.traffic_event import TrafficEvent

class TrafficDataDBImport():
    def traffic_data_import(self, files):
        engine = create_engine(settings['db_connection'])

        session = sessionmaker()
        session.configure(bind=engine)
        Base.metadata.create_all(engine)    

        processor = TrafficDataProcessor()
        traffic_events = processor.process_data_files(files)

        session_import = session()
    
        for traffic_event in traffic_events:
            session_import.add(traffic_event)
        
        session_import.commit()
