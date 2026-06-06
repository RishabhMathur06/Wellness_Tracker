from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from datetime import datetime
from app.core.database import Base

class Metric(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, default="default_user")
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Emotion & Stress Tracking
    stress_score = Column(Float, default=0.0)    # 0.0 to 10.0
    anxiety_score = Column(Float, default=0.0)   # 0.0 to 10.0
    detected_emotions = Column(JSON, default=list) # e.g. ["calm", "happy"]
    
    # Source can be "image" or "chat"
    source = Column(String, default="chat")
    
    notes = Column(String, nullable=True)
