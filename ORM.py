import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from geoalchemy2 import Geometry
from traffic_data_import import *
from traffic_data_process import *

Base = declarative_base()

class Site(Base):
    __tablename__ = 'site'
    
    site_id = Column(Integer, primary_key = True)
    location = Column(Geometry(geometry_type='POINT'), nullable=False)
    adt = Column(Integer, nullable = True)
    
class TrafficEvent(Base):
    __tablename__ = 'traffic_event'
    
    site_id = Column(Integer, ForeignKey('site.site_id'), primary_key=True)
    site = relationship(Site)
    
    event_date_time = Column(DateTime, nullable=False, primary_key=True)
    direction = Column(String, nullable=False, primary_key=True)
    count = Column(Integer, nullable=False)

from sqlalchemy import create_engine
engine = create_engine('postgresql://localhost/traffic')
 
from sqlalchemy.orm import sessionmaker
session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)

files = ['003 Avenue SW West of 058 Street SW 2012-Jun-23.xls']
traffic_events = process_data_files(files)

session_import = session()
    
for traffic_event in traffic_events:
    session_import.add(traffic_event)
    
session_import.commit()