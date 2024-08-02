from sqlmodel import Session, create_engine, select

from app.core.config import settings

engine = create_engine(str(settings.POSTGRES_DSN))
