from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

engine = create_engine('postgres://danielmc86:Freqm0d+@172.17.0.2/retailProj' , echo=False)

Base.metadata.bind = engine

session = sessionmaker()
session.configure(bind=engine)
s = session()