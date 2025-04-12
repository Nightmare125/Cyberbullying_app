# app/db/models.py
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, TIMESTAMP
from datetime import datetime
from app.db.database import Base, engine

Base.metadata.create_all(bind=engine)
class User(Base):
    __tablename__ = "users"

    UserID = Column(Integer, primary_key=True, index=True)
    Username = Column(String(255), unique=True)
    Email = Column(String(255), unique=True)
    Password = Column(String(255))
    IsAdmin = Column(Boolean, default=False)

class Post(Base):
    __tablename__ = "posts"

    PostID = Column(Integer, primary_key=True, index=True)
    UserID = Column(Integer)
    Content = Column(Text)
    Timestamp = Column(TIMESTAMP, default=datetime.utcnow)
    IsAbusive = Column(Boolean, default=False)


class Report(Base):
    __tablename__ = "reports"

    ReportID = Column(Integer, primary_key=True, index=True)
    PostID = Column(Integer)
    Status = Column(Boolean, default=False)
    Timestamp = Column(TIMESTAMP, default=datetime.utcnow)
