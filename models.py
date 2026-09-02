from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

class AdSuggestion(Base):
    __tablename__ = "ad_suggestions"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(String, index=True)
    ad_id = Column(String, index=True)
    suggested_action = Column(String) # e.g., "PAUSE", "INCREASE_BUDGET"
    reason = Column(String)
    status = Column(String, default="PENDING") # PENDING, APPROVED, REJECTED
    created_at = Column(DateTime, default=datetime.utcnow)
