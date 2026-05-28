from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from core.config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class WebhookModel(Base):
    __tablename__ = "webhooks"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(String)
    metodo = Column(String)
    acao = Column(String)
    payload = Column(Text)
    headers = Column(Text)
    ip_origem = Column(String)
    data_criacao = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()