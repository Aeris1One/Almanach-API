from sqlmodel import create_engine, SQLModel

from app.core.config import settings

engine = create_engine(str(settings.POSTGRES_DSN))


def init_db():
    SQLModel.metadata.create_all(engine)
