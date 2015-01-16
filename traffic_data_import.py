from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def traffic_data_import(events):
    engine = create_engine('postgresql://localhost/traffic')
    
    session = sessionmaker()
    session.configure(bind=engine)

    session_import = session()
    
    for traffic_event in events:
        session_import.add(traffic_event)
    
    session_import.commit()

