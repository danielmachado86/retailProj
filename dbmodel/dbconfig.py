from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

engine = create_engine('postgres://qbxzyxxpozarvq:23893424c889d724ff47f9659e95936bbac79f055c42787cc9a3388c19f5916c@ec2-54-197-249-140.compute-1.amazonaws.com/d122dfvdltfe2s' , echo=False)

Base.metadata.bind = engine

session = sessionmaker()
session.configure(bind=engine)
s = session()