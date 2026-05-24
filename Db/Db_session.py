from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings import DATABASE_URL
from db.models import Base

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

async def init_db():
    Base.metadata.create_all(engine)
