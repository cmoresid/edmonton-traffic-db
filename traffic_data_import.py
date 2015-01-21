from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from traffic_data_processor import TrafficDataProcessor

from model.base import Base
from model.site import Site
from model.traffic_event import TrafficEvent

def traffic_data_import(files):
    engine = create_engine('postgresql://localhost/traffic')

    session = sessionmaker()
    session.configure(bind=engine)
    Base.metadata.create_all(engine)    

    processor = TrafficDataProcessor()
    traffic_events = processor.process_data_files(files)

    session_import = session()
    
    for traffic_event in traffic_events:
        session_import.add(traffic_event)
        
    session_import.commit()

traffic_data_import(['ABRoad.xls','009-2014-Jul.xls'])