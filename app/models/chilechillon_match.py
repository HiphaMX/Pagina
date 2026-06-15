from sqlalchemy import Column, Integer, String
from app.core.database import Base

class ChileChillonMatch(Base):
    __tablename__ = "chilechillon_matches"

    id = Column(Integer, primary_key=True, index=True)
    phase = Column(String, nullable=False)
    teamA = Column(String, nullable=True)
    teamB = Column(String, nullable=True)
    scoreA = Column(Integer, nullable=True)
    scoreB = Column(Integer, nullable=True)
    status = Column(String, nullable=False, default="upcoming")
