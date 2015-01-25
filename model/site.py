from sqlalchemy import Column, Integer, String
from geoalchemy2 import Geometry
from base import Base

class Site(Base):
	"""Represents a traffic monitoring site; which usually
	an intersection.
	"""
    __tablename__ = 'site'
    
    site_id = Column(String, primary_key=True)
    address = Column(String, nullable=False)
    location = Column(Geometry(geometry_type='POINT', srid=4326), nullable=True)
    adt = Column(Integer, nullable = True)

