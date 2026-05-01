import datetime
import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from config import Config

# Ensure the data directory exists within the Docker volume
os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)

Base = declarative_base()

class ScanResult(Base):
    __tablename__ = "scan_results"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(100))
    file_size_kb = Column(Float)
    status = Column(String(20))  # SAFE / SUSPICIOUS
    risk_score = Column(Float)
    reason = Column(Text)
    storage_path = Column(String(1024))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

# SQLite engine optimized for containerized VM hosting
engine = create_engine(
    Config.DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
