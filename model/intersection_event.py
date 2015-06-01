from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Sequence
from sqlalchemy.orm import relationship
from base import Base
from model.site import Site


class IntersectionEvent(Base):
    """Represents a traffic monitoring event."""
    __tablename__ = 'intersection_event'

    id = Column(Integer, Sequence('seq_intersection_event_id', start=1, increment=1), primary_key=True)
    site_id = Column(String, ForeignKey('site.site_id'), nullable=True)
    site = relationship(Site)

    event_type = Column(String(50), nullable=False)
    event_date_time = Column(DateTime, nullable=False)
    direction = Column(String(3), nullable=False)
    turn_direction = Column(String(1), nullable=True)
    count = Column(Integer, nullable=False)
