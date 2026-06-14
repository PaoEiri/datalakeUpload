from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base  # <-- añade declarative_base

from src.config import settings

DATABASE_URL = settings.database_url

engine = create_engine(
    DATABASE_URL,
    future=True,
    echo=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

Base = declarative_base()  # <-- añade esta línea