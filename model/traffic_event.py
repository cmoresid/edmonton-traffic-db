from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from base import Base
from site import Site

class TrafficEvent(Base):
    __tablename__ = 'traffic_event'
    
    site_id = Column(String, ForeignKey('site.site_id'), primary_key=True)
    site = relationship(Site)
    
    event_date_time = Column(DateTime, nullable=False, primary_key=True)
    direction = Column(String(3), nullable=False, primary_key=True)
    count = Column(Integer, nullable=False)
